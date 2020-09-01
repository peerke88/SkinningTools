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
        self._maxSpin = QSpinBox()
        self._maxSpin.setFixedSize(self.__iconSize, self.__iconSize+10)
        vtexMax_Btn = svgButton("force max infl.", os.path.join(_DIR, "Icons/Empty.svg"), size=self.__iconSize)
        frzBone_Btn = svgButton("freeze joints", os.path.join(_DIR, "Icons/FreezeJoint.svg"), size=self.__iconSize)

        for w in [self._maxSpin, vtexMax_Btn]:
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

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

        addChecks(self, AvgWght_Btn, ["use distance"] )
        addChecks(self, trsfrSK_Btn, ["smooth", "uvSpace"] )
        addChecks(self, trsfrPS_Btn, ["smooth", "uvSpace"] )
        addChecks(self, nghbors_Btn, ["full"] )
        addChecks(self, nghbrsP_Btn, ["full"] )
        addChecks(self, delBone_Btn, ["use parent", "delete", "fast"] )
        addChecks(self, unifyBn_Btn, ["query"] )

        AvgWght_Btn.clicked.connect( self._AvgWght_func )
        cpyWght_Btn.clicked.connect( partial( interface.copyVtx, self.progressBar ) )
        swchVtx_Btn.clicked.connect( partial( interface.switchVtx, self.progressBar ) )
        BoneLbl_Btn.clicked.connect( partial( interface.labelJoints, self.progressBar ) )
        shellUn_btn.clicked.connect( partial( interface.unifyShells, self.progressBar ) )
        trsfrSK_Btn.clicked.connect( partial( self._trsfrSK_func, False) )
        trsfrPS_Btn.clicked.connect( partial( self._trsfrSK_func, True) )
        nghbors_Btn.clicked.connect( partial( self._nghbors_func, False, self.progressBar ) )
        nghbrsP_Btn.clicked.connect( partial( self._nghbors_func, True, self.progressBar ) )
        smthVtx_Btn.clicked.connect( partial( interface.smooth, self.progressBar ) )
        smthBrs_Btn.clicked.connect( interface.paintSmoothBrush )
        toJoint_Btn.clicked.connect( partial( interface.convertToJoint, self.progressBar ) )
        rstPose_Btn.clicked.connect( partial( interface.resetPose, self.progressBar ) )

        copy2bn_Btn.clicked.connect( partial( interface.moveBones, False,  self.progressBar ) )
        b2bSwch_Btn.clicked.connect( partial( interface.moveBones, True, self.progressBar ) )
        showInf_Btn.clicked.connect( partial( interface.showInfVerts, self.progressBar ) )
        delBone_Btn.clicked.connect( self._delBone_func)
        addinfl_Btn.clicked.connect( partial( interface.addNewJoint, self.progressBar ) )
        unifyBn_Btn.clicked.connect( self._unifyBn_func )
        seltInf_Btn.clicked.connect( partial( interface.selectJoints, self.progressBar ) )
        sepMesh_Btn.clicked.connect( partial( interface.seperateSkinned, self.progressBar ) )
        onlySel_Btn.clicked.connect( partial( interface.getJointInfVers, self.progressBar ) )
        infMesh_Btn.clicked.connect( partial( interface.getMeshFromJoints, self.progressBar ) )
        vtexMax_Btn.clicked.connect( partial( self.vtexMax_func, False ) )
        vtxOver_Btn.clicked.connect( partial( self.vtexMax_func, True ) )
        frzBone_Btn.clicked.connect( partial( interface.freezeJoint, self.progressBar ) )

    # -- buttons with extra functionality
    def _AvgWght_func(self):
        interface.avgVtx(self.sender().checks["use distance"].isChecked(), self.BezierGraph, self.progressBar )

    def _trsfrSK_func(self, inPlace):
        chkbxs = self.sender().checks
        interface.copySkin(inPlace, chkbxs["smooth"].isChecked(), chkbxs["uvSpace"].isChecked(), self.progressBar)

    def _nghbors_func(self, both):
        interface.neighbors(both, self.sender().checks["full"].isChecked(), self.progressBar)

    def _delBone_func(self):
        chkbxs = self.sender().checks
        interface.removeJoint(chkbxs["use parent"].isChecked(), chkbxs["delete"].isChecked(), chkbxs["fast"].isChecked(), self.progressBar)
        
    def _unifyBn_func(self):
        interface.unifySkeletons( self.sender().checks["query"].isChecked(), self.progressBar)

    def vtexMax_func(self, query):
        if query:
            interface.getMaxInfl(self._maxSpin.value(), self.progressBar)
            return
        interface.setMaxInfl(self._maxSpin.value(), self.progressBar)
