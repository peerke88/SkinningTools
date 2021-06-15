# -*- coding: utf-8 -*-
from maya.api import OpenMaya
from maya import cmds

from SkinningTools.UI.utils import *
from SkinningTools.Maya import interface
from SkinningTools.Maya.tools import shared, mathUtils


class ApiWeights():
    """ this class handles all the management of a skincluster on a mesh
    mutliple meshes can be handled at once

    the default information gathered is:
    meshes
    vertices as indices
    joints influences as list
    all joint influences from all meshes at the same time as list
    skincluster names
    skinweights as a list of floats

    extra info can be gathered for matching skincluster information to a new mesh:
    vertex positions in bindpose
    joint positions in bindpose
    the bounding box of a mesh to check if the closest positions are going to work
    the uv coordinates of the mesh if applicable
    """

    def __init__(self, extraInfo=False):
        """ constructor method

        :param extraInfo: if `True` will gather more info about the current meshes, if `False` will only gather the base info needed
        :type extraInfo: bool
        """
        self.__extraInfo = extraInfo
        self.doInit()

    def doInit(self):
        """ init of all the data that we want to gather
        seperated as we might want to clear the values when necessary
        """
        self.meshWeights = {}
        self.meshVerts = {}
        self.meshInfluences = {}
        self.allInfJoints = list()
        self.meshSkinClusters = {}
        self.meshNodes = list()
        if self.__extraInfo:
            self.meshPositions = {}
            self.inflPositions = {}
            self.boundingBoxes = {}
            self.uvCoords = {}

    def selectedVertIds(self, node):
        """ get the current selection of vertices, if mesh is seleced we take all vertices, if node is given we take information from that node
        seperated as we might want to clear the values when necessary

        :param node: a node specified to get vertex information from
        :type node: string
        :return: list of vertex ids
        :rtype: list
        """
        selection = interface.getSelection()
        vertices = shared.convertToVertexList(selection)
        if vertices == []:
            return None
        vtxArrays = shared.convertToIndexList(vertices)
        return vtxArrays

    def getSkinFn(self, dagPath=None):
        """ get the openmaya skinFn from the current object or skincluster

        :param dagPath: dagpath to search skincluster
        :type dagPath: OpenMaya.MFnDagpath
        :return: the openmaya version of the skincluster
        :rtype: OpenMayaAnim.MFnSkinCluster
        """
        if not dagPath:
            return None
        skinCluster = shared.skinCluster(dagPath.fullPathName(), True)
        if not skinCluster:
            return None, None
        skinFn = shared.getMfnSkinCluster(dagPath.fullPathName())
        return skinFn, skinCluster

    def getData(self, inNodes=None, progressBar=None):
        """ this function gathers all the data for the given nodes

        :param inNodes: list of mesh nodes to gather skinning information from
        :type inNodes: list
        :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
        :type progressBar: QProgressBar
        """
        if progressBar:
            setProgress(0, progressBar, "start gathering skinData")
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

        percentage = 79.0 / len(currentNodes)

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

            if self.__extraInfo:
                self.meshPositions[node] = []
                uvCoords = []
                vertIter = OpenMaya.MItMeshVertex(meshPath)
                while not vertIter.isDone():
                    pos = vertIter.position(OpenMaya.MSpace.kWorld)
                    self.meshPositions[node].append(smart_roundVec([pos.x, pos.y, pos.z], 3))
                    try:
                        u, v, __ = vertIter.getUVs()
                        uvCoords.append([u[0], v[0]])
                    except:
                        uvCoords.append(None)
                    vertIter.next()
                self.uvCoords[node] = uvCoords

            skinFn, skinName = self.getSkinFn(meshPath)
            if skinFn is None:
                continue
            self.meshSkinClusters[node] = skinName

            # originalShape = cmds.ls(cmds.listHistory(skinName), type="deformableShape")[0]

            vtxArry = shared.getComponents(meshPath, component)
            self.meshVerts[node] = vtxArry

            singleIdComp = OpenMaya.MFnSingleIndexedComponent()
            vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
            singleIdComp.addElements(vtxArry)

            jPos = []
            infDags = skinFn.influenceObjects()
            infIndices = OpenMaya.MIntArray(len(infDags), 0)
            for x, jntDag in enumerate(infDags):
                infIndices[x] = int(skinFn.indexForInfluenceObject(infDags[x]))

                if self.__extraInfo:
                    floatMat = cmds.getAttr("%s.bindPreMatrix[%i]" % (skinName, infIndices[x]))
                    jntTrs = OpenMaya.MTransformationMatrix(mathUtils.floatToMatrix(floatMat).inverse())
                    vec = jntTrs.translation(OpenMaya.MSpace.kWorld)
                    jPos.append(smart_roundVec([vec.x, vec.y, vec.z], 3))

            if self.__extraInfo:
                self.inflPositions[node] = jPos

                boundingBox = OpenMaya.MBoundingBox()
                for i in self.meshPositions[node]:
                    point = OpenMaya.MPoint(*i)
                    boundingBox.expand(point)
                self.boundingBoxes[node] = [smart_roundVec(boundingBox.min, 3), smart_roundVec(boundingBox.max, 3)]

            amountInfluences = len(infIndices)
            weights = skinFn.getWeights(meshPath, vertexComp)
            _wght = weights[0]
            weights = [[_wght[int(i + j * amountInfluences)] for i in range(amountInfluences)] for j in range(int(len(_wght) / amountInfluences))]
            self.meshWeights[node] = weights

            jointInfluences = [infDags[x].fullPathName() for x in range(len(infIndices))]
            self.meshInfluences[node] = jointInfluences
            self.allInfJoints += jointInfluences
            if progressBar:
                setProgress((index * percentage), progressBar, "get data from: %s" % (node))

        self.allInfJoints = sorted(list(set(self.allInfJoints)))

        if progressBar:
            setProgress(95.0, progressBar, "gathered data")
