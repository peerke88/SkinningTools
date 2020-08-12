# -*- coding: utf-8 -*-
from .qtUtil import *

class QColorButton(QPushButton):
    colorChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.clicked.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color == None:
            self.setStyleSheet('background-color: #5D5D5D')
        
        self.setStyleSheet("background-color: %s;" % self._color)

    def color(self):
        return self._color

    def onColorPicker(self):
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mouseClickEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)
      
        return super(QColorButton, self).mousePressEvent(e)
