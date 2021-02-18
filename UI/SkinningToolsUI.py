# -*- coding: utf-8 -*-
__VERSION__ = "5.0.20210218"

from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *

from SkinningTools.Maya import interface, api

_DIR = os.path.dirname(__file__)
_DEBUG = getDebugState()

from SkinningTools.UI.advancedToolTip import AdvancedToolTip
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl
from SkinningTools.UI.fallofCurveUI import BezierGraph
from SkinningTools.UI.messageProgressBar import MessageProgressBar
from SkinningTools.UI.tearOff.editableTab import TabWidget
from SkinningTools.UI.tearOff.tearOffDialog import *
from SkinningTools.UI.weightEditor import weightEditor

if _DEBUG:
    from SkinningTools.UI.tabs.skinBrushes import SkinBrushes
from SkinningTools.UI.tabs.mayaToolsHeader import MayaToolsHeader
from SkinningTools.UI.tabs.skinSliderSetup import SkinSliderSetup
from SkinningTools.UI.tabs.vertAndBoneFunction import VertAndBoneFunction
from SkinningTools.UI.tabs.vertexWeightMatcher import *
from SkinningTools.UI.tabs.initialWeightUI import InitWeightUI
from SkinningTools.UI.tabs.softSelectUI import SoftSelectionToWeightsWidget
from SkinningTools.UI.tabs.weightsUI import WeightsUI

