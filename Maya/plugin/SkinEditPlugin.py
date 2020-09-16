# -*- coding: utf-8 -*-
import sys
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
 
kPluginCmdName = "SkinEditor"

def maya_useNewAPI():
    pass
    
class SkinEditClass( OpenMaya.MPxCommand ):
    
    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
    
    def doIt(self, args):
        self.parseArguments( args )
        self.redoIt()
    
    def getDagpath(self, node, extendToShape=False):
        sellist = OpenMaya.MGlobal.getSelectionListByName(node)
        try:
            if extendToShape:
                return sellist.getDagPath(0).extendToShape()
            return sellist.getDagPath(0)
        except:
            return sellist.getDependNode(0)

    def getMfnSkinCluster(self, mDag):
        return OpenMayaAnim.MFnSkinCluster(self.getDagpath(mDag))

    def parseArguments(self, args):
        argData = OpenMaya.MArgParser(self.syntax(), args)
            
        _mesh, _skinCluster =  argData.getObjectStrings()
        self.mesh = _mesh
        self.skinCluster = self.getMfnSkinCluster(_skinCluster)

        self.vertID = OpenMaya.MIntArray()
        self.newWeights = OpenMaya.MDoubleArray()
        self.jointID = OpenMaya.MIntArray()
        self.origWeights = OpenMaya.MDoubleArray()

        if argData.isFlagSet( '-vid'):
            vertAmount = argData.numberOfFlagUses('-vid')
            for i in xrange(vertAmount):
                self.vertID.append( argData.getFlagArgumentList('-vid', i ).asInt(0) )
        if argData.isFlagSet( '-nw'):
            weightAmount = argData.numberOfFlagUses('-nw')
            for i in xrange(weightAmount):
                self.newWeights.append( argData.getFlagArgumentList('-nw', i ).asDouble(0) )
        if argData.isFlagSet( '-jid'):
            jntAmount = argData.numberOfFlagUses('-jid')
            for i in xrange(jntAmount):
                self.jointID.append( argData.getFlagArgumentList('-jid', i ).asInt(0) )
        if argData.isFlagSet( '-ow'):
            weightAmount = argData.numberOfFlagUses('-ow')
            for i in xrange(weightAmount):
                self.origWeights.append( argData.getFlagArgumentList('-ow', i ).asDouble(0) )
        return True
        
    def redoIt(self):
        self.setWeight(self.newWeights)
    
    def undoIt(self):
        self.setWeight(self.origWeights)
        
    def setWeight(self, inWeights):
        sList = OpenMaya.MSelectionList()
        sList.add(self.mesh)
        meshDag, component = sList.getComponent(0)
        singleIdComp = OpenMaya.MFnSingleIndexedComponent()
        vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent )
        singleIdComp.addElements(self.vertID)
        self.skinCluster.setWeights(meshDag, vertexComp , self.jointID , inWeights , True)
 
    def isUndoable(self):
        return True
 

def cmdCreator():
    return SkinEditClass() 
    
def syntaxCreator():
    syntax = OpenMaya.MSyntax()
    syntax.setObjectType(OpenMaya.MSyntax.kStringObjects, 2,2) # < (mesh, skincluster)
    
    syntax.addFlag( '-vid', '-vertID', OpenMaya.MSyntax.kLong )
    syntax.addFlag( '-nw', '-newWeights', OpenMaya.MSyntax.kDouble )
    syntax.addFlag( '-jid', '-jointID', OpenMaya.MSyntax.kLong )
    syntax.addFlag( '-ow', '-origWeights', OpenMaya.MSyntax.kDouble )
    syntax.makeFlagMultiUse('-vid')
    syntax.makeFlagMultiUse('-nw')
    syntax.makeFlagMultiUse('-jid')
    syntax.makeFlagMultiUse('-ow')

    return syntax

def initializePlugin( mobject ):
    mplugin = OpenMaya.MFnPlugin( mobject )
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator )
    except:
        raise
 
def uninitializePlugin( mobject ):
    mplugin = OpenMaya.MFnPlugin( mobject )
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        raise