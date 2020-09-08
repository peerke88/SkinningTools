from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class VertAndBoneFunction(QWidget):
    def __init__(self, inGraph = None, inProgressBar = None, parent = None):
        super(VertAndBoneFunction, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__iconSize = 40

        self.progressBar = inProgressBar
        self.BezierGraph = inGraph
        self.borderSelection = interface.NeighborSelection()
        self.__addVertNBoneFunc()

    def __addVertNBoneFunc(self):
        g = nullGridLayout()
        self.layout().addLayout(g)

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
        rstPose_Btn = svgButton("recalc bind", os.path.join(_DIR, "Icons/resetJoint.svg"), size=self.__iconSize)
        cutMesh_Btn = svgButton("create proxy", os.path.join(_DIR, "Icons/proxy.svg"), size=self.__iconSize)

        copy2bn_Btn = svgButton("move bone infl.", os.path.join(_DIR, "Icons/Bone2Bone.svg"), size=self.__iconSize)
        b2bSwch_Btn = svgButton("swap bone infl.", os.path.join(_DIR, "Icons/Bone2Boneswitch.svg"), size=self.__iconSize)
        showInf_Btn = svgButton("influenced vtx", os.path.join(_DIR, "Icons/selectinfl.svg"), size=self.__iconSize)
        delBone_Btn = svgButton("remove joint", os.path.join(_DIR, "Icons/jointDelete.svg"), size=self.__iconSize)
        addinfl_Btn = svgButton("add joint", os.path.join(_DIR, "Icons/addJoint.svg"), size=self.__iconSize)
        unifyBn_Btn = svgButton("unify bind map", os.path.join(_DIR, "Icons/unify.svg"), size=self.__iconSize)
        seltInf_Btn = svgButton("attached joints", os.path.join(_DIR, "Icons/selectJnts.svg"), size=self.__iconSize)
        sepMesh_Btn = svgButton("seperate skinMesh", os.path.join(_DIR, "Icons/seperate.svg"), size=self.__iconSize)
        onlySel_Btn = svgButton("prune excluded infl.", os.path.join(_DIR, "Icons/onlySel.svg"), size=self.__iconSize)
        infMesh_Btn = svgButton("influenced meshes", os.path.join(_DIR, "Icons/infMesh.svg"), size=self.__iconSize)

        maxL = nullHBoxLayout()
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(self.__iconSize, self.__iconSize+10)
        vtexMax_Btn = svgButton("force max infl.", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        frzBone_Btn = svgButton("freeze joints", os.path.join(_DIR, "Icons/FreezeJoint.svg"), size=self.__iconSize)
        for w in [self._maxSpin, vtexMax_Btn]:
            maxL.addWidget(w)
        vtxOver_Btn = svgButton("sel infl. > max", os.path.join(_DIR, "Icons/vertOver.svg"), size=self.__iconSize)

        growL = nullHBoxLayout()
        storsel_Btn = svgButton("store internal", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        self.shrinks_Btn = svgButton("-", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        self.growsel_Btn = svgButton("+", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        for i, w in enumerate([self.shrinks_Btn, storsel_Btn, self.growsel_Btn]):
            if i != 1:
                w.setEnabled(False)
                w.setMaximumWidth(30)
                w.setStyleSheet("QPushButton { text-align: center; }")
            growL.addWidget(w)

        self.__buttons = [AvgWght_Btn, cpyWght_Btn, swchVtx_Btn, BoneLbl_Btn, shellUn_btn, trsfrSK_Btn, 
                         trsfrPS_Btn, nghbors_Btn, nghbrsP_Btn, smthVtx_Btn, smthBrs_Btn, toJoint_Btn, rstPose_Btn, 
                         cutMesh_Btn, copy2bn_Btn, b2bSwch_Btn, showInf_Btn, delBone_Btn, addinfl_Btn, unifyBn_Btn, 
                         seltInf_Btn, sepMesh_Btn, onlySel_Btn, infMesh_Btn, maxL, vtxOver_Btn, frzBone_Btn, growL]
        for index, btn in enumerate(self.__buttons):
            row = index / 14
            if isinstance(btn, QLayout):
                g.addLayout(btn, index - (row * 14), row)
                continue
            g.addWidget(btn, index - (row * 14), row)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

        addChecks(self, AvgWght_Btn, ["use distance"] )
        addChecks(self, trsfrSK_Btn, ["smooth", "uvSpace"] )
        addChecks(self, trsfrPS_Btn, ["smooth", "uvSpace"] )
        addChecks(self, nghbors_Btn, ["full"] )
        addChecks(self, nghbrsP_Btn, ["full", "growing"] )
        addChecks(self, cutMesh_Btn, ["internal", "fast"] )
        addChecks(self, delBone_Btn, ["use parent", "delete", "fast"] )
        addChecks(self, unifyBn_Btn, ["query"] )
        addChecks(self, onlySel_Btn, ["invert"] )
        onlySel_Btn.checks["invert"].stateChanged.connect(partial(self._pruneOption, onlySel_Btn))
        
        AvgWght_Btn.clicked.connect( self._AvgWght_func )
        cpyWght_Btn.clicked.connect( partial( interface.copyVtx, self.progressBar ) )
        swchVtx_Btn.clicked.connect( partial( interface.switchVtx, self.progressBar ) )
        BoneLbl_Btn.clicked.connect( partial( interface.labelJoints, self.progressBar ) )
        shellUn_btn.clicked.connect( partial( interface.unifyShells, self.progressBar ) )
        trsfrSK_Btn.clicked.connect( partial( self._trsfrSK_func, trsfrSK_Btn, False) )
        trsfrPS_Btn.clicked.connect( partial( self._trsfrSK_func, trsfrPS_Btn, True) )
        nghbors_Btn.clicked.connect( partial( self._nghbors_func, nghbors_Btn, False ) )
        nghbrsP_Btn.clicked.connect( partial( self._nghbors_func, nghbrsP_Btn, True ) )
        smthVtx_Btn.clicked.connect( partial( interface.smooth, self.progressBar ) )
        smthBrs_Btn.clicked.connect( interface.paintSmoothBrush )
        toJoint_Btn.clicked.connect( partial( interface.convertToJoint, self.progressBar ) )
        rstPose_Btn.clicked.connect( partial( interface.resetPose, self.progressBar ) )
        cutMesh_Btn.clicked.connect( partial( self._cutMesh_func, self.progressBar ))

        copy2bn_Btn.clicked.connect( partial( interface.moveBones, False,  self.progressBar ) )
        b2bSwch_Btn.clicked.connect( partial( interface.moveBones, True, self.progressBar ) )
        showInf_Btn.clicked.connect( partial( interface.showInfVerts, self.progressBar ) )
        delBone_Btn.clicked.connect( self._delBone_func)
        addinfl_Btn.clicked.connect( partial( interface.addNewJoint, self.progressBar ) )
        unifyBn_Btn.clicked.connect( self._unifyBn_func )
        seltInf_Btn.clicked.connect( partial( interface.selectJoints, self.progressBar ) )
        sepMesh_Btn.clicked.connect( partial( interface.seperateSkinned, self.progressBar ) )
        onlySel_Btn.clicked.connect( self._pruneSel_func )
        infMesh_Btn.clicked.connect( partial( interface.getMeshFromJoints, self.progressBar ) )
        vtexMax_Btn.clicked.connect( partial( self._vtexMax_func, False ) )
        vtxOver_Btn.clicked.connect( partial( self._vtexMax_func, True ) )
        frzBone_Btn.clicked.connect( partial( interface.freezeJoint, self.progressBar ) )
        storsel_Btn.clicked.connect( self._storesel_func)
        self.shrinks_Btn.clicked.connect( self._shrinks_func)
        self.growsel_Btn.clicked.connect( self._growsel_func)

    # -- buttons with extra functionality
    def _pruneOption(self, btn, value):
        btn.setText("prune excluded infl.")
        if btn.checks["invert"].isChecked():
            btn.setText("prune selected infl.")

    def _AvgWght_func(self):
        print self.sender()
        interface.avgVtx(self.sender().checks["use distance"].isChecked(), self.BezierGraph, self.progressBar )

    def _trsfrSK_func(self, sender,  inPlace):
        chkbxs = sender.checks
        interface.copySkin(inPlace, chkbxs["smooth"].isChecked(), chkbxs["uvSpace"].isChecked(), self.progressBar)

    def _nghbors_func(self, sender, both):
        growing = False
        if "growing" in sender.checks.keys():
            growing = sender.checks["growing"].isChecked()
        interface.neighbors(both, growing, sender.checks["full"].isChecked(), self.progressBar)

    def _delBone_func(self):
        chkbxs = self.sender().checks
        interface.removeJoint(chkbxs["use parent"].isChecked(), chkbxs["delete"].isChecked(), chkbxs["fast"].isChecked(), self.progressBar)
        
    def _unifyBn_func(self):
        interface.unifySkeletons( self.sender().checks["query"].isChecked(), self.progressBar)

    def _vtexMax_func(self, query):
        if query:
            interface.getMaxInfl(self._maxSpin.value(), self.progressBar)
            return
        interface.setMaxInfl(self._maxSpin.value(), self.progressBar)

    def _cutMesh_func(self):
        chkbxs = self.sender().checks

    def _pruneSel_func(self):
        inverse = self.sender().checks["invert"].isChecked()
        interface.keepOnlyJoints(inverse)

    def _storesel_func(self, *args):
        self.borderSelection.storeSel()
        self.shrinks_Btn.setEnabled(False)
        self.growsel_Btn.setEnabled(True)

    def _shrinks_func(self, *args):
        self.borderSelection.shrink()
        if self.borderSelection.getBorderIndex() == 0:
            self.shrinks_Btn.setEnabled(False)

    def _growsel_func(self, *args):
        self.shrinks_Btn.setEnabled(True)
        if self.borderSelection.getBorderIndex() == 0:
            self.shrinks_Btn.setEnabled(False)
        self.borderSelection.grow()
        