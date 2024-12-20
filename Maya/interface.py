# -*- coding: utf-8 -*-

# @note:
#  this file will represent an interface between the ui and the actual commands
# this is where all the selection gets logged and the right arguments get piped through
from maya import cmds, OpenMaya as OldOpenMaya, OpenMayaUI as OldOpenMayaUI
from SkinningTools.Maya.mayaWidget import *
from SkinningTools.Maya.api import *
from SkinningTools.Maya.tools import shared, joints, mesh, skinCluster, mathUtils, holdFetch
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.dialogs.jointLabel import JointLabel
from SkinningTools.UI.dialogs.jointName import JointName
from random import randint
from functools import partial
import os, platform, sys

cmds.selectPref(tso=True)


def getInterfaceDir():
    return os.path.dirname(os.path.abspath(__file__))


def showToolTip(inBool):
    cmds.help(popupMode=inBool)


def getAllJoints(useSelection=False):
    return cmds.ls(sl=useSelection, type="joint")


@shared.dec_repeat
def doSkinPercent(bone, value, operation):
    skinCluster.doSkinPercent(bone, value, operation)

# ensure we get ordered selection and all in long names


def getSelection():
    return cmds.ls(os=1, l=1, fl=1)


def doSelect(input, replace=True):
    if input == '':
        cmds.select(cl=1)
        return
    cmds.select(input, r=replace)


def getCurrentMeshJoints():
    selection = getSelection()
    if len(selection) > 1:
        selection = selection[0]
    if "." in selection:
        selection = selection.split('.')[0]
    return joints.getInfluencingJoints(selection)


def setSmoothAware(input):
    cmds.softSelect(e=True, softSelectFalloff=input)


def getSmoothAware():
    return cmds.softSelect(q=True, softSelectFalloff=True)


def skinnedJointColors():
    return [[161, 106, 48], [159, 161, 48], [104, 161, 48],
            [48, 161, 93], [48, 161, 161], [48, 103, 161],
            [111, 48, 161], [161, 48, 106]]


def setJointLocked(inJoint, inValue):
    cmds.setAttr("%s.liw" % inJoint, inValue)


def getLockData(inObject):
    inJoints = joints.getInfluencingJoints(inObject)
    locked = []
    for joint in inJoints:
        if cmds.getAttr("%s.liw" % joint):
            locked.append(joint)
    return locked


def forceLoadPlugin(inPlugin):
    if not inPlugin.endswith(".py"):
        inPlugin = "%s.py" % inPlugin
    pluginPath = os.path.join(getInterfaceDir(), "plugin/%s" % inPlugin)
    loaded = cmds.pluginInfo(pluginPath, q=True, loaded=True)
    registered = cmds.pluginInfo(pluginPath, q=True, registered=True)

    if not registered or not loaded:
        cmds.loadPlugin(pluginPath)

# --- maya menus ---


def mirrorSkinOptions():
    cmds.optionVar(stringValue=("mirrorSkinAxis", "YZ"))
    cmds.optionVar(intValue=("mirrorSkinWeightsSurfaceAssociationOption", 1))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption1", 3))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption2", 2))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption3", 1))
    cmds.optionVar(intValue=("mirrorSkinNormalize", 1))
    cmds.MirrorSkinWeightsOptions()


def copySkinWeightsOptions():
    cmds.optionVar(intValue=("copySkinWeightsSurfaceAssociationOption", 1))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption1", 4))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption2", 4))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption3", 6))
    cmds.optionVar(intValue=("copySkinWeightsNormalize", 1))
    cmds.CopySkinWeightsOptions()


def uniteSkinned():
    selection = getSelection()
    cmds.polyUniteSkinned(selection, ch=0, mergeUVSets=1)


def removeUnused(progressBar=None):
    selection = getSelection()
    joints.removeUnusedInfluences(selection, progressBar)


def resetToBindPoseobject(progressBar=None):
    selection = getSelection()
    joints.resetToBindPoseobject(selection, progressBar)

# --- dcc ---


