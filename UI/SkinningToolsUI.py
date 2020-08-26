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
        self.__iconSize = 40
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
        g = nullGridLayout()

        g.addWidget(QLabel("  skin:"), 0, 0)
        g.addWidget(QLabel("  Vtx :"), 1, 0)

        g.addWidget(QPushButton("Save >>"), 0, 1)
        g.addWidget(QPushButton("Save >>"), 1, 1)

        g.addWidget(QLineEdit(), 0, 2)
        g.addWidget(QLineEdit(), 1, 2)

        g.addWidget(QPushButton("<< Load"), 0, 3)
        g.addWidget(QPushButton("<< Load"), 1, 3)

        filePath = self._updateGraph()

        self.graph = toolButton(filePath, size=self.__graphSize)
        self.graph.clicked.connect(self._showGraph)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addLayout(g)
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

        AvgWght_Btn = svgButton("avarage vtx", os.path.join(_DIR, "Icons/AvarageVerts.svg"), size=self.__iconSize)
        cpyWght_Btn = svgButton("copy vtx", os.path.join(_DIR, "Icons/copy2Mult.svg"), size=self.__iconSize)
        swchVtx_Btn = svgButton("switch vtx", os.path.join(_DIR, "Icons/vert2vert.svg"), size=self.__iconSize)
        BoneLbl_Btn = svgButton("label joints", os.path.join(_DIR, "Icons/jointLabel.svg"), size=self.__iconSize)
        shellUn_btn = svgButton("unify shells", os.path.join(_DIR, "Icons/shellUnify.svg"), size=self.__iconSize)
        trsfrSK_Btn = svgButton("skin to skin", os.path.join(_DIR, "Icons/skinToSkin.svg"), size=self.__iconSize)
        trsfrPS_Btn = svgButton("skin to pose", os.path.join(_DIR, "Icons/skinToPose.svg"), size=self.__iconSize)
        nghbors_Btn = svgButton("neighbors", os.path.join(_DIR, "Icons/neighbors.svg"), size=self.__iconSize)
        nghbrsP_Btn = svgButton("neighbors + ", os.path.join(_DIR, "Icons/neighborsPlus.svg"), size=self.__iconSize)
        smthVtx_Btn = svgButton("smooth", os.path.join(_DIR, "Icons/smooth.svg"), size=self.__iconSize)
        smthBrs_Btn = svgButton("smooth Brush", os.path.join(_DIR, "Icons/brush.svg"), size=self.__iconSize)
        toJoint_Btn = svgButton("convert to joint", os.path.join(_DIR, "Icons/toJoints.svg"), size=self.__iconSize)
        rstPose_Btn = svgButton("reset Pose", os.path.join(_DIR, "Icons/resetJoint.svg"), size=self.__iconSize)

        copy2bn_Btn = svgButton("move bone infl.", os.path.join(_DIR, "Icons/Bone2Bone.svg"), size=self.__iconSize)
        b2bSwch_Btn = svgButton("swap bone infl.", os.path.join(_DIR, "Icons/Bone2Boneswitch.svg"), size=self.__iconSize)
        showInf_Btn = svgButton("select vertices", os.path.join(_DIR, "Icons/selectinfl.svg"), size=self.__iconSize)
        delBone_Btn = svgButton("delete joint", os.path.join(_DIR, "Icons/jointDelete.svg"), size=self.__iconSize)
        addinfl_Btn = svgButton("add joint", os.path.join(_DIR, "Icons/addJoint.svg"), size=self.__iconSize)
        unifyBn_Btn = svgButton("unify skeletons", os.path.join(_DIR, "Icons/unify.svg"), size=self.__iconSize)
        seltInf_Btn = svgButton("select joints", os.path.join(_DIR, "Icons/selectJnts.svg"), size=self.__iconSize)
        sepMesh_Btn = svgButton("seperate mesh", os.path.join(_DIR, "Icons/seperate.svg"), size=self.__iconSize)
        onlySel_Btn = svgButton("only selected infl.", os.path.join(_DIR, "Icons/onlySel.svg"), size=self.__iconSize)
        infMesh_Btn = svgButton("influenced meshes", os.path.join(_DIR, "Icons/infMesh.svg"), size=self.__iconSize)

        maxL = nullHBoxLayout()
        spin = QSpinBox()
        spin.setFixedSize(self.__iconSize, self.__iconSize+10)
        vtexMax_Btn = svgButton("force max infl.", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        frzBone_Btn = svgButton("freeze joints", os.path.join(_DIR, "Icons/FreezeJoint.svg"), size=self.__iconSize)

        for w in [spin, vtexMax_Btn]:
            maxL.addWidget(w)
        vtxOver_Btn = svgButton("sel infl. > max", os.path.join(_DIR, "Icons/vertOver.svg"), size=self.__iconSize)
        self.__buttons = [AvgWght_Btn, cpyWght_Btn, swchVtx_Btn, BoneLbl_Btn, shellUn_btn, trsfrSK_Btn, 
                         trsfrPS_Btn, nghbors_Btn, nghbrsP_Btn, smthVtx_Btn, smthBrs_Btn, toJoint_Btn, rstPose_Btn, 
                         copy2bn_Btn, b2bSwch_Btn, showInf_Btn, delBone_Btn, addinfl_Btn, unifyBn_Btn, 
                         seltInf_Btn, sepMesh_Btn, onlySel_Btn, infMesh_Btn, maxL, vtxOver_Btn, frzBone_Btn]
        for index, btn in enumerate(self.__buttons):
            row = index / 13
            if isinstance(btn, QLayout):
                g.addLayout(btn, index - (row * 13), row)
                continue
            g.addWidget(btn, index - (row * 13), row)

        v.addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

        addChecks(self, AvgWght_Btn, ["use distance"] )
        addChecks(self, trsfrSK_Btn, ["smooth", "uvSpace"] )
        addChecks(self, trsfrPS_Btn, ["smooth", "uvSpace"] )
        addChecks(self, nghbors_Btn, ["full"] )
        addChecks(self, nghbrsP_Btn, ["full"] )
        addChecks(self, delBone_Btn, ["use parent", "delete", "fast"] )
        addChecks(self, unifyBn_Btn, ["query"] )

        #@note: make sure the flags are adjusted by button settings
        AvgWght_Btn.clicked.connect( partial( interface.avgVtx, True, self.BezierGraph, self.progressBar ) )
        cpyWght_Btn.clicked.connect( partial( interface.copyVtx, self.progressBar ) )
        swchVtx_Btn.clicked.connect( partial( interface.switchVtx, self.progressBar ) )
        BoneLbl_Btn.clicked.connect( partial( interface.labelJoints, self.progressBar ) )
        shellUn_btn.clicked.connect( partial( interface.unifyShells, self.progressBar ) )
        trsfrSK_Btn.clicked.connect( partial( interface.copySkin, False, True, False, self.progressBar) )
        trsfrPS_Btn.clicked.connect( partial( interface.copySkin, True, True, False, self.progressBar) )
        nghbors_Btn.clicked.connect( partial( interface.neighbors, False, True, self.progressBar ) )
        nghbrsP_Btn.clicked.connect( partial( interface.neighbors, True, True, self.progressBar ) )
        smthVtx_Btn.clicked.connect( partial( interface.smooth, self.progressBar ) )
        smthBrs_Btn.clicked.connect( interface.smoothBrush )
        toJoint_Btn.clicked.connect( partial( interface.convertToJoint, self.progressBar ) )
        rstPose_Btn.clicked.connect( partial( interface.resetPose, self.progressBar ) )

        copy2bn_Btn.clicked.connect( partial( interface.moveBones, False,  self.progressBar ) )
        b2bSwch_Btn.clicked.connect( partial( interface.moveBones, True, self.progressBar ) )
        showInf_Btn.clicked.connect( partial( interface.showInfVerts, self.progressBar ) )
        delBone_Btn.clicked.connect( partial( interface.removeJoint, True, True, False, self.progressBar ) )
        addinfl_Btn.clicked.connect( partial( interface.addNewJoint, self.progressBar ) )
        unifyBn_Btn.clicked.connect( partial( interface.unifySkeletons, False,  self.progressBar ) )
        seltInf_Btn.clicked.connect( partial( interface.selectJoints, self.progressBar ) )
        sepMesh_Btn.clicked.connect( partial( interface.seperateSkinned, self.progressBar ) )
        onlySel_Btn.clicked.connect( partial( interface.getJointInfVers, self.progressBar ) )
        infMesh_Btn.clicked.connect( partial( interface.getMeshFromJoints, self.progressBar ) )
        vtexMax_Btn.clicked.connect( partial( interface.setMaxInfl, 8, self.progressBar ) )
        vtxOver_Btn.clicked.connect( partial( interface.getMaxInfl, 8, self.progressBar ) )
        frzBone_Btn.clicked.connect( partial( interface.freezeJoint, self.progressBar ) )

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
