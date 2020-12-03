from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.tabs.skinBrushes import rodPaintSmoothBrush, updateBrushCommand, _CTX
from functools import partial
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()

# @todo: maybe convert the favourite functionality to a tag system instead of a list based function
# this could make code easier to read and adjust + more simple to find the objects necessary

class VertAndBoneFunction(QWidget):
    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        super(VertAndBoneFunction, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 40
        self.__editMode = False
        self.noAction = False
        self._dict = {}
        self.style = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #a69c83);"
        self.favourited = []
        self.individualBtns = []
        self.__favSettings = []

        self.progressBar = inProgressBar
        self.BezierGraph = inGraph
        self.borderSelection = interface.NeighborSelection()
        
        self.toolFrame = QFrame()
        self.toggleBtn = arrowButton(Qt.UpArrow, [QSizePolicy.Expanding, QSizePolicy.Minimum] )
        self.layout().addWidget(self.toolFrame)
        self.layout().addWidget(self.toggleBtn)
        self.toggleBtn.clicked.connect(self.showTools)

        self.showTools()
        self.__favTools()
        self.__addVertNBoneFunc()
        self._connections()
        self.changeLayout()

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ------------------------------- visibility tools ------------------------------- 
    def showTools(self):
        self.__editMode = not self.__editMode
        if self.__editMode:
            self.toolFrame.hide()
            self.toggleBtn.setArrowType(Qt.DownArrow)
        else:
            self.toolFrame.show()
            self.toggleBtn.setArrowType(Qt.UpArrow)
    
    def __favTools(self):
        self.toolFrame.setLayout(nullHBoxLayout())
        self.toolFrame.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.picker = toolButton(":/eyeDropper.png")
        self.setFavcheck = toolButton(":/SE_FavoriteStarDefault.png")
        self.setFavcheck.setCheckable(True)
        self.toolFrame.layout().addWidget(self.picker)
        self.toolFrame.layout().addWidget(self.setFavcheck) #< convert this to a button with a * for favourites
        self.toolFrame.layout().addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))

    def _connections(self):
        self.picker.clicked.connect(self.active)
        self.setFavcheck.toggled.connect(self.changeLayout)

    # ------------------------------- button creation ------------------------------- 
    def __addVertNBoneFunc(self):
        self.gridLayout = nullGridLayout()
        self.layout().addLayout(self.gridLayout)

        def _svgPath(svg):
            return os.path.join(_DIR, "Icons/%s.svg"%svg)

        # -- button creation
        AvgWght_Btn = svgButton("average vtx", _svgPath("AvarageVerts"), size=self.__IS)
        cpyWght_Btn = svgButton("copy vtx", _svgPath("copy2Mult"), size=self.__IS)
        swchVtx_Btn = svgButton("switch vtx", _svgPath("vert2vert"), size=self.__IS)
        BoneLbl_Btn = svgButton("label joints", _svgPath("jointLabel"), size=self.__IS)
        shellUn_btn = svgButton("unify shells", _svgPath("shellUnify"), size=self.__IS)
        trsfrSK_Btn = svgButton("skin to skin", _svgPath("skinToSkin"), size=self.__IS)
        trsfrPS_Btn = svgButton("skin to pose", _svgPath("skinToPose"), size=self.__IS)
        nghbors_Btn = svgButton("neighbors", _svgPath("neighbors"), size=self.__IS)
        hammerV_Btn = svgButton("weight hammer", _svgPath("hammer"), size=self.__IS)
        toJoint_Btn = svgButton("convert to joint", _svgPath("toJoints"), size=self.__IS)
        rstPose_Btn = svgButton("recalc bind", _svgPath("resetJoint"), size=self.__IS)
        cutMesh_Btn = svgButton("create proxy", _svgPath("proxy"), size=self.__IS)
        SurfPin_Btn = svgButton("add Surface pin", _svgPath("meshPin"), size=self.__IS)
        copy2bn_Btn = svgButton("move bone infl.", _svgPath("Bone2Bone"), size=self.__IS)
        b2bSwch_Btn = svgButton("swap bone infl.", _svgPath("Bone2Boneswitch"), size=self.__IS)
        showInf_Btn = svgButton("influenced vtx", _svgPath("selectinfl"), size=self.__IS)
        delBone_Btn = svgButton("remove joint", _svgPath("jointDelete"), size=self.__IS)
        addinfl_Btn = svgButton("add joint", _svgPath("addJoint"), size=self.__IS)
        unifyBn_Btn = svgButton("unify bind map", _svgPath("unify"), size=self.__IS)
        seltInf_Btn = svgButton("attached joints", _svgPath("selectJnts"), size=self.__IS)
        sepMesh_Btn = svgButton("extract skinned mesh", _svgPath("seperate"), size=self.__IS)
        onlySel_Btn = svgButton("prune excluded infl.", _svgPath("onlySel"), size=self.__IS)
        infMesh_Btn = svgButton("influenced meshes", _svgPath("infMesh"), size=self.__IS)
        BindFix_Btn = svgButton("fix bind mesh", _svgPath("fixBind"), size=self.__IS)
        delBind_Btn = svgButton("del bindPose", _svgPath("delbind"), size=self.__IS)
        vtxOver_Btn = svgButton("sel infl. > max", _svgPath("vertOver"), size=self.__IS)

        # -- complex button layout creation
        smthBrs_Lay = QWidget()
        smthBrs_Lay.setLayout(nullHBoxLayout())
        initSmt_Btn = svgButton("BP", _svgPath("Empty"), size=self.__IS)
        initSmt_Btn.setMaximumWidth(35)
        smthBrs_Btn = svgButton("smooth", _svgPath("brush"), size=self.__IS)
        self._smthSpin = QDoubleSpinBox()
        self._smthSpin.setFixedSize(self.__IS + 10, self.__IS + 10)
        self._smthSpin.setEnabled(False)
        self._smthSpin.setSingleStep(.05)
        smthBrs_Lay.attached = [initSmt_Btn, smthBrs_Btn, self._smthSpin]
        for w in smthBrs_Lay.attached:
            w.grp = smthBrs_Lay
            smthBrs_Lay.layout().addWidget(w)

        max_Lay = QWidget()
        max_Lay.setLayout(nullHBoxLayout())
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(self.__IS, self.__IS + 10)
        self._maxSpin.setMinimum(1)
        self._maxSpin.setValue(4)
        vtexMax_Btn = svgButton("force max infl.", _svgPath("Empty"), size=self.__IS)
        frzBone_Btn = svgButton("freeze joints", _svgPath("FreezeJoint"), size=self.__IS)
        max_Lay.attached = [vtexMax_Btn]
        vtexMax_Btn.grp = max_Lay
        for w in [self._maxSpin, vtexMax_Btn]:
            max_Lay.layout().addWidget(w)

        grow_Lay = QWidget()
        grow_Lay.setLayout(nullHBoxLayout())
        storsel_Btn = svgButton("store internal", _svgPath("Empty"), size=self.__IS)
        self.shrinks_Btn = svgButton("", _svgPath("shrink"), size=self.__IS)
        self.growsel_Btn = svgButton("", _svgPath("grow"), size=self.__IS)
        grow_Lay.attached = [self.shrinks_Btn, storsel_Btn, self.growsel_Btn]
        for i, w in enumerate(grow_Lay.attached):
            w.grp = grow_Lay
            if i != 1:
                w.setEnabled(False)
                w.setMaximumWidth(30)
            grow_Lay.layout().addWidget(w)

        self.__buttons = [AvgWght_Btn, cpyWght_Btn, swchVtx_Btn, BoneLbl_Btn, shellUn_btn, trsfrSK_Btn,
                          trsfrPS_Btn, nghbors_Btn, smthBrs_Lay, hammerV_Btn, toJoint_Btn, frzBone_Btn, rstPose_Btn, cutMesh_Btn, SurfPin_Btn,
                          copy2bn_Btn, b2bSwch_Btn, showInf_Btn, delBone_Btn, addinfl_Btn, unifyBn_Btn,
                          seltInf_Btn, sepMesh_Btn, onlySel_Btn, infMesh_Btn, max_Lay, vtxOver_Btn, BindFix_Btn, delBind_Btn,  grow_Lay ]

        self.filter()

        # -- add extra functionality to buttons
        addChecks(self, AvgWght_Btn, ["use distance"])
        addChecks(self, trsfrSK_Btn, ["smooth", "uvSpace"])
        addChecks(self, trsfrPS_Btn, ["smooth", "uvSpace"])
        addChecks(self, nghbors_Btn, ["growing", "full"])
        addChecks(self, toJoint_Btn, ["specify name"])
        addChecks(self, cutMesh_Btn, ["internal", "use opm"])
        addChecks(self, delBone_Btn, ["use parent", "delete", "fast"])
        addChecks(self, unifyBn_Btn, ["query"])
        addChecks(self, onlySel_Btn, ["invert"])
        addChecks(self, BindFix_Btn, ["model only", "in Pose"])
        addChecks(self, smthBrs_Btn, ["relax", "volume"])
        
        self.checkedButtons = [AvgWght_Btn, trsfrSK_Btn, trsfrPS_Btn, nghbors_Btn, toJoint_Btn, 
                               cutMesh_Btn, delBone_Btn, unifyBn_Btn, onlySel_Btn, BindFix_Btn, smthBrs_Btn]

        # -- singal connections                     
        smthBrs_Btn.checks["relax"].stateChanged.connect(partial(self._updateBrush_func, smthBrs_Btn))
        smthBrs_Btn.checks["volume"].stateChanged.connect(self._smthSpin.setEnabled)
        onlySel_Btn.checks["invert"].stateChanged.connect(partial(self._pruneOption, onlySel_Btn))
        AvgWght_Btn.clicked.connect(partial(self._AvgWght_func, AvgWght_Btn))
        cpyWght_Btn.clicked.connect(partial(interface.copyVtx, self.progressBar))
        swchVtx_Btn.clicked.connect(partial(interface.switchVtx, self.progressBar))
        BoneLbl_Btn.clicked.connect(partial(interface.labelJoints, False, self.progressBar))
        shellUn_btn.clicked.connect(partial(interface.unifyShells, self.progressBar))
        trsfrSK_Btn.clicked.connect(partial(self._trsfrSK_func, trsfrSK_Btn, False))
        trsfrPS_Btn.clicked.connect(partial(self._trsfrSK_func, trsfrPS_Btn, True))
        nghbors_Btn.clicked.connect(partial(self._nghbors_func, nghbors_Btn))
        initSmt_Btn.clicked.connect(interface.initBpBrush)
        smthBrs_Btn.clicked.connect(partial(self._smoothBrs_func, smthBrs_Btn))
        toJoint_Btn.clicked.connect(partial(self._convertToJoint_func, toJoint_Btn))
        rstPose_Btn.clicked.connect(partial(interface.resetPose, self.progressBar))
        cutMesh_Btn.clicked.connect(partial(self._cutMesh_func, cutMesh_Btn))
        hammerV_Btn.clicked.connect(partial(interface.hammerVerts, self.progressBar))
        SurfPin_Btn.clicked.connect(interface.pinToSurface)
        copy2bn_Btn.clicked.connect(partial(interface.moveBones, False, self.progressBar))
        b2bSwch_Btn.clicked.connect(partial(interface.moveBones, True, self.progressBar))
        showInf_Btn.clicked.connect(partial(interface.showInfVerts, self.progressBar))
        delBone_Btn.clicked.connect(partial(self._delBone_func, delBone_Btn))
        addinfl_Btn.clicked.connect(partial(interface.addNewJoint, self.progressBar))
        unifyBn_Btn.clicked.connect(partial(self._unifyBn_func, unifyBn_Btn))
        seltInf_Btn.clicked.connect(partial(interface.selectJoints, self.progressBar))
        sepMesh_Btn.clicked.connect(partial(interface.seperateSkinned, self.progressBar))
        onlySel_Btn.clicked.connect(partial(self._pruneSel_func, onlySel_Btn))
        infMesh_Btn.clicked.connect(partial(interface.getMeshFromJoints, self.progressBar))
        vtexMax_Btn.clicked.connect(partial(self._vtexMax_func, False))
        vtxOver_Btn.clicked.connect(partial(self._vtexMax_func, True))
        frzBone_Btn.clicked.connect(partial(interface.freezeJoint, self.progressBar))
        storsel_Btn.clicked.connect(self._storesel_func)
        delBind_Btn.clicked.connect(partial(interface.deleteBindPoses, self.progressBar))
        self.shrinks_Btn.clicked.connect(self._shrinks_func)
        self.growsel_Btn.clicked.connect(self._growsel_func)
        BindFix_Btn.clicked.connect(partial(self._bindFix_func, BindFix_Btn))
        self._smthSpin.valueChanged.connect(partial(self._updateBrush_func, smthBrs_Btn))

        for w in [initSmt_Btn, storsel_Btn]:
            w.setStyleSheet("QPushButton { text-align: center; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444); }")

    # -------------------------------  convenience functions for grouped layouts ------------------------------- 
    def getButtonSetup(self, btn):
        if hasattr(btn, "attached"):
            return btn.attached
        return [btn]

    def getGroupedLayout(self, inBtn):
        if hasattr(inBtn, "grp"):
            return inBtn.grp.attached
        else:
            return [inBtn]

    def getGroup(self, inBtn):
        if hasattr(inBtn, "grp"):
            return inBtn.grp
        else:
            return inBtn

    # -------------------------------  functionality for adding buttons to layout normal/favourites ------------------------------- 

    def getFavSettings(self):
        return self.__favSettings

    def setFavSettings(self, inSettings):
        if inSettings is None:
            return
        self.__favSettings = inSettings
        for index in self.__favSettings:
            btn = self.__buttons[int(index)]
            for b in self.getGroupedLayout(btn):
                self.favourited.append(b)

    favSettings = property( getFavSettings, setFavSettings)

    def getCheckValues(self):
        fullList = []
        for btn in self.checkedButtons:
            checkList = []
            for key, value in btn.checks.iteritems():
                checkList.append([key, value.isChecked()])
            fullList.append(checkList)
        return fullList

    def setCheckValues(self, values):
        if values is None:
            return
        for index, btn in enumerate(self.checkedButtons):
            for key, value in values[index]:
                btn.checks[key].setChecked(value)

    checkValues = property( getCheckValues, setCheckValues)

    def changeLayout(self, *_):
        if self.setFavcheck.isChecked():
            self.setFavcheck.setIcon(QIcon(":/SE_FavoriteStar.png"))
            self._setFavLayout()

        else:
            self.setFavcheck.setIcon(QIcon(":/SE_FavoriteStarDefault.png"))
            self._setBtnLayout()
    
    def filter( self, *_):
        for btn in self.__buttons:
            if hasattr(btn, "attached"):
                for w in btn.attached:
                    self._dict[w] = w.styleSheet()  
                    self.individualBtns.append(w) 
                    w.installEventFilter(self)  
                continue
            self._dict[btn] = btn.styleSheet()
            self.individualBtns.append(btn)      
            btn.installEventFilter(self) 

    def _clearLayout(self):
        for btn in self.__buttons:
            btn.setParent(None)

    def _setFavLayout(self):
        self._clearLayout()
        
        _checked = []
        toDisplay = []
        for btn in self.favourited:
            if btn in _checked:
                continue
            if hasattr(btn, "grp"):
                _checked.extend(self.getGroupedLayout(btn))
                toDisplay.append(btn.grp)
                continue
            toDisplay.append(btn)

        _rc = len(toDisplay)*.5
        attached = []
        index = 0
        for btn in toDisplay:
            row = int(index / _rc)
            self.gridLayout.addWidget(btn, index - (row * _rc), row)
            index += 1

    def _setBtnLayout(self):
        self._clearLayout()
        _rc = int(len(self.__buttons)*.5)
        for index, btn in enumerate(self.__buttons):
            row = index / _rc
            self.gridLayout.addWidget(btn, index - (row * _rc), row)

    def _convertStyleSheet(self, inStyleSheet):
        if not "background-color" in inStyleSheet:
            return inStyleSheet

        presplit = inStyleSheet.split("background-color: qlineargradient(", 1)
        postsplit = presplit[1].split(");", 1)[1]
        return "%s%s%s"%(presplit[0], self.style, postsplit)

    def active(self, *_):
        self.noAction = not self.noAction
        for btn in self.individualBtns:
            btn.blockSignals(self.noAction)        
        
        if self.noAction:
            self.picker.setIcon(QIcon(":/nodeGrapherDockBack.png"))
            for b in self.favourited:
                b.setStyleSheet(self._convertStyleSheet(b.styleSheet()))
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        else:
            self.picker.setIcon(QIcon(":/eyeDropper.png"))
            for btn, value in self._dict.iteritems():
                btn.setStyleSheet(value)
            QApplication.restoreOverrideCursor()

    def eventFilter(self, obj, event):
        if event is None:
            return
        if event.type() == QEvent.MouseButtonPress:
            obj = QApplication.widgetAt(QCursor.pos())
            if obj in self.individualBtns:
                if obj in self.favourited:
                    self.__favSettings.remove(self.__buttons.index(self.getGroup(obj)))
                    for btn in self.getGroupedLayout(obj):
                        btn.setStyleSheet(self._dict[btn])
                        self.favourited.remove(btn)
                else:
                    self.__favSettings.append(self.__buttons.index(self.getGroup(obj)))
                    for btn in self.getGroupedLayout(obj):
                        btn.setStyleSheet(self._convertStyleSheet(btn.styleSheet()))
                        self.favourited.append(btn)
                
        return super(VertAndBoneFunction, self).eventFilter( obj, event)
    
    # ------------------------------- button connections --------------------------------------------

    # -- checkbox modifiers    
    def _pruneOption(self, btn, value):
        btn.setText("prune %s infl."%["excluded, selected"][btn.checks["invert"].isChecked()])

    # -- buttons with extra functionality
    def _AvgWght_func(self, sender):
        interface.avgVtx(sender.checks["use distance"].isChecked(), self.BezierGraph.curveAsPoints(), self.progressBar)

    def _trsfrSK_func(self, sender, inPlace):
        interface.copySkin(inPlace, sender.checks["smooth"].isChecked(), sender.checks["uvSpace"].isChecked(), self.progressBar)

    def _nghbors_func(self, sender):
        interface.neighbors(sender.checks["growing"].isChecked(), sender.checks["full"].isChecked(), self.progressBar)

    def _convertToJoint_func(self, sender):
        interface.convertToJoint(sender.checks["specify name"].isChecked(), self.progressBar)

    def _delBone_func(self, sender):
        interface.removeJoint(sender.checks["use parent"].isChecked(), sender.checks["delete"].isChecked(), sender.checks["fast"].isChecked(), self.progressBar)

    def _unifyBn_func(self, sender):
        interface.unifySkeletons(sender.checks["query"].isChecked(), self.progressBar)

    def _vtexMax_func(self, query):
        if query:
            return interface.getMaxInfl(self._maxSpin.value(), self.progressBar)
        interface.setMaxInfl(self._maxSpin.value(), self.progressBar)

    def _cutMesh_func(self, sender):
        interface.cutMesh(sender.checks["internal"].isChecked(), sender.checks["use opm"].isChecked(), self.progressBar)

    def _pruneSel_func(self, sender):
        interface.keepOnlyJoints(sender.checks["invert"].isChecked())

    def _storesel_func(self, *args):
        self.borderSelection.storeSel()
        self.shrinks_Btn.setEnabled(False)
        self.growsel_Btn.setEnabled(True)

    def _shrinks_func(self, *args):
        self.borderSelection.shrink()
        self.shrinks_Btn.setEnabled(self.borderSelection.getBorderIndex() != 0)

    def _growsel_func(self, *args):
        self.shrinks_Btn.setEnabled(self.borderSelection.getBorderIndex() != 0)
        self.borderSelection.grow()

    def _bindFix_func(self, sender,  *args):
        interface.prebindFixer(sender.checks["model only"].isChecked(), sender.checks["in Pose"].isChecked(), self.progressBar)

    def _smoothBrs_func(self, sender,  *args):
        _radius = 0.0
        if sender.checks["volume"].isChecked():
            _radius = self._smthSpin.value()

        rodPaintSmoothBrush(_radius, int(sender.checks["relax"].isChecked()))

    def _updateBrush_func(self, sender,  *args):
        _radius = 0.0
        if sender.checks["volume"].isChecked():
            _radius = self._smthSpin.value()
        selection = interface.getSelection()
        sc = api.skinClusterForObject(selection[0])
        if sc:
            updateBrushCommand(_CTX, sc, _radius, int(sender.checks["relax"].isChecked()))