def dccToolButtons(progressBar=None):
    from SkinningTools.UI.utils import buttonsToAttach

    mb01 = buttonsToAttach('Smooth Bind', cmds.SmoothBindSkinOptions)
    mb02 = buttonsToAttach('Rigid Bind', cmds.RigidBindSkinOptions)
    mb03 = buttonsToAttach('Detach Skin', cmds.DetachSkinOptions)
    mb04 = buttonsToAttach('Paint Skin Weights', cmds.ArtPaintSkinWeightsToolOptions)
    mb05 = buttonsToAttach('Mirror Skin Weights', mirrorSkinOptions)
    mb06 = buttonsToAttach('Copy Skin Weights', copySkinWeightsOptions)
    mb07 = buttonsToAttach('Prune Weights', cmds.PruneSmallWeightsOptions)
    mb08 = buttonsToAttach('Combine skinned mesh', uniteSkinned)
    mb09 = buttonsToAttach('Remove unused influences', partial(removeUnused, progressBar))
    mb10 = buttonsToAttach('goto bind-pose', partial(resetToBindPoseobject, progressBar)) #  (use preBindMatrix data)

    return [mb01, mb02, mb03, mb04, mb05, mb06, mb07, mb08, mb09, mb10]


# --- tools ---
@shared.dec_repeat
def avgVtx(useDistance=True, weightAverageWindow=None, progressBar=None):
    selection = getSelection()
    result = skinCluster.AvarageVertex(selection, useDistance, weightAverageWindow, progressBar)
    doSelect(selection, True)
    return result


@shared.dec_repeat
def copyVtx(progressBar=None):
    selection = getSelection()
    result = skinCluster.Copy2MultVertex(selection, selection[-1], progressBar)
    return result


@shared.dec_repeat
def switchVtx(progressBar=None):
    selection = getSelection()
    result = skinCluster.switchVertexWeight(selection[0], selection[1], progressBar)
    return result


@shared.dec_repeat
def labelJoints(selectionBased=False, doCheck=True, progressBar=None):
    jnts = cmds.ls(type="joint")
    jntAmount = len(jnts)
    if doCheck:
        _reLabel = False
        for _ in range(5):
            if cmds.getAttr(jnts[randint(0, jntAmount - 1)] + '.type') == 0:
                _reLabel = True
        if not _reLabel:
            return True
    dialog = JointLabel(title="label selected joints" if selectionBased else "label joints")
    dialog.exec_()
    result = joints.autoLabelJoints(dialog.L_txt.text(), dialog.R_txt.text(), selectionBased, progressBar)
    return result


def hold():
    holdFetch.hold(True)


def fetch():
    holdFetch.fetch()


def createPolySkeleton(radius=1):
    dlg = QDialog()
    dlg.setLayout(nullVBoxLayout())
    hlay = nullVBoxLayout()
    hlay.addWidget(QLabel("radius value: "))
    spin = QDoubleSpinBox()
    spin.setValue(1)
    hlay.addWidget(spin)
    dlg.layout().addLayout(hlay)
    btn = pushButton("build poly skeleton")
    dlg.layout().addWidget(btn)
    btn.clicked.connect(dlg.accept)
    dlg.exec_()

    if dlg.result() == 0:
        return None

    mesh.polySkeleton(spin.value())
    return True


@shared.dec_repeat
def unifyShells(progressBar=None):
    selection = getSelection()
    result = skinCluster.hardSkinSelectionShells(selection, progressBar)
    return result


@shared.dec_repeat
def copySkin(inplace, smooth, uvSpace, progressBar=None):
    labelJoints()
    selection = getSelection()
    result = skinCluster.transferSkinning(selection[0], selection[1:], inplace, smooth, uvSpace, progressBar)
    return result


@shared.dec_repeat
def neighbors(both, growing, full, maxinf, progressBar=None):
    selection = getSelection()
    result = skinCluster.smoothAndSmoothNeighbours(selection, both, growing, full, maxinf, progressBar)
    return result


@shared.dec_repeat
@shared.dec_loadPlugin(os.path.join(getInterfaceDir(), "plugin/averageWeightPlugin.py"))
def smooth(progressBar=None):
    selection = getSelection()
    result = skinCluster.neighbourAverage(selection, progressBar=progressBar)
    return result


@shared.dec_repeat
def convertToJoint(inName=None, progressBar=None):
    if inName == True:
        dialog = JointName()
        dialog.exec_()
        inName = dialog.txt.text()

    if inName in ['', False, None]:
        inName = None

    selection = getSelection()
    if "." in selection[0]:
        result = joints.convertVerticesToJoint(selection, inName, progressBar)
        return result

    result = joints.convertClusterToJoint(selection, inName, progressBar)
    return result


@shared.dec_repeat
def resetPose(resetBindPoseNode=True, progressBar=None):
    selection = getSelection()
    jnts = []
    meshes = []
    results = []
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue
        meshes.append(obj)
    for mesh in meshes:
        skinClusterName = shared.skinCluster(mesh, True)
        if not skinClusterName:
            continue
        if resetBindPoseNode:            
            _res = joints.resetBindPoseNodeSkinCluster(skinClusterName, progressBar)
        else:
            _res = joints.resetSkinnedJoints(jnts, skinClusterName, progressBar)
        results.append(_res)
    return results


@shared.dec_repeat
def moveBones(swap=False, progressBar=None):
    selection = getSelection()
    jnts = []
    mesh = ''
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue
        mesh = obj

    if len(jnts) != 2:
        print("Please select exactly two joints as first and second selection.")
        return

    if mesh == '':
        print("Please select one mesh as third selection.")
        return

    if swap:
        result = joints.BoneSwitch(jnts[0], jnts[1], mesh, progressBar)
        return result

    result = joints.BoneMove(jnts[0], jnts[1], mesh, progressBar)
    return result


@shared.dec_repeat
def showInfVerts(progressBar=None):
    selection = getSelection()
    jnts = []
    mesh = ''
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue
        mesh = obj

    result = joints.ShowInfluencedVerts(mesh, jnts, progressBar)
    doSelect(result, True)
    return result


@shared.dec_repeat
def removeJoint(useParent=True, delete=True, fast=False, progressBar=None):
    selection = getSelection()
    jnts = []
    mesh = []
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue
        mesh.append(obj)

    result = joints.removeJoints(mesh, jnts, useParent, delete, fast, progressBar)
    return result


@shared.dec_repeat
def addNewJoint(progressBar=None):
    selection = getSelection()
    jnts = []
    mesh = ''
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue
        mesh = obj

    result = joints.addCleanJoint(jnts, mesh, progressBar)
    return result


@shared.dec_repeat
def unifySkeletons(query=False, progressBar=None):
    selection = getSelection()
    result = joints.comparejointInfluences(selection, query, progressBar)
    if query:
        cmds.select(result, r=1)
    return result


@shared.dec_repeat
def selectJoints(progressBar=None):
    selection = getSelection()
    result = joints.getInfluencingJoints(selection)
    cmds.select(result, r=1)
    return result


@shared.dec_repeat
def seperateSkinned(progressBar=None):
    selection = getSelection()
    if "." in selection[0]:
        result = skinCluster.extractSkinnedShells(selection, progressBar)
    else:
        result = skinCluster.seperateSkinnedObject(selection[0], progressBar)
    return result


@shared.dec_repeat
def keepOnlyJoints(invert=False, progressBar=None):
    selection = getSelection()
    jnts = []
    for obj in selection:
        if cmds.objectType(obj) == "joint":
            jnts.append(obj)
            continue

    result = skinCluster.keepOnlySelectedInfluences(selection, jnts, invert, progressBar)
    return result


@shared.dec_repeat
def getMeshFromJoints(progressBar=None):
    selection = getSelection()
    result = joints.getMeshesInfluencedByJoint(selection, progressBar)
    cmds.select(result, r=1)
    return result


@shared.dec_repeat
def setMaxInfl(amountInfluences=8, progressBar=None):
    selection = getSelection()
    result = skinCluster.setMaxJointInfluences(selection[0], amountInfluences, progressBar)
    return result


@shared.dec_repeat
def getMaxInfl(amountInfluences=8, progressBar=None):
    selection = getSelection()
    result = skinCluster.getVertOverMaxInfluence(selection[0], amountInfluences, progressBar)
    cmds.select(result[0], r=1)
    return result


@shared.dec_repeat
def freezeJoint(progressBar=None):
    selection = getSelection()
    result = joints.freezeSkinnedJoints(selection, progressBar=progressBar)
    return result


