from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.Maya.tools import shared

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

        self.dag = shared.getDagpath(obj)
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
        infAmount = len(influences)
        newWeigths = [0.0] * infAmount
        amountNeighbors = len(nbWeigths)
        for i, joint in enumerate(influences):

            for j in range(i, amountNeighbors, infAmount):
                w = ((origWeights[i] / amountNeighbors) * (1 - value)) + ((nbWeigths[j] / amountComps) * value)
                newWeigths[i] += w

        if self.maintainMaxInfl:
            weights = zip(newWeigths, influences)
            excess = sorted(weights, reverse=True)[self.maxInfluences:]
            for e in excess:
                newWeigths[e[1]] = 0.0

        if self.normalize == 1:
            total = sum(newWeigths)

            if total < 1e-6:
                factor = 0
            else:
                factor = 1.0 / total

            for i, weight in enumerate(newWeigths):
                newWeigths[i] = weight * factor

        return newWeigths, influences

    def setWeights(self, index, value):
        if not self.obj:
            return [None] * 5

        singleIdComp = OpenMaya.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
        singleIdComp.addElement(index)

        origWeigths = self.skinCluster.getWeights(self.dag, vertexComp)[0]

        iterVertLoop = OpenMaya.MItMeshVertex(self.obj)
        iterVertLoop.setIndex(index)
        intArray = iterVertLoop.getConnectedVertices()

        vertexComps = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
        singleIdComp.addElements(intArray)
        compAmount = len(intArray)

        nbWeights = self.skinCluster.getWeights(self.dag, vertexComps)[0]

        infDags = self.skinCluster.influenceObjects()
        infIndexes = OpenMaya.MIntArray(len(infDags), 0)
        for x in range(len(infDags)):
            infIndexes[x] = int(self.skinCluster.indexForInfluenceObject(infDags[x]))

        newWeights, newInfl = self.calcWeights(value, origWeigths, nbWeights, infIndexes, compAmount)

        singleIdComp = OpenMaya.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
        singleIdComp.addElement(index)

        skinWeights = OpenMaya.MDoubleArray(len(newWeights), 0)
        for i in range(len(newWeights)):
            skinWeights[i] = newWeights[i]

        self.skinCluster.setWeights(self.dag, vertexComp, newInfl, skinWeights)# newWeights

        return [self.skinCluster, self.dag, vertexComp, newInfl, origWeigths]



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

    def doIt(self, args):
        self.index = args.asInt(1)
        self.value = args.asDouble(2)

        self.data = smoothWeights.setWeights(self.index, self.value)

    def undoIt(self):
        if not all(self.data):
            return

        skinCluster, dag, component, influences, weights = self.data
        skinCluster.setWeights(dag, component, influences, weights, 1)

    def redoIt(self):
        if not self.index or not self.value:
            return

        self.data = smoothWeights.setWeights(self.index, self.value)

    def isUndoable(self):
        return True


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
