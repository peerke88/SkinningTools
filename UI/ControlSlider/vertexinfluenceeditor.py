# -*- coding: utf-8 -*-
import functools, re
from SkinningTools.Maya import api
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl


class VertexInfluenceEditor(QGroupBox):
    lockIcon = QIcon(':/nodeGrapherUnlocked.png')
    unlockIcon = QIcon(':/lockGeneric.png')

    def __unusedJointsBox(self):
        unusedJoints = QGroupBox()
        unusedJoints.setTitle('Unused influences')
        unusedJoints.setFlat(True)
        l = nullVBoxLayout()
        unusedJoints.setLayout(l)
        unusedJoints.setCheckable(True)
        unusedJoints.toggled.connect(self._toggleGroupBox)
        self.__unusedJoints = unusedJoints

    def _toggleGroupBox(self, state):
        layout = self.sender().layout()
        counter = 0
        while True:
            item = layout.itemAt(counter)
            if not item:
                return
            counter += 1
            widget = item.widget()
            if not widget:
                continue
            widget.setVisible(state)

    def __lineEdit_FieldEditted(self, *_):
        self.sender().setStyleSheet('')
        if set(self.sender().displayText()).difference(set(".0123456789")):
            self.sender().setStyleSheet('background-color: #f00;')

    def __init__(self, skinCluster, vtxLName, skinBones, weights, parent=None):
        super(VertexInfluenceEditor, self).__init__(parent=None)
        self.setMinimumHeight(0)

        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self._toggleGroupBox)
        self.setTitle(vtxLName.rsplit('|', 1)[-1])
        self.setLayout(nullVBoxLayout())

        self.__target = (skinCluster, vtxLName)
        self.__influences = skinBones

        self.__sliders = []

        hasUnused = False
        self.__unusedJointsBox()

        self.__busyWithCallback = False

        divider = QFrame()
        divider.setFrameStyle(QFrame.HLine)
        divider.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        divider.setLineWidth(1)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(divider)

        unusedSliders = 0
        for i, skBone in enumerate(skinBones):
            sliderLayout = nullHBoxLayout()
            sliderFrame = QFrame()
            sliderFrame.setLayout(sliderLayout)
            gripSlider = SliderControl(skBone, label=skBone.rsplit('|', 1)[-1], mn=0.0, mx=1.0, rigidRange=True, labelOnSlider=True)
            gripSlider.slider.setValue(weights[i])
            gripSlider.slider.valueChanged.connect(functools.partial(self.__updateWeights, i))
            gripSlider.lineEdit.textEdited[unicode].connect(self.__lineEdit_FieldEditted)

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

        numSliders = len(self.__sliders)
        if numSliders - 1 == 0:
            return  # no other sliders to edit

        totalValue = 0.0
        offset = newValue

        totalLength = 0.0
        for i in range(numSliders):
            if i == setId:
                continue
            slider, __ = self.__sliders[i]
            if not slider.isEnabled():
                totalLength += slider.slider.value()

        if offset > (1.0 - totalLength):
            offset = (1.0 - totalLength)
            newValue = offset

        weights = [0.0] * numSliders
        for i in range(numSliders):
            if i == setId:
                continue
            slider, __ = self.__sliders[i]
            if not slider.isEnabled():
                offset += slider.slider.value()
                continue
            weights[i] = slider.slider.value()
            totalValue += weights[i]

        weights[setId] = newValue
        if totalValue == 0:
            scale = (1.0 - offset) / (numSliders - 1)
        else:
            scale = (1.0 - offset) / totalValue
        for i in range(numSliders):
            if i == setId:
                continue
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
        # self._snapHiliteNode(self.__target)
        self.__busyWithCallback = False

        # apply to skincluster
        stack = []
        for i in range(numSliders):
            stack.append((self.__influences[i], weights[i]))

        api.skinPercent(*self.__target, normalize=True, transformValue=stack)
