# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
import os
from SkinningTools.Maya import api, interface

TOOLTIPDIRECTORY = os.path.join(interface.getInterfaceDir(), "helpFiles")
class AdvancedToolTip(QWidget):
    def __init__(self, rect, parent=None):
        super(AdvancedToolTip, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(rect)
        
        self.inText = ""
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(3,3,3,3)
        self.setLayout(self.layout)

    def toolTipExists(self, imageName):
        files = os.listdir(TOOLTIPDIRECTORY)
        if imageName in files:
            return True
        return False
    
    def setTip(self, inText):
        self.inText = inText
            
    def setGifImage(self, gifName):
        gifImage = os.path.join(TOOLTIPDIRECTORY, "%s.gif"%gifName )
        self.movie = QMovie( gifImage )
        size = self.geometry().height()
        self.movie.setScaledSize(QSize(size, size))
        self.movie.setCacheMode( QMovie.CacheAll )
        self.textLabel = QTextEdit(self.inText)
        self.textLabel.setMinimumWidth(size)
        self.textLabel.setMaximumWidth(size)
        self.textLabel.setEnabled(False)
        self.gifLabel = QLabel()
        self.gifLabel.setMovie( self.movie )
        self.movie.start()

        self.layout.addWidget(self.gifLabel)
        self.layout.addWidget(self.textLabel)

