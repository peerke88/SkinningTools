# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *


class TearOffDialog(QDialog):
    closed = pyqtSignal(QDialog)

    def __init__(self, tabName, parent=None):
        super(TearOffDialog, self).__init__(parent, Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('TearOff : %s' % tabName)
        self.__tabName = tabName
        self.__tabWidget = None
        self.__index = -1
        self.__listView = None
        return

    def gettabName(self):
        return self.__tabName

    def settabName(self, inTabName):
        self.__tabName = inTabName

    tabName = property(gettabName, settabName)

    def setOriginalState(self, index, tabWidget):
        self.__index = index
        self.__tabWidget = tabWidget

    def addwidget(self, listView):
        self.layout().addWidget(listView)
        self.__listView = listView

    def resize(self, *args):
        if len(args) == 1 and isinstance(args[0], QSize):
            size = args[0]
            args = tuple([size])
        super(TearOffDialog, self).resize(*args)

    def closeEvent(self, event):
        mainWindow = self.__tabWidget.window()
        maintabNames = [self.__tabWidget.tabText(i) for i in range(self.__tabWidget.count())]
        if self.__tabName not in maintabNames:
            self.__tabWidget.addView(self.__tabName, self.__index, self.__listView)
        self.closed.emit(self)
        super(TearOffDialog, self).closeEvent(event)
