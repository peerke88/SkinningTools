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

from ..qtUtil import *

from skinningTool.skinningTools import SkinningTools
from .vertexinfluenceeditor import VertexInfluenceEditor

class SkinningToolsSliderList(QWidget):
    def __init__(self):
        super(SkinningToolsSliderList, self).__init__()
        self.setLayout(QVBoxLayout())
        self.update()

    def update(self):
        # clear
        while True:
            child = self.layout().takeAt(0)
            if not child:
                break
            widget = child.widget()
            if not widget:
                continue
            widget.deleteLater()

        # get long selection
        step = cmds.ls(sl=True, l=True)
        if not step: return
        vertices = SkinningTools().convertToVertexList(step)
        if not vertices: return


        skinClusterCache = {}
        for vertex in vertices[:20]: # truncate the list to it will never cause a leak
            mesh = vertex.rsplit('.',1)[0]
            if mesh in skinClusterCache:
                skinCluster, skinBones = skinClusterCache[mesh]
            else:
                skinCluster = SkinningTools.skinCluster(mesh)
                if not skinCluster:
                    return
                skinBones = cmds.skinCluster(skinCluster, q=True, influence=True)
                skinClusterCache[mesh] = skinCluster, skinBones

            weights = []
            for bone in skinBones:
                weights.append( cmds.skinPercent(skinCluster, vertex, transform=bone, q=True, value=True) )
            self.layout().addWidget(VertexInfluenceEditor(skinCluster, vertex, skinBones, weights))

        self.layout().addStretch(1)

        cmds.select(vertices[:20])
        
        mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
        mel.eval('doMenuComponentSelection("%s", "%s");'%(vertices[0].split('.')[0], "vertex"))
        
        if self.isVisible():
            self.finalize()

    def showEvent(self, event):
        super(SkinningToolsSliderList, self).showEvent(event)
        self.finalize()

    def finalize(self):
        '''
        This function hides all unused influences
        Doing this before the widget is visible
        creates bugs in the minimumHeight of the
        widget when it is set to visible.
        '''
        iter = 0
        while True:
            item = self.layout().itemAt(iter)
            iter += 1
            if not item:
                return
            widget = item.widget()
            if not widget:
                continue
            widget.finalize()