@shared.dec_repeat
@shared.dec_loadPlugin(os.path.join(getInterfaceDir(), "plugin/averageWeightPlugin.py"))
def paintSmoothBrush():
    _ctx = "AverageWghtCtx"
    _brush_init = "paintAverageWghtCtxInitialize"
    _brush_update = "paintAverageWghtCtxUpdate"

    if not cmds.artUserPaintCtx(_ctx, query=True, exists=True):
        cmds.artUserPaintCtx(_ctx)

    cmds.artUserPaintCtx(_ctx, edit=True, ic=_brush_init,
                         svc=_brush_update, whichTool="userPaint", fullpaths=True,
                         outwhilepaint=True, brushfeedback=False, selectedattroper="additive")

    cmds.setToolTo(_ctx)


@shared.dec_repeat
def hammerVerts(progressBar=None):
    selection = getSelection()
    result = skinCluster.hammerVerts(selection, False, progressBar)
    return result


def getNeightbors(inComps):
    objType = cmds.objectType(inComps[0])
    if objType == 'mesh':
        convertedFaces = cmds.polyListComponentConversion(inComps, tf=True)
        return shared.convertToVertexList(convertedFaces)

    if objType == "nurbsSurface":
        cmds.select(cl=1)
        cmds.nurbsSelect(inComps, gs=1)
        return cmds.ls(sl=1, fl=1)

    if objType == "lattice":
        return shared.growLatticePoints(inComps)

    cmds.error("current type --%s-- not valid for this commmand, only surface or polygon can be used!" % objType)


def cutMesh(internal, maya2020, progressBar=None):
    selection = getSelection()
    if "." in selection[0]:
        selection = [selection[0].split(".")[0]]

    meshes = []
    _toDelete = []
    for obj in selection:
        _fix = cmds.duplicate(obj)[0]
        _toDelete.append(_fix)
        skinCluster.transferSkinning(obj, _fix, True, True, False, None)

        msh = mesh.cutCharacterFromSkin(obj, internal, maya2020, progressBar)
        meshes.append(msh)
    cmds.group(meshes, n="lowRez")
    cmds.delete(_toDelete)


def pinToSurface():
    selection = getSelection()
    if "." in selection[0]:
        vertices = shared.convertToVertexList(selection)
        driveMesh = vertices[0].split(".")[0]
        pos = []
        for vert in vertices:
            pos.append(cmds.xform(vert, q=1, ws=1, t=1))
        center = mathUtils.getCenterPosition(pos)
        transform = cmds.spaceLocator()[0]
        cmds.xform(transform, ws=1, t=center)
    elif len(selection) == 2:
        child = cmds.listRelatives(selection[0], s=1, fullPath=1) or None
        if child is None:
            transform = selection[0]
            driveMesh = selection[1]
        elif cmds.objectType(child) == "mesh":
            driveMesh = selection[0]
            transform = selection[1]
        else:
            driveMesh = selection[1]
            transform = selection[0]
    else:
        cmds.error("selection does not match, needs polygon mesh and transform object, or polygon selection")

    shared.skinConstraint(driveMesh, transform)


def prebindFixer(doModel, inPose, progressBar=None):
    # @note:
    # this displays the originshape when moving joints, need to make sure both shapes are visibile maybe when using the inpose == False
    # maybe double check if this could be changed, so that once an opject is in edit mode either way, the next click will always make sure the objects is set to a default state
    selection = getSelection()
    if len(selection) > 1:
        selection = selection[0]
    if "." in selection:
        selection = selection.split('.')[0]

    if doModel or inPose:
        mesh.toggleDisplayOrigShape(selection, both=inPose)

    else:
        joints.toggleMoveSkinnedJoints(selection, inPose, progressBar=None)


def getUVInfo(inMesh):
    allUvSets = cmds.polyUVSet(inMesh, q=1, auv=1)
    currentUvSet = cmds.polyUVSet(inMesh, q=1, cuv=1)
    uvSets = currentUvSet
    for s in allUvSets:
        if s in uvSets:
            continue
        uvSets.append(s)
    return uvSets


def transferUV(source, target, sMap="map1", tMap="map1", progressBar=None):
    skinCluster.transferUvToSkinnedObject(source, target, sMap, tMap, progressBar)


def deleteBindPoses(progressBar=None):
    joints.removeBindPoses(progressBar)


def getMayaVersion():
    mayaVersion = str(cmds.about(apiVersion=True))[:-2]
    if "maya" in sys.executable and platform.system() == "Windows":
        mayaVersion = sys.executable.split("Maya")[-1].split(os.sep)[0]
    elif platform.system() != "Windows":
        mayaVersion = cmds.about(version=1)
    return mayaVersion


