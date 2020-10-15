# -*- coding: utf-8 -*-
from maya.api import OpenMaya, OpenMayaAnim
from maya import cmds

from SkinningTools.Maya import interface, api
from SkinningTools.Maya.tools import shared, mathUtils

class ApiWeights():
    def __init__(self):
        self.doInit()

    def doInit(self):
        self.meshWeights = {}
        self.meshVerts = {}
        self.meshInfluences = {}
        self.allInfJoints = list()
        self.meshSkinClusters = {}
        self.meshNodes = list()
        self.meshPositions = {}
        self.inflPositions = {}

    def selectedVertIds(self, node, show_bad=False):
        selection = interface.getSelection()
        vertices = shared.convertToVertexList(selection)
        if vertices == []:
            return None
        vtxArrays = shared.convertToIndexList(vertices)
        return vtxArrays

    def getSkinFn(self, dagPath=None):
        if not dagPath:
            return None
        skinCluster = shared.skinCluster(dagPath.fullPathName(), True)
        if not skinCluster:
            return None, None
        skinFn = shared.getMfnSkinCluster(dagPath.fullPathName())
        return skinFn, skinCluster

    def getData(self, inNodes = None, progressBar = None):
        if progressBar:
            utils.setProgress(0, progressBar, "start gathering skinData" )
        self.doInit()
        selection = inNodes
        
        if inNodes == None:
            selection = interface.getSelection()

        currentNodes = []
        for node in selection:
            if "." in node:
                name = node.split('.')[0]
                currentNodes.append(name)
                continue
            currentNodes.append(node)
        
        percentage = 79.0/len(currentNodes)
        
        for index, node in enumerate(list(set(currentNodes))):
            if cmds.objectType(node) != "transform":
                if not cmds.nodeType(node) == 'mesh':
                    continue
                node = cmds.listRelatives(node, p=True, f=True)[0]
            shape = cmds.listRelatives(node, s=1, type="mesh") or None
            if shape is None:
                continue
                   
            sList = OpenMaya.MSelectionList()
            sList.add(node)
            meshPath, component = sList.getComponent(0) 
            
            self.meshNodes.append(node)
            
            skinFn, skinName = self.getSkinFn(meshPath)
            if skinFn is None:
                continue
            self.meshSkinClusters[node] = skinName
            
            originalShape = cmds.ls(cmds.listHistory(skinName), type = "deformableShape")[0]
            
            vtxArry = shared.getComponents(meshPath, component)
            self.meshVerts[node] = vtxArry

            self.meshPositions[node] = []
            for index, id in enumerate(vtxArry):
                pos = cmds.xform("%s.vtx[%i]"%(originalShape,index), q=1, ws=1, t=1)
                self.meshPositions[node].append(pos)
            
            singleIdComp = OpenMaya.MFnSingleIndexedComponent()
            vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent )
            singleIdComp.addElements(vtxArry)
            
            jPos = []
            infDags = skinFn.influenceObjects()
            infIndices = OpenMaya.MIntArray( len(infDags), 0 )
            for x, jntDag in enumerate(infDags):
                infIndices[x] = int(skinFn.indexForInfluenceObject(infDags[x]))

                # note: instead of getting the data of the joint based on joint position we get the bindpose position!
                # jntTRS = OpenMaya.MFnTransform(jntDag)
                # jPos.append(jntTRS.translation(OpenMaya.MSpace.kWorld))
                floatMat = cmds.getAttr("%s.bindPreMatrix[%i]"%(skinName, infIndices[x])) 
                jntTrs = OpenMaya.MTransformationMatrix(mathUtils.floatToMatrix(floatMat).inverse())
                vec = jntTrs.translation(OpenMaya.MSpace.kWorld)
                jPos.append([vec.x, vec.y, vec.z])

            self.inflPositions[node] = jPos
            amountInfluences = len(infIndices)

            weights = skinFn.getWeights( meshPath , vertexComp)
            _wght = weights[0]
            weights = [[_wght[i+j*amountInfluences] for i in xrange(amountInfluences)] for j in xrange(len(_wght)/amountInfluences)]
            self.meshWeights[node] = weights
            
            jointInfluences = [infDags[x].fullPathName() for x in range(len(infIndices))]
            self.meshInfluences[node] = jointInfluences
            self.allInfJoints += jointInfluences
            if progressBar:
                utils.setProgress((index * percentage), progressBar, "get data from: %s"%(node))
            
        self.allInfJoints = sorted(list(set(self.allInfJoints)))

        if progressBar:
            utils.setProgress(95.0, progressBar, "gathered data")
        
