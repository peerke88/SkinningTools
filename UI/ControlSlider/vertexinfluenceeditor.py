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
import os, re, functools, logging
from math import sqrt, sin, cos, pi
from maya import cmds, OpenMaya

from ..qtUtil import *

from .sliderControl import SliderControl
from skinningTool import mscreen
mscreen.logger.setLevel( logging.CRITICAL )

class VertexInfluenceEditor(QGroupBox):
    lockIcon = QIcon('%s/Icon/openlock.png'%os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    unlockIcon = QIcon('%s/Icon/closedlock.png'%os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

    def _lookAt(self, pos1, pos2):
        aim =OpenMaya.MVector().zAxis

        source = OpenMaya.MVector(pos1[0], pos1[1],pos1[2])
        target = OpenMaya.MVector(pos2[0], pos2[1],pos2[2])

        aimVector = (target - source).normal()

        quat = OpenMaya.MQuaternion()
        QuatU = OpenMaya.MQuaternion(aim, aimVector).asEulerRotation()
        
        return (QuatU.x, QuatU.y,QuatU.z)
        
    def _hiliteNode(self, radius):
        POINTS = []
        r = radius
        fullRange = pi*12.5
        for angle in range(int(fullRange)+1):
            POINTS.append(( r*cos(angle/6.25), r*sin(angle/6.25), 0 ))

        circle = mscreen.drawCurve(POINTS, color=mscreen.COLOR_RED, drawInFront = True)
        point = mscreen.drawPoint((0.0,0.0,0.0), mscreen.COLOR_YELLOW, drawInFront = True)
        return circle, point

    def _activeCamera(self):
        camera = cmds.modelEditor(cmds.playblast(ae=True), q=True, camera=True)
        if not camera:
            camera = cmds.modelEditor(cmds.modelEditor(q=True, activeView=True), q=True, camera=True)
        if not camera:
            return
        if cmds.ls(camera, type='shape'):
            camera = cmds.listRelatives(camera, p=True, f=True)
        return camera

    def _snapHiliteNode(self, vertex):
        pos = cmds.xform(vertex, q=True, ws=True, t=True)
        camera = self._activeCamera()
        if not camera: return False
        camPos = cmds.xform(camera, q=True, ws=True, rp=True)
        euler = self._lookAt(pos, camPos)

        scale = sqrt((camPos[0]-pos[0])*(camPos[0]-pos[0])+
            (camPos[1]-pos[1])*(camPos[1]-pos[1])+
            (camPos[2]-pos[2])*(camPos[2]-pos[2])) * 0.01
        
        mscreen.clear() 
        hilite, vtx= self._hiliteNode(scale)
        hilite.move(pos[0], pos[1], pos[2])
        hilite.rotate( euler[0], euler[1],euler[2], False)
        vtx.move(pos[0], pos[1], pos[2])
        mscreen.refresh()
        
        return True

    @staticmethod
    def VLayout():
        l = QVBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0,0,0,0)
        return l

    @staticmethod
    def HLayout():
        l = QHBoxLayout()
        l.setSpacing(0)
        l.setContentsMargins(0,0,0,0)
        return l

    def __unusedJointsBox(self):
        unusedJoints = QGroupBox()
        unusedJoints.setTitle('Unused influences')
        unusedJoints.setFlat(True)
        l = VertexInfluenceEditor.VLayout()
        unusedJoints.setLayout(l)
        unusedJoints.setCheckable(True)
        unusedJoints.toggled.connect(self._toggleGroupBox)
        self.__unusedJoints = unusedJoints

    def _toggleGroupBox(self, state):
        layout = self.sender().layout()
        iter = 0
        while True:
            item = layout.itemAt(iter)
            if not item:
                return
            iter += 1
            widget = item.widget()
            if not widget:
                continue
            widget.setVisible(state)

    def __lineEdit_CorrectFolderCharacters(self, inLineEdit):
        return re.search(r'[\\/:<>"]', inLineEdit) or re.search(r'[*?|]', inLineEdit) or re.search(r'[A-Z]', inLineEdit) or re.search(r'[a-z]', inLineEdit)
    
    def __lineEdit_FieldEditted(self,*args):
        Controller_name_text = self.sender().displayText()
        if self.__lineEdit_CorrectFolderCharacters(Controller_name_text) is not None or Controller_name_text == '':
            self.sender().setStyleSheet('background-color: #f00;')
        else:
            self.sender().setStyleSheet('')

    def __init__(self, skinCluster, vertexFullPath, skinBones, weights):
        super(VertexInfluenceEditor, self).__init__()
        self.setMinimumHeight(0)

        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self._toggleGroupBox)
        self.setTitle(vertexFullPath.rsplit('|',1)[-1])
        self.setLayout(VertexInfluenceEditor.VLayout())

        self.__target = (skinCluster, vertexFullPath)
        self.__influences = skinBones

        self.__sliders = []

        hasUnused = False
        self.__unusedJointsBox()

        self.__busyWithCallback = False
        
        divider = QFrame()
        divider.setFrameStyle(QFrame.HLine)
        divider.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        divider.setLineWidth(1)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(divider)

        unusedSliders = 0
        for i in range(len(skinBones)):
            sliderLayout = VertexInfluenceEditor.HLayout()
            sliderFrame = QFrame()
            sliderFrame.setLayout(sliderLayout)
            gripSlider = SliderControl(skinBones[i], label=skinBones[i].rsplit('|',1)[-1], min=0.0, max=1.0, rigidRange=True, labelOnSlider=True)
            gripSlider.slider.setValue(weights[i])
            gripSlider.slider.valueChanged.connect(functools.partial(self.__updateWeights, i))
            gripSlider.lineEdit.textEdited[unicode].connect( self.__lineEdit_FieldEditted )

            sliderLayout.addWidget(gripSlider)
            lbl = VertexInfluenceEditor.lockIcon
            parent = self.layout()
            if weights[i] <= 0.00001:
                unusedSliders += 1
                lbl = VertexInfluenceEditor.unlockIcon
                parent = self.__unusedJoints.layout()
                hasUnused = True
                gripSlider.setEnabled(False)
            lockButton = QPushButton(lbl, '')
            lockButton.clicked.connect(functools.partial(self.__toggleLock, i))
            sliderLayout.addWidget(lockButton)
            parent.addWidget(sliderFrame)

            self.__sliders.append((gripSlider, lockButton))

        if hasUnused:
            self.layout().addWidget(self.__unusedJoints)

    def enterEvent(self, event):
        super(VertexInfluenceEditor, self).enterEvent(event)
        if not self._snapHiliteNode(self.__target):
            mscreen.clear()
            mscreen.refresh()

    def leaveEvent(self, event):
        super(VertexInfluenceEditor, self).leaveEvent(event)
        mscreen.clear()
        mscreen.refresh()

    def finalize(self):
        self.__unusedJoints.setChecked(False)

    def __toggleLock(self, index):
        slider, button = self.__sliders[index]
        if slider.isEnabled():
            button.setIcon(VertexInfluenceEditor.unlockIcon)
            slider.setEnabled(False)
        else:
            button.setIcon(VertexInfluenceEditor.lockIcon)
            slider.setEnabled(True)

    def __updateWeights(self, setId, newValue):
        '''
        normalize all other weights so we can cleanly inject the new value

        calculate what weight will remain after injecting the new value
        then multiply all other weights by that value, so that all other weights added together = the remainder
        this works because the sum of all weights is first made to be 1.0, then we do (1.0 * 1.0 - newValue) where each 1.0 is actually the list of weights

        these steps are optimized to 'find the total value we should divide by to normalize'
        and 'multiply by the remainder and divide by the total value at the same time', so instead of 2 steps (normalize and multiply separately)
        we just multiply by a ratio of (1.0 - newValue) / initialRemainderTotal

        the target weight can be set either at the start or at the end because it's index is otherwise ignored
        '''
        if self.__busyWithCallback:
            # callback fired by a setValue which was called by another slider's updateWeights
            return
        self.__busyWithCallback = True

        numSliders = len(self.__sliders)
        if numSliders - 1 == 0:
            return #no other sliders to edit

        totalValue = 0.0
        offset = newValue

        totalLength = 0.0
        for i in range(numSliders):
            if i == setId: continue
            slider, __ = self.__sliders[i]
            if not slider.isEnabled(): 
                totalLength += slider.slider.value()

        if offset > (1.0 - totalLength):
            offset = (1.0 - totalLength)
            newValue = offset
        
        weights = [0.0] * numSliders
        for i in range(numSliders):
            if i == setId: continue
            slider, __ = self.__sliders[i]
            if not slider.isEnabled():
                offset += slider.slider.value()
                continue
            weights[i] = slider.slider.value()
            totalValue += weights[i]

        slider, __ = self.__sliders[setId]
        weights[setId] = newValue
        if totalValue == 0:
            scale = (1.0 - offset) / (numSliders - 1)
        else:
            scale = (1.0 - offset) / totalValue
        for i in range(numSliders):
            if i == setId: continue
            slider, __ = self.__sliders[i]
            if not slider.isEnabled(): 
                if slider.slider.value() == 0.0:
                    continue
                else:
                    weights[i] = slider.slider.value()
                continue
            if totalValue == 0:
                weights[i] = scale
            else:
                weights[i] *= scale
            slider.slider.setValue(weights[i])
        self._snapHiliteNode(self.__target)
        self.__busyWithCallback = False

        # apply to skincluster
        stack = []
        for i in range(numSliders):
            stack.append((self.__influences[i], weights[i]))
        cmds.skinPercent(*self.__target, normalize=True, transformValue=stack)