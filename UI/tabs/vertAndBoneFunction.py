from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = True

class VertAndBoneFunction(QWidget):
    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        super(VertAndBoneFunction, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 40

        self.progressBar = inProgressBar
        self.BezierGraph = inGraph
        self.borderSelection = interface.NeighborSelection()
        self.__addVertNBoneFunc()

    def __addVertNBoneFunc(self):
        g = nullGridLayout()
        self.layout().addLayout(g)

        def _svgPath(svg):
            return os.path.join(_DIR, "Icons/%s.svg"%svg)

        AvgWght_Btn = svgButton("avarage vtx", _svgPath("AvarageVerts"), size=self.__IS)
        cpyWght_Btn = svgButton("copy vtx", _svgPath("copy2Mult"), size=self.__IS)
        swchVtx_Btn = svgButton("switch vtx", _svgPath("vert2vert"), size=self.__IS)
        BoneLbl_Btn = svgButton("label joints", _svgPath("jointLabel"), size=self.__IS)
        shellUn_btn = svgButton("unify shells", _svgPath("shellUnify"), size=self.__IS)
        trsfrSK_Btn = svgButton("skin to skin", _svgPath("skinToSkin"), size=self.__IS)
        trsfrPS_Btn = svgButton("skin to pose", _svgPath("skinToPose"), size=self.__IS)
        nghbors_Btn = svgButton("neighbors", _svgPath("neighbors"), size=self.__IS)
        smthBrs_Btn = svgButton("smooth Brush", _svgPath("brush"), size=self.__IS)
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

        maxL = nullHBoxLayout()
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(self.__IS, self.__IS + 10)
        self._maxSpin.setMinimum(1)
        self._maxSpin.setValue(4)
        vtexMax_Btn = svgButton("force max infl.", _svgPath("Empty"), size=self.__IS)
        frzBone_Btn = svgButton("freeze joints", _svgPath("FreezeJoint"), size=self.__IS)
        for w in [self._maxSpin, vtexMax_Btn]:
            maxL.addWidget(w)
        vtxOver_Btn = svgButton("sel infl. > max", _svgPath("vertOver"), size=self.__IS)

        growL = nullHBoxLayout()
        storsel_Btn = svgButton("store internal", _svgPath("Empty"), size=self.__IS)
        self.shrinks_Btn = svgButton("-", _svgPath("Empty"), size=self.__IS)
        self.growsel_Btn = svgButton("+", _svgPath("Empty"), size=self.__IS)
        for i, w in enumerate([self.shrinks_Btn, storsel_Btn, self.growsel_Btn]):
            if i != 1:
                w.setEnabled(False)
                w.setMaximumWidth(30)
                w.setStyleSheet("QPushButton { text-align: center; }")
            growL.addWidget(w)

        self.__buttons = [AvgWght_Btn, cpyWght_Btn, swchVtx_Btn, BoneLbl_Btn, shellUn_btn, trsfrSK_Btn,
                          trsfrPS_Btn, nghbors_Btn, smthBrs_Btn, toJoint_Btn, frzBone_Btn, rstPose_Btn, cutMesh_Btn, SurfPin_Btn,
                          copy2bn_Btn, b2bSwch_Btn, showInf_Btn, delBone_Btn, addinfl_Btn, unifyBn_Btn,
                          seltInf_Btn, sepMesh_Btn, onlySel_Btn, infMesh_Btn, maxL, vtxOver_Btn, BindFix_Btn,  growL ]

        _rc = int(len(self.__buttons)*.5)
        for index, btn in enumerate(self.__buttons):
            row = index / _rc
            if isinstance(btn, QLayout):
                g.addLayout(btn, index - (row * _rc), row)
                continue
            g.addWidget(btn, index - (row * _rc), row)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

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
        onlySel_Btn.checks["invert"].stateChanged.connect(partial(self._pruneOption, onlySel_Btn))

        AvgWght_Btn.clicked.connect(partial(self._AvgWght_func, AvgWght_Btn))
        cpyWght_Btn.clicked.connect(partial(interface.copyVtx, self.progressBar))
        swchVtx_Btn.clicked.connect(partial(interface.switchVtx, self.progressBar))
        BoneLbl_Btn.clicked.connect(partial(interface.labelJoints, False, self.progressBar))
        shellUn_btn.clicked.connect(partial(interface.unifyShells, self.progressBar))
        trsfrSK_Btn.clicked.connect(partial(self._trsfrSK_func, trsfrSK_Btn, False))
        trsfrPS_Btn.clicked.connect(partial(self._trsfrSK_func, trsfrPS_Btn, True))
        nghbors_Btn.clicked.connect(partial(self._nghbors_func, nghbors_Btn))
        smthBrs_Btn.clicked.connect(interface.paintSmoothBrush)
        toJoint_Btn.clicked.connect(partial(self._convertToJoint_func, toJoint_Btn))
        rstPose_Btn.clicked.connect(partial(interface.resetPose, self.progressBar))
        cutMesh_Btn.clicked.connect(partial(self._cutMesh_func, cutMesh_Btn))
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
        self.shrinks_Btn.clicked.connect(self._shrinks_func)
        self.growsel_Btn.clicked.connect(self._growsel_func)
        BindFix_Btn.clicked.connect(partial(self._bindFix_func))

        if _DEBUG:
            for chk in [smthBrs_Btn]:
                chk.setStyleSheet("background-color: red")

    # -- checkbox modifiers    
    def _pruneOption(self, btn, value):
        btn.setText("prune %s infl."%["excluded, selected"][btn.checks["invert"].isChecked()])

    # -- buttons with extra functionality
    def _AvgWght_func(self, sender):
        interface.avgVtx(sender.checks["use distance"].isChecked(), self.BezierGraph, self.progressBar)

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

    def _bindFix_func(self, *args):
        interface.prebindFixer(sender.checks["model only"].isChecked(), sender.checks["in Pose"].isChecked(), self.progressBar)
