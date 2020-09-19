# -*- coding: utf-8 -*-
from maya.api import OpenMaya, OpenMayaAnim
from maya import cmds

from SkinningTools.Maya import interface, api
from SkinningTools.Maya.tools import shared

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

    def getData(self):
        self.doInit()
        selection = interface.getSelection()
        currentNodes = []
        for node in selection:
            if "." in node:
                name = node.split('.')[0]
                currentNodes.append(name)
                continue
            currentNodes.append(node)
        
        for node in list(set(currentNodes)):
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
            
            vtxArry = shared.getComponents(meshPath, component)
            self.meshVerts[node] = vtxArry

            meshFn = OpenMaya.MFnMesh(meshPath)
            positions = meshFn.getPoints(OpenMaya.MSpace.kWorld)
            
            singleIdComp = OpenMaya.MFnSingleIndexedComponent()
            vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent )
            singleIdComp.addElements(vtxArry)

            nPos = []
            for index in vtxArry:
                nPos.append(positions[index])
            self.meshPositions[node] = nPos
            
            jPos = []
            infDags = skinFn.influenceObjects()
            infIndices = OpenMaya.MIntArray( len(infDags), 0 )
            for x, jntDag in enumerate(infDags):
                infIndices[x] = int(skinFn.indexForInfluenceObject(infDags[x]))
                jntTRS = OpenMaya.MFnTransform(jntDag)
                jPos.append(jntTRS.translation(OpenMaya.MSpace.kWorld))

            self.inflPositions[node] = jPos
            amountInfluences = len(infIndices)

            weights = skinFn.getWeights( meshPath , vertexComp)
            _wght = weights[0]
            weights = [[_wght[i+j*amountInfluences] for i in xrange(amountInfluences)] for j in xrange(len(_wght)/amountInfluences)]
            self.meshWeights[node] = weights
            
            jointInfluences = [infDags[x].fullPathName() for x in range(len(infIndices))]
            self.meshInfluences[node] = jointInfluences
            self.allInfJoints += jointInfluences
            
        self.allInfJoints = sorted(list(set(self.allInfJoints)))

        
