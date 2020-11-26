# -*- coding: utf-8 -*-
__VERSION__ = "5.0.20201126"
_DEBUG = False

def getDebugState():
    return _DEBUG

import tempfile, os
from functools import partial

from SkinningTools.py23 import *
# @todo: add multiple interfaces later for different packages 
# when using maya:
from SkinningTools.Maya import api, interface

from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.tearOff.editableTab import EditableTabWidget
from SkinningTools.UI.tearOff.tearOffDialog import *
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl
from SkinningTools.UI.fallofCurveUI import BezierGraph
from SkinningTools.UI.messageProgressBar import MessageProgressBar
from SkinningTools.UI.advancedToolTip import AdvancedToolTip
from SkinningTools.UI.weightEditor import weightEditor

from SkinningTools.UI.tabs.vertAndBoneFunction import VertAndBoneFunction
if _DEBUG:
    from SkinningTools.UI.tabs.skinBrushes import SkinBrushes
from SkinningTools.UI.tabs.mayaToolsHeader import MayaToolsHeader
from SkinningTools.UI.tabs.vertexWeightMatcher import *
from SkinningTools.UI.tabs.skinSliderSetup import SkinSliderSetup
from SkinningTools.UI.tabs.weightsUI import WeightsUI

_DIR = os.path.dirname(__file__)

