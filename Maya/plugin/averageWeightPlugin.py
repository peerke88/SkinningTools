from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.Maya.tools import shared

CONTEXT_INIT = "paintAverageWghtCtxInitialize"
CONTEXT_UPDATE = "paintAverageWghtCtxUpdate"
kCreator = "Trevor van Hoof & Perry Leijten"
kVersion = "1.0.20200831"

def maya_useNewAPI( ):
    pass

class AverageWghtCtx(object):
    def __init__(self):
        self.reset()
    
    def initialize(self, obj):
        if not obj:
            self.reset()
            return 

        self.dag = shared.getDagpath(obj)
        self.obj = self.dag.getDependNode(0)
        
        self.skinCluster = shared.getMfnSkinCluster(self.obj)
        
        maxInfPLG = self.skinCluster.findPlug("maxInfluences")
        normalizePLG = self.skinCluster.findPlug("normalizeWeights")
        mainTainPLG = self.skinCluster.findPlug("maintainMaxInfluences")
        
        self.maxInfluences = maxInfPLG.asInt()
        self.normalize = normalizePLG.asInt()
        self.maintainMaxInfl = mainTainPLG.asBool()
        
        self.infl = OpenMaya.MDagPathArray()
        self.skinCluster.influenceObjects(self.infl)
            
        self.lockedInfl = []
        for i in range(self.infl.length()):
            path = self.infl[i].fullPathName()
            locked = cmds.getAttr("%s.liw"%path)
            self.lockedInfl.append(locked)

    def reset(self):
        self.obj = None
        self.dag = None
        self.skinCluster = None
        
        self.maxInfluences = 0
        self.normalize = 0
        self.maintainMaxInfl = False
        
        self.infl = OpenMaya.MDagPathArray()
        self.lockedInfl = []
    
    def calcWeights(self, value, origWeights, nbWeigths, influences, amountComps):
        infAmount = (influences[-1]+1)
        newWeigths = [0.0]*infAmount
        amountNeighbors = len(nbWeigths)
        for i, joint in enumerate(influences):
            if self.lockedInfl[i]:
                newWeigths[i] = origWeights[i]
                continue
            
            for j in range(i, amountNeighbors, infAmount):
                w = ((origWeights[i]/amountNeighbors)*(1-value))+((nbWeigths[j]/numC)*value)
                newWeigths[i] += w
         
        if self.maintainMaxInfluences:
            weights = zip(newWeigths, influenceNew)
            excess = sorted(weights, reverse=True)[self.maxInfluences:]
            for e in excess:    
                newWeigths[e[1]] = 0.0
                
        if self.normalizeMode == 1:
            lockedTotal = sum( [ newWeigths[i]  for i in range(newWeigths.length()) if self.lockedInfl[i] ] )
            
            total = sum(newWeigths) - lockedTotal
            
            if lockedTotal >= 1.0 or total < 1e-6:
                factor = 0
            else:
                factor = (1.0-lockedTotal)/total            
            
            for i, weight in enumerate(newWeigths):
                if self.lockedInfl[i]:
                    continue
                newWeigths[i] = weight * factor

        return newWeigths, influenceNew

    def setWeights(self, index, value):
        if not self.obj:
            return [None]*5

        singleIdComp = OpenMaya.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create( OpenMaya.MFn.kMeshVertComponent )
        vertexComp.addElements( index )
        
        origWeigths = self.skinCluster(self.dag, vertexComp)

        iterVertLoop = OpenMaya.MItMeshVertex(self.obj)
        intArray = iterVertLoop.getConnectedVertices(index)
        vertexComps = singleIdComp.create( OpenMaya.MFn.kMeshVertComponent )
        vertexComps.addElements( intArray )
        compAmount = len(vertexComps)

        nbWeights = self.skinCluster(self.dag, vertexComps)

        infDags = self.skinCluster.influenceObjects()
        infIndexes = OpenMaya.MIntArray( len( infDags ) , 0 )
        for x in xrange( len( infDags ) ):
            infIndexes[x] = int( self.skinCluster.indexForInfluenceObject( infDags[x] ) )

        newWeights, newInfl = self.calcWeights(value, origWeigths, nbWeights, infIndexes, len(vertexComps))
        
        self.skinCluster.setWeights( self.dag,  vertexComp,  newInfl,  newWeights)
        
        return [self.skinCluster, self.dag, component, influencesN, origWeigths]



smoothWeights = AverageWghtCtx()

class AverageWghtCtxInitialize(OpenMaya.MPxCommand):
    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
 
    def doIt( self, args ):
        obj = args.asString(0)
        smoothWeights.initialize(obj)

def creatorInit():     
    return OpenMaya.asMPxPtr(AverageWghtCtxInitialize())

def initialize():  
    syntax = OpenMaya.MSyntax()  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    return syntax

class AverageWghtCtxUpdate(OpenMaya.MPxCommand):
    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
 
    def doIt( self, args ):            
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
    return OpenMaya.asMPxPtr(AverageWghtCtxUpdate())

def syntaxUpdate():  
    syntax = OpenMaya.MSyntax()  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    syntax.addArg(OpenMaya.MSyntax.kLong)  
    syntax.addArg(OpenMaya.MSyntax.kDouble)  
    return syntax  

def initializePlugin( mObject ):
    plugin = OpenMaya.MFnPlugin(mObject, kCreator, kVersion, "any")
    
    for command, creator, syntax in [(CONTEXT_INIT, creatorInit, initialize),(CONTEXT_UPDATE, creatorUpdate, syntaxUpdate)]:
        try:            
            plugin.registerCommand(command, creator, syntax)
        except:         
            raise 
 
def uninitializePlugin(mObject):
    plugin = OpenMaya.MFnPlugin(mObject)
    
    for command in [ CONTEXT_INIT, CONTEXT_UPDATE ]:
        try:            
            plugin.deregisterCommand(command)
        except:         
            raise 