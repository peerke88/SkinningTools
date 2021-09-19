# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from SkinningTools.UI.tabs.skinBrushes import rodPaintSmoothBrush, updateBrushCommand, _CTX, pathToSmoothBrushPlugin
from functools import partial
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()

# @todo: maybe convert the favourite functionality to a tag system instead of a list based function
# this could make code easier to read and adjust + more simple to find the objects necessary
#  ^^^ this now needs to change as language settings broke the favourite functionality


class VertAndBoneFunction(QWidget):
    """ the widget that holds all custom single button / buttongroup functions for authoring in the dcc tools
    """
    toolName = "VertAndBoneFunction"

    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        """ the constructor

        :param inGraph: the graph function that allows change of the average weight function
        :type inGraph: BezierGraph
        :param inProgressBar: the progressbar to show progress on tools current state
        :type inProgressBar: QProgressBar
        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(VertAndBoneFunction, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__defaults()

        self.progressBar = inProgressBar
        self.BezierGraph = inGraph
        self.borderSelection = interface.NeighborSelection()

        self.toolFrame = QFrame()
        self.toggleBtn = arrowButton(Qt.UpArrow, [QSizePolicy.Expanding, QSizePolicy.Minimum])
        self.layout().addWidget(self.toolFrame)
        self.layout().addWidget(self.toggleBtn)
        self.toggleBtn.clicked.connect(self.showTools)

        self.showTools()
        self.__favTools()
        self.__addVertNBoneFunc()
        self._connections()
        self.changeLayout()

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __defaults(self):
        self.__IS = 40

        self.__scaleFactor = 1
        self.__editMode = False
        self.noAction = False

        self._dict = {}
        self._Btn = {}
        self._remp = {}

        self.favourited = []
        self.individualBtns = []
        self.__favSettings = []

        self.style = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #a69c83);"

    # --------------------------------- translation ----------------------------------

    def translate(self, localeDict={}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.items():
            if isinstance(self._Btn[key], QCheckBox):
                self._Btn[key].displayText = value
                self._Btn[key].setToolTip(value)
            else:
                self._Btn[key].setText(value)

        for key, value in localeDict.items():
            if hasattr(self._Btn[key], "getNameInfo"):
                for k, v in self._Btn[key].getNameInfo.items():
                    v.setText(localeDict[self._remp[k]])

    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self._Btn.items():
            if isinstance(self._Btn[key], QCheckBox):
                _ret[key] = value.displayText
            else:
                _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName)
        _trs = translator.showUI(_dict, widgetName=self.toolName)

    # ------------------------------- visibility tools -------------------------------

    def showTools(self):
        """ switch function to show or hide elements
        """
        self.__editMode = not self.__editMode
        if self.__editMode:
            self.toolFrame.hide()
            self.toggleBtn.setArrowType(Qt.DownArrow)
        else:
            self.toolFrame.show()
            self.toggleBtn.setArrowType(Qt.UpArrow)

    def __favTools(self):
        """ favourite tools button, this button will allow the user to choose their favourite tools and display them
        """
        self.picker = toolButton(":/eyeDropper.png")
        self.setFavcheck = toolButton(":/SE_FavoriteStarDefault.png")
        self.setFavcheck.setCheckable(True)

        self.toolFrame.setLayout(nullHBoxLayout())
        self.toolFrame.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.toolFrame.layout().addWidget(self.picker)
        self.toolFrame.layout().addWidget(self.setFavcheck)  # < convert this to a button with a * for favourites
        self.toolFrame.layout().addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))

    def _connections(self):
        """ signal connections
        """
        self.picker.clicked.connect(self.active)
        self.setFavcheck.toggled.connect(self.changeLayout)

    # ------------------------------- size adjustment -------------------------------

    def _setIconSize(self, iconSize):
        self.__IS = iconSize
        if self._Btn == {}:
            return

        for name, button in self._Btn.items():
            button.setIconSize(QSize(iconSize, iconSize))

        self._smthSpin.setFixedSize(int(50 * self.__scaleFactor), 23 if iconSize < 13 else iconSize + 10)
        self._maxSpin.setFixedSize(int(40 * self.__scaleFactor), 23 if iconSize < 13 else iconSize + 10)
        self.shrinks_Btn.setIconSize(QSize(iconSize, iconSize))
        self.growsel_Btn.setIconSize(QSize(iconSize, iconSize))

    def _getIconSize(self):
        return self.__IS

    iconSize = property(_getIconSize, _setIconSize)

    def adjustSize(self, fontSize):

        self.__scaleFactor = 1.0 if fontSize / 12.0 < 1.0 else fontSize / 12.0
        if self._Btn == {}:
            return
        self._smthSpin.setFixedSize(int(50 * self.__scaleFactor), 23 if self.__IS < 13 else self.__IS + 10)
        self._maxSpin.setFixedSize(int(40 * self.__scaleFactor), 23 if self.__IS < 13 else self.__IS + 10)

    # ------------------------------- button creation -------------------------------

    def __addVertNBoneFunc(self):
        """ here we will create and modify all the seperate buttons that work with the dcc tool
        """
        self.gridLayout = nullGridLayout()
        self.layout().addLayout(self.gridLayout)

        def _svgPath(svg):
            return os.path.join(_DIR, "Icons/%s.svg" % svg)

        # -- button creation
        self._Btn["AvgWght_Btn"] = svgButton("average vtx", _svgPath("AvarageVerts"), size=self.__IS, toolTipInfo="Averagevtx")
        self._Btn["cpyWght_Btn"] = svgButton("copy vtx", _svgPath("copy2Mult"), size=self.__IS, toolTipInfo="Copyvtx")
        self._Btn["swchVtx_Btn"] = svgButton("switch vtx", _svgPath("vert2vert"), size=self.__IS, toolTipInfo="Switchvtx")
        self._Btn["BoneLbl_Btn"] = svgButton("label joints", _svgPath("jointLabel"), size=self.__IS, toolTipInfo="Labeljoints")
        self._Btn["shellUn_btn"] = svgButton("unify shells", _svgPath("shellUnify"), size=self.__IS, toolTipInfo="Unifyshells")
        self._Btn["trsfrSK_Btn"] = svgButton("skin to skin", _svgPath("skinToSkin"), size=self.__IS, toolTipInfo="Skin2skin")
        self._Btn["trsfrPS_Btn"] = svgButton("skin to pose", _svgPath("skinToPose"), size=self.__IS, toolTipInfo="Skin2Pose")
        self._Btn["nghbors_Btn"] = svgButton("neighbors", _svgPath("neighbors"), size=self.__IS, toolTipInfo="neighbors")
        self._Btn["hammerV_Btn"] = svgButton("weight hammer", _svgPath("hammer"), size=self.__IS, toolTipInfo="weightHammer")
        self._Btn["toJoint_Btn"] = svgButton("convert to joint", _svgPath("toJoints"), size=self.__IS, toolTipInfo="convert")
        self._Btn["rstPose_Btn"] = svgButton("recalc bind", _svgPath("resetJoint"), size=self.__IS, toolTipInfo="recalcBind")
        self._Btn["cutMesh_Btn"] = svgButton("create proxy", _svgPath("proxy"), size=self.__IS, toolTipInfo="proxy")
        self._Btn["SurfPin_Btn"] = svgButton("add Surface pin", _svgPath("meshPin"), size=self.__IS, toolTipInfo="surfacePin")
        self._Btn["copy2bn_Btn"] = svgButton("move bone infl.", _svgPath("Bone2Bone"), size=self.__IS, toolTipInfo="boneMove")
        self._Btn["b2bSwch_Btn"] = svgButton("swap bone infl.", _svgPath("Bone2Boneswitch"), size=self.__IS, toolTipInfo="boneMove")
        self._Btn["showInf_Btn"] = svgButton("influenced vtx", _svgPath("selectinfl"), size=self.__IS, toolTipInfo="selInfl")
        self._Btn["delBone_Btn"] = svgButton("remove joint", _svgPath("jointDelete"), size=self.__IS, toolTipInfo="delJoint")
        self._Btn["addinfl_Btn"] = svgButton("add joint", _svgPath("addJoint"), size=self.__IS, toolTipInfo="addJoint")
        self._Btn["unifyBn_Btn"] = svgButton("unify bind map", _svgPath("unify"), size=self.__IS, toolTipInfo="unifyJoint")
        self._Btn["seltInf_Btn"] = svgButton("attached joints", _svgPath("selectJnts"), size=self.__IS, toolTipInfo="selJoints")
        self._Btn["sepMesh_Btn"] = svgButton("extract skinned mesh", _svgPath("seperate"), size=self.__IS, toolTipInfo="seperate")
        self._Btn["onlySel_Btn"] = svgButton("prune excluded infl.", _svgPath("onlySel"), size=self.__IS, toolTipInfo="prune")
        self._Btn["infMesh_Btn"] = svgButton("influenced meshes", _svgPath("infMesh"), size=self.__IS, toolTipInfo="getMesh")
        self._Btn["BindFix_Btn"] = svgButton("fix bind mesh", _svgPath("fixBind"), size=self.__IS, toolTipInfo="fixBind")
        self._Btn["delBind_Btn"] = svgButton("del bindPose", _svgPath("delbind"), size=self.__IS, toolTipInfo="delBp")
        self._Btn["vtxOver_Btn"] = svgButton("sel infl. > max", _svgPath("vertOver"), size=self.__IS, toolTipInfo="getMax")

        # -- complex button layout creation
        api.loadPlugin(pathToSmoothBrushPlugin())

        smthBrs_Lay = QWidget()
        smthBrs_Lay.setLayout(nullHBoxLayout())
        self._Btn["initSmt_Btn"] = svgButton("BP", _svgPath("Empty"), size=self.__IS, toolTipInfo="smoothBrush")
        self._Btn["initSmt_Btn"].setMaximumWidth(35)
        self._Btn["smthBrs_Btn"] = svgButton("smooth", _svgPath("brush"), size=self.__IS, toolTipInfo="smoothBrush")
        self._smthSpin = QDoubleSpinBox()
        self._smthSpin.setFixedSize(int(50 * self.__scaleFactor), self.__IS)
        self._smthSpin.setEnabled(False)
        self._smthSpin.setSingleStep(.05)
        self._smthSpin.setWhatsThis("smoothBrush")
        smthBrs_Lay.attached = [self._Btn["initSmt_Btn"], self._Btn["smthBrs_Btn"], self._smthSpin]
        for w in smthBrs_Lay.attached:
            w.grp = smthBrs_Lay
            smthBrs_Lay.layout().addWidget(w)

        max_Lay = QWidget()
        max_Lay.setLayout(nullHBoxLayout())
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(int(40 * self.__scaleFactor), self.__IS)
        self._maxSpin.setMinimum(1)
        self._maxSpin.setValue(4)
        self._maxSpin.setWhatsThis("setMax")
        self._Btn["vtexMax_Btn"] = svgButton("force max infl.", _svgPath("Empty"), size=self.__IS, toolTipInfo="setMax")
        self._Btn["frzBone_Btn"] = svgButton("freeze joints", _svgPath("FreezeJoint"), size=self.__IS, toolTipInfo="freezeJoint")
        max_Lay.attached = [self._Btn["vtexMax_Btn"]]
        self._Btn["vtexMax_Btn"].grp = max_Lay
        for w in [self._maxSpin, self._Btn["vtexMax_Btn"]]:
            max_Lay.layout().addWidget(w)

        grow_Lay = QWidget()
        grow_Lay.setLayout(nullHBoxLayout())
        self._Btn["storsel_Btn"] = svgButton("store internal", _svgPath("Empty"), size=self.__IS, toolTipInfo="extend")
        self.shrinks_Btn = svgButton("", _svgPath("shrink"), size=self.__IS, toolTipInfo="extend")
        self.growsel_Btn = svgButton("", _svgPath("grow"), size=self.__IS, toolTipInfo="extend")
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
                          self._Btn["seltInf_Btn"], self._Btn["sepMesh_Btn"], self._Btn["onlySel_Btn"], self._Btn["infMesh_Btn"], max_Lay, self._Btn["vtxOver_Btn"], self._Btn["BindFix_Btn"], self._Btn["delBind_Btn"], grow_Lay]

        self.filter()

        # -- add extra functionality to buttons
        addChecks(self, self._Btn["AvgWght_Btn"], ["use distance"])
        addChecks(self, self._Btn["shellUn_btn"], ["use vtx polyShell"])
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
        self._Btn["polyShell"] = self._Btn["shellUn_btn"].checks["use vtx polyShell"]
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

        self._remp = {"use distance": "dist", "use vtx polyShell": "polyShell", "smooth": "smooth", "uvSpace": "uvSpace", "smooth": "smooth1",
                      "uvSpace": "uvSpace1", "growing": "growing", "full": "full", "specify name": "specify name",
                      "internal": "internal", "use opm": "use opm", "use parent": "use parent", "delete": "delete",
                      "fast": "fast", "query": "query", "invert": "invert", "model only": "model only",
                      "in Pose": "in Pose", "relax": "relax", "volume": "volume"}

        self.checkedButtons = [self._Btn["AvgWght_Btn"], self._Btn["shellUn_btn"], self._Btn["trsfrSK_Btn"], self._Btn["trsfrPS_Btn"], self._Btn["nghbors_Btn"], self._Btn["toJoint_Btn"],
                               self._Btn["cutMesh_Btn"], self._Btn["delBone_Btn"], self._Btn["unifyBn_Btn"], self._Btn["onlySel_Btn"], self._Btn["BindFix_Btn"], self._Btn["smthBrs_Btn"]]

        # -- singal connections
        self._Btn["smthBrs_Btn"].checks["relax"].stateChanged.connect(partial(self._updateBrush_func, self._Btn["smthBrs_Btn"]))
        # self._Btn["onlySel_Btn"].checks["invert"].stateChanged.connect( partial( self._pruneOption, self._Btn["onlySel_Btn"] ) )
        self._Btn["smthBrs_Btn"].checks["volume"].stateChanged.connect(self._smthSpin.setEnabled)

        self._Btn["trsfrSK_Btn"].clicked.connect(partial(self._trsfrSK_func, self._Btn["trsfrSK_Btn"], False))
        self._Btn["trsfrPS_Btn"].clicked.connect(partial(self._trsfrSK_func, self._Btn["trsfrPS_Btn"], True))

        self._Btn["AvgWght_Btn"].clicked.connect(partial(self._AvgWght_func, self._Btn["AvgWght_Btn"]))
        self._Btn["shellUn_btn"].clicked.connect(partial(self._Unify_func, self._Btn["shellUn_btn"]))  # interface.unifyShells, self.progressBar ) )
        self._Btn["nghbors_Btn"].clicked.connect(partial(self._nghbors_func, self._Btn["nghbors_Btn"]))
        self._Btn["smthBrs_Btn"].clicked.connect(partial(self._smoothBrs_func, self._Btn["smthBrs_Btn"]))
        self._Btn["toJoint_Btn"].clicked.connect(partial(self._convertToJoint_func, self._Btn["toJoint_Btn"]))
        self._Btn["delBone_Btn"].clicked.connect(partial(self._delBone_func, self._Btn["delBone_Btn"]))
        self._Btn["unifyBn_Btn"].clicked.connect(partial(self._unifyBn_func, self._Btn["unifyBn_Btn"]))
        self._Btn["onlySel_Btn"].clicked.connect(partial(self._pruneSel_func, self._Btn["onlySel_Btn"]))
        self._Btn["BindFix_Btn"].clicked.connect(partial(self._bindFix_func, self._Btn["BindFix_Btn"]))
        self._Btn["cutMesh_Btn"].clicked.connect(partial(self._cutMesh_func, self._Btn["cutMesh_Btn"]))

        self._Btn["vtexMax_Btn"].clicked.connect(partial(self._vtexMax_func, False))
        self._Btn["vtxOver_Btn"].clicked.connect(partial(self._vtexMax_func, True))

        self._Btn["BoneLbl_Btn"].clicked.connect(partial(interface.labelJoints, False, self.progressBar))
        self._Btn["copy2bn_Btn"].clicked.connect(partial(interface.moveBones, False, self.progressBar))
        self._Btn["b2bSwch_Btn"].clicked.connect(partial(interface.moveBones, True, self.progressBar))

        self._Btn["cpyWght_Btn"].clicked.connect(partial(interface.copyVtx, self.progressBar))
        self._Btn["swchVtx_Btn"].clicked.connect(partial(interface.switchVtx, self.progressBar))
        self._Btn["rstPose_Btn"].clicked.connect(partial(interface.resetPose, self.progressBar))
        self._Btn["hammerV_Btn"].clicked.connect(partial(interface.hammerVerts, self.progressBar))
        self._Btn["showInf_Btn"].clicked.connect(partial(interface.showInfVerts, self.progressBar))
        self._Btn["addinfl_Btn"].clicked.connect(partial(interface.addNewJoint, self.progressBar))
        self._Btn["seltInf_Btn"].clicked.connect(partial(interface.selectJoints, self.progressBar))
        self._Btn["sepMesh_Btn"].clicked.connect(partial(interface.seperateSkinned, self.progressBar))
        self._Btn["infMesh_Btn"].clicked.connect(partial(interface.getMeshFromJoints, self.progressBar))
        self._Btn["frzBone_Btn"].clicked.connect(partial(interface.freezeJoint, self.progressBar))
        self._Btn["delBind_Btn"].clicked.connect(partial(interface.deleteBindPoses, self.progressBar))

        self._Btn["initSmt_Btn"].clicked.connect(interface.initBpBrush)
        self._Btn["SurfPin_Btn"].clicked.connect(interface.pinToSurface)
        self._Btn["storsel_Btn"].clicked.connect(self._storesel_func)

        self.shrinks_Btn.clicked.connect(self._shrinks_func)
        self.growsel_Btn.clicked.connect(self._growsel_func)

        self._smthSpin.valueChanged.connect(partial(self._updateBrush_func, self._Btn["smthBrs_Btn"]))

        for w in [self._Btn["initSmt_Btn"], self._Btn["storsel_Btn"]]:
            w.setStyleSheet("QPushButton { text-align: center; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444); }")

    # -------------------------------  convenience functions for grouped layouts -------------------------------
    def getButtonSetup(self, btn):
        """ convenience function to figure out which buttons are connected to the layout
        this will check for layouts

        :param btn: the widget with seperate attribute to check if its part of a group
        :type btn: QWidget
        :return: list of attached objects
        :rtype: list
        """
        if hasattr(btn, "attached"):
            return btn.attached
        return [btn]

    def getGroupedLayout(self, inBtn):
        """ convenience function to figure out which buttons are connected to the layout

        :param btn: the widget with seperate attribute to check if its part of a group
        :type btn: QWidget
        :return: list of attached objects
        :rtype: list
        """
        if hasattr(inBtn, "grp"):
            return inBtn.grp.attached
        else:
            return [inBtn]

    def getGroup(self, inBtn):
        """convenience function to figure out which layouts the buttons are connected to

        :param btn: the widget with seperate attribute to check if its part of a group
        :type btn: QWidget
        :return: the layout the objects are attached to
        :rtype: QLayout
        """
        if hasattr(inBtn, "grp"):
            return inBtn.grp
        else:
            return inBtn

    # -------------------------------  functionality for adding buttons to layout normal/favourites -------------------------------

    def getFavSettings(self):
        """ get the current settings on which elements are targeted as favourite

        :return: list of all elements that are set as favourite
        :rtype: list
        """
        return self.__favSettings

    def setFavSettings(self, inSettings):
        """ set the favourite objects from given settings

        :param inSettings: list of elements that are set as favourite
        :type inSettings: list
        """
        if inSettings is None:
            return
        self.__favSettings = []
        for index in inSettings:
            btn = self.__buttons[int(index)]
            self.__favSettings.append(int(index))
            for b in self.getGroupedLayout(btn):
                self.favourited.append(b)

    """favourite settings property"""
    favSettings = property(getFavSettings, setFavSettings)

    def getCheckValues(self):
        """ get the values fo all checkable attributes in the current tool

        :return: list of all checked values
        :rtype: list
        """
        fullList = []
        for btn in self.checkedButtons:
            checkList = []
            for key, value in btn.checks.items():
                checkList.append([key, value.isChecked()])
            fullList.append(checkList)
        return fullList

    def setCheckValues(self, values):
        """ set the values of the buttons to be checked based on the given settings

        :param values: list of values from settings to set the checked state of button attributes
        :type values: list
        """
        if values is None:
            return
        for index, btn in enumerate(self.checkedButtons):
            for key, value in values[index]:
                btn.checks[key].setChecked(value)

    """ckecked attributes property"""
    checkValues = property(getCheckValues, setCheckValues)

    def changeLayout(self, *_):
        """ change layout function based on the state of the favourit settings
        """
        if self.setFavcheck.isChecked():
            self.setFavcheck.setIcon(QIcon(":/SE_FavoriteStar.png"))
            self._setFavLayout()
            return

        self.setFavcheck.setIcon(QIcon(":/SE_FavoriteStarDefault.png"))
        self._setBtnLayout()

    def filter(self, *_):
        """ install the eventfilter for assigning fouvourite settings
        """
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
        """ make sure that the buttons are unparented but not destroyed
        """
        for btn in self.__buttons:
            btn.setParent(None)

    def _setFavLayout(self):
        """ repopulate the current widget with only buttons that are assigned as favourite
        """
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

        _rc = len(toDisplay) * .5
        attached = []
        index = 0
        for btn in toDisplay:
            row = int(index / _rc)
            self.gridLayout.addWidget(btn, index - (row * _rc), row)
            index += 1

    def _setBtnLayout(self):
        """ populate the current widget with all objects
        """
        self._clearLayout()
        _rc = int(len(self.__buttons) * .5)
        for index, btn in enumerate(self.__buttons):
            row = int(index / _rc)
            self.gridLayout.addWidget(btn, index - (row * _rc), row)

    def _convertStyleSheet(self, inStyleSheet):
        """ stylesheet change for display if the object is being selected
        """
        if not "background-color" in inStyleSheet:
            return inStyleSheet

        presplit = inStyleSheet.split("background-color: qlineargradient(", 1)
        postsplit = presplit[1].split(");", 1)[1]
        return "%s%s%s" % (presplit[0], self.style, postsplit)

    def active(self, *_):
        """ the settings to actively assign the favourite toolsets
        """
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
            for btn, value in self._dict.items():
                btn.setStyleSheet(value)
            QApplication.restoreOverrideCursor()

    def eventFilter(self, obj, event):
        """ event filter,
        this event filter listens to the mouse events on certain buttons to figure out if they can be chosen as favourite
        the event filter will display the current elements and groups as favourite when possible
        """
        if event is None or self is None:
            return
        if event.type() == QEvent.MouseButtonPress:
            obj = QApplication.widgetAt(QCursor.pos())
            if obj in self.individualBtns and self.noAction:
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

        return super(VertAndBoneFunction, self).eventFilter(obj, event)

    # ------------------------------- button connections --------------------------------------------

    # -- checkbox modifiers
    def _pruneOption(self, btn, value):
        #@todo: check if we can get this to work with language changes
        btn.setText("prune %s infl." % ["excluded, selected"][btn.checks["invert"].isChecked()])

    # -- buttons with extra functionality
    def _AvgWght_func(self, sender):
        """ average weight connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.avgVtx(sender.checks["use distance"].isChecked(), self.BezierGraph.curveAsPoints(), self.progressBar)

    def _Unify_func(self, sender):
        if sender.checks["use vtx polyShell"].isChecked():
            interface.setHardShellWeight(self.progressBar)
            return
        interface.unifyShells(self.progressBar)

    def _trsfrSK_func(self, sender, inPlace):
        """ transfer skin connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        :param inPlace: differentiates between skin and pose functionality
        :type inPlace: bool
        """
        interface.copySkin(inPlace, sender.checks["smooth"].isChecked(), sender.checks["uvSpace"].isChecked(), self.progressBar)

    def _nghbors_func(self, sender):
        """ neighbours smoothing connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.neighbors(True, sender.checks["growing"].isChecked(), sender.checks["full"].isChecked(), self.progressBar)

    def _convertToJoint_func(self, sender):
        """ convert selection to joint connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.convertToJoint(sender.checks["specify name"].isChecked(), self.progressBar)

    def _delBone_func(self, sender):
        """ delete bone connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.removeJoint(sender.checks["use parent"].isChecked(), sender.checks["delete"].isChecked(), sender.checks["fast"].isChecked(), self.progressBar)

    def _unifyBn_func(self, sender):
        """ unify influence map connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.unifySkeletons(sender.checks["query"].isChecked(), self.progressBar)

    def _vtexMax_func(self, query):
        """ maximum influences per vertex connection function using the extra attributes

        :param query: if `True` will return the vertices, if `False` sets the max influences
        :type query: bool
        """
        if query:
            return interface.getMaxInfl(self._maxSpin.value(), self.progressBar)
        interface.setMaxInfl(self._maxSpin.value(), self.progressBar)

    def _cutMesh_func(self, sender):
        """ cut mesh by influences connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.cutMesh(sender.checks["internal"].isChecked(), sender.checks["use opm"].isChecked(), self.progressBar)

    def _pruneSel_func(self, sender):
        """ prune influences connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.keepOnlyJoints(sender.checks["invert"].isChecked())

    def _storesel_func(self, *args):
        """ store the current component selection and alter the connected buttons
        """
        self.borderSelection.storeSel()
        self.shrinks_Btn.setEnabled(False)
        self.growsel_Btn.setEnabled(True)

    def _shrinks_func(self, *args):
        """ shrink the current selection
        """
        self.borderSelection.shrink()
        self.shrinks_Btn.setEnabled(self.borderSelection.getBorderIndex() != 0)

    def _growsel_func(self, *args):
        """ grow the current selection
        """
        self.borderSelection.grow()
        self.shrinks_Btn.setEnabled(self.borderSelection.getBorderIndex() != 0)

    def _bindFix_func(self, sender, *args):
        """ fix the bind map connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        interface.prebindFixer(sender.checks["model only"].isChecked(), sender.checks["in Pose"].isChecked(), self.progressBar)

    def _smoothBrs_func(self, sender, *args):
        """ smooth brush connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        _radius = 0.0
        if sender.checks["volume"].isChecked():
            _radius = self._smthSpin.value()

        rodPaintSmoothBrush(_radius, int(sender.checks["relax"].isChecked()))

    def _updateBrush_func(self, sender, *args):
        """ update smooth brush connection function using the extra attributes

        :param sender: button object on which the checkbox is attached
        :type sender: QPushButton
        """
        _radius = 0.0
        if sender.checks["volume"].isChecked():
            _radius = self._smthSpin.value()
        selection = interface.getSelection()
        if selection == []:
            return
        sc = api.skinClusterForObject(selection[0])
        if sc:
            updateBrushCommand(_CTX, sc, _radius, int(sender.checks["relax"].isChecked()))


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd = QMainWindow(mainWindow)
    mwd.setWindowTitle("VertAndBoneFunction Test window")
    wdw = VertAndBoneFunction(parent=mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
