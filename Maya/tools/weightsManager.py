# -*- coding: utf-8 -*-
import json
from SkinningTools.Maya import interface
from SkinningTools.Maya.tools import shared
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from SkinningTools.Maya.tools.apiWeights import ApiWeights
from SkinningTools.UI.dialogs.remapDialog import RemapDialog
from SkinningTools.UI.dialogs.meshSelector import MeshSelector
from random import randint

# Note: temporary, or move entire class over to maya.tools
from maya import cmds
from maya.api import OpenMaya


class WeightsManager(object):
    """
    this is the manager class, maybe make a different ui class to attach these elements to
    when loading there are 4 scenarios:

    1. 1 to 1 the mesh and joints are exactly the same ( need to find a way to double check the vertex order to make sure)

    2. mesh is not the same, joints are (we need to find the best possible match using closest vertex/uvs) try baricentric coordinates where possible

    3. mesh is the same but joints are not (remap joints with the remapper, this can be closest joint, joint naming etc.) 

    4. mesh and joints are total mismatch (double check if joints are somewhate in a similar position and bounding box of the mesh is within range, maybe also do a check on joint hierarchy)

    -------------------------------

    allow files to be stored anywhere on the pc, maybe keep track on where its placed using qsettings
    also have a folder structure tree and file window next to each other for this
    place a base file setup where these files can be stored by default for quick save and load
    """

    def __init__(self, inProgressBar=None):
        """ contructor method

        :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
        :type progressBar: QProgressBar
        """
        super(WeightsManager, self).__init__()
        self.progressBar = inProgressBar

        self.skinInfo = ApiWeights(True)

    def gatherData(self):
        """ gather the data from current selection of objects

        :return: data from current selected objects
        :rtype: dict
        """
        setProgress(0, self.progressBar, "start gathering skinData")

        inObjects = interface.getSelection()
        self.skinInfo.getData(inObjects, self.progressBar)

        _jsonDict = {}
        _jsonDict["meshes"] = self.skinInfo.meshNodes
        _jsonDict["weights"] = self.skinInfo.meshWeights
        _vertIDS = {}
        for key, value in self.skinInfo.meshVerts.items():
            _vertIDS[key] = [x for x in value]
        _jsonDict["vertIds"] = _vertIDS
        _jsonDict["infl"] = self.skinInfo.meshInfluences
        _jsonDict["allJnts"] = self.skinInfo.allInfJoints
        _jsonDict["clusters"] = self.skinInfo.meshSkinClusters
        _jsonDict["vertPos"] = self.skinInfo.meshPositions
        _jsonDict["jntPos"] = self.skinInfo.inflPositions
        _jsonDict["bbox"] = self.skinInfo.boundingBoxes
        _jsonDict["uvs"] = self.skinInfo.uvCoords

        setProgress(100.0, self.progressBar, "data saved")
        return _jsonDict

    def readData(self, jsonFile):
        """ read the data from a json file

        :return: data from the json file
        :rtype: dict
        """
        with open(jsonFile) as f:
            data = json.load(f)
        return data

    def importData(self, jsonFile, workMesh=None, scale=1.0, closestNPoints=3, uvBased=False):
        """ import data from a json file 
        this setup tries to make it possible to load skinning information that does not match the original object

        :todo: make sure it works only on the workmesh if given
        :todo: fix the setup in a way that it works with the given scale

        :param jsonFile: the file that holds all the skinning information
        :type jsonFile: string
        :param closestNPoints: closest amount of positions to search from
        :type closestNPoints: int
        :param uvBased: if `True` will try to search information based on UV's, if `False`  will use the points in the 3d scene
        :type uvBased: bool
        """
        setProgress(0, self.progressBar, "start loading data")
        _data = self.readData(jsonFile)

        # get all information on objects in the scene
        _currentMeshes = list(set(cmds.listRelatives(cmds.ls(sl=0, type="mesh"), parent=1)))
        bbInfo = {}
        for curMesh in _currentMeshes:
            __BB = cmds.exactWorldBoundingBox(curMesh)
            bbInfo[curMesh] = [smart_roundVec(__BB[:3], 3), smart_roundVec(__BB[3:6], 3)]

        # remap mesh names if the names from the file are not present (bbox is first denominator to find similar meshes)
        remapMesh = {}
        for curMesh in _data["meshes"]:
            if cmds.objExists(curMesh):
                remapMesh[curMesh] = curMesh
                continue
            selector = MeshSelector(inMesh=curMesh, inBB=_data["bbox"][curMesh], meshes=bbInfo)
            selector.exec_()

            remapMesh[curMesh] = selector.combo.currentText()

        # remap joints in the scene if the joint naming does not match with stuff on file
        _needsRemapJoint = False
        for joint in _data["allJnts"]:
            if cmds.objExists(joint):
                continue
            _needsRemapJoint = True

        # create a remapping dictionary for all joints
        currentJoints = cmds.ls(sl=0, type="joint")
        connectionDict = {i: i for i in _data["allJnts"]}
        if _needsRemapJoint:
            _remap = RemapDialog(leftSide=_data["allJnts"], rightSide=currentJoints, parent=self)
            _remap.exec_()
            connectionDict = _remap.getConnectionInfo()

        setProgress(20, self.progressBar, "loading mesh data")
        percentage = 79.0 / (len(remapMesh.keys()))
        # for each mesh we now do the skinning operation
        for iterIdx, (inMesh, toMesh) in enumerate(remapMesh.items()):
            closest = self.checkNeedsClosestVtxSearch(_data, inMesh, toMesh)

            # check if we are uv based and if uv's are available
            canDoUV = uvBased
            vertPos, uvCoords = self._getPosAndUvCoords(toMesh)
            if canDoUV and closest:
                if None in _data["uvs"][inMesh] or None in uvCoords:
                    canDoUV = False

            # remap closest n-number positon weights
            if closest:
                if canDoUV:
                    closestWghtId, distanceWeight = remapClosestPoints(_data["uvs"][inMesh], uvCoords, closestNPoints)
                else:
                    closestWghtId, distanceWeight = remapClosestPoints(_data["vertPos"][inMesh], vertPos, closestNPoints)
            else:
                closestWghtId = {i: i for i in _data["vertIds"][inMesh]}
                distanceWeight = {i: [1] for i in _data["vertIds"][inMesh]}

            # convert closest positions to actual weights
            closestWeights = []
            if closest:
                for i in _data["vertIds"][inMesh]:
                    setWeights = [0.0] * len(_data["infl"][inMesh])
                    for _id, wghtIndex in enumerate(closestWghtId[i]):
                        oldweights = [x * distanceWeight[i][_id] for x in _data["weights"][inMesh][wghtIndex]]
                        for j, wt in enumerate(oldweights):
                            setWeights[j] += wt
                    closestWeights.append(setWeights)
            else:
                closestWeights = _data["weights"][inMesh]

            # remap based on joint dict
            jointWeights = []
            if _needsRemapJoint:
                for index in _data["vertIds"][inMesh]:
                    _intermediate = [0.0] * len(_data["infl"][inMesh])
                    for key, value in connectionDict.items():
                        prevIndex = _data["infl"][inMesh].index[key]
                        outIndex = currentJoints.index[value]
                        _intermediate[outIndex] = closestWeights[index][prevIndex]
                    jointWeights.extend(_intermediate)
            else:
                for weightList in closestWeights:
                    jointWeights.extend(weightList)

            # gather or build information
            sc = shared.skinCluster(toMesh)
            jnts = connectionDict.values()
            if sc is None:
                sc = cmds.skinCluster(toMesh, jnts, tsb=1)

            verts = shared.convertToVertexList(toMesh)
            vertIds = shared.convertToIndexList(verts)

            shared.setWeights(toMesh, jointWeights)
            setProgress(20 + (percentage * iterIdx), self.progressBar, "loading %s Data" % toMesh)

        setProgress(100, self.progressBar, "imported Data")

    def _getPosAndUvCoords(self, inMesh):
        """ get positional data of the current mesh's components

        :param inMesh: the mesh to gather data from
        :type inMesh: string
        :return: list of positions and uv coordinates
        :rtype: list
        """
        positions = []
        uvCoords = []
        meshPath = shared.getDagpath(inMesh)
        vertIter = OpenMaya.MItMeshVertex(meshPath)
        while not vertIter.isDone():
            pos = vertIter.position(OpenMaya.MSpace.kWorld)
            positions.append(smart_roundVec([pos.x, pos.y, pos.z], 3))
            try:
                u, v, __ = vertIter.getUVs()
                uvCoords.append([u[0], v[0]])
            except:
                uvCoords.append(None)
            vertIter.next()
        return positions, uvCoords

    def checkNeedsClosestVtxSearch(self, data, fromMesh, toMesh):
        """ check the current mesh's positional data with the stored data

        :param data: data from the stored meshes
        :type data: dict
        :param fromMesh: the direct mesh to compare with that was stored
        :type fromMesh: string
        :param toMesh: the mesh that will get the information
        :type toMesh: string
        :return: `True` if object data does not match
        :rtype: bool
        """
        _needsClosest = False
        for i in range(5):
            _id = randint(0, (data["vertIds"][fromMesh][-1] + 1))
            pos = smart_roundVec(data["vertPos"][fromMesh][_id], 3)
            nPos = smart_roundVec(cmds.xform("%s.vtx[%i]" % (toMesh, _id), q=1, ws=1, t=1), 3)
            if pos == nPos:
                continue
            _needsClosest = True
        return _needsClosest
