# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.tearOff.editableTab import EditableTabWidget
from SkinningTools.UI.tearOff.tearOffDialog import *
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.fallofCurveUI import BezierGraph
from SkinningTools.UI.messageProgressBar import MessageProgressBar
import tempfile, os
from functools import partial

from SkinningTools.UI.tabs.vertAndBoneFunction import VertAndBoneFunction
from SkinningTools.UI.tabs.mayaToolsHeader import MayaToolsHeader
from SkinningTools.UI.tabs.vertexWeightMatcher import TransferWeightsWidget, ClosestVertexWeightWidget

__VERSION__ = "5.0.20200820"
# _DIR = os.path.dirname(os.path.abspath(__file__))


class SkinningTools(QMainWindow):
    def __init__(self, parent=None):
        super(SkinningTools, self).__init__(parent)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        self.setWindowFlags(Qt.Tool)
        self.progressBar = MessageProgressBar()

        self.__defaults()

        mainLayout = nullVBoxLayout(None, 3)
        mainWidget.setLayout(mainLayout)

        self.__menuSetup()
        self.__tabsSetup()

        self.__mayaToolsSetup()
        self.__skinSliderSetup()
        self.__componentEditSetup()
        self.__weightManagerSetup()

        mainLayout.addWidget(self.tabs)

        self.loadUIState()
        
        mainLayout.addWidget(self.progressBar)

        api.dccInstallEventFilter()

    # ------------------------- defaults -------------------------------

    def __defaults(self):
        # self.__graphSize = 60
        # self.__iconSize = 40
        self.settings = QSettings("uiSkinSave", "SkinningTools")
        self.__liveIMG = QPixmap(":/UVPivotLeft.png")
        self.__notLiveIMG = QPixmap(":/enabled.png")
        self.__isConnected = QPixmap(":/hsDownStreamCon.png")
        self.__notConnected = QPixmap(":/hsNothing.png")
        self.BezierGraph = BezierGraph()

    # ------------------------- ui Setups ---------------------------------
    def __menuSetup(self):
        self.setMenuBar(QMenuBar())
        self.menuBar().setLayoutDirection(Qt.RightToLeft)
        self.extraMenu = QMenu('Extra', self)
        helpAction = QMenu('', self)
        helpAction.setIcon(QIcon(":/QR_help.png"))

        self.holdAction = QAction("hold Model", self)
        self.fetchAction = QAction("fetch Model", self)
        self.objSkeletonAction = QAction("skeleton -> obj", self)
        docAction = QAction("Docs", self)
        self.tooltipAction = QAction("Enhanced ToolTip", self)
        self.tooltipAction.setCheckable(True)

        for act in [self.holdAction, self.fetchAction, self.objSkeletonAction]:
            self.extraMenu.addAction(act)
        for act in [docAction, self.tooltipAction]:
            helpAction.addAction(act)

        self.changeLN = QAction("[EN]", self)

        self.menuBar().addMenu(helpAction)
        self.menuBar().addMenu(self.extraMenu)
        self.menuBar().addAction(self.changeLN)

    def __tabsSetup(self):
        self.tabs = EditableTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.tearOff.connect(self.tearOff)

    def __mayaToolsSetup(self):
        tab = self.tabs.addGraphicsTab("Maya Tools")

        self.mayaToolsTab = EditableTabWidget()
        self.mayaToolsTab.tearOff.connect(self.tearOff)

        v = nullVBoxLayout()
        widget = MayaToolsHeader(self.BezierGraph, self.progressBar, self)
        v.addWidget(widget)
        v.addWidget(self.mayaToolsTab)
        tab.view.frame.setLayout(v)

        self.__addVertNBoneFunc()
        self.__addCopyRangeFunc()
        self.__addSimpleTools()

    def __addSimpleTools(self):
        tab = self.mayaToolsTab.addGraphicsTab("Simple Maya Tools")
        v = nullVBoxLayout()
        tab.view.frame.setLayout(v)
        buttons = interface.dccToolButtons()
        for btn in buttons:
            v.addWidget(btn)
        v.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __addVertNBoneFunc(self):
        tab = self.mayaToolsTab.addGraphicsTab("Vertex & bone functions")
        v = nullVBoxLayout()
        widget = VertAndBoneFunction(self.BezierGraph, self.progressBar, self)
        v.addWidget(widget)
        tab.view.frame.setLayout(v)

    def __addCopyRangeFunc(self):
        tab = self.mayaToolsTab.addGraphicsTab("copy functions")
        v = nullVBoxLayout()
        tab.view.frame.setLayout(v)

        closest = ClosestVertexWeightWidget()
        transfer = TransferWeightsWidget()
        for w in [closest, transfer]:
            v.addWidget(w)
        v.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __skinSliderSetup(self):
        tab = self.tabs.addGraphicsTab("Skin Slider")
        self.inflEdit = SkinningToolsSliderList()
        v = nullVBoxLayout()
        h = nullHBoxLayout()
        cnct = toolButton(self.__notConnected)
        rfr = toolButton(":/playbackLoopingContinuous_100.png")
        live = toolButton(self.__liveIMG)
        
        cnct.setCheckable(True)
        live.setCheckable(True)

        live.clicked.connect(self._updateLive)
        cnct.clicked.connect(self._updateConnect)

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [cnct, rfr, live]:
            h.addWidget(btn)

        v.addLayout(h)
        tab.view.frame.setLayout(v)
        v.addWidget(self.inflEdit)

    def __componentEditSetup(self):
        self.tabs.addGraphicsTab("Component Editor")

    def __weightManagerSetup(self):
        self.tabs.addGraphicsTab("Weight Manager")

    # ------------------------- connections ---------------------------------

    def _updateLive(self):
        liveBtn = self.sender()
        if liveBtn.isChecked():
            liveBtn.setIcon(QIcon(self.__notLiveIMG))
        else:
            liveBtn.setIcon(QIcon(self.__liveIMG))

    def _updateConnect(self):
        liveBtn = self.sender()
        if liveBtn.isChecked():
            liveBtn.setIcon(QIcon(self.__isConnected))
        else:
            liveBtn.setIcon(QIcon(self.__notConnected))

    # ------------------------- utilities ---------------------------------

    def _tabName(self, index=-1, mainTool=None):
        if mainTool is None:
            raise NotImplementedError()
        if index < 0:
            index = mainTool.currentIndex()
        return mainTool.tabText(index)

    def tearOff(self, index, pos=QPoint()):
        tabs = self.sender()
        view = tabs.viewAtIndex(index)
        dlg = TearOffDialog(self._tabName(index, tabs), self)
        dlg.setOriginalState(index, tabs)
        dlg.addwidget(view)
        if pos.y() > -1:
            dlg.move(pos)

        dlg.show()
        tabs.removeTab(index)

    # -------------------- window geometry -------------------------------

    def saveUIState(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("tools", self.mayaToolsTab.currentIndex())
        self.settings.setValue("tabs", self.tabs.currentIndex())

    def loadUIState(self):
        getGeo = self.settings.value("geometry")
        if getGeo == None:
            return
        self.restoreGeometry(getGeo)
        tools = {"tools": self.mayaToolsTab,
                "tabs": self.tabs}
        for key, comp in tools.iteritems():
            index = self.settings.value(key)
            if index is None:
                index = 0
            comp.setCurrentIndex(index)            

    def hideEvent(self, event):
        self.saveUIState()


def showUI():
    window_name = 'SkinningTools: %s' % __VERSION__
    mainWindow = api.get_maya_window()

    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == window_name:
                child.close()
                child.deleteLater()
    window = SkinningTools(mainWindow)
    window.setObjectName(window_name)
    window.setWindowTitle(window_name)
    window.show()

    return window
