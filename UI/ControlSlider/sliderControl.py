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
from ..qtUtil import *

from functools import partial
from .abstractControl import AbstractControl
from .slider import Slider

class SliderControl(AbstractControl):
    editModeRequested = pyqtSignal()
    editModeEnded = pyqtSignal()

    startScrub = pyqtSignal()
    endScrub = pyqtSignal()

    def __init__(self, name, label='slider control', min=-100.0, max=100.0, rigidRange=False, parent=None, labelOnSlider=False):
        AbstractControl.__init__(self, name, parent)
        self.editModeLock = False

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(6,4,3,3)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.hide()
        self.lineEdit.installEventFilter(self)

        if labelOnSlider:
            self.slider = Slider(min, max, self, label)
        else:
            self.slider = Slider(min, max, self)
        self.slider.rigidRange = rigidRange
        self.slider.installEventFilter(self)

        self.startScrub.connect(partial(self.slider.setPaintLabel, False))
        self.endScrub.connect(partial(self.slider.setPaintLabel, True))

        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.slider)
        if not labelOnSlider:
            self.label = QLabel(label, self)
            self.layout.addWidget(self.label)

        self.slider.valueChanged.connect(self.evaluateLogic)

    def editBegin(self, value):
        self.editModeRequested.emit()
        self.slider.hide()
        self.lineEdit.setText(value)
        self.lineEdit.setFocus(Qt.MouseFocusReason)
        self.lineEdit.deselect()
        self.lineEdit.show()
        self.repaint()
    
    def editEnd(self):
        if self.editModeLock == True:
            return
        self.lineEdit.hide()
        strValue = str(self.lineEdit.text())
        try:
            newValue = eval(strValue)
            self.slider.setValue(newValue)
        except:
            pass
        self.slider.show()
        self.slider.setFocus(Qt.MouseFocusReason)

        self.editModeEnded.emit()

    def eventFilter(self, obj, event):
        if obj==self.slider:
            if event.type() == QEvent.MouseButtonPress:
                self.startScrub.emit()
                self.slider.setFocus(Qt.MouseFocusReason)
            elif event.type() == QEvent.MouseButtonRelease:
                self.endScrub.emit()
                self.mouseReleaseEvent(event)
            elif event.type() == QEvent.MouseButtonDblClick:
                self.editBegin(self.slider.getValueAsString())
            elif event.type() == QEvent.KeyPress:
                if event.key() in (42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58):
                    self.editBegin(event.text())
            elif event.type() == QEvent.Enter:
                self.slider.setPaintLabel(False)
            elif event.type() == QEvent.Leave:
                self.slider.setPaintLabel(True)
            return False

        elif obj==self.lineEdit:
            if obj.isEnabled() == True:
                if event.type() == QEvent.KeyPress:
                    if event.key() == 16777220: # return key
                        self.editEnd()
                        obj.setStyleSheet('')
                elif event.type() == QEvent.FocusOut:
                    self.editEnd()
            return False

        else:
            return AbstractControl.eventFilter(self, obj, event)



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    def logic1():
        print ('hey hey')
        pippo = 2+3
        print ('pippo', pippo)
        print (sys)

    def logic2(who):
        print ('hello from %s' %who)

    
    w = QWidget()
    w.setWindowTitle('Slider Controls')
    l = QVBoxLayout(w)
    s1 = SliderControl('slider_1', -10, 10, w)
    s1.setLogicFunction(logic1)
    s2 = SliderControl('slider_2', -100, 100, w)
    s2.setLogicFunction(logic2, s2)
    l.addWidget(s1)
    l.addWidget(s2)
    w.show()
    
    sys.exit(app.exec_())

