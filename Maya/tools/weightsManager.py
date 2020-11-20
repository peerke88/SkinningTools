# -*- coding: utf-8 -*-
import os, shutil, tempfile, json
from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import shared
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools.apiWeights import ApiWeights
from SkinningTools.UI.dialogs.remapDialog import RemapDialog
from SkinningTools.UI.dialogs.meshSelector import MeshSelector
from random import randint

#Note: temporary, or move entire class over to maya.tools
from maya import cmds


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
    def __init__(self, inProgressBar = None):
        super(WeightsManager, self).__init__()
        self.progressBar = inProgressBar

        self.skinInfo = ApiWeights(True)

        
    def gatherData(self):
        setProgress(0, self.progressBar, "start gathering skinData" )

        inObjects = interface.getSelection()
        self.skinInfo.getData(inObjects, self.progressBar)

        _jsonDict = {}
        _jsonDict["meshes"] = self.skinInfo.meshNodes
        _jsonDict["weights"] = self.skinInfo.meshWeights
        # fix these values so they are using json safe lists
        _vertIDS = {}
        for key, value in self.skinInfo.meshVerts.iteritems():
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
        with open(jsonFile) as f:
            data = json.load(f)
        return data

    def importData(self, jsonFile, closestNPoints = 3, uvBased = False):
        _data = readData(jsonFile)
        
        # get all information on objects in the scene
        _currentMeshes = list(set(cmds.listRelatives(cmds.ls(sl=0, type = "mesh"), parent= 1)))
        bbInfo = {}
        for curMesh in _currentMeshes:
            __BB = cmds.exactWorldBoundingBox(node)
            bbInfo[curMesh] = [smart_round(__BB[:3], 3), smart_round(__BB[3:6], 3)]

        # remap mesh names if the names from the file are not present (bbox is first denominator to find similar meshes)
        remapMesh = {}
        for curMesh in _data["meshes"]:
            if cmds.objExists(curMesh):
                remapMesh[curMesh] = curMesh 
                continue
            selector = MeshSelector(inMesh = curMesh, inBB = _data["bbox"][curMesh], meshes = bbInfo)
            selector.exec_()

            remapMesh[curMesh] = selector.combo.currentText()
        
        # remap joints in the scene if the joint naming does not match with stuff on file
        _needsRemapJoint = False
        for joint in _jsonDict["allJoints"]:
            if cmds.objExists(joint):
                continue
            _needsRemapJoint = True

        # create a remapping dictionary for all joints
        currentJoints = cmds.ls(sl=0, type = "joint")
        connectionDict = { i : i for i in _jsonDict["allJoints"] }
        if _needsRemapJoint:
            _remap = RemapDialog(leftSide = _jsonDict["allJoints"], rightSide = currentJoints, parent = self)
            _remap.exec_()
            connectionDict = _remap.getConnectionInfo()
        
        # for each mesh we now do the skinning operation
        for inMesh, toMesh in remapMesh.iteritems():
            closest = checkNeedsClosestVtxSearch(_data, inMesh, toMesh)

            # check if we are uv based and if uv's are available
            canDoUV = uvBased
            vertPos, uvCoords = _getPosAndUvCoords(toMesh)
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
                closestWghtId = {i:i for i in _data["vertIds"][inMesh]}
                distanceWeight = {i:[1] for i in _data["vertIds"][inMesh]}

            #convert closest positions to actual weights
            if closest:
                closestWeights = []
                for i in _data["vertIds"][inMesh]:
                    setWeights = [0.0] * len(_data["infl"][inMesh])
                    for _id, wghtIndex in enumerate(closestWghtId[i]):
                        oldweights = [x * distanceWeight[i][_id] for x in _data["weights"][inMesh][wghtIndex]]
                        for j, wt in enumerate(oldweights):
                            setWeights[j] += wt
                    closestWeights.append(setWeights)
            else:
                closestWeights = _data["weights"][inMesh][::]

            # remap based on joint dict
            if _needsRemapJoint:
                jointWeights = []  
                for index in _data["vertIds"][inMesh]:
                    _intermediate = [0.0] * len(_data["infl"][inMesh])
                    for key, value in connectionDict.iteritems():    
                        prevIndex = _data["infl"][inMesh].index[key]
                        outIndex = currentJoints.index[value]
                        _intermediate[outIndex] = closestWeights[index][prevIndex]
                    jointWeights.append_intermediate
            else:
                jointWeights = closestWeights[::]

            # gather or build information
            sc = shared.skincluster(toMesh)
            jnts = connectionDict.values()
            if sc is None:
                sc = cmds.skinCluster(toMesh, jnts, tsb=1 )

            verts = shared.convertToVertexList(toMesh)
            vertIds = shared.convertToIndexList(verts)

            cmds.SkinEditor(toMesh, sc, vid=vertIds, nw = jointWeights, jid = jnts, ow = jointWeights )
        

    def _getPosAndUvCoords(self, inMesh):
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
        return uvCoords
        
    def checkNeedsClosestVtxSearch(self, data, fromMesh, toMesh):
        _needsClosest = False
        for i in xrange(5):
            _id =  randint(0, (_data["vertIds"][fromMesh][-1] + 1))
            pos = smart_roundVec(_data["vertPos"][fromMesh][_id], 3)
            nPos = smart_roundVec(cmds.xform("%s.vtx[%i]"%(toMesh, _id), q=1, ws=1,t=1), 3)
            if pos == nPos:
                continue
            _needsClosest = True
        return _needsClosest

