# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.tearOff.editableTab import EditableTabWidget
from SkinningTools.UI.tearOff.tearOffDialog import *
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.fallofCurveUI import BezierGraph
from SkinningTools.UI.messageProgressBar import MessageProgressBar
from SkinningTools.UI.vertexWeightMatcher import TransferWeightsWidget, ClosestVertexWeightWidget
import tempfile, os
from functools import partial

__VERSION__ = "5.0.20200820"
_DIR = os.path.dirname(os.path.abspath(__file__))


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
        self.__graphSize = 60
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
        h = nullHBoxLayout()

        filePath = self._updateGraph()

        self.graph = toolButton(filePath, size=self.__graphSize)
        self.graph.clicked.connect(self._showGraph)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(self.graph)

        v.addLayout(h)
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
        g = nullGridLayout()
        v.addLayout(g)
        tab.view.frame.setLayout(v)

        AvgWght_Btn = svgButton("avarage", os.path.join(_DIR, "Icons/AvarageVerts.svg"), size=60)
        cpyWght_Btn = svgButton("copy", os.path.join(_DIR, "Icons/copy2Mult.svg"), size=60)
        swchVtx_Btn = svgButton("switch", os.path.join(_DIR, "Icons/vert2vert.svg"), size=60)
        BoneLbl_Btn = svgButton("label", os.path.join(_DIR, "Icons/jointLabel.svg"), size=60)
        shellUn_btn = svgButton("shells", os.path.join(_DIR, "Icons/shellUnify.svg"), size=60)
        trsfrSK_Btn = svgButton("skinToSkin", os.path.join(_DIR, "Icons/skinToSkin.svg"), size=60)
        trsfrPS_Btn = svgButton("skinToPose", os.path.join(_DIR, "Icons/skinToPose.svg"), size=60)
        nghbors_Btn = svgButton("neighbors", os.path.join(_DIR, "Icons/neighbors.svg"), size=60)
        nghbrsP_Btn = svgButton("neighbors + ", os.path.join(_DIR, "Icons/neighborsPlus.svg"), size=60)
        smthVtx_Btn = svgButton("smooth", os.path.join(_DIR, "Icons/smooth.svg"), size=60)
        smthBrs_Btn = svgButton("sm.Brush", os.path.join(_DIR, "Icons/brush.svg"), size=60)
        toJoint_Btn = svgButton("Convert", os.path.join(_DIR, "Icons/toJoints.svg"), size=60)

        copy2bn_Btn = svgButton("move", os.path.join(_DIR, "Icons/Bone2Bone.svg"), size=60)
        b2bSwch_Btn = svgButton("swap", os.path.join(_DIR, "Icons/Bone2Boneswitch.svg"), size=60)
        showInf_Btn = svgButton("select", os.path.join(_DIR, "Icons/selectinfl.svg"), size=60)
        delBone_Btn = svgButton("BoneDelete", os.path.join(_DIR, "Icons/jointDelete.svg"), size=60)
        addinfl_Btn = svgButton("add", os.path.join(_DIR, "Icons/addJoint.svg"), size=60)
        unifyBn_Btn = svgButton("unify", os.path.join(_DIR, "Icons/unify.svg"), size=60)
        seltInf_Btn = svgButton("selectinfl", os.path.join(_DIR, "Icons/selectJnts.svg"), size=60)
        sepMesh_Btn = svgButton("seperateMesh", os.path.join(_DIR, "Icons/seperate.svg"), size=60)
        onlySel_Btn = svgButton("only sel infl.", os.path.join(_DIR, "Icons/onlySel.svg"), size=60)
        infMesh_Btn = svgButton("infl. meshes", os.path.join(_DIR, "Icons/infMesh.svg"), size=60)
        maxL = nullHBoxLayout()
        spin = QSpinBox()
        vtexMax_Btn = svgButton("max infl.", '', size=60)
        for w in [spin, vtexMax_Btn]:
            maxL.addWidget(w, 1)
        vtxOver_Btn = svgButton("infl. > max", os.path.join(_DIR, "Icons/vertOver.svg"), size=60)

        for index, btn in enumerate([AvgWght_Btn, cpyWght_Btn, swchVtx_Btn, BoneLbl_Btn, shellUn_btn, trsfrSK_Btn, 
                                     trsfrPS_Btn, nghbors_Btn, nghbrsP_Btn, smthVtx_Btn, smthBrs_Btn, toJoint_Btn, 
                                     copy2bn_Btn, b2bSwch_Btn, showInf_Btn, delBone_Btn, addinfl_Btn, unifyBn_Btn, 
                                     seltInf_Btn, sepMesh_Btn, onlySel_Btn, infMesh_Btn, maxL, vtxOver_Btn]):
            row = index / 12
            if isinstance(btn, QLayout):
                g.addLayout(btn, index - (row * 12), row)
                continue
            g.addWidget(btn, index - (row * 12), row)

        v.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

        AvgWght_Btn.clicked.connect(partial(interface.avgVtx, self.progressBar ))
        cpyWght_Btn.clicked.connect(partial(interface.copyVtx, self.progressBar ))
        # b2bSwch_Btn.clicked.connect(partial(interface, self.progressBar ))
        # copy2bn_Btn.clicked.connect(partial(interface, self.progressBar ))
        # showInf_Btn.clicked.connect(partial(interface, self.progressBar ))
        swchVtx_Btn.clicked.connect(partial(interface.switchVtx, self.progressBar ))
        BoneLbl_Btn.clicked.connect(partial(interface.labelJoints, self.progressBar ))
        # delBone_Btn.clicked.connect(partial(interface, self.progressBar ))
        # seltInf_Btn.clicked.connect(partial(interface, self.progressBar ))
        # unifyBn_Btn.clicked.connect(partial(interface, self.progressBar ))
        # smthVtx_Btn.clicked.connect(partial(interface, self.progressBar ))
        trsfrSK_Btn.clicked.connect(partial(interface.copySkin, False, True, False, self.progressBar))
        trsfrPS_Btn.clicked.connect(partial(interface.copySkin, True, True, False, self.progressBar))
        # addinfl_Btn.clicked.connect(partial(interface, self.progressBar ))

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
        cnct_Btn = toolButton(self.__notConnected)
        cnct_Btn.setCheckable(True)
        cnct_Btn.clicked.connect(self._updateConnect)
        rfr = toolButton(":/playbackLoopingContinuous_100.png")
        live = toolButton(self.__liveIMG)
        live.setCheckable(True)
        live.clicked.connect(self._updateLive)

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [cnct_Btn, rfr, live]:
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
