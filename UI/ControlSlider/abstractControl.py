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

class AbstractControl(QWidget):
    preLogicEvaluation  = pyqtSignal()
    postLogicEvaluation = pyqtSignal()

    def __init__(self, name, parent=None):
        QWidget.__init__(self, parent)

        self.name = name
        self.selected = False
        ## pointer to a function
        self._logic = None
        self._logicArgs = (self,)

    def setLogicFunction(self, function, *args, **kwds):
        self._logic = function
        self._logicArgs = (args, kwds)

    def paintEvent(self, e):
        QWidget.paintEvent(self, e)
        qp = QPainter()
        qp.begin(self)
        
        size = self.size()
        w = size.width()
        h = size.height()
        if self.selected == True:
            qp.setBrush(Qt.NoBrush)
            pen = QPen(QColor(96, 127, 156), 1, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(2, 1, w-2, 1)
            qp.drawLine(w-1, 2, w-1, h-2)
            qp.drawLine(2, h-1, w-2, h-1)
            qp.drawLine(1, 2, 1, h-2)

        qp.end()

    def evaluateLogic(self):
        self.preLogicEvaluation.emit()
        if self._logic is not None:
            self._logic(self, *self._logicArgs[0], **self._logicArgs[1])     
        self.postLogicEvaluation.emit()
