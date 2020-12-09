# -*- coding: utf-8 -*-
import os
from SkinningTools.UI.qt_util import *
from SkinningTools.Maya import api, interface

TOOLTIPDIRECTORY = os.path.join(interface.getInterfaceDir(), "helpFiles")


class AdvancedToolTip(QWidget):
    """ advanced tooltip window
    allows the text of any language to be displayed together with a gif image to show what the current object could do for the user
    """
    def __init__(self, rect, parent=None):
        """ the constructor
        
        :param rect: the size of the widgets
        :type rect: QRect
        :param parent: the parent widget
        :type parent: QWidget
        """
        super(AdvancedToolTip, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(rect)

        self.inText = ""
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(self.layout)

    def toolTipExists(self, imageName):
        """ check if the image to display exists

        :return: True or False depending on if the image exists
        :rtype: bool
        """
        files = os.listdir(TOOLTIPDIRECTORY)
        if imageName in files:
            return True
        return False

    def setTip(self, inText):
        """ set the text for the tooltip

        :param inText: the tooltip text
        :type inText: string
        """
        self.inText = inText

    def setGifImage(self, gifName):
        """ set the gif to the current object and play automatically

        :param gifName: the path to the gif object
        :type gifName: string
        """
        gifImage = os.path.join(TOOLTIPDIRECTORY, "%s.gif" % gifName)
        self.movie = QMovie(gifImage)
        size = self.geometry().height()
        self.movie.setScaledSize(QSize(size, size))
        self.movie.setCacheMode(QMovie.CacheAll)
        self.textLabel = QTextEdit(self.inText)
        self.textLabel.setMinimumWidth(size)
        self.textLabel.setMaximumWidth(size)
        self.textLabel.setEnabled(False)
        self.gifLabel = QLabel()
        self.gifLabel.setMovie(self.movie)
        self.movie.start()

        self.layout.addWidget(self.gifLabel)
        self.layout.addWidget(self.textLabel)
