# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
from maya import cmds, mel
from .brushtoolbase import BrushToolBase
from skinningTool.skinningTools import SkinningTools


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
        self.__skin = SkinningTools().skinCluster(self.__target, True)
        
    def setValue(self, slot, index, value):
        if self.__skin is None: return
        indexedPath = '%s.vtx[%s]'%(self.__target, index)
        cmds.AverageVtxWeight(indexedPath, sc=self.__skin, wt=value)
        