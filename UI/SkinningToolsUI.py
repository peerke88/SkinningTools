# -*- coding: utf-8 -*-
from .qt_util import *
from .tearOff.editableTab import EditableTabWidget
from .tearOff.tearOffDialog import *
from ..Maya.tools.shared import *


__VERSION__ = "5.0.20200812"

class SkinningTools(QMainWindow):
    def __init__(self, parent=None):
        super(SkinningTools, self).__init__(parent)
        mainWidget = QWidget()
        self.setWindowFlags( Qt.Tool )
        self.setCentralWidget(mainWidget)

        self.settings = QSettings("uiSave","SkinningTools")
        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)
        
        self.__menuSetup()
        self.__tabsSetup()

        self.__mayaToolsSetup()
        self.__skinSliderSetup()
        self.__componentEditSetup()
        self.__weightManagerSetup()

        mainLayout.addWidget(self.tabs)
        
        self.loadUIState()

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
        # menu = self.menuBar().addMenu('')

        self.extraMenu   = QMenu('Extra', self)
        self.holdAction  = QAction("hold Model", self)
        self.fetchAction = QAction("fetch Model", self)
        self.objSkeletonAction = QAction("skeleton -> obj", self)
        for act in [self.holdAction, self.fetchAction, self.objSkeletonAction]:
            self.extraMenu.addAction(act)

        helpAction = QMenu('', self)
        helpAction.setIcon( QIcon(":/QR_help.png"))
        helpAction.setStatusTip('help Functions')

        docAction = QAction("Docs", self)
        self.tooltipAction = QAction("Enhanced ToolTip", self)
        self.tooltipAction.setCheckable(True)
        for act in [docAction, self.tooltipAction]:
            helpAction.addAction(act)

        self.changeLN = QAction("[EN]", self)

        self.menuBar().addMenu( helpAction )
        self.menuBar().addMenu(self.extraMenu)
        self.menuBar().addAction( self.changeLN )

    def __tabsSetup(self):
        self.tabs = EditableTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.tearOff.connect(self.tearOff)

    def __mayaToolsSetup(self):
        tab = self.tabs.addGraphicsTab("Maya Tools")
        v = QVBoxLayout()
        tab.view.frame.setLayout(v)
        buttons =  mayaToolsWindow()
        for button in buttons:
            v.addWidget(button)

    def __skinSliderSetup(self):
        tab = self.tabs.addGraphicsTab("Skin Slider")

    def __componentEditSetup(self):
        tab = self.tabs.addGraphicsTab("Component Editor")

    def __weightManagerSetup(self):
        tab = self.tabs.addGraphicsTab("Weight Manager")


    def tearOff(self, index, pos = QPoint()):
        view = self.tabs.viewAtIndex(index)
        dlg = TearOffDialog(self.mapName(index), self)
        dlg.setOriginalState(index, self.tabs)
        dlg.addwidget(view)
        if pos.y() > -1:
            dlg.move(pos)

        dlg.show()
        self.tabs.removeTab(index)

    # ------------------------- utilities ---------------------------------

    def saveUIState(self):
        state = []
        state.append(self.saveGeometry())
        self.settings.setValue("windowState", state)

    def loadUIState(self):
        state = [None]
        getState = self.settings.value("windowState")
        if getState == None:
            return
        if state[0] is not None:
            self.restoreGeometry(state[0])

    def __lineEdit_FalseFolderCharacters1(self, inLineEdit):                                                                    
        return re.search(r'[\\/:\[\]<>"!@#$%^&-.]', inLineEdit) or re.search(r'[*?|]', inLineEdit) or re.match(r'[0-9]', inLineEdit) or re.search(u'[\u4E00-\u9FFF]+', inLineEdit, re.U) or re.search(u'[\u3040-\u309Fー]+', inLineEdit, re.U) or re.search(u'[\u30A0-\u30FF]+', inLineEdit, re.U)
        
    def __lineEdit_FalseFolderCharacters2(self, inLineEdit):   
        return re.search(r'[\\/:\[\]<>"!@#$%^&-]', inLineEdit) or re.search(r'[*?|]', inLineEdit) or "." in inLineEdit or (len(inLineEdit) >0 and inLineEdit[0].isdigit()) or re.search(u'[\u4E00-\u9FFF]+', inLineEdit, re.U) or re.search(u'[\u3040-\u309Fー]+', inLineEdit, re.U) or re.search(u'[\u30A0-\u30FF]+', inLineEdit, re.U)
    
    def __lineEdit_Color(self, inLineEdit, inColor):                                                                        
        PalleteColor = QPalette(inLineEdit.palette())
        PalleteColor.setColor(QPalette.Base,QColor(inColor))
        inLineEdit.setPalette(PalleteColor)
    
    def __lineEdit_FieldEditted(self, inLineEdit, button, option = 1, *args):
        inText = inLineEdit.text()
        if (option == 1 and not self.__lineEdit_FalseFolderCharacters1(inText) in [None, True]) or (option == 2 and not self.__lineEdit_FalseFolderCharacters2(inText) in [None, False]):
            self.__lineEdit_Color(inLineEdit, 'red')
            button.setEnabled(False)
        elif inText == "":
            button.setEnabled(False)
        else:
            self.__lineEdit_Color(inLineEdit, self.__qt_normal_color)
            button.setEnabled(True)

    def mapName(self, index = -1):
        if index < 0:
            index = self.tabs.currentIndex()
        return self.tabs.tabText(index)

    def tearOff(self, index, pos = QPoint()):
        view = self.tabs.viewAtIndex(index)
        dlg = TearOffDialog(self.mapName(index), self)
        dlg.setOriginalState(index, self.tabs)
        dlg.addwidget(view)
        if pos.y() > -1:
            dlg.move(pos)
        dlg.resize(300, 200)
        dlg.show()
        self.tabs.removeTab(index)
    
    def closeEvent(self, event):
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

    window_name = 'SkinningTools: %s'%__VERSION__
    mainWindow = get_maya_window()

    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == window_name:
                child.close()
                child.deleteLater()
    window = SkinningTools(mainWindow)
    window.setObjectName(window_name)
    window.setWindowTitle(window_name)
    window.show( )

    return window