def getPluginSuffix():
    pluginSuffix = ".mll"
    if platform.system() == "Darwin":
        pluginSuffix = ".bundle"
    if platform.system() == "Linux":
        pluginSuffix = ".bundle"
    return pluginSuffix


def pathToPlugin(pluginName):
    pluginFile = "%s%s" % (pluginName, getPluginSuffix())
    version = getMayaVersion()
    for dirName, __, fList in os.walk(getInterfaceDir()):
        if version in dirName and pluginFile in fList:
            return os.path.join(dirName, pluginFile)


@shared.dec_loadPlugin(pathToPlugin("smooth_brush_maya"))
def initBpBrush():
    selection = getSelection()
    sc = shared.skinCluster(selection[0])
    cmds.SBR_cache_manager(buildCache=sc)


def setHardShellWeight(inProgressBar=None):
    _copy = vertexWeight()
    selection = shared.convertToVertexList(getSelection())
    amount = len(selection)
    precentage = 99.0 / amount
    setProgress(0, inProgressBar, "start creating hard shells")
    processed = []
    for index, vert in enumerate(selection):
        if vert in processed:
            continue

        _copy.getVtxWeight(vert)

        face = cmds.polyListComponentConversion(vert, tf=1)
        moreFaces = cmds.filterExpand(face, sm=34, fp=1)
        mesh = face[0].split('.')[0]
        idx = shared.convertToIndexList(moreFaces)[0]
        faces = cmds.polySelect(q=1, extendToShell=idx)
        shell = shared.convertToCompList(faces, mesh, "f")
        processed.extend(shared.convertToVertexList(shell))

        _copy.setVtxWeight(shell)
        setProgress(precentage * index, inProgressBar, "converting hard shell")

    setProgress(100, inProgressBar, "processed all shells in selection")


class vertexWeight(object):
    def __init__(self, inProgressBar=None):
        self.vertexWeightInfo = None
        self.boneInfo = None
        self.__progressBar = inProgressBar

    def getVtxWeight(self, inSelection=None):
        selection = getSelection()
        if inSelection:
            selection = inSelection

        if not selection:
            cmds.error("nothing selected")

        vtxs = shared.convertToVertexList(selection)
        sc = shared.skinCluster(vtxs[0].split('.')[0])
        index = int(vtxs[0][vtxs[0].index("[") + 1: -1])
        self.boneInfo = cmds.listConnections("%s.matrix" % sc, source=True)

        averageList = []
        for vtx in vtxs:
            averageList.append(cmds.skinPercent(sc, vtx, q=1, v=1))

        self.vertexWeightInfo = [sum(x) / len(vtxs) for x in zip(*averageList)]
        return index

    @shared.dec_undo
    def setVtxWeight(self, inSelection=None):
        selection = getSelection()
        if inSelection:
            selection = inSelection

        if not selection:
            cmds.error("nothing selected")

        vtxs = shared.convertToVertexList(selection)
        mesh = vtxs[0].split('.')[0]
        sc = shared.skinCluster(mesh)
        boneInfo = cmds.listConnections("%s.matrix" % sc, source=True)
        missingJoints = list(set(self.boneInfo) - set(boneInfo))

        joints.addCleanJoint(missingJoints, mesh, self.__progressBar)

        transformValueList = []
        for i, jnt in enumerate(self.boneInfo):
            transformValueList.append([jnt, self.vertexWeightInfo[i]])

        cmds.skinPercent(sc, selection, transformValue=transformValueList, normalize=1, zeroRemainingInfluences=True)


