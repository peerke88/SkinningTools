# -*- coding: utf-8 -*-
import os, shutil, tempfile, json
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools.apiWeights import ApiWeights
from SkinningTools.UI.dialogs.remapDialog import RemapDialog
from SkinningTools.UI.dialogs.meshSelector import MeshSelector
from random import randint

#Note: temporary, or move entire class over to maya.tools
from maya import cmds

class WeightsManager(object):
    def __init__(self, inProgressBar = None):
        super(WeightsManager, self).__init__()
        self.progressBar = inProgressBar

        self.skinInfo = ApiWeights(True)

        

    def gatherData(self, inObjects, weightdirectory, fileName, binary=False):
        setProgress(0, self.progressBar, "start gathering skinData" )

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

        with open(os.path.join(weightdirectory, '%s.skinWeights'%fileName), 'w') as f:
            json.dump(_jsonDict, f, encoding='utf-8', ensure_ascii = not binary, indent=4)

        setProgress(100.0, self.progressBar, "data saved")

    def readData(self, jsonFile):

        with open(jsonFile) as f:
            data = json.load(f)
        return data

    def importData(self, jsonFile, closestNPoints = 3, uvBased = False):
        _data = readData(jsonFile)
        
        _currentMeshes = list(set(cmds.listRelatives(cmds.ls(sl=0, type = "mesh"), parent= 1)))
        bbInfo = {}
        for mesh in _currentMeshes:
            __BB = cmds.exactWorldBoundingBox(node)
            bbInfo[mesh] = [smart_round(__BB[:3], 3), smart_round(__BB[3:6], 3)]

        remapMesh = {}
        for mesh in _data["meshes"]:
            if cmds.objExists(mesh):
                remapMesh[mesh] = mesh 
                continue
            selector = MeshSelector(inMesh = mesh, inBB = _data["bbox"][mesh], bbInfo)
            selector.exec_()

            remapMesh[mesh] = selector.combo.currentText()
        
        _needsRemapJoint = False
        for joint in _jsonDict["allJoints"]:
            if cmds.objExists(joint):
                continue
            _needsRemapJoint = True

        currentJoints = cmds.ls(sl=0, type = "joint")
        connectionDict = { i : i for i in _jsonDict["allJoints"] }
        if _needsRemapJoint:
            _remap = RemapDialog(leftSide = _jsonDict["allJoints"], rightSide = currentJoints, parent = self)
            _remap.exec_()
            connectionDict = _remap.getConnectionInfo()
        
        for mesh, toMesh in remapMesh.iteritems():
            _closest = checkNeedsClosestVtxSearch(_data, mesh, toMesh)


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

        # @Todo: check i

        # _meshes = data["meshes"]

        # for mesh in _meshes:
        #     print "------- %s -------"%mesh
        #     print data["weights"][mesh]
        #     print data["vertIds"][mesh]
        #     print data["influences"][mesh]
        #     print data["skinclusters"][mesh]
        #     print data["vertPositions"][mesh]
        #     print data["jntPositions"][mesh]


'''
# todo

store all information as json (check for better faster information storage?) json storage choose for ascii or binary

maybe check this?
https://developers.google.com/protocol-buffers/docs/pythontutorial


when loading there are 4 scenarios:

1. 1 to 1 the mesh and joints are exactly the same ( need to find a way to double check the vertex order to make sure)

2. mesh is not the same, joints are (we need to find the best possible match using closest vertex/uvs) try baricentric coordinates where possible

3. mesh is the same but joints are not (remap joints with the remapper, this can be closest joint, joint naming etc.) 

4. mesh and joints are total mismatch (double check if joints are somewhate in a similar position and bounding box of the mesh is within range, maybe also do a check on joint hierarchy)


-------------------------------

allow files to be stored anywhere on the pc, maybe keep track on where its placed using qsettings
also have a folder structure tree and file window next to each other for this
place a base file setup where these files can be stored by default for quick save and load
'''