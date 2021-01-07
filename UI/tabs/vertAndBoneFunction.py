from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.tabs.skinBrushes import rodPaintSmoothBrush, updateBrushCommand, _CTX
from functools import  partial
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()

# @todo: maybe convert the favourite functionality to a tag system instead of a list based function
# this could make code easier to read and adjust + more simple to find the objects necessary
#  ^^^ this now needs to change as language settings broke the favourite functionality

class VertAndBoneFunction(QWidget):
    toolName = "VertAndBoneFunction"

    def __init__(self, local = "en", inGraph=None, inProgressBar=None, parent=None):
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
        self._Btn = {}
        self.__locale = local

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

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
            if isinstance(self._Btn[key], QCheckBox):
                self._Btn[key].displayText = value
            else:
                self._Btn[key].setText(value)
        
    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self._Btn.iteritems():
            if isinstance(self._Btn[key], QCheckBox):
                _ret[key] = value.displayText
            else:
                _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
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
        self.picker = toolButton(":/eyeDropper.png")
        self.setFavcheck = toolButton(":/SE_FavoriteStarDefault.png")
        self.setFavcheck.setCheckable(True)

        self.toolFrame.setLayout(nullHBoxLayout())
        self.toolFrame.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
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
        self._Btn["AvgWght_Btn"] = svgButton("average vtx", _svgPath("AvarageVerts"), size=self.__IS)
        self._Btn["cpyWght_Btn"] = svgButton("copy vtx", _svgPath("copy2Mult"), size=self.__IS)
        self._Btn["swchVtx_Btn"] = svgButton("switch vtx", _svgPath("vert2vert"), size=self.__IS)
        self._Btn["BoneLbl_Btn"] = svgButton("label joints", _svgPath("jointLabel"), size=self.__IS)
        self._Btn["shellUn_btn"] = svgButton("unify shells", _svgPath("shellUnify"), size=self.__IS)
        self._Btn["trsfrSK_Btn"] = svgButton("skin to skin", _svgPath("skinToSkin"), size=self.__IS)
        self._Btn["trsfrPS_Btn"] = svgButton("skin to pose", _svgPath("skinToPose"), size=self.__IS)
        self._Btn["nghbors_Btn"] = svgButton("neighbors", _svgPath("neighbors"), size=self.__IS)
        self._Btn["hammerV_Btn"] = svgButton("weight hammer", _svgPath("hammer"), size=self.__IS)
        self._Btn["toJoint_Btn"] = svgButton("convert to joint", _svgPath("toJoints"), size=self.__IS)
        self._Btn["rstPose_Btn"] = svgButton("recalc bind", _svgPath("resetJoint"), size=self.__IS)
        self._Btn["cutMesh_Btn"] = svgButton("create proxy", _svgPath("proxy"), size=self.__IS)
        self._Btn["SurfPin_Btn"] = svgButton("add Surface pin", _svgPath("meshPin"), size=self.__IS)
        self._Btn["copy2bn_Btn"] = svgButton("move bone infl.", _svgPath("Bone2Bone"), size=self.__IS)
        self._Btn["b2bSwch_Btn"] = svgButton("swap bone infl.", _svgPath("Bone2Boneswitch"), size=self.__IS)
        self._Btn["showInf_Btn"] = svgButton("influenced vtx", _svgPath("selectinfl"), size=self.__IS)
        self._Btn["delBone_Btn"] = svgButton("remove joint", _svgPath("jointDelete"), size=self.__IS)
        self._Btn["addinfl_Btn"] = svgButton("add joint", _svgPath("addJoint"), size=self.__IS)
        self._Btn["unifyBn_Btn"] = svgButton("unify bind map", _svgPath("unify"), size=self.__IS)
        self._Btn["seltInf_Btn"] = svgButton("attached joints", _svgPath("selectJnts"), size=self.__IS)
        self._Btn["sepMesh_Btn"] = svgButton("extract skinned mesh", _svgPath("seperate"), size=self.__IS)
        self._Btn["onlySel_Btn"] = svgButton("prune excluded infl.", _svgPath("onlySel"), size=self.__IS)
        self._Btn["infMesh_Btn"] = svgButton("influenced meshes", _svgPath("infMesh"), size=self.__IS)
        self._Btn["BindFix_Btn"] = svgButton("fix bind mesh", _svgPath("fixBind"), size=self.__IS)
        self._Btn["delBind_Btn"] = svgButton("del bindPose", _svgPath("delbind"), size=self.__IS)
        self._Btn["vtxOver_Btn"] = svgButton("sel infl. > max", _svgPath("vertOver"), size=self.__IS)

        # -- complex button layout creation
        smthBrs_Lay = QWidget()
        smthBrs_Lay.setLayout(nullHBoxLayout())
        self._Btn["initSmt_Btn"] = svgButton("BP", _svgPath("Empty"), size=self.__IS)
        self._Btn["initSmt_Btn"].setMaximumWidth(35)
        self._Btn["smthBrs_Btn"] = svgButton("smooth", _svgPath("brush"), size=self.__IS)
        self._smthSpin = QDoubleSpinBox()
        self._smthSpin.setFixedSize(self.__IS + 10, self.__IS + 10)
        self._smthSpin.setEnabled(False)
        self._smthSpin.setSingleStep(.05)
        smthBrs_Lay.attached = [self._Btn["initSmt_Btn"], self._Btn["smthBrs_Btn"], self._smthSpin]
        for w in smthBrs_Lay.attached:
            w.grp = smthBrs_Lay
            smthBrs_Lay.layout().addWidget(w)

        max_Lay = QWidget()
        max_Lay.setLayout(nullHBoxLayout())
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(self.__IS, self.__IS + 10)
        self._maxSpin.setMinimum(1)
        self._maxSpin.setValue(4)
        self._Btn["vtexMax_Btn"] = svgButton("force max infl.", _svgPath("Empty"), size=self.__IS)
        self._Btn["frzBone_Btn"] = svgButton("freeze joints", _svgPath("FreezeJoint"), size=self.__IS)
        max_Lay.attached = [self._Btn["vtexMax_Btn"]]
        self._Btn["vtexMax_Btn"].grp = max_Lay
        for w in [self._maxSpin, self._Btn["vtexMax_Btn"]]:
            max_Lay.layout().addWidget(w)

        grow_Lay = QWidget()
        grow_Lay.setLayout(nullHBoxLayout())
        self._Btn["storsel_Btn"] = svgButton("store internal", _svgPath("Empty"), size=self.__IS)
        self.shrinks_Btn = svgButton("", _svgPath("shrink"), size=self.__IS)
        self.growsel_Btn = svgButton("", _svgPath("grow"), size=self.__IS)
        grow_Lay.attached = [self.shrinks_Btn, self._Btn["storsel_Btn"], self.growsel_Btn]
        for i, w in enumerate(grow_Lay.attached):
            w.grp = grow_Lay
            if i != 1:
                w.setEnabled(False)
                w.setMaximumWidth(30)
            grow_Lay.layout().addWidget(w)

        self.__buttons = [self._Btn["AvgWght_Btn"], self._Btn["cpyWght_Btn"], self._Btn["swchVtx_Btn"], self._Btn["BoneLbl_Btn"], self._Btn["shellUn_btn"], self._Btn["trsfrSK_Btn"],
                          self._Btn["trsfrPS_Btn"], self._Btn["nghbors_Btn"], smthBrs_Lay, self._Btn["hammerV_Btn"], self._Btn["toJoint_Btn"], self._Btn["frzBone_Btn"], self._Btn["rstPose_Btn"], self._Btn["cutMesh_Btn"], self._Btn["SurfPin_Btn"],
                          self._Btn["copy2bn_Btn"], self._Btn["b2bSwch_Btn"], self._Btn["showInf_Btn"], self._Btn["delBone_Btn"], self._Btn["addinfl_Btn"], self._Btn["unifyBn_Btn"],
                          self._Btn["seltInf_Btn"], self._Btn["sepMesh_Btn"], self._Btn["onlySel_Btn"], self._Btn["infMesh_Btn"], max_Lay, self._Btn["vtxOver_Btn"], self._Btn["BindFix_Btn"], self._Btn["delBind_Btn"],  grow_Lay ]

        self.filter()

        # -- add extra functionality to buttons
        addChecks(self, self._Btn["AvgWght_Btn"], ["use distance"])
        addChecks(self, self._Btn["trsfrSK_Btn"], ["smooth", "uvSpace"])
        addChecks(self, self._Btn["trsfrPS_Btn"], ["smooth", "uvSpace"])
        addChecks(self, self._Btn["nghbors_Btn"], ["growing", "full"])
        addChecks(self, self._Btn["toJoint_Btn"], ["specify name"])
        addChecks(self, self._Btn["cutMesh_Btn"], ["internal", "use opm"])
        addChecks(self, self._Btn["delBone_Btn"], ["use parent", "delete", "fast"])
        addChecks(self, self._Btn["unifyBn_Btn"], ["query"])
        addChecks(self, self._Btn["onlySel_Btn"], ["invert"])
        addChecks(self, self._Btn["BindFix_Btn"], ["model only", "in Pose"])
        addChecks(self, self._Btn["smthBrs_Btn"], ["relax", "volume"])
        
        self._Btn["dist"] = self._Btn["AvgWght_Btn"].checks["use distance"]
        self._Btn["smooth"] = self._Btn["trsfrSK_Btn"].checks["smooth"]
        self._Btn["uvSpace"] = self._Btn["trsfrSK_Btn"].checks["uvSpace"]
        self._Btn["smooth1"] = self._Btn["trsfrPS_Btn"].checks["smooth"]
        self._Btn["uvSpace1"] = self._Btn["trsfrPS_Btn"].checks["uvSpace"]
        self._Btn["growing"] = self._Btn["nghbors_Btn"].checks["growing"]
        self._Btn["full"] = self._Btn["nghbors_Btn"].checks["full"]
        self._Btn["specify name"] = self._Btn["toJoint_Btn"].checks["specify name"]
        self._Btn["internal"] = self._Btn["cutMesh_Btn"].checks["internal"]
        self._Btn["use opm"] = self._Btn["cutMesh_Btn"].checks["use opm"]
        self._Btn["use parent"] = self._Btn["delBone_Btn"].checks["use parent"]
        self._Btn["delete"] = self._Btn["delBone_Btn"].checks["delete"]
        self._Btn["fast"] = self._Btn["delBone_Btn"].checks["fast"]
        self._Btn["query"] = self._Btn["unifyBn_Btn"].checks["query"]
        self._Btn["invert"] = self._Btn["onlySel_Btn"].checks["invert"]
        self._Btn["model only"] = self._Btn["BindFix_Btn"].checks["model only"]
        self._Btn["in Pose"] = self._Btn["BindFix_Btn"].checks["in Pose"]
        self._Btn["relax"] = self._Btn["smthBrs_Btn"].checks["relax"]
        self._Btn["volume"] = self._Btn["smthBrs_Btn"].checks["volume"]


        self.checkedButtons = [self._Btn["AvgWght_Btn"], self._Btn["trsfrSK_Btn"], self._Btn["trsfrPS_Btn"], self._Btn["nghbors_Btn"], self._Btn["toJoint_Btn"], 
                               self._Btn["cutMesh_Btn"], self._Btn["delBone_Btn"], self._Btn["unifyBn_Btn"], self._Btn["onlySel_Btn"], self._Btn["BindFix_Btn"], self._Btn["smthBrs_Btn"]]

        # -- singal connections                     
        self._Btn["smthBrs_Btn"].checks["relax"].stateChanged.connect( partial( self._updateBrush_func, self._Btn["smthBrs_Btn"] ) )
        self._Btn["onlySel_Btn"].checks["invert"].stateChanged.connect( partial( self._pruneOption, self._Btn["onlySel_Btn"] ) )
        self._Btn["smthBrs_Btn"].checks["volume"].stateChanged.connect(self._smthSpin.setEnabled)
        
        self._Btn["trsfrSK_Btn"].clicked.connect( partial( self._trsfrSK_func, self._Btn["trsfrSK_Btn"], False ) )
        self._Btn["trsfrPS_Btn"].clicked.connect( partial( self._trsfrSK_func, self._Btn["trsfrPS_Btn"], True ) )

        self._Btn["AvgWght_Btn"].clicked.connect( partial( self._AvgWght_func, self._Btn["AvgWght_Btn"] ) )
        self._Btn["nghbors_Btn"].clicked.connect( partial( self._nghbors_func, self._Btn["nghbors_Btn"] ) )
        self._Btn["smthBrs_Btn"].clicked.connect( partial( self._smoothBrs_func, self._Btn["smthBrs_Btn"] ) )
        self._Btn["toJoint_Btn"].clicked.connect( partial( self._convertToJoint_func, self._Btn["toJoint_Btn"] ) )
        self._Btn["delBone_Btn"].clicked.connect( partial( self._delBone_func, self._Btn["delBone_Btn"] ) )
        self._Btn["unifyBn_Btn"].clicked.connect( partial( self._unifyBn_func, self._Btn["unifyBn_Btn"] ) )
        self._Btn["onlySel_Btn"].clicked.connect( partial( self._pruneSel_func, self._Btn["onlySel_Btn"] ) )
        self._Btn["BindFix_Btn"].clicked.connect( partial( self._bindFix_func, self._Btn["BindFix_Btn"] ) )
        self._Btn["cutMesh_Btn"].clicked.connect( partial( self._cutMesh_func, self._Btn["cutMesh_Btn"] ) )
        
        self._Btn["vtexMax_Btn"].clicked.connect( partial( self._vtexMax_func, False ) )
        self._Btn["vtxOver_Btn"].clicked.connect( partial( self._vtexMax_func, True ) )
        
        self._Btn["BoneLbl_Btn"].clicked.connect( partial( interface.labelJoints, False, self.progressBar ) )
        self._Btn["copy2bn_Btn"].clicked.connect( partial( interface.moveBones, False, self.progressBar ) )
        self._Btn["b2bSwch_Btn"].clicked.connect( partial( interface.moveBones, True, self.progressBar ) )

        self._Btn["cpyWght_Btn"].clicked.connect( partial( interface.copyVtx, self.progressBar ) )
        self._Btn["swchVtx_Btn"].clicked.connect( partial( interface.switchVtx, self.progressBar ) )
        self._Btn["shellUn_btn"].clicked.connect( partial( interface.unifyShells, self.progressBar ) )
        self._Btn["rstPose_Btn"].clicked.connect( partial( interface.resetPose, self.progressBar ) )
        self._Btn["hammerV_Btn"].clicked.connect( partial( interface.hammerVerts, self.progressBar ) )
        self._Btn["showInf_Btn"].clicked.connect( partial( interface.showInfVerts, self.progressBar ) )
        self._Btn["addinfl_Btn"].clicked.connect( partial( interface.addNewJoint, self.progressBar ) )
        self._Btn["seltInf_Btn"].clicked.connect( partial( interface.selectJoints, self.progressBar ) )
        self._Btn["sepMesh_Btn"].clicked.connect( partial( interface.seperateSkinned, self.progressBar ) )
        self._Btn["infMesh_Btn"].clicked.connect( partial( interface.getMeshFromJoints, self.progressBar ) )
        self._Btn["frzBone_Btn"].clicked.connect( partial( interface.freezeJoint, self.progressBar ) )
        self._Btn["delBind_Btn"].clicked.connect( partial( interface.deleteBindPoses, self.progressBar ) )
        
        self._Btn["initSmt_Btn"].clicked.connect(interface.initBpBrush)
        self._Btn["SurfPin_Btn"].clicked.connect(interface.pinToSurface)
        self._Btn["storsel_Btn"].clicked.connect(self._storesel_func)
        
        self.shrinks_Btn.clicked.connect(self._shrinks_func)
        self.growsel_Btn.clicked.connect(self._growsel_func)

        self._smthSpin.valueChanged.connect( partial( self._updateBrush_func, self._Btn["smthBrs_Btn"] ) )

        for w in [self._Btn["initSmt_Btn"], self._Btn["storsel_Btn"]]:
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
            return
        
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
        if event is None or self is None:
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


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("VertAndBoneFunction Test window")
    wdw = VertAndBoneFunction(parent = mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw