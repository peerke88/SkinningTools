# -*- coding: utf-8 -*-
import functools
from functools import partial
from SkinningTools.Maya import api
from SkinningTools.Maya.tools import weightMath
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import QGroupBox, QIcon, QWidget, QPushButton
from SkinningTools.UI.utils import WeightSolver, nullVBoxLayout, nullHBoxLayout
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl


class VertexInfluenceEditor(QGroupBox):
    lockIcon = QIcon(':/nodeGrapherUnlocked.png')
    unlockIcon = QIcon(':/lockGeneric.png')

    def __lineEdit_FieldEditted(self, *_):
        self.sender().setStyleSheet('')
        if set(self.sender().displayText()).difference(set(".0123456789")):
            self.sender().setStyleSheet('background-color: #f00;')

    def __init__(self, skinCluster, vtxLName, skinBones, weights, parent=None):
        super(VertexInfluenceEditor, self).__init__(parent=None)
        self.setMinimumHeight(0)

        self.__info = {}
        self._hideZero = True
        self.__sliders = []
        self._solver = WeightSolver.Uniform

        if len(vtxLName) > 1:
            self.setTitle("Multi Slider")
            try:
                self.setToolTip(str(api.getIds(vtxLName)))
            except:
                pass
        else:
            self.setTitle(vtxLName[0].rsplit('|', 1)[-1])
            self.setToolTip(str(vtxLName))

        self.setLayout(nullVBoxLayout())

        self.__target = (skinCluster, vtxLName)
        self.__influences = skinBones
        self.__busyWithCallback = False

        for i, skBone in enumerate(skinBones):
            sliderLayout = nullHBoxLayout()
            sliderFrame = QWidget()
            sliderFrame.setLayout(sliderLayout)
            sliderFrame.isUsed = True

            gripSlider = SliderControl(skBone, label=skBone.rsplit('|', 1)[-1], mn=0.0, mx=1.0, rigidRange=True, labelOnSlider=True)
            gripSlider.slider.setValue(weights[i])

            gripSlider.startScrub.connect(partial(api.startUndo, "skinSliderChunk"))
            gripSlider.endScrub.connect(partial(api.endUndo, "skinSliderChunk"))
            gripSlider.slider.valueChanged.connect(functools.partial(self.__updateWeights, i))
            gripSlider.lineEdit.textEdited[unicode].connect(self.__lineEdit_FieldEditted)

            sliderLayout.addWidget(gripSlider)
            lbl = VertexInfluenceEditor.lockIcon
            parent = self.layout()

            if weights[i] <= 0.00001:
                lbl = VertexInfluenceEditor.unlockIcon
                sliderFrame.isUsed = False
                gripSlider.setEnabled(False)

            lockButton = QPushButton(lbl, '')
            lockButton.clicked.connect(functools.partial(self.__toggleLock, i))

            lockButton.setStyleSheet("")
            if lbl == VertexInfluenceEditor.unlockIcon:
                lockButton.setStyleSheet("background-color: lightred")

            sliderLayout.addWidget(lockButton)
            parent.addWidget(sliderFrame)

            self.__info[skBone] = sliderFrame
            self.__sliders.append((gripSlider, lockButton))

    def _setSolver(self, idx):
        if isinstance(idx, int):
            self._solver = [WeightSolver.Uniform, WeightSolver.PriorityLow, WeightSolver.PriorityHigh][idx]
        else:
            self._solver = idx

    solver = property(None, _setSolver)

    def hideZero(self, state):
        self._hideZero = state

    def showBones(self, inBones):
        for bone, frame in self.__info.items():
            if self._hideZero:
                if frame.isUsed and bone in inBones:
                    frame.setVisible(True)
                else:
                    frame.setVisible(False)
            else:
                frame.setVisible(bone in inBones)

    def getCurrentBones(self):
        return self.__info.keys()

    def __toggleLock(self, index):
        slider, button = self.__sliders[index]
        if slider.isEnabled():
            button.setIcon(VertexInfluenceEditor.unlockIcon)
            slider.setEnabled(False)
            button.setStyleSheet("background-color: lightred")
        else:
            button.setIcon(VertexInfluenceEditor.lockIcon)
            slider.setEnabled(True)
            button.setStyleSheet("")

    def __updateWeights(self, setId, newValue):
        """
        normalize all other weights so we can cleanly inject the new value

        calculate what weight will remain after injecting the new value
        then multiply all other weights by that value, so that all other weights added together = the remainder
        this works because the sum of all weights is first made to be 1.0, then we do (1.0 * 1.0 - newValue) where each 1.0 is actually the list of weights

        these steps are optimized to 'find the total value we should divide by to normalize'
        and 'multiply by the remainder and divide by the total value at the same time', so instead of 2 steps (normalize and multiply separately)
        we just multiply by a ratio of (1.0 - newValue) / initialRemainderTotal

        the target weight can be set either at the start or at the end because it's index is otherwise ignored
        """
        if self.__busyWithCallback:
            # callback fired by a setValue which was called by another slider's updateWeights
            return
        self.__busyWithCallback = True

        try:
            numSliders = len(self.__sliders)
            if numSliders < 2:
                return
            weights = self.uniformNormalisation(setId, numSliders, newValue)
        finally:
            self.__busyWithCallback = False

        # apply to skincluster
        stack = []
        for i in range(numSliders):
            stack.append((self.__influences[i], weights[i]))

        api.skinPercent(*self.__target, normalize=True, transformValue=stack)

    
    def uniformNormalisation(self, setId, numSliders, newValue):
        """Apply the pure slider policy, then update the enabled controls."""
        sliders = self.__sliders[:numSliders]
        values = [control.slider.value() for control, button in sliders]
        enabled = [control.isEnabled() for control, button in sliders]
        solver = {WeightSolver.Uniform: 'uniform', WeightSolver.PriorityLow: 'low',
                  WeightSolver.PriorityHigh: 'high'}.get(self._solver, 'uniform')
        weights = weightMath.sliderWeights(values, enabled, setId, newValue, solver)
        for i, (control, button) in enumerate(sliders):
            if i != setId and enabled[i]:
                control.slider.setValue(weights[i])
        return weights
