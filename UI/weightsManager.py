# -*- coding: utf-8 -*-
import os, shutil, tempfile, json
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools.apiWeights import ApiWeights
from SkinningTools.UI.remapDialog import remapDialog

#Note: temporary
from maya import cmds

class WeightsManager(object):
    def __init__(self):
        super(WeightsManager, self).__init__()
        self.progressBar = None

        self.skinInfo = ApiWeights()

        

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
            bbInfo[mesh] = [__BB[:3], __BB[3:6]]

        remapMesh = {}
        for mesh in _data["meshes"]:
            if cmds.objExists(mesh):
                remapMesh[mesh] = mesh 
                continue
            remapMesh.append(mesh)
        
        _needsRemapJoint = False
        for joint in _jsonDict["allJoints"]:
            if cmds.objExists(joint):
                continue
            _needsRemapJoint = True


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