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

from skinningTool.SkinWeightsEditor import selectableview
from skinningTool.SkinWeightsEditor import model

class _DoubleSpinBoxDelegate(QDoubleSpinBox):
    submitted = pyqtSignal(float)

    def __init__(self, *args):
        super(_DoubleSpinBoxDelegate, self).__init__(*args)
        self.installEventFilter(self)
        self.setSingleStep(.01)
        self.setMinimum(.0)
        self.setMaximum(1.0)

    def eventFilter(self, sender, event):
        if sender == self and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.close()
                return True
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.submitted.emit(self.value())
                self.close()
                return True
        return False


class SkinWeightsEditor(selectableview.SkinWeightsSelectable):
    def __init__(self, *args):
        super(SkinWeightsEditor, self).__init__(*args)
        self.__editor = _DoubleSpinBoxDelegate(self)
        self.__editor.hide()
        self.__editor.setFocusPolicy(Qt.StrongFocus)
        self.__editor.focusOutEvent = lambda e: self.__editor.close()

        self.value = 0.0
        self.__editor.submitted.connect(self.__setSelectedValues)

    def mouseReleaseEvent(self, event):
        # finalize highlighting
        super(SkinWeightsEditor, self).mouseReleaseEvent(event)
        # open editor
        c, r = self.rowColumnAt(-self.geometry().topLeft() + QPoint(self.CELL_WIDTH * 0.7, self.CELL_HEIGHT * 0.7))
        if c < 0 or r < 0:
            return

        c = min(max(c, self._selectionArea[0]), self._selectionArea[2])
        c = min(c, self.model().columnCount() - 1)
        r = min(max(r, self._selectionArea[1]), self._selectionArea[3])
        r = min(r, self.model().rowCount() - 1)

        self.__editor.setValue(self.model().value(c, r))

        self.popupEditor(QRect(c * self.CELL_WIDTH,
                           r * self.CELL_HEIGHT,
                           self.CELL_WIDTH,
                           self.CELL_HEIGHT))


    def __setSelectedValues(self, value):
        cols = range(self._selectionArea[0], self._selectionArea[2] + 1)
        rows = range(self._selectionArea[1], self._selectionArea[3] + 1)
        self._model.setValues(cols, rows, [value] * (len(rows) * len(cols)))
        self.repaint()
        self.clearSelection()

    def popupEditor(self, area):
        self.__editor.setGeometry(area)
        self.__editor.show()
        self.__editor.setFocus()
        self.__editor.selectAll()


class SkinWeightsWidget(selectableview.SkinWeightsTable):
    def _initView(self, model):
        self._view = SkinWeightsEditor(model)
        self.setMouseTracking(True)

    def mouseReleaseEvent(self, event):
        # finalize highlighting
        super(SkinWeightsWidget, self).mouseReleaseEvent(event)
        # top-left cell
        c, r = self._view.rowColumnAt(-self._view.geometry().topLeft() + QPoint(self._view.CELL_WIDTH * 0.7, self._view.CELL_HEIGHT * 0.7))
        # clamp to selected columns
        right = self._columnAt(event.pos().x())
        c = min(max(c, self._selectColumnLeft), right)
        # open editor at cell
        self._view.popupEditor(QRect(c * self._view.CELL_WIDTH,
                           r * self._view.CELL_HEIGHT,
                           self._view.CELL_WIDTH,
                           self._view.CELL_HEIGHT))