class skinWeight(object):
    # @TODO: check to make sure when remapped if skinweights neew remap as well!
    def __init__(self, inProgressBar=None):
        self.weightInfo = None
        self.boneInfo = None
        self.__progressBar = inProgressBar

    def getSkinWeight(self):
        selection = getSelection()
        if not selection:
            cmds.error("nothing selected")

        mesh = selection[0]
        if "." in mesh:
            mesh = mesh.split('.')[0]

        sc = shared.skinCluster(mesh)
        self.boneInfo = cmds.listConnections("%s.matrix" % sc, source=True)
        self.weightInfo = shared.getWeights(mesh)
        return mesh

    def needsRemap(self):
        toCheck = set(self.boneInfo).intersection(set(cmds.ls(type="joint")))
        return (not toCheck == set(self.boneInfo))

    def calcRemap(self, remapDict):
        joints = []
        for jnt in self.boneInfo:
            joints.append(remapDict[jnt])
        self.boneInfo = joints

    def setSkinWeights(self):
        selection = getSelection()
        if not selection:
            cmds.error("nothing selected")

        mesh = selection[0]
        if "." in mesh:
            mesh = mesh.split('.')[0]

        sc = shared.skinCluster(mesh, True)
        if sc is None:
            sc = cmds.skinCluster(mesh, self.boneInfo, tsb=1)[0]
        boneInfo = cmds.listConnections("%s.matrix" % sc, source=True)

        missingJoints = list(set(self.boneInfo) - set(boneInfo))
        joints.addCleanJoint(missingJoints, mesh, self.__progressBar)

        shared.setWeights(mesh, self.weightInfo)


class NeighborSelection(object):
    def __init__(self):
        self.__bdrSel = None
        self.__bdrIndex = 0
        self.__bdrSelBase = []

    def getBorderIndex(self):
        return self.__bdrIndex

    def storeSel(self, *_):
        self.__bdrSelBase = shared.convertToVertexList(getSelection())
        self.__bdrSel = None
        self.__bdrIndex = 0

    def shrink(self, *_):
        self.__bdrIndex -= 1
        self.__borderSel()

    def grow(self, *_):
        self.__bdrIndex += 1
        self.__borderSel()

    def __borderSel(self, *_):
        for i in range(self.__bdrIndex):
            toConvert = self.__bdrSel
            if i == 0:
                toConvert = self.__bdrSelBase
            self.__bdrSel = getNeightbors(toConvert)

        if self.__bdrIndex == 0:
            cmds.select(self.__bdrSelBase, r=1)
            return

        borderSelect = list(set(self.__bdrSel) ^ set(self.__bdrSelBase))
        cmds.select(borderSelect, r=1)


# ------------------ maya viewport function -------------------------

def objectUnderMouse(margin=4, selectionType="joint"):
    def selectFromScreenApi(x, y, x_rect=None, y_rect=None):
        # find object under mouse, (silently select the object using api and clear selection)
        # using old maya api as selectFromScreen does not exist in new version
        sel = OldOpenMaya.MSelectionList()
        OldOpenMaya.MGlobal.getActiveSelectionList(sel)

        if None not in (x_rect, y_rect):
            OldOpenMaya.MGlobal.selectFromScreen(x, y, x_rect, y_rect, OldOpenMaya.MGlobal.kReplaceList)
        else:
            OldOpenMaya.MGlobal.selectFromScreen(x, y, OldOpenMaya.MGlobal.kReplaceList)
        objects = OldOpenMaya.MSelectionList()
        OldOpenMaya.MGlobal.getActiveSelectionList(objects)

        OldOpenMaya.MGlobal.setActiveSelectionList(sel, OldOpenMaya.MGlobal.kReplaceList)

        fromScreen = []
        objects.getSelectionStrings(fromScreen)
        return fromScreen

    def getSelectionModeIcons():
        # fix if anything other then object selection is used
        selectionMode = None
        if cmds.selectMode(q=1, object=1):
            selectionMode = "object"
        elif cmds.selectMode(q=1, component=1):
            selectionMode = "component"
        elif cmds.selectMode(q=1, hierarchical=1):
            selectionMode = "hierarchical"
        return selectionMode

    maskOn = cmds.selectType(q=True, joint=True)
    cmds.selectType(joint=True)
    active_view = OldOpenMayaUI.M3dView.active3dView()
    pos = QCursor.pos()
    widget = QApplication.widgetAt(pos)

    relPos = widget.mapFromGlobal(pos)

    foundObjects = selectFromScreenApi(relPos.x() - margin,
                                       active_view.portHeight() - relPos.y() - margin,
                                       relPos.x() + margin,
                                       active_view.portHeight() - relPos.y() + margin)
    if selectionType == "joint":

        sm = getSelectionModeIcons()
        cmds.selectMode(object=True)
        cmds.selectType(joint=maskOn)
        cmds.selectMode(**{sm: 1})

    foundBone = False
    boneName = ''
    for fobj in foundObjects:
        if cmds.objectType(fobj) == selectionType:
            foundBone = True
            boneName = fobj
            break
    return foundBone, boneName
