import math
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.Maya.tools import shared
from SkinningTools.Maya.plugin.SkinEditPlugin import SkinEditClass

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
        if math.isnan(value) or math.isinf(value) or not 0.0 <= value <= 1.0:
            raise ValueError('Smoothing strength must be finite in [0, 1]')
        count = len(influences)
        if not count or len(origWeights) != count or len(nbWeigths) != count * amountComps:
            raise ValueError('Smoothing weight dimensions do not match')
        if any(math.isnan(w) or math.isinf(w) or not 0.0 <= w <= 1.0
               for w in list(origWeights) + list(nbWeigths)):
            raise ValueError('Smoothing weights must be finite in [0, 1]')
        # Strength zero and isolated vertices are exact no-ops, including limits.
        if value == 0.0 or amountComps == 0:
            return list(origWeights), influences
        locked = getattr(self, 'locked', [False] * count)
        newWeigths = [origWeights[i] if locked[i] else
                      origWeights[i] * (1.0-value) +
                      sum(nbWeigths[j] for j in range(i, len(nbWeigths), count)) / amountComps * value
                      for i in range(count)]
        if self.maintainMaxInfl:
            if self.maxInfluences < 1:
                raise ValueError('Maximum influences must be positive')
            locked_count = sum(locked[i] and newWeigths[i] > 0.0 for i in range(count))
            if locked_count > self.maxInfluences:
                raise ValueError('Locked influences exceed maximum influences')
            ranked = sorted((i for i in range(count) if not locked[i]),
                            key=lambda i: (-newWeigths[i], i))
            for i in ranked[self.maxInfluences-locked_count:]:
                newWeigths[i] = 0.0
        if self.normalize == 1:
            locked_sum = sum(newWeigths[i] for i in range(count) if locked[i])
            if locked_sum > 1.0 + 1e-6:
                raise ValueError('Locked weights exceed normalization budget')
            total = sum(newWeigths[i] for i in range(count) if not locked[i])
            if total:
                factor = max(0.0, 1.0-locked_sum) / total
                for i in range(count):
                    if not locked[i]:
                        newWeigths[i] *= factor
            elif 0.0 < locked_sum < 1.0-1e-6 and any(not item for item in locked):
                raise ValueError('No unlocked weight to fill normalization budget')
        return newWeigths, influences

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
        influences = self.skinCluster.influenceObjects()
        indices = OpenMaya.MIntArray(range(len(influences)))
        self.locked = [cmds.getAttr(inf.fullPathName() + '.liw') for inf in influences]
        # Read current settings for each edit, not cached initialization settings.
        self.maxInfluences = self.skinCluster.findPlug('maxInfluences', True).asInt()
        self.maintainMaxInfl = self.skinCluster.findPlug('maintainMaxInfluences', True).asBool()
        self.normalize = self.skinCluster.findPlug('normalizeWeights', True).asInt()
        weights, unused = self.calcWeights(value, origWeights, neighborWeights, indices, len(neighbors))
        self.writer = SkinEditClass()
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
        try:
            plugin.registerCommand(command, creator, syntax)
        except:
            raise


def uninitializePlugin(mObject):
    plugin = OpenMaya.MFnPlugin(mObject)

    for command in [CONTEXT_INIT, CONTEXT_UPDATE]:
        try:
            plugin.deregisterCommand(command)
        except:
            raise
