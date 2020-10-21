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

        

    def gatherData(self, inObjects, weightdirectory):
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



        utils.setProgress(100.0, progressBar, "data saved")
        