# -*- coding: utf-8 -*-
from ..qtUtil import *

class Slider(QWidget):
    valueChanged  = pyqtSignal(float)

    def __init__(self, min, max, parent=None, label=None):
        QWidget.__init__(self, parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.__min = float(min)
        self.__max = float(max)
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
        return '%0.3f' %self.__value

    def setValue(self, value):
        if self.rigidRange == True:
            if value>self.__max:
                value=self.__max
            elif value<self.__min:
                value=self.__min

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

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
      
    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        # background
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(101, 101, 101))
        qp.drawRoundedRect(0, 0, w-1, h-1, 3, 3)

        # slider bar
        value = self.value()
        qp.setPen(Qt.NoPen)
        qp.setBrush(Qt.SolidPattern)
        # qp.setBrush(QColor(255,170, 0)) ## orange but too bright? 
        qp.setBrush(QColor(128, 155, 172))
        qp.drawRoundedRect(0, 0, self.sliderPosition()-1, h-1, 3, 3)

        # draw
        qp.setBrush(Qt.NoBrush)
        if self.hasFocus() == True:
            pen = QPen(QColor(96, 127, 156), 2, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(2, 1, w-2, 1)
            qp.drawLine(w-1, 2, w-1, h-2)
            qp.drawLine(2, h-1, w-2, h-1)
            qp.drawLine(1, 2, 1, h-2)
        else:
            pen = QPen(QColor(20, 20, 20), 1, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawRoundedRect(0, 0, w-1, h-1, 3, 3)

        # print value
        pen = QPen(QColor(230, 230, 230), 1, Qt.SolidLine)
        qp.setPen(pen)
        if self.__label is not None and self.paintLabel:
            valueStr = self.__label
        else:
            valueStr = unicode(self.getValueAsString())
        fontMetrics = qp.fontMetrics()
        valueStrLength = fontMetrics.width(valueStr)
        qp.drawText(QPointF(w*0.5-valueStrLength*0.5, h-6), valueStr)

    def sliderPosition(self):
        val = self.value()
        w = float( self.width() )
        d = self.maximum() - self.minimum()
        ival = val - self.__min
        if ival <= 0:
            ival = 0.0
 
        p = ival/d
        return w*p

    def mouseMoveEvent(self, evt):
        pos = float( evt.pos().x() )
        w = float( self.width() )
        d = self.maximum() - self.minimum()
        val = d*(pos/w)
        self.setValue(val+self.__min)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    slider = GripSlider(-10, 10)
    slider.show()
    
    sys.exit(app.exec_())

