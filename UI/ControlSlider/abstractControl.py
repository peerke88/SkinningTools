# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *


class AbstractControl(QWidget):
    preLogicEvaluation = pyqtSignal()
    postLogicEvaluation = pyqtSignal()

    def __init__(self, name, parent=None):
        QWidget.__init__(self, parent)

        self.name = name
        self.selected = False
        ## pointer to a function
        self._logic = None
        self._logicArgs = (self,), {}

    def setLogicFunction(self, function, *args, **kwargs):
        self._logic = function
        self._logicArgs = (args, kwargs)

    def paintEvent(self, e):
        QWidget.paintEvent(self, e)
        qp = QPainter()
        qp.begin(self)

        size = self.size()
        w = size.width()
        h = size.height()

        if not self.selected:
            qp.end()
            return

        qp.setBrush(Qt.NoBrush)
        pen = QPen(QColor(96, 127, 156), 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(2, 1, w - 2, 1)
        qp.drawLine(w - 1, 2, w - 1, h - 2)
        qp.drawLine(2, h - 1, w - 2, h - 1)
        qp.drawLine(1, 2, 1, h - 2)

        qp.end()

    def evaluateLogic(self):
        self.preLogicEvaluation.emit()
        if self._logic is not None:
            self._logic(self, *self._logicArgs[0], **self._logicArgs[1])
        self.postLogicEvaluation.emit()
