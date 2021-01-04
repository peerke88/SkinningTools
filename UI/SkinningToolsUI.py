# -*- coding: utf-8 -*-
__VERSION__ = "5.0.20201221"

from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *

from SkinningTools.Maya import interface

_DIR = os.path.dirname(__file__)
_DEBUG = getDebugState()

from SkinningTools.UI.advancedToolTip import AdvancedToolTip
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl
from SkinningTools.UI.fallofCurveUI import BezierGraph
from SkinningTools.UI.messageProgressBar import MessageProgressBar
from SkinningTools.UI.tearOff.editableTab import EditableTabWidget
from SkinningTools.UI.tearOff.tearOffDialog import *
from SkinningTools.UI.weightEditor import weightEditor

if _DEBUG:
    from SkinningTools.UI.tabs.skinBrushes import SkinBrushes
from SkinningTools.UI.tabs.mayaToolsHeader import MayaToolsHeader
from SkinningTools.UI.tabs.skinSliderSetup import SkinSliderSetup
from SkinningTools.UI.tabs.vertAndBoneFunction import VertAndBoneFunction
from SkinningTools.UI.tabs.vertexWeightMatcher import *
from SkinningTools.UI.tabs.weightsUI import WeightsUI

import webbrowser

class SkinningToolsUI(interface.DockWidget):
    """ main skinningtools UI class
    """

    toolName = 'SkinningTools: %s' % __VERSION__

    def __init__(self, newPlacement=False, parent=None):
        """ the constructor
        generates the layout of the ui and attaches multiple widgest to several tabs
        
        :param newPlacement: if `True` will place the ui according to the parents best guess, if `False` will take the information from the settings
        :type newPlacement: bool
        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(SkinningToolsUI, self).__init__(parent)
        # placeholder image
        self.setWindowIcon(QIcon(":/commandButton.png"))

        __sel = interface.getSelection()
        interface.doSelect('')

        self.setWindowTitle(self.__class__.toolName)
        
        self.__uiElements()
        self.__defaults()

        mainLayout = nullVBoxLayout(None, 3)
        self.setLayout(mainLayout)

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
        interface.dccInstallEventFilter()

        self._callbackFilter()
        interface.doSelect(__sel)

    def __uiElements(self):
        """ several general UI elements that should be visible most of the times
        also loads the settings necessary for storing and retrieving information
        """
        self.settings = QSettings(os.path.join(_DIR,'settings.ini'), QSettings.IniFormat)
        self.progressBar = MessageProgressBar(self)
        self.BezierGraph = BezierGraph()

    def __defaults(self):
        """ some default local variables for the current UI    
        """
        interface.showToolTip(True)
        self._timer = QTimer()
        self._timer.timeout.connect(self._displayToolTip)
        self.currentWidgetAtMouse = None
        self.toolTipWindow = None
        self.__timing = 700

    def __connections(self):
        """ connection to a callback filter to make sure that the seperate marking menu is created
        """
        self.tabs.currentChanged.connect(self._callbackFilter)

    # ------------------------- ui Setups ---------------------------------
    def __menuSetup(self):
        """ the menubar
        this will hold information on language, simple copy/paste(hold fetch) functionality and all the documentation/settings
        """
        self.menuBar = QMenuBar(self)
        self.menuBar.setLayoutDirection(Qt.RightToLeft)
        self.extraMenu = QMenu('Extra', self)
        helpAction = QMenu('', self)
        helpAction.setIcon(QIcon(":/QR_help.png"))

        self.holdAction = QAction("hold Model", self)
        self.fetchAction = QAction("fetch Model", self)
        self.objSkeletonAction = QAction("skeleton -> obj", self)
        apiAction = QAction("API documentation", self)
        docAction = QAction("UI documentation", self)
        self.tooltipAction = QAction("Enhanced ToolTip", self)
        self.tooltipAction.setCheckable(True)

        for act in [self.holdAction, self.fetchAction, self.objSkeletonAction]:
            self.extraMenu.addAction(act)
        for act in [apiAction, docAction, self.tooltipAction]:
            helpAction.addAction(act)

        self.changeLN = QMenu("[EN]", self)
        
        for language in ["[EN]", "[日本]"]:
            ac = QAction(language, self)
            self.changeLN.addAction(ac)
            ac.triggered.connect(self._changeLanguage)

        self.holdAction.triggered.connect(interface.hold)
        self.fetchAction.triggered.connect(interface.fetch)
        self.objSkeletonAction.triggered.connect(interface.createPolySkeleton)
        apiAction.triggered.connect(self._openApiHelp)

        #@todo: add the functionality later
        self.tooltipAction.setEnabled(False)

        self.menuBar.addMenu(helpAction)
        self.menuBar.addMenu(self.extraMenu)
        self.menuBar.addMenu(self.changeLN)
        self.layout().setMenuBar(self.menuBar)

    def _openApiHelp(self):
        """ open the web page with the help documentation and api information
        """
        webUrl = r"https://www.perryleijten.com/skinningtool/html/"
        webbrowser.open(webUrl)

    def _changeLanguage(self):
        """ change the ui language
        """
        self.changeLN.setTitle(self.sender().text())

    def __tabsSetup(self):
        """ main tab widget which will hold all other widget information
        """
        self.tabs = EditableTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.tearOff.connect(self.tearOff)
        self.tabs.tabBar().setWest()

    def __mayaToolsSetup(self):
        """ the main tab, this will hold all the dcc tool information
        all vertex and bone manipulating contexts will be placed here  

        :note: this needs to change when we move over to different dcc
        """
        tab = self.tabs.addGraphicsTab("Maya Tools", useIcon = ":/menuIconSkinning.png")

        self.mayaToolsTab = EditableTabWidget()
        self.mayaToolsTab.tearOff.connect(self.tearOff)

        vLayout = nullVBoxLayout()
        widget = MayaToolsHeader(self.BezierGraph, self.progressBar, self)
        vLayout.addWidget(widget)
        vLayout.addWidget(self.mayaToolsTab)
        tab.view.frame.setLayout(vLayout)

        self.__addVertNBoneFunc()
        #@todo: add a tab here that allows you to grab tools you use frequently (store this in qsettings)
        if _DEBUG:
            self.__addBrushTools()
        self.__addCopyRangeFunc()
        self.__addSimpleTools()

    def __addSimpleTools(self):
        """ this part of the ui will gather the information from dcc directly, 
        most of the settings attached to these buttons and windows are set to a default that would work wel in most cases
        """
        tab = self.mayaToolsTab.addGraphicsTab("Simple Maya Tools", useIcon = ":/SP_FileDialogListView.png")
        vLayout = nullVBoxLayout()
        tab.view.frame.setLayout(vLayout)
        buttons = interface.dccToolButtons(self.progressBar)
        for btn in buttons:
            vLayout.addWidget(btn)
        vLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __addVertNBoneFunc(self):
        """ button layout gahtering lots of different tools that make editting weights 
        """
        tab = self.mayaToolsTab.addGraphicsTab("Vertex && bone functions", useIcon = ":/create.png")
        vLayout = nullVBoxLayout()
        self.vnbfWidget = VertAndBoneFunction(self.BezierGraph, self.progressBar, self)
        vLayout.addWidget(self.vnbfWidget)
        tab.view.frame.setLayout(vLayout)

    def __addBrushTools(self):
        """ simple brush tools that enable Rodolphes relax weight tools
        :note: only for debug as this has been converted into a single button
        """
        tab = self.mayaToolsTab.addGraphicsTab("Brushes", useIcon = ":/menuIconPaintEffects.png")
        vLayout = nullVBoxLayout()
        widget = SkinBrushes(parent=self)
        vLayout.addWidget(widget)
        tab.view.frame.setLayout(vLayout)

    def __addCopyRangeFunc(self):
        """ mutliple tools that require more inpute, mostly to remap certain elements in the scene
        """
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
        # this feature is to be added later; needs to be thuroughly tested!
        # _dict["Assign soft selection"] = [AssignWeightsWidget(self), ":/Grab.png"]
        
        for key, value in _dict.iteritems():
            _tab = self.copyToolsTab.addGraphicsTab(key, useIcon = value[1])
            _vLay = nullVBoxLayout()
            _tab.view.frame.setLayout(_vLay)
            _vLay.addWidget(value[0])

    def __skinSliderSetup(self):
        """ skinslider tab, the functionality of tweaking the weights on the selected components by changing the corresponding bone values
        """
        tab = self.tabs.addGraphicsTab("Skin Slider", useIcon = ":/nodeGrapherModeConnectedLarge.png")
        vLayout = nullVBoxLayout()

        self.skinSlider = SkinSliderSetup(self)
        self.skinSlider.isInView = False
        self.skinSlider.createCallback()

        vLayout.addWidget(self.skinSlider)
        tab.view.frame.setLayout(vLayout)

    def __componentEditSetup(self):
        """ revamped component editor with a lot of extra functionalities, based on the Maya component editor but build from scratch to make it more powerfull
        """
        interface.forceLoadPlugin("SkinEditPlugin")
        tab = self.tabs.addGraphicsTab("Component Editor", useIcon = ":/list.svg")
        vLayout = nullVBoxLayout()
        
        self.editor = weightEditor.WeightEditorWindow(self)
        self.editor.isInView = False
        vLayout.addWidget(self.editor)
        tab.view.frame.setLayout(vLayout)

    def __weightManagerSetup(self):
        """ weight manager function, save and load skinweights to seperate files
        """
        interface.forceLoadPlugin("SkinEditPlugin")
        tab = self.tabs.addGraphicsTab("Weight Manager", useIcon = ":/menuIconEdit.png")
        vLayout = nullVBoxLayout()
        self.__weightUI = WeightsUI(self.settings, self.progressBar, self)
        vLayout.addWidget(self.__weightUI)
        tab.view.frame.setLayout(vLayout)

    # ------------------------- utilities ---------------------------------

    def _callbackFilter(self, *args):
        """ callbacks for both the skinsliders and the component editor to update after the mouse has left the window and has returned
        this to make sure that the user is always working with the latest setup
        """
        if self.skinSlider is not None:
            self.skinSlider.isInView = not self.skinSlider.visibleRegion().isEmpty() 
            if self.skinSlider.isInView :
                self.skinSlider._update()
        
        if self.editor is not None:
            self.editor.isInView = not self.editor.visibleRegion().isEmpty()
            if self.editor.isInView :
                self.editor.getSkinWeights()

    def _tabName(self, index=-1, mainTool=None):
        """get the name of the tab at given index

        :param index: the index at which to get the tab name
        :type index: int 
        :param mainTool: the parent object to request tabnames from
        :type maintool: Qwidget
        :return: name of the current tab
        :rtype: string
        """
        if mainTool is None:
            raise NotImplementedError()
        if index < 0:
            index = mainTool.currentIndex()
        return mainTool.tabText(index)

    def tearOff(self, index, pos=QPoint()):
        """get the name of the tab at given index

        :param index: the index of the tab that needs to be torn off
        :type index: int 
        :param pos: the position at which to place the torn off tabe
        :type pos: Qwidget
        """
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
        """ the event at which to reload both the skinsliders and the component editor

        :param event: the event that is triggerd
        :type event: QEvent
        :return: the output of the inherited functions
        :rtype: superclass
        """
        self._callbackFilter()
        return super(SkinningToolsUI, self).enterEvent(event)

    def recurseMouseTracking(self, parent, flag):
        """ convenience function to add mousetracking to all elements that are part of the current tool this way we can attach tooltips to everything

        :param parent: the parent object that can hold moustracking events and from which to search all possible children in the hierarchy
        :type parent: Qwidget
        :param flag: if `True` turns mouse tracking on, if `False` turns mousetracking off
        :type flag: bool
        """
        if hasattr(parent, "mouseMoveEvent"):
            parent.setMouseTracking(flag)
            parent.__mouseMoveEvent = parent.mouseMoveEvent
            parent.mouseMoveEvent = partial(self.childMouseMoveEvent, parent)

        for child in parent.children():
            if isinstance(child, SliderControl):
                continue
            self.recurseMouseTracking(child, flag)

    def _mouseTracking(self, event):
        """ the event at which to display the tooltip windows

        :param event: the event that is triggerd
        :type event: QEvent
        """
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
        """ the overloaded function to track mouse movements on children

        :param child: the child object at which to set mouse tracking
        :type child: QWidget
        :param event: the event that is triggerd
        :type event: QEvent
        """
        self._mouseTracking(event)
        return child.__mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        """ the move event

        :param event: the event that is triggerd
        :type event: QEvent
        """
        self._mouseTracking(event)
        super(SkinningToolsUI, self).mouseMoveEvent(event)

    def _displayToolTip(self):
        """ the tooltip function, allows the tooltip to spawn a seperate window above the current object
        the tooltip wil spawn based on a timer and will remove itself when the cursor moves away
        :note: tooltips are currently disabled as there are no images to show or text to display
        """
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
        """ save the current state of the ui in a seperate ini file, this should also hold information later from a seperate settings window

        :todo: instead of only geometry also store torn of tabs for each posssible object
        :todo: save the geometries of torn of tabs as well
        :todo: store the settings used in the vertex and bone functions tabs
        """
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("tools", self.mayaToolsTab.currentIndex())
        self.settings.setValue("tabs", self.tabs.currentIndex())
        self.settings.setValue("vnbf", self.vnbfWidget.getCheckValues())
        self.settings.setValue("favs", self.vnbfWidget.getFavSettings())
        self.settings.setValue("useFav", self.vnbfWidget.setFavcheck.isChecked())
        self.settings.setValue("copyTls", self.copyToolsTab.currentIndex())

    def loadUIState(self):
        """ load the previous set information from the ini file where possible, if the ini file is not there it will start with default settings
        """
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
        self.vnbfWidget.setFavSettings(self.settings.value("favs",[]))
        self.vnbfWidget.setFavcheck.setChecked(bool(self.settings.value("useFav",False)))

    def hideEvent(self, event):
        """ the hide event is something that is triggered at the same time as close,
        sometimes the close event is not handled correctly by maya so we add the save state in here to make sure its always triggered
        :note: its only storing info so it doesnt break anything
        """
        QApplication.restoreOverrideCursor()
        self.saveUIState()
        super(SkinningToolsUI, self).hideEvent(event)

    def closeEvent(self, event):
        """ the close event, 
        we save the state of the ui but we also force delete a lot of the skinningtool elements,
        normally python would do garbage collection for you, but to be sure that nothing is stored in memory that does not get deleted we 
        force the deletion here as well. somehow this avoids crashes in maya!
        """
        QApplication.restoreOverrideCursor()
        self.saveUIState()
        try:
            self.skinSlider.clearCallback()
            self.editor.setClose()
            interface._cleanEventFilter()
            self.skinSlider.deleteLater()
            del self.skinSlider
            self.editor.deleteLater()
            del self.editor
        except:
            self.deleteLater()


def showUI(newPlacement=False):
    """ convenience function to show the current user interface in maya,

    :param newPlacement: if `True` will force the tool to not read the ini file, if `False` will open the tool as intended
    :type newPlacement: bool
    """
    mainWindow = interface.get_maya_window()
    dock = SkinningToolsUI(newPlacement, mainWindow)
    dock.run()