class SkinningToolsUI(QMainWindow):
    def __init__(self, newPlacement=False, parent=None):
        super(SkinningToolsUI, self).__init__(parent)
        # placeholder image
        self.setWindowIcon(QIcon(":/commandButton.png"))

        mainWidget = QWidget()
        self.__editor = None

        __sel = interface.getSelection()
        interface.doSelect('')

        self.setCentralWidget(mainWidget)
        
        self.__uiElements()
        self.__defaults()

        mainLayout = nullVBoxLayout(None, 3)
        mainWidget.setLayout(mainLayout)

        self.__menuSetup()
        self.__tabsSetup()

        self.__mayaToolsSetup()
        self.__skinSliderSetup()
        self.__componentEditSetup()
        self.__weightManagerSetup()

        self.__connections()
        mainLayout.addWidget(self.tabs)
        mainLayout.addWidget(self.progressBar)

        if not newPlacement:
            self.loadUIState()

        self.recurseMouseTracking(self, True)
        api.dccInstallEventFilter()

        self._callbackFilter()
        interface.doSelect(__sel)

    def __uiElements(self):
        self.settings = QSettings(os.path.join(_DIR,'settings.ini'), QSettings.IniFormat)
        self.progressBar = MessageProgressBar(self)
        self.BezierGraph = BezierGraph()

    def __defaults(self):
        interface.showToolTip(True)
        self._timer = QTimer()
        self._timer.timeout.connect(self._displayToolTip)
        self.currentWidgetAtMouse = None
        self.toolTipWindow = None
        self.__timing = 700

    def __connections(self):
        self.tabs.currentChanged.connect(self._callbackFilter)

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
        
        #@todo: add the functionality later
        helpAction.setEnabled(False)
        self.changeLN.setEnabled(False)

        self.menuBar().addMenu(helpAction)
        self.menuBar().addMenu(self.extraMenu)
        self.menuBar().addAction(self.changeLN)

    def __tabsSetup(self):
        self.tabs = EditableTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.tearOff.connect(self.tearOff)
        self.tabs.tabBar().setWest()


    def __mayaToolsSetup(self):
        tab = self.tabs.addGraphicsTab("Maya Tools", useIcon = ":/menuIconSkinning.png")

        self.mayaToolsTab = EditableTabWidget()
        self.mayaToolsTab.tearOff.connect(self.tearOff)

        vLayout = nullVBoxLayout()
        widget = MayaToolsHeader(self.BezierGraph, self.progressBar, self)
        vLayout.addWidget(widget)
        vLayout.addWidget(self.mayaToolsTab)
        tab.view.frame.setLayout(vLayout)

        self.__addVertNBoneFunc()
        if _DEBUG:
            self.__addBrushTools()
        self.__addCopyRangeFunc()
        self.__addSimpleTools()

    def __addSimpleTools(self):
        tab = self.mayaToolsTab.addGraphicsTab("Simple Maya Tools", useIcon = ":/SP_FileDialogListView.png")
        vLayout = nullVBoxLayout()
        tab.view.frame.setLayout(vLayout)
        buttons = interface.dccToolButtons(self.progressBar)
        for btn in buttons:
            vLayout.addWidget(btn)
        vLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __addVertNBoneFunc(self):
        tab = self.mayaToolsTab.addGraphicsTab("Vertex && bone functions", useIcon = ":/create.png")
        vLayout = nullVBoxLayout()
        self.vnbfWidget = VertAndBoneFunction(self.BezierGraph, self.progressBar, self)
        vLayout.addWidget(self.vnbfWidget)
        tab.view.frame.setLayout(vLayout)

    def __addBrushTools(self):
        tab = self.mayaToolsTab.addGraphicsTab("Brushes", useIcon = ":/menuIconPaintEffects.png")
        vLayout = nullVBoxLayout()
        widget = SkinBrushes(parent=self)
        vLayout.addWidget(widget)
        tab.view.frame.setLayout(vLayout)

    def __addCopyRangeFunc(self):
        tab = self.mayaToolsTab.addGraphicsTab("copy functions", useIcon = ":/lassoSelect.png")
        vLayout = nullVBoxLayout()
        tab.view.frame.setLayout(vLayout)

        self.copyToolsTab = EditableTabWidget()
        self.copyToolsTab.tearOff.connect(self.tearOff)

        vLayout.addWidget(self.copyToolsTab)
        _dict = OrderedDict()
        _dict["Copy closest weigth"] = [ClosestVertexWeightWidget(self), ":/arcLengthDimension.svg"]
        _dict["Transfer weigths"] = [TransferWeightsWidget(self), ":/alignSurface.svg"]
        _dict["Transfer Uv's"] = [TransferUvsWidget(self), ":/UVEditorBakeTexture.png"]
        _dict["Assign soft selection"] = [AssignWeightsWidget(self), ":/Grab.png"]
        
        for key, value in _dict.iteritems():
            _tab = self.copyToolsTab.addGraphicsTab(key, useIcon = value[1])
            _vLay = nullVBoxLayout()
            _tab.view.frame.setLayout(_vLay)
            _vLay.addWidget(value[0])

    def __skinSliderSetup(self):
        tab = self.tabs.addGraphicsTab("Skin Slider", useIcon = ":/nodeGrapherModeConnectedLarge.png")
        vLayout = nullVBoxLayout()
        self.__skinSlider = SkinSliderSetup(self)
        self.__skinSlider.isInView = False
        self.__skinSlider.createCallback()

        vLayout.addWidget(self.__skinSlider)
        tab.view.frame.setLayout(vLayout)

    def __componentEditSetup(self):
        interface.forceLoadPlugin("SkinEditPlugin")
        tab = self.tabs.addGraphicsTab("Component Editor", useIcon = ":/list.svg")
        vLayout = nullVBoxLayout()
        self.__editor = weightEditor.WeightEditorWindow(self)
        self.__editor.isInView = False
        vLayout.addWidget(self.__editor)
        tab.view.frame.setLayout(vLayout)

    def __weightManagerSetup(self):
        interface.forceLoadPlugin("SkinEditPlugin")
        tab = self.tabs.addGraphicsTab("Weight Manager", useIcon = ":/menuIconEdit.png")
        vLayout = nullVBoxLayout()
        self.__weightUI = WeightsUI(self.settings, self.progressBar, self)
        vLayout.addWidget(self.__weightUI)
        tab.view.frame.setLayout(vLayout)

    # ------------------------- utilities ---------------------------------

    def _callbackFilter(self, *args):
        self.__skinSlider.isInView = not self.__skinSlider.visibleRegion().isEmpty() 
        self.__editor.isInView = not self.__editor.visibleRegion().isEmpty()
        
        if self.__skinSlider.isInView :
            self.__skinSlider._update()
        if self.__editor.isInView :
            self.__editor.getSkinWeights()

    def _tabName(self, index=-1, mainTool=None):

        if mainTool is None:
            raise NotImplementedError()
        if index < 0:
            index = mainTool.currentIndex()
        return mainTool.tabText(index)

    def tearOff(self, index, pos=QPoint()):
        tabs = self.sender()
        view = tabs.viewAtIndex(index)
        dialog = TearOffDialog(self._tabName(index, tabs), self)
        if view.windowDispIcon is not None:
            dialog.setWindowIcon(QIcon(view.windowDispIcon))
        dialog.setOriginalState(index, tabs)
        dialog.addwidget(view)
        if pos.y() > -1:
            dialog.move(pos)

        dialog.show()
        tabs.removeTab(index)

    # -------------------- tool tips -------------------------------------

    def enterEvent(self, event):
        self._callbackFilter()
        return super(SkinningToolsUI, self).enterEvent(event)

    def recurseMouseTracking(self, parent, flag):
        if hasattr(parent, "mouseMoveEvent"):
            parent.setMouseTracking(flag)
            parent.__mouseMoveEvent = parent.mouseMoveEvent
            parent.mouseMoveEvent = partial(self.childMouseMoveEvent, parent)

        for child in parent.children():
            if isinstance(child, SliderControl):
                continue
            self.recurseMouseTracking(child, flag)

    def _mouseTracking(self, event):
        if QT_VERSION == "pyside2":
            point = QPoint(event.screenPos().x(), event.screenPos().y())
        else:
            point = QPoint(event.globalPos().x(), event.globalPos().y())
        curWidget = widgetsAt(point)

        def _removeTT():
            if self.toolTipWindow is not None:
                self.toolTipWindow.deleteLater()
            self.toolTipWindow = None
            self._timer.stop()

        if curWidget == None and self.toolTipWindow != None:
            _removeTT()
        if self.currentWidgetAtMouse != curWidget:
            if self.toolTipWindow != None:
                _removeTT()

            if not isinstance(curWidget, QPushButton):  # <- add multiple checks if more implemented then just buttons
                _removeTT()
                self.currentWidgetAtMouse = None
                return

            self.currentWidgetAtMouse = curWidget
            self._timer.start(self.__timing)

    def childMouseMoveEvent(self, child, event):
        self._mouseTracking(event)
        return child.__mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        self._mouseTracking(event)
        super(SkinningToolsUI, self).mouseMoveEvent(event)

    def _displayToolTip(self):
        self._timer.stop()
        if (self.currentWidgetAtMouse is None) or (self.tooltipAction.isChecked() == False):
            return
        tip = self.currentWidgetAtMouse.whatsThis()

        size = 250
        if QDesktopWidget().screenGeometry().height() > 1080:
            size *= 1.5
        rect = QRect(QCursor.pos().x() + 20, QCursor.pos().y() - (40 + size), size, size)
        if (self.window().pos().y() + (self.height() / 2)) > QCursor.pos().y():
            rect = QRect(QCursor.pos().x() + 20, QCursor.pos().y() + 20, size, size)

        self.toolTipWindow = AdvancedToolTip(rect)
        # @TODO: change this to only display text if gif does not exist
        # if not self.toolTipWindow.toolTipExists(tip):
        #     return 
        self.toolTipWindow.setTip(str(tip))
        self.toolTipWindow.setGifImage(tip)
        self.toolTipWindow.show()

    # -------------------- window states -------------------------------

    def saveUIState(self):
        # TODO: instead of only geometry also store torn of tabs for each posssible object
        # save the geometries of torn of tabs as well
        # store the settings used in the vertex and bone functions tabs
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("tools", self.mayaToolsTab.currentIndex())
        self.settings.setValue("tabs", self.tabs.currentIndex())
        self.settings.setValue("vnbf", self.vnbfWidget.getCheckValues())
        self.settings.setValue("copyTls", self.copyToolsTab.currentIndex())

    def loadUIState(self):
        getGeo = self.settings.value("geometry", None)
        if getGeo is None:
            return

        self.restoreGeometry(getGeo)
        tools = { "tools": self.mayaToolsTab,
                  "tabs": self.tabs,
                  "copyTls": self.copyToolsTab,
                }
        for key, comp in tools.iteritems():
            index = self.settings.value(key, 0)
            if index is None:
                index = 0
            elif index > comp.count()-1:
                index = -1
            comp.setCurrentIndex(index)
        self.vnbfWidget.setCheckValues(self.settings.value("vnbf",None))

    def hideEvent(self, event):
        self.saveUIState()
        try:
            self.__skinSlider.clearCallback()
            self.__editor.setClose()
            api._cleanEventFilter()
            self.__skinSlider.deleteLater()
            del self.__skinSlider
            self.__editor.deleteLater()
            del self.__editor
        except:
            self.deleteLater()


def getSkinningToolsWindowName():
    return 'SkinningTools: %s' % __VERSION__


def closeSkinningToolsMainWindow(windowName=getSkinningToolsWindowName(), mainWindow = api.get_maya_window()):
    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == windowName:
                child.close()
                child.deleteLater()


def showUI(newPlacement=False):
    windowName = getSkinningToolsWindowName()
    mainWindow = api.get_maya_window()
    closeSkinningToolsMainWindow(windowName, mainWindow)
    window = SkinningToolsUI(newPlacement, mainWindow)
    window.setObjectName(windowName)
    window.setWindowTitle(windowName)
    window.show()

    return window

