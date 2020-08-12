# -*- coding: utf-8 -*-
from .brushtoolbase import BrushToolBase
from maya import cmds


class GlobalSkinSmoothBrush(BrushToolBase):
    '''initialises the brushtool with the averageweight command, so it smoothes values based on all influencing joints'''

    def __init__(self):
        super(GlobalSkinSmoothBrush, self).__init__(self.__class__.__name__)

        self.__target = None
        self.__skin = None

        self.updateDuringStroke = True

    def initialize(self, objectName):
        self.__target = cmds.ls(objectName, l=1)
        if self.__target is None or self.__target == []:
            cmds.error("could not find target to initialize smooth brush")
        else:
            self.__target = self.__target[0]
        print(self.__target)
        self.__skin = api.skinClusterForObject(self.__target)

    def setValue(self, slot, index, value):
        if self.__skin is None: return
        indexedPath = '%s.vtx[%s]' % (self.__target, index)
        cmds.AverageVtxWeight(indexedPath, sc=self.__skin, wt=value)
