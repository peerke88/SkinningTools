# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *


class TearOffDialog(QDialog):
    """ the dialog that holds tab that is torn off
    """
    closed = pyqtSignal(QDialog)

    def __init__(self, tabName, parent=None):
        """ the constructor
                
        :param tabName: name of the tab to use
        :type tabName: string
        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(TearOffDialog, self).__init__(parent, Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('TearOff : %s' % tabName)
        self.__tabName = tabName
        self.__tabWidget = None
        self.__index = -1
        self.__cWidget = None
        return

    def gettabName(self):
        """ get the current name of the tab

        :return: the original name of the tab
        :rtype: string
        """
        return self.__tabName

    def settabName(self, inTabName):
        """ set the new name for the tab

        :param inTabName: the new name for the tab
        :type inTabName: string
        """
        self.__tabName = inTabName
        self.setWindowTitle('TearOff : %s' % inTabName)

    """tab name property"""
    tabName = property(gettabName, settabName)

    def setOriginalState(self, index, tabWidget):
        """ override for the original state of the tab
        sets the new widget and index

        :param index: the index on which the tab should be placed when the widget is closed
        :type index: int
        :param tabWidget: the new widget to use for the tabs
        :type tabWidget: QWidget
        """
        self.__index = index
        self.__tabWidget = tabWidget

    def addwidget(self, inWidget):
        """ the widget to add to the current dialogs layout

        :param inWidget: the widget to use for extracted dialog
        :type inWidget: QWidget
        """
        self.layout().addWidget(inWidget)
        self.__cWidget = inWidget

    def resize(self, *args):
        """ convenience function to resize the current dialog
        """
        if len(args) == 1 and isinstance(args[0], QSize):
            size = args[0]
            args = tuple([size])
        super(TearOffDialog, self).resize(*args)

    def closeEvent(self, event):
        """ management function to reset the current widgets position and parent when the dialog is closed
        """
        mainWindow = self.__tabWidget.window()
        maintabNames = [self.__tabWidget.tabText(i) for i in range(self.__tabWidget.count())]
        if self.__tabName not in maintabNames:
            self.__tabWidget.addView(self.__tabName, self.__index, self.__cWidget)
        self.closed.emit(self)
        super(TearOffDialog, self).closeEvent(event)