import webbrowser, os, warnings, zipfile

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
        self.setWindowIcon(QIcon(":/commandButton.png"))
        
        __sel = interface.getSelection()
        interface.doSelect('')

        self.setWindowTitle(self.__class__.toolName)
        
        self.__defaults()
        self.__uiElements()

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

        if newPlacement:
            self.settings.clear()
            
        self.loadUIState()
        self.recurseMouseTracking(self, True)
        
        self._callbackFilter()
        self._tooltips = loadLanguageFile(self.changeLN.title(), "tooltips")

        interface.doSelect(__sel)

    def __uiElements(self):
        """ several general UI elements that should be visible most of the times
        also loads the settings necessary for storing and retrieving information
        """
        _ini = os.path.join(_DIR,'settings.ini')
        self.settings = QSettings(_ini, QSettings.IniFormat)
        self.progressBar = MessageProgressBar(self)
        self.BezierGraph = BezierGraph(settings = self.settings, parent = self)
        self.languageWidgets.append(self.BezierGraph)

    def __defaults(self):
        """ some default local variables for the current UI    
        """
        self.textInfo = {}
        self.languageWidgets = []
        interface.showToolTip(True)
        self._timer = QTimer()
        self._timer.timeout.connect(self._displayToolTip)
        self.currentWidgetAtMouse = None
        self.toolTipWindow = None
        self.__timing = 700
        self.__dialogGeo = {}
        
    def __connections(self):
        """ connection to a callback filter to make sure that the seperate marking menu is created
        """
        self.tabs.currentChanged.connect(self._callbackFilter)

    # ------------------------- ui Setups ---------------------------------
    def __menuSetup(self):
        """ the menubar
        this will hold information on language, simple copy/paste(hold fetch) functionality and all the documentation/settings
        documentation will open specifically for the current open tab, next to that we also have a markingmenu button as this is available all the time
        """
        self.menuBar = QMenuBar(self)
        self.menuBar.setLayoutDirection(Qt.RightToLeft)
        self.textInfo["extraMenu"] = QMenu('Extra', self)
        helpAction = QMenu('', self)
        helpAction.setIcon(QIcon(":/QR_help.png"))

        self.textInfo["holdAction"] = QAction("hold Model", self)
        self.textInfo["fetchAction"] = QAction("fetch Model", self)
        self.textInfo["objSkeletonAction"] = QAction("skeleton -> obj", self)
        self.textInfo["apiAction"] = QAction("API documentation", self)
        self.textInfo["docAction"] = QAction("UI documentation", self)
        self.textInfo["mmAction"] = QAction("Marking Menu doc", self)
        self.textInfo["tooltipAction"] = QAction("Enhanced ToolTip", self)
        self.textInfo["tooltipAction"].setCheckable(True)

        for act in [self.textInfo["holdAction"], self.textInfo["fetchAction"], self.textInfo["objSkeletonAction"]]:
            self.textInfo["extraMenu"].addAction(act)
        for act in [self.textInfo["apiAction"], self.textInfo["docAction"],self.textInfo["mmAction"], self.textInfo["tooltipAction"]]:
            helpAction.addAction(act)

        self.changeLN = QMenu("en", self)
        languageFiles = os.listdir(os.path.join(_DIR, "languages"))
        for language in languageFiles:
            ac = QAction(language, self)
            self.changeLN.addAction(ac)
            ac.triggered.connect(self._changeLanguage)

        self.textInfo["holdAction"].triggered.connect(interface.hold)
        self.textInfo["fetchAction"].triggered.connect(interface.fetch)
        self.textInfo["objSkeletonAction"].triggered.connect(interface.createPolySkeleton)
        self.textInfo["apiAction"].triggered.connect(self._openApiHelp)
        self.textInfo["docAction"].triggered.connect(self._openDocHelp)
        self.textInfo["mmAction"].triggered.connect(partial(self._openDocHelp, True))
        self.textInfo["tooltipAction"].triggered.connect(self._tooltipsCheck)

        self.menuBar.addMenu(helpAction)
        self.menuBar.addMenu(self.textInfo["extraMenu"])
        self.menuBar.addMenu(self.changeLN)
        self.layout().setMenuBar(self.menuBar)
    
    def _tooltipsCheck(self):
        if not self.textInfo["tooltipAction"].isChecked():
            return 
        _toolPath = os.path.join(interface.getInterfaceDir(), "tooltips")
        
        if not os.path.exists(_toolPath):
            os.makedirs(_toolPath)

        if os.listdir(_toolPath) != []:
            return
        
        warnings.warn("no information found")
        dlDlg = QuickDialog("download tooltips")
        dlDlg.layout().insertWidget(0, QLabel("do you want to download them now?"))
        dlDlg.layout().insertWidget(0, QLabel("no tooltips found, possibly not downloaded yet."))
        dlDlg.exec_()
        if dlDlg.result() == 0:
            self.textInfo["tooltipAction"].setChecked(False)
            return

        files = {
                "toolTips.zip" : "https://firebasestorage.googleapis.com/v0/b/skinningtoolstooltips.appspot.com/o/tooltips.zip?alt=media&token=07f5c1b1-f8c2-4f18-83ce-2ea65eee4187"
        }
        try:
            gDriveDownload(files, _toolPath, self.progressBar) 
            with zipfile.ZipFile(os.path.join(_toolPath, "toolTips.zip")) as zip_ref:
                zip_ref.extractall(_toolPath)
        except:
            warnings.warn("could not downoad tooltips at this time, server is overloaded, please try again tomorrow!")
            
    def _openApiHelp(self):
        """ open the web page with the help documentation and api information
        """
        webUrl = r"https://www.perryleijten.com/skinningtool/html/"
        webbrowser.open(webUrl)

    def _openDocHelp(self, isMarkingMenu = False):
        """ open the corresponding pdf page with the help documentation tool information
        """

        _copy = {0: "ClosestVertexWeightWidget",
                 1: "AssignWeightsWidget",
                 2: "TransferUvsWidget"}
        _tools = {0: "VertAndBoneFunction",
                  1: _copy,
                  2: "MayaTools"}
        _base = {0: _tools,
                 1: "SkinSliderSetup",
                 2: "WeightEditorWindow",
                 3: "weightUI"}
        _other = "BezierGraph"

        _helpInfo = _base[self.tabs.currentIndex()]
        if type(_helpInfo) == dict:
            _helpInfo = _helpInfo[self.mayaToolsTab.currentIndex()]
        if type(_helpInfo) == dict:
            _helpInfo = _helpInfo[self.copyToolsTab.currentIndex()]
        if self.BezierGraph.isVisible():
            _helpInfo = _other
        if isMarkingMenu:
            _helpInfo = "MarkingMenu"

        _helpFile = os.path.join(interface.getInterfaceDir(), "docs/%s/%s.pdf"%(self.changeLN.title(), _helpInfo))
        
        try:
            os.startfile( r'file:%s'%_helpFile )  
        except:
            try:
                warnings.warn("could not open Pdf file, trying through webrowser!")
                webbrowser.open_new( r'file:%s'%_helpFile )  
            except Exception as e:
                warnings.warn(e)

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.iteritems():
            if hasattr(self.textInfo[key], "tearOffTabName"):
                self.textInfo[key].tabParent.setTabText(self.textInfo[key].cIndex, value)
            elif isinstance(self.textInfo[key], QMenu):
                self.textInfo[key].setTitle(value)
            else:
                self.textInfo[key].setText(value)
        
    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.iteritems():
            if hasattr(self.textInfo[key], "tearOffTabName"):
                _ret[key] = self.textInfo[key].tearOffTabName
            elif isinstance(self.textInfo[key], QMenu):
                _ret[key] = value.title()
            else:
                _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName.split(":")[0])
        _trs = translator.showUI(_dict, widgetName = self.toolName.split(":")[0])

    def _changeLanguage(self, lang = None):
        """ change the ui language

        :param lang: the shortname of the language to change the ui to
        :type lang: string
        """
        if lang is None:
            lang = self.sender().text()
        
        self.changeLN.setTitle(lang)

        for widget in self.languageWidgets:
            _dict = loadLanguageFile(lang, widget.toolName)
            widget.translate(_dict)

        _dict =loadLanguageFile(lang, self.toolName.split(":")[0])
        self.translate(_dict)
        self._tooltips = loadLanguageFile(lang, "tooltips")

    # --------------------------------------------------------------------------------

    def __tabsSetup(self):
        """ main tab widget which will hold all other widget information
        """
        self.tabs = TabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.tearOff.connect(self.tearOff)
        self.tabs.tabBar().setWest()

    def __mayaToolsSetup(self):
        """ the main tab, this will hold all the dcc tool information
        all vertex and bone manipulating contexts will be placed here  

        :note: this needs to change when we move over to different dcc
        """
        self.textInfo["mayaTab"] = self.tabs.addGraphicsTab("Maya Tools", useIcon = ":/menuIconSkinning.png")
        self.textInfo["mayaTab"].tabParent = self.tabs
        self.mayaToolsTab = TabWidget()
        self.mayaToolsTab.tearOff.connect(self.tearOff)

        vLayout = nullVBoxLayout()
        widget = MayaToolsHeader(self.BezierGraph, self.progressBar, self)
        vLayout.addWidget(widget)
        vLayout.addWidget(self.mayaToolsTab)
        self.textInfo["mayaTab"].view.frame.setLayout(vLayout)
        self.languageWidgets.append(widget)

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
        self.textInfo["simpleTab"] = self.mayaToolsTab.addGraphicsTab("Simple Maya Tools", useIcon = ":/SP_FileDialogListView.png")
        self.textInfo["simpleTab"].tabParent = self.mayaToolsTab
        vLayout = nullVBoxLayout()
        self.textInfo["simpleTab"].view.frame.setLayout(vLayout)
        buttons = interface.dccToolButtons(self.progressBar)
        for btn in buttons:
            self.textInfo["%s_BTN"%btn.text()] = btn
            vLayout.addWidget(btn)
        vLayout.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __addVertNBoneFunc(self):
        """ button layout gahtering lots of different tools that make editting weights 
        """
        self.textInfo["vnbTab"] = self.mayaToolsTab.addGraphicsTab("Vertex && bone functions", useIcon = ":/create.png")
        self.textInfo["vnbTab"].tabParent = self.mayaToolsTab
        vLayout = nullVBoxLayout()
        self.vnbfWidget = VertAndBoneFunction(self.BezierGraph, self.progressBar, self)
        self.languageWidgets.append(self.vnbfWidget)
        vLayout.addWidget(self.vnbfWidget)
        self.textInfo["vnbTab"].view.frame.setLayout(vLayout)

    def __addBrushTools(self):
        """ simple brush tools that enable Rodolphes relax weight tools
        :note: only for debug as this has been converted into a single button
        """
        self.textInfo["brushTab"] = self.mayaToolsTab.addGraphicsTab("Brushes", useIcon = ":/menuIconPaintEffects.png")
        self.textInfo["brushTab"].tabParent = self.mayaToolsTab
        vLayout = nullVBoxLayout()
        widget = SkinBrushes(parent=self)
        vLayout.addWidget(widget)
        self.textInfo["brushTab"].view.frame.setLayout(vLayout)

    def __addCopyRangeFunc(self):
        """ mutliple tools that require more inpute, mostly to remap certain elements in the scene
        """
        self.textInfo["copyTab"] = self.mayaToolsTab.addGraphicsTab("copy functions", useIcon = ":/lassoSelect.png")
        self.textInfo["copyTab"].tabParent = self.mayaToolsTab
        vLayout = nullVBoxLayout()
        self.textInfo["copyTab"].view.frame.setLayout(vLayout)

        self.copyToolsTab = TabWidget()
        self.copyToolsTab.tearOff.connect(self.tearOff)

        vLayout.addWidget(self.copyToolsTab)
        _dict = OrderedDict()
        _dict["Copy closest weigth"] = [ClosestVertexWeightWidget(self), ":/arcLengthDimension.svg"]
        _dict["Transfer weigths"] = [TransferWeightsWidget(self), ":/alignSurface.svg"]
        _dict["Transfer Uv's"] = [TransferUvsWidget(self), ":/UVEditorBakeTexture.png"]
        _dict["initial SkinBind"] = [InitWeightUI(self), ":/menuIconPaintEffects.png"]
        _dict["Assign Soft Select"] = [SoftSelectionToWeightsWidget(self), ":/Grab.png"]
        
        for index, (key, value) in enumerate(_dict.iteritems()):
            self.textInfo["copyTab_%s"%(index)] = self.copyToolsTab.addGraphicsTab(key, useIcon = value[1])
            self.textInfo["copyTab_%s"%(index)].tabParent = self.copyToolsTab
            _vLay = nullVBoxLayout()
            self.textInfo["copyTab_%s"%(index)].view.frame.setLayout(_vLay)
            value[0].addLoadingBar(self.progressBar)
            if hasattr(value[0], "translate"):
                self.languageWidgets.append(value[0])
            _vLay.addWidget(value[0])

    def __skinSliderSetup(self):
        """ skinslider tab, the functionality of tweaking the weights on the selected components by changing the corresponding bone values
        """
        self.textInfo["sliderTab"] = self.tabs.addGraphicsTab("Skin Slider", useIcon = ":/nodeGrapherModeConnectedLarge.png")
        self.textInfo["sliderTab"].tabParent = self.tabs
        vLayout = nullVBoxLayout()

        self.skinSlider = SkinSliderSetup(self)
        self.languageWidgets.append(self.skinSlider)
        self.skinSlider.isInView = False
        self.skinSlider.createCallback()

        vLayout.addWidget(self.skinSlider)
        self.textInfo["sliderTab"].view.frame.setLayout(vLayout)

    def __componentEditSetup(self):
        """ revamped component editor with a lot of extra functionalities, based on the Maya component editor but build from scratch to make it more powerfull
        """
        interface.forceLoadPlugin("SkinEditPlugin")
        self.textInfo["editorTab"] = self.tabs.addGraphicsTab("Component Editor", useIcon = ":/list.svg")
        self.textInfo["editorTab"].tabParent = self.tabs
        vLayout = nullVBoxLayout()
        
        self.editor = weightEditor.WeightEditorWindow(self)
        self.languageWidgets.append(self.editor)
        self.editor.isInView = False
        vLayout.addWidget(self.editor)
        self.textInfo["editorTab"].view.frame.setLayout(vLayout)

    def __weightManagerSetup(self):
        """ weight manager function, save and load skinweights to seperate files
        """
        interface.forceLoadPlugin("SkinEditPlugin")
        self.textInfo["wmTab"] = self.tabs.addGraphicsTab("Weight Manager", useIcon = ":/menuIconEdit.png")
        self.textInfo["wmTab"].tabParent = self.tabs
        vLayout = nullVBoxLayout()
        self.__weightUI = WeightsUI(self.settings, self.progressBar, self)
        self.languageWidgets.append(self.__weightUI)
        vLayout.addWidget(self.__weightUI)
        self.textInfo["wmTab"].view.frame.setLayout(vLayout)

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
        
        if dialog.gettabName() in self.__dialogGeo.keys():
            dialog.restoreGeometry(self.__dialogGeo[dialog.gettabName()])
        
        if pos.y() > -1:
            dialog.move(pos)

        dialog.closed.connect(self.storeTearOffInfo)
        dialog.show()
        tabs.removeTab(index)

    def storeTearOffInfo(self, dialog):
        self.__dialogGeo[dialog.gettabName()] = dialog.saveGeometry()

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
                self.toolTipWindow.hide()
                self.toolTipWindow.deleteLater()
            self.toolTipWindow = None
            self._timer.stop()

        if curWidget == None and self.toolTipWindow is not None:
            _removeTT()
        if self.currentWidgetAtMouse != curWidget:
            if self.toolTipWindow is not None:
                _removeTT()

            if not isinstance(curWidget, QWidget):  # <- add multiple checks if more implemented then just buttons
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
        tip = self.currentWidgetAtMouse.whatsThis()

        if (self.currentWidgetAtMouse is None) or (self.textInfo["tooltipAction"].isChecked() == False):
            if str(tip) in self._tooltips.keys():
                self.currentWidgetAtMouse.setToolTip(self._tooltips[tip])
            return
        
        if not str(tip) in self._tooltips.keys():
            return

        size = 250
        if QDesktopWidget().screenGeometry().height() > 1080:
            size *= 1.5
        rect = QRect(QCursor.pos().x() + 20, QCursor.pos().y() - (40 + size), size, size)
        if (self.window().pos().y() + (self.height() / 2)) > QCursor.pos().y():
            rect = QRect(QCursor.pos().x() + 20, QCursor.pos().y() + 20, size, size)

        self.toolTipWindow = AdvancedToolTip(rect)
        self.toolTipWindow.setTip(self._tooltips[str(tip)].replace("^", "\n"))
        self.toolTipWindow.setGifImage(tip)
        self.toolTipWindow.show()

    # -------------------- window states -------------------------------

    def saveUIState(self):
        """ save the current state of the ui in a seperate ini file, this should also hold information later from a seperate settings window

        :todo: instead of only geometry also store torn of tabs for each posssible object
        :todo: save the geometries of torn of tabs as well
        """
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("tools", self.mayaToolsTab.currentIndex())
        self.settings.setValue("tabs", self.tabs.currentIndex())
        self.settings.setValue("vnbf", self.vnbfWidget.getCheckValues())
        self.settings.setValue("favs", self.vnbfWidget.getFavSettings())
        self.settings.setValue("useFav", self.vnbfWidget.setFavcheck.isChecked())
        self.settings.setValue("copyTls", self.copyToolsTab.currentIndex())
        self.settings.setValue("language", self.changeLN.title())
        self.settings.setValue("toolTips", self.textInfo["tooltipAction"].isChecked())
        self.settings.setValue("dialogsInfo", self.__dialogGeo)
        
    def loadUIState(self):
        """ load the previous set information from the ini file where possible, if the ini file is not there it will start with default settings
        """
        getGeo = self.settings.value("geometry", None)
        if not getGeo in [None, "None"]:
            self.restoreGeometry(getGeo)
        tools = { "tools": self.mayaToolsTab,
                  "tabs": self.tabs,
                  "copyTls": self.copyToolsTab,
                }
        for key, comp in tools.iteritems():
            index = self.settings.value(key, 0)
            if index in [None, "None", "0"]:
                index = 0
            elif int(index) > comp.count()-1:
                index = -1
            comp.setCurrentIndex(int(index))
        self.vnbfWidget.setCheckValues(self.settings.value("vnbf",None))
        self.vnbfWidget.setFavSettings(self.settings.value("favs",[]))
        useFav = self.settings.value("useFav",False)
        if useFav in [False, "False", "false"]:
            useFav = 0
        self.vnbfWidget.setFavcheck.setChecked(bool(useFav))
        self._changeLanguage(self.settings.value("language","en"))

        _toolTipSetting = self.settings.value("toolTips", False)

        if _toolTipSetting in [False, "false", "False"]:
            _toolTipSetting = False
        self.textInfo["tooltipAction"].setChecked(bool(_toolTipSetting))
        
        self.__dialogGeo = self.settings.value("dialogsInfo", {})
        
    def hideEvent(self, event):
        """ the hide event is something that is triggered at the same time as close,
        sometimes the close event is not handled correctly by maya so we add the save state in here to make sure its always triggered
        :note: its only storing info so it doesnt break anything
        """
        QApplication.restoreOverrideCursor()
        if not self.toolTipWindow is None:
            self.toolTipWindow.hide()
            self.toolTipWindow.deleteLater()
        self.saveUIState()
        api._cleanEventFilter()
        super(SkinningToolsUI, self).hideEvent(event)

    def showEvent(self, event):
        api.dccInstallEventFilter()

    def closeEvent(self, event):
        """ the close event, 
        we save the state of the ui but we also force delete a lot of the skinningtool elements,
        normally python would do garbage collection for you, but to be sure that nothing is stored in memory that does not get deleted we 
        force the deletion here as well. somehow this avoids crashes in maya!
        """
        QApplication.restoreOverrideCursor()
        api._cleanEventFilter()
        self.saveUIState()
        try:
            self.skinSlider.clearCallback()
            self.editor.setClose()
            self.skinSlider.deleteLater()
            del self.skinSlider
            self.editor.deleteLater()
            del self.editor
        except:
            self.deleteLater()
        return True


def showUI(newPlacement=False):
    """ convenience function to show the current user interface in maya,

    :param newPlacement: if `True` will force the tool to not read the ini file, if `False` will open the tool as intended
    :type newPlacement: bool
    """
    dock = SkinningToolsUI(newPlacement, parent = None)
    dock.run()
    return dock