from maya.api import OpenMaya
from SkinningTools.Maya.tools import shared, weightMath, weightWrite

CONTEXT_INIT = "paintAverageWghtCtxInitialize"
CONTEXT_UPDATE = "paintAverageWghtCtxUpdate"
kCreator = "Trevor van Hoof & Perry Leijten"
kVersion = "1.0.20200831"

def maya_useNewAPI():
    pass


class AverageWghtCtx(object):
    def __init__(self):
        self.reset()

    def initialize(self, obj):
        if not obj:
            self.reset()
            return

        self.dag = shared.getDagpath(obj, True)
        self.obj = self.dag.node()

        self.skinCluster = shared.getMfnSkinCluster(self.dag)

        maxInfPLG = self.skinCluster.findPlug("maxInfluences", True)
        normalizePLG = self.skinCluster.findPlug("normalizeWeights", True)
        mainTainPLG = self.skinCluster.findPlug("maintainMaxInfluences", True)

        self.maxInfluences = maxInfPLG.asInt()
        self.normalize = normalizePLG.asInt()
        self.maintainMaxInfl = mainTainPLG.asBool()

        self.infl = self.skinCluster.influenceObjects()

    def reset(self):
        self.obj = None
        self.dag = None
        self.skinCluster = None

        self.maxInfluences = 0
        self.normalize = 0
        self.maintainMaxInfl = False

        self.infl = OpenMaya.MDagPathArray()

    def calcWeights(self, value, origWeights, nbWeigths, influences, amountComps):
        if len(influences) != len(origWeights):
            raise ValueError('Smoothing weight dimensions do not match')
        weights = weightMath.blendWeights(value, origWeights, nbWeigths, amountComps,
            normalize=self.normalize == 1,
            maximum=self.maxInfluences if self.maintainMaxInfl else None,
            locked=getattr(self, 'locked', None))
        return weights, influences

    def setWeights(self, index, value):
        if self.obj is None:
            return [None] * 5
        if index < 0 or index >= OpenMaya.MFnMesh(self.dag).numVertices:
            raise ValueError('Invalid smoothing vertex')
        singleIdComp = OpenMaya.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
        singleIdComp.addElement(index)
        origWeights = self.skinCluster.getWeights(self.dag, vertexComp)[0]
        iterator = OpenMaya.MItMeshVertex(self.dag)
        iterator.setIndex(index)
        neighbors = iterator.getConnectedVertices()
        componentFn = OpenMaya.MFnSingleIndexedComponent()
        neighborComp = componentFn.create(OpenMaya.MFn.kMeshVertComponent)
        componentFn.addElements(neighbors)
        neighborWeights = self.skinCluster.getWeights(self.dag, neighborComp)[0] if neighbors else []
        mapping = weightWrite.influenceMapping(self.skinCluster)
        indices = OpenMaya.MIntArray([physical for dag, physical, logical in mapping])
        self.locked = weightWrite.influenceLocks(mapping)
        # Read current settings for each edit, not cached initialization settings.
        self.maxInfluences = self.skinCluster.findPlug('maxInfluences', True).asInt()
        self.maintainMaxInfl = self.skinCluster.findPlug('maintainMaxInfluences', True).asBool()
        self.normalize = self.skinCluster.findPlug('normalizeWeights', True).asInt()
        weights, unused = self.calcWeights(value, origWeights, neighborWeights, indices, len(neighbors))
        self.writer = weightWrite.WeightBatch()
        operation = self.writer._prepare({'mesh': self.dag.fullPathName(),
            'skinCluster': self.skinCluster.name(), 'vertices': [index],
            'influences': list(indices), 'weights': weights, 'normalize': False})
        self.writer.operations = [operation]
        self.writer._apply([operation['newWeights']])
        return [self.skinCluster, self.dag, vertexComp, indices, origWeights]



smoothWeights = AverageWghtCtx()


class AverageWghtCtxInitialize(OpenMaya.MPxCommand):
    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    def doIt(self, args):
        obj = args.asString(0)
        smoothWeights.initialize(obj)


def creatorInit():
    return AverageWghtCtxInitialize()


def initialize():
    syntax = OpenMaya.MSyntax()
    syntax.addArg(OpenMaya.MSyntax.kString) # OpenMaya.MSyntax.kLong
    return syntax


class AverageWghtCtxUpdate(OpenMaya.MPxCommand):
    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
        self._ready = False

    def doIt(self, args):
        self.index = args.asInt(1)
        self.value = args.asDouble(2)
        self.data = smoothWeights.setWeights(self.index, self.value)
        if self.data[0] is None:
            raise RuntimeError('Smoothing context is not initialized')
        self.writer = smoothWeights.writer
        self.before = self.writer.operations[0]['oldWeights']
        self.after = self.writer.operations[0]['newWeights']
        self._ready = True

    def _apply(self, weights):
        self.writer._apply([weights])

    def undoIt(self):
        self._apply(self.before)

    def redoIt(self):
        self._apply(self.after)

    def isUndoable(self):
        return self._ready


def creatorUpdate():
    return AverageWghtCtxUpdate()


def syntaxUpdate():
    syntax = OpenMaya.MSyntax()
    syntax.addArg(OpenMaya.MSyntax.kLong)
    syntax.addArg(OpenMaya.MSyntax.kLong)
    syntax.addArg(OpenMaya.MSyntax.kDouble)
    return syntax


def initializePlugin(mObject):
    plugin = OpenMaya.MFnPlugin(mObject, kCreator, kVersion, "any")

    for command, creator, syntax in [(CONTEXT_INIT, creatorInit, initialize), (CONTEXT_UPDATE, creatorUpdate, syntaxUpdate)]:
        plugin.registerCommand(command, creator, syntax)


def uninitializePlugin(mObject):
    plugin = OpenMaya.MFnPlugin(mObject)

    for command in [CONTEXT_INIT, CONTEXT_UPDATE]:
        plugin.deregisterCommand(command)
