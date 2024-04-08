from SkinningTools.Maya import api, interface
from SkinningTools.Maya.interface import getInterfaceDir
from SkinningTools.Maya.tools import shared
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
from maya import cmds
from maya import mel
import os

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()
_CTX = "artUserPaintContext"  # "AverageWghtCtx"


def pathToSmoothBrushPlugin():
    version = api.getMayaVersion()
    extension = api.getPluginSuffix()
    return getInterfaceDir() + "/plugin/smoothBrushRodCpp/lib/maya%s/release/smooth_brush_maya%s" % (version, extension)
    # return getInterfaceDir()+"/plugin/smoothBrushRodCpp/lib/maya%s/debug/smooth_brush_maya_debug%s"%(version,extension)


dec_loadSmoothBrush = shared.dec_loadPlugin(pathToSmoothBrushPlugin())


class BrushMode:
    SMOOTH = 0
    RELAX = 1
    UNDEF = 2


def buildSmoothBrushCommand(context, skinClusterName, radiusExtraLinks, brushMode):
    cmd = "SBR_brush "
    if brushMode == BrushMode.SMOOTH:
        cmd += "-smooth " + skinClusterName + " "
    else:
        cmd += "-relaxation " + skinClusterName + " "

    cmd += "-brushContext " + context + " "
    if radiusExtraLinks > 0.0:
        cmd += "-enableExtraLinks " + str(radiusExtraLinks) + " "

    # the flag -brushMask must be last
    # (arguments will be defined when called back from artUserPaintCtx)
    cmd += "-brushMask "
    return cmd


def getSelectedSKinCLuster():
    shapes = api.selectedSkinnedShapes()
    if len(shapes) < 1:
        return ""
    dag = shared.getDagpath(shapes[0])
    skinCluster = shared.skinCluster(dag.fullPathName())
    return skinCluster


def updateBrushCommand(context, skinCluster, radiusExtraLinks, brushMode):
    brushCommand = buildSmoothBrushCommand(context,
                                           skinCluster,
                                           radiusExtraLinks,
                                           brushMode)

    cmds.artUserPaintCtx(context, edit=True, setArrayValueCommand=brushCommand)


'''
@param radiusExtraLinks: if 0.0 disabled
'''


@shared.dec_repeat
@dec_loadSmoothBrush
def rodPaintSmoothBrush(radiusExtraLinks=0.0, brushMode=BrushMode.SMOOTH):
    print("ROD BRUSHES")
    _brush_init = "rodSmoothBrushInit"

    skinCluster = getSelectedSKinCLuster()
    if len(skinCluster) == 0:
        print("Select a skinned mesh first")
    print(skinCluster)

    import maya.mel as mel
    mel.eval("global proc rodSmoothBrushInit(string $name){ return; }")

    if not cmds.artUserPaintCtx(_CTX, query=True, exists=True):
        cmds.artUserPaintCtx(_CTX)

    cmds.artUserPaintCtx(_CTX, edit=True, ic=_brush_init,
                         # svc=_brush_update,
                         whichTool="userPaint", fullpaths=True,
                         outwhilepaint=True, brushfeedback=False, selectedattroper="additive",
                         fc="", gvc="", gsc="", gac="", tcc="")

    updateBrushCommand(_CTX, skinCluster, radiusExtraLinks, brushMode)

    cmds.setToolTo(_CTX)


class SkinBrushes(QWidget):

    def __init__(self, parent=None):
        super(SkinBrushes, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 40

        self.__addBrushFunc()

    def __addBrushFunc(self):

        mainVertLayout = nullVBoxLayout()
        # mainVertLayout.setMargin(5)
        self.layout().addLayout(mainVertLayout)

        def _svgPath(svg):
            return os.path.join(_DIR, "Icons/%s.svg" % svg)

        # Radio buttons: Smooth|Relax
        hLayoutBrushType = nullHBoxLayout()
        self.smoothBrush_radio = QRadioButton("Smooth", self)
        self.relaxBrush_radio = QRadioButton("Relax", self)
        self.smoothBrush_radio.setChecked(True)
        self.smoothBrush_radio.clicked.connect(self.changeBrushType)
        self.relaxBrush_radio.clicked.connect(self.changeBrushType)
        hLayoutBrushType.addWidget(self.smoothBrush_radio)
        hLayoutBrushType.addWidget(self.relaxBrush_radio)
        mainVertLayout.addLayout(hLayoutBrushType)

        # Init/Toggle Brush button
        hLayoutButtons = nullVBoxLayout()
        bindPose_Btn = QPushButton("Init Bind Pose")
        bindPose_Btn.clicked.connect(self.toggleBindPoseButton)
        smthBrs_Btn = svgButton("Toggle Brush", _svgPath("brush"), size=self.__IS)
        smthBrs_Btn.clicked.connect(self.toggleBrushButton)
        hLayoutButtons.addWidget(bindPose_Btn)
        hLayoutButtons.addWidget(smthBrs_Btn)
        mainVertLayout.addLayout(hLayoutButtons)

        # Parameters
        hLayoutParameters = nullHBoxLayout()
        self.volume_chckBx = QCheckBox("Volume", self)
        self.radius_dSpinBx = QDoubleSpinBox(self)
        self.radius_dSpinBx.setMinimum(0.0)
        self.radius_dSpinBx.setSingleStep(0.1)
        self.radius_dSpinBx.valueChanged.connect(self.radiusValueChanged)
        hLayoutParameters.addWidget(self.volume_chckBx)
        hLayoutParameters.addWidget(self.radius_dSpinBx)
        hLayoutParameters.addItem(QSpacerItem(2, 4, QSizePolicy.Expanding, QSizePolicy.Minimum))
        mainVertLayout.addLayout(hLayoutParameters)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

        if False:  # _DEBUG:
            for chk in [smthBrs_Btn]:
                chk.setStyleSheet("background-color: red")

    def getRadius(self):
        radius = 0.0
        if self.volume_chckBx.isEnabled():
            radius = self.radius_dSpinBx.value()
        return radius

    def getBrushMode(self):
        if self.smoothBrush_radio.isChecked():
            return BrushMode.SMOOTH
        elif self.relaxBrush_radio.isChecked():
            return BrushMode.RELAX
        else:
            return BrushMode.UNDEF

    def updateBrush(self):
        skinCluster = getSelectedSKinCLuster()
        if len(skinCluster) > 0:
            updateBrushCommand(_CTX, skinCluster, self.getRadius(), self.getBrushMode())

    # -- buttons with extra functionality
    @dec_loadSmoothBrush
    def toggleBrushButton(self):
        rodPaintSmoothBrush(self.getRadius(), self.getBrushMode())

    @dec_loadSmoothBrush
    def toggleBindPoseButton(self):
        skinCluster = getSelectedSKinCLuster()
        if len(skinCluster) == 0:
            print("Select a skinned mesh first")
        print(skinCluster)
        mel.eval('SBR_cache_manager -buildCache "' + skinCluster + '"')

    def radiusValueChanged(self, value):
        self.updateBrush()

    def changeBrushType(self):
        self.updateBrush()
