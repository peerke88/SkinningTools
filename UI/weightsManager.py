# -*- coding: utf-8 -*-
import os, shutil, tempfile, json
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools.apiWeights import ApiWeights

class WeightsManager(object):
    def __init__(self):
        super(WeightsManager, self).__init__()
        self.progressBar = None

        self.skinInfo = ApiWeights()

        

    def gatherData(self, inObjects, weightdirectory, fileName, binary=False):
        utils.setProgress(0, progressBar, "start gathering skinData" )

        self.skinInfo.getData(inObjects, self.progressBar)

        _jsonDict = {}
        #todo: fix these values so they are using json safe lists
        _jsonDict["meshes"] = self.skinInfo.meshNodes
        _jsonDict["weights"] = self.skinInfo.meshWeights
        _jsonDict["vertIds"] = [x for x in self.skinInfo.meshVerts]
        _jsonDict["influences"] = self.skinInfo.meshInfluences
        _jsonDict["allJoints"] = self.skinInfo.allInfJoints
        _jsonDict["skinclusters"] = self.skinInfo.meshSkinClusters
        _jsonDict["vertPositions"] = self.skinInfo.meshPositions
        _jsonDict["jntPositions"] = self.skinInfo.inflPositions

        print type(_jsonDict["meshes"]), _jsonDict["meshes"]
        print type(_jsonDict["weights"]), _jsonDict["weights"]
        print type(_jsonDict["vertIds"]), _jsonDict["vertIds"]
        print type(_jsonDict["influences"]), _jsonDict["influences"]
        print type(_jsonDict["allJoints"]), _jsonDict["allJoints"]
        print type(_jsonDict["skinclusters"]), _jsonDict["skinclusters"]
        print type(_jsonDict["vertPositions"]), _jsonDict["vertPositions"]
        print type(_jsonDict["jntPositions"]), _jsonDict["jntPositions"]

        with open(os.path.join(weightdirectory, '%s.skinWeights'%fileName), 'w') as f:
            json.dump(data, f, encoding='utf-8', ensure_ascii = not binary, indent=4)

        utils.setProgress(100.0, progressBar, "data saved")

    def readData(self, jsonFile):

        with open(jsonFile) as f:
            data = json.load(f)

        _meshes = data["meshes"]
        print _meshes


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