# -*- coding: utf-8 -*-
from .qt_util import *
from .utils import *
from .tearOff.editableTab import EditableTabWidget
from .tearOff.tearOffDialog import *
from ..Maya.tools.shared import *
from .ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from .fallofCurveUI import BezierGraph
from functools import partial
import tempfile, os

__VERSION__ = "5.0.20200812"


class SkinningTools(QMainWindow):
    def __init__(self, parent=None):
        super(SkinningTools, self).__init__(parent)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        self.setWindowFlags(Qt.Tool)
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

    # ------------------------- defaults -------------------------------
    def __defaults(self):
        self.__graphSize = 60
        self.settings = QSettings("uiSkinSave", "SkinningTools")
        self.__liveIMG = QPixmap(":/UVPivotLeft.png")
        self.__notLiveIMG = QPixmap(":/enabled.png")
        self.BezierGraph = BezierGraph()

    # ------------------------- contextMenu -------------------------------

    def btnContextMenu(self, point):
        popMenu = QMenu(self)
        action = QAction(self.__lang['delete'], self)
        popMenu.addAction(action)
        action.triggered.connect(partial(self.deleteButton, self.sender()))
        popMenu.exec_(self.sender().mapToGlobal(point))

    def filterContextMenu(self, point):
        popMenu = QMenu(self)
        action = QAction(self.__lang['uncheck all'], self)
        popMenu.addAction(action)
        action.triggered.connect(self.unCheckFilters)
        popMenu.exec_(self.sender().mapToGlobal(point))

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
        h = nullHBoxLayout()

        filePath = self._updateGraph()

        self.graph = toolButton(filePath)
        self.graph.setFixedSize(QSize(self.__graphSize, self.__graphSize))
        self.graph.setIconSize(QSize(self.__graphSize, self.__graphSize))
        self.graph.clicked.connect(self._showGraph)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(self.graph)

        v.addLayout(h)
        v.addWidget(self.mayaToolsTab)
        tab.view.frame.setLayout(v)

        self.__addVertNBoneFunc()
        self.__addSimpleTools()

    def __addSimpleTools(self):
        tab = self.mayaToolsTab.addGraphicsTab("Simple Maya Tools")
        v = nullVBoxLayout()
        tab.view.frame.setLayout(v)
        buttons = mayaToolsWindow()
        for button in buttons:
            v.addWidget(button)
        v.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __addVertNBoneFunc(self):
        tab = self.mayaToolsTab.addGraphicsTab("Vertex & bone functions")

    def __skinSliderSetup(self):
        tab = self.tabs.addGraphicsTab("Skin Slider")
        self.inflEdit = SkinningToolsSliderList()
        v = nullVBoxLayout()
        h = nullHBoxLayout()
        rfr = toolButton(":/playbackLoopingContinuous_100.png")
        live = toolButton(self.__liveIMG)
        live.setCheckable(True)
        live.clicked.connect(self._updateLive)

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [rfr, live]:
            h.addWidget(btn)

        v.addLayout(h)
        tab.view.frame.setLayout(v)
        v.addWidget(self.inflEdit)

    def __componentEditSetup(self):
        self.tabs.addGraphicsTab("Component Editor")

    def __weightManagerSetup(self):
        self.tabs.addGraphicsTab("Weight Manager")

    # ------------------------- connections ---------------------------------

    def _showGraph(self):
        self.BezierGraph.show()

    def _updateLive(self):
        liveBtn = self.sender()
        if liveBtn.isChecked():
            liveBtn.setIcon(QIcon(self.__notLiveIMG))
        else:
            liveBtn.setIcon(QIcon(self.__liveIMG))

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

    def _updateGraph(self):
        filePath = os.path.join(tempfile.gettempdir(), 'screenshot.jpg')
        QPixmap.grabWidget(self.BezierGraph.view).save(filePath, 'jpg')
        return filePath

    def _updateGraphButton(self):
        filePath = self._updateGraph()
        self.graph.setIcon(QIcon(QPixmap(filePath)))
        self.graph.setIconSize(QSize(self.__graphSize, self.__graphSize))

    # -------------------- window geometry -------------------------------

    def saveUIState(self):
        self.settings.setValue("geometry", self.saveGeometry())

    def loadUIState(self):
        getGeo = self.settings.value("geometry")
        if getGeo == None:
            return
        self.restoreGeometry(getGeo)

    def hideEvent(self, event):
        self.saveUIState()


def showUI():
    def get_maya_window():
        for widget in QApplication.allWidgets():
            try:
                if widget.objectName() == "MayaWindow":
                    return widget
            except:
                pass
        return None

    window_name = 'SkinningTools: %s' % __VERSION__
    mainWindow = get_maya_window()

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
