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
# --------------------------------------------------------------------------------------
from UI.qt_util import *
from py23 import *


class SkinWeightsViewport(QWidget):
    scrolled = pyqtSignal()

    CELL_WIDTH = 52
    CELL_HEIGHT = 17
    PADDING = 3

    def __init__(self, model, *args):
        super(SkinWeightsViewport, self).__init__(*args)
        self._model = model
        self._model.changed.connect(self.update)
        self.headerData = None

    def model(self):
        return self._model

    def sizeHint(self):
        s = QSize(self._model.columnCount() * SkinWeightsViewport.CELL_WIDTH, self._model.rowCount() * SkinWeightsViewport.CELL_HEIGHT)
        self.setMinimumSize(s)
        return s

    def _drawRow(self, painter, startCol, endCol, row, x, y, colCount):
        while startCol < endCol:
            v = self._model.value(startCol, row)

            r = QRect(x + SkinWeightsViewport.PADDING, y, SkinWeightsViewport.CELL_WIDTH - SkinWeightsViewport.PADDING - 1, SkinWeightsViewport.CELL_HEIGHT - 1)
            painter.drawText(r, Qt.AlignTop | Qt.AlignLeft, '%.3f' % v)

            x += SkinWeightsViewport.CELL_WIDTH
            startCol += 1

    def visibleSpan(self):
        rect = self.visibleRegion().boundingRect()

        c = int(rect.x() / SkinWeightsViewport.CELL_WIDTH)
        cols = int(rect.right() / SkinWeightsViewport.CELL_WIDTH) + 1
        cols = min(cols, self._model.columnCount())

        r = int(rect.y() / SkinWeightsViewport.CELL_HEIGHT)
        rows = int(rect.bottom() / SkinWeightsViewport.CELL_HEIGHT) + 1
        rows = min(rows, self._model.rowCount())

        return c, r, cols, rows

    def rowColumnAt(self, pos):
        if self._model.columnCount() == 0 or self._model.rowCount() == 0:
            return -1, -1

        x = int(pos.x() / SkinWeightsViewport.CELL_WIDTH)
        y = int(pos.y() / SkinWeightsViewport.CELL_HEIGHT)

        return min(max(x, 0), self._model.columnCount() - 1), min(max(y, 0), self._model.rowCount() - 1)

    def updateHeaderData(self):
        rect = self.visibleRegion().boundingRect()
        c, r, cols, rows = self.visibleSpan()

        self.headerData = [c, r, cols, rows, rect.x(), rect.y()]

    def paintEvent(self, event):
        rect = self.visibleRegion().boundingRect()
        colCount = self._model.columnCount()
        c, r, cols, rows = self.visibleSpan()

        x = c * SkinWeightsViewport.CELL_WIDTH
        y = r * SkinWeightsViewport.CELL_HEIGHT

        self.headerData = [c, r, cols, rows, rect.x(), rect.y()]

        painter = QPainter(self)
        pen = painter.pen()
        painter.setPen(Qt.NoPen)
        if QT_VERSION == "pyqt4":
            painter.setBrush(QPalette(QPalette.Active).alternateBase())
        elif QT_VERSION == "pyside":
            painter.setBrush(QApplication.palette().alternateBase())
        else:
            painter.setBrush(QApplication.palette("").alternateBase())
        painter.drawRect(rect)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(pen)

        while r < rows:
            self._drawRow(painter, c, cols, r, x, y, colCount)
            y += SkinWeightsViewport.CELL_HEIGHT
            r += 1

        self.scrolled.emit()


class SkinWeightsView(QWidget):
    def __init__(self, model, *args):
        super(SkinWeightsView, self).__init__(*args)
        self._initView(model)
        self._view.scrolled.connect(self.update)

        ar = QScrollArea()
        ar.setWidget(self._view)
        ar.setWidgetResizable(True)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(ar)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(SkinWeightsViewport.CELL_WIDTH, SkinWeightsViewport.CELL_HEIGHT, 0, 0)

        self.setMinimumWidth(SkinWeightsViewport.CELL_WIDTH * 2.5)
        self.setMinimumHeight(SkinWeightsViewport.CELL_HEIGHT * 2.5)

    def _initView(self, model):
        self._view = SkinWeightsViewport(model)

    def headerLabel(self, index):
        return self._view.model().influenceName(index)

    def _columnAt(self, x):
        margins = list(self.layout().getContentsMargins())
        margins[0] += -self._view.headerData[4] + SkinWeightsViewport.PADDING
        c = int((x - margins[0]) / SkinWeightsViewport.CELL_WIDTH)
        return min(c, self._view.model().columnCount() - 1)

    def paintEvent(self, event):
        self._view.updateHeaderData()
        if self._view.headerData is None:
            return
        painter = QPainter(self)

        margins = list(self.layout().getContentsMargins())
        margins[0] += -self._view.headerData[4] + SkinWeightsViewport.PADDING
        margins[1] -= self._view.headerData[5]

        # draw column labels
        c = self._view.headerData[0]
        while c < self._view.headerData[2]:
            area = QRect(c * SkinWeightsViewport.CELL_WIDTH + margins[0],
                         0,
                         SkinWeightsViewport.CELL_WIDTH - SkinWeightsViewport.PADDING,
                         SkinWeightsViewport.CELL_HEIGHT)

            txt = self.headerLabel(c)
            painter.drawText(area, Qt.AlignCenter | Qt.AlignLeft, txt)
            c += 1

        # draw row labels
        for r in xrange(self._view.headerData[1], self._view.model().rowCount()):
            area = QRect(SkinWeightsViewport.PADDING,
                         r * SkinWeightsViewport.CELL_HEIGHT + margins[1],
                         SkinWeightsViewport.CELL_WIDTH - SkinWeightsViewport.PADDING,
                         SkinWeightsViewport.CELL_HEIGHT)
            painter.drawText(area, Qt.AlignCenter | Qt.AlignRight, self._view.model().rowLabel(r))

        # draw background
        painter.setPen(Qt.NoPen)
        if QT_VERSION == "pyqt4":
            painter.setBrush(QPalette(QPalette.Active).alternateBase())
        elif QT_VERSION == "pyside":
            painter.setBrush(QApplication.palette().alternateBase())
        else:
            painter.setBrush(QApplication.palette("").alternateBase())
        painter.drawRect(0, 0, SkinWeightsViewport.CELL_WIDTH, SkinWeightsViewport.CELL_HEIGHT)
