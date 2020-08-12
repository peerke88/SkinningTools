# -*- coding: utf-8 -*-
# Copyright (C) 2020 Perry Leijten
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
from ..qt_util import *

class TearOffDialog(QDialog):
    closed = pyqtSignal(QDialog)

    def __init__(self, mapName, parent = None):
        super(TearOffDialog, self).__init__(parent, Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('TearOff : %s'%mapName)
        self.__mapName = mapName
        self.__tabWidget = None
        self.__index = -1
        self.__listView = None
        return

    def getMapName(self):
        return self.__mapName

    def setMapName(self, inMapname):
        self.__mapName = inMapname

    mapName = property(getMapName, setMapName)

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
        mainMapNames = [ self.__tabWidget.tabText(i) for i in xrange(self.__tabWidget.count()) ]
        if self.__mapName not in mainMapNames:
            self.__tabWidget.addView(self.__mapName, self.__index, self.__listView)
        self.closed.emit(self)
        super(TearOffDialog, self).closeEvent(event)