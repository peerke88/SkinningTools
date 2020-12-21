# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.py23 import *


class Slider(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, mn, mx, parent=None, label=None):
        QWidget.__init__(self, parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.__min = float(mn)
        self.__max = float(mx)
        self.__value = 0.0
        self.__label = label
        self.rigidRange = False
        self.paintLabel = True

        self.setFocusPolicy(Qt.StrongFocus)

    def setPaintLabel(self, value):
        self.paintLabel = value
        self.repaint()

    def sizeHint(self):
        return QSize(100, 20)

    def value(self):
        return self.__value

    def getValueAsString(self):
        return '%0.3f' % self.__value

    def setValue(self, value):
        if self.rigidRange:
            if value > self.__max:
                value = self.__max
            elif value < self.__min:
                value = self.__min

        self.__value = value
        self.repaint()
        self.valueChanged.emit(value)

    def maximum(self):
        return self.__max

    def setMaximum(self, value):
        self.__max = value
        self.repaint()

    def minimum(self):
        return self.__min

    def setMinimum(self, value):
        self.__min = value
        self.repaint()

    def setRange(self, minValue, maxValue):
        self.setMinimum(minValue)
        self.setMaximum(maxValue)

    def paintEvent(self, _):
        painter = QPainter()
        painter.begin(self)
        self.drawWidget(painter)
        painter.end()

    def drawWidget(self, painter):
        size = self.size()
        w = size.width()
        h = size.height()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(101, 101, 101))
        painter.drawRoundedRect(0, 0, w - 1, h - 1, 3, 3)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.SolidPattern)

        painter.setBrush(QColor(128, 155, 172))
        painter.drawRoundedRect(0, 0, self.sliderPosition() - 1, h - 1, 3, 3)

        painter.setBrush(Qt.NoBrush)
        if self.hasFocus():
            pen = QPen(QColor(96, 127, 156), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(2, 1, w - 2, 1)
            painter.drawLine(w - 1, 2, w - 1, h - 2)
            painter.drawLine(2, h - 1, w - 2, h - 1)
            painter.drawLine(1, 2, 1, h - 2)
        else:
            pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRoundedRect(0, 0, w - 1, h - 1, 3, 3)

        pen = QPen(QColor(230, 230, 230), 1, Qt.SolidLine)
        painter.setPen(pen)
        if self.__label is not None and self.paintLabel:
            valueStr = self.__label
        else:
            valueStr = unicode(self.getValueAsString())
        fontMetrics = painter.fontMetrics()
        valueStrLength = fontMetrics.width(valueStr)
        painter.drawText(QPointF(w * 0.5 - valueStrLength * 0.5, h - 6), valueStr)

    def sliderPosition(self):
        w = float(self.width())
        d = self.maximum() - self.minimum()
        ival = self.value() - self.__min
        if ival <= 0:
            ival = 0.0

        p = ival / d
        return w * p

    def mouseMoveEvent(self, event):
        pos = float(event.pos().x())
        w = float(self.width())
        d = self.maximum() - self.minimum()
        val = d * (pos / w)
        self.setValue(val + self.__min)
