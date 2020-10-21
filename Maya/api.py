"""
Maya stub of imports used in the UI library.

The idea is to make this file as short as possible
while leaving room for other packages to implement features.
"""
import functools,os

from SkinningTools.Maya.tools import shared, joints
from SkinningTools.Maya.tools import weightPaintUtils
from SkinningTools.UI.markingMenu import MarkingMenuFilter
from SkinningTools.UI.qt_util import QObject, QApplication
from maya import cmds, mel
from maya.api import OpenMaya

_DEBUG = True

def get_maya_window():
    for widget in QApplication.allWidgets():
        try:
            if widget.objectName() == "MayaWindow":
                return widget
        except:
            pass
    return None


def selectedObjectVertexList(includeObjects=False):
    step = cmds.ls(sl=True, l=True)
    if not step:
        return []
    res = shared.convertToVertexList(step) or []
    if includeObjects:
        return [(r.split('.', 1)[0], r) for r in res]
    return res


skinPercent = cmds.skinPercent
meshVertexList = shared.convertToVertexList
addCleanJoint = joints.addCleanJoint

def selectedSkinnedShapes():
    selectedShapes = set(cmds.ls(sl=True, l=True, o=True, type='shape') or [])
    t = cmds.ls(sl=True, l=True, o=True, type='transform')
    if t:
        selectedShapes += set(cmds.listRelatives(t, c=True, f=True, type='shape') or [])

    result = []
    for skinCluster in cmds.ls(type='skinCluster'):
        for skinnedShape in cmds.ls(cmds.skinCluster(skinCluster, q=True, g=True) or [], l=True) or []:
            if skinnedShape in selectedShapes:
                result.append(skinnedShape)

    return result


def connectSelectionChangedCallback(callback):
    return cmds.scriptJob(e=('SelectionChanged', callback))


def disconnectCallback(handle):
    if isinstance(handle, int):  # in the future we can also handle MCallbackId from API callbacks here
        cmds.scriptJob(kill=handle, force=True)
    else:
        print("Unrecognized handle")


skinClusterForObject = shared.skinCluster
skinClusterForObjectHeadless = functools.partial(shared.skinCluster, silent=True)
dec_undo = shared.dec_undo

def getApiDir():
    return os.path.dirname(os.path.abspath(__file__))


def dec_loadPlugin(input):
    return shared.dec_loadPlugin(os.path.join(getApiDir(), "plugin/%s"%input))


def skinClusterInfluences(skinCluster):
    return cmds.ls(cmds.listConnections("%s.matrix" % skinCluster, source=True), l=1)


def getSkinWeights(geometry):
    return shared.getWeights(geometry)
    


def setSkinWeights(geometry, skinCluster, weights, influenceIndices=None):
    if influenceIndices:
        cmds.skinPercent(skinCluster, geometry, tv=zip(influenceIndices, weights))
    else:
        cmds.SkinWeights(geometry, skinCluster, nwt=weights)


def getSingleVertexWeight(skinClusterHandle, vertexHandle, influenceHandle):
    # given a skin,  a vertex and a joint, return the weight
    # skin cluster can be obtained with skinClusterForObject
    # mvertex can be obtained with selectedObjectVertexList(True), joint can be obtained with skinClusterInfluences
    return cmds.skinPercent(skinClusterHandle, vertexHandle, q=True, t=influenceHandle)


def getSingleVertexWeights(skinClusterHandle, vertexHandle):
    # given a skin and a vertex, return the weight
    # skin cluster can be obtained with skinClusterForObject
    # vertex can be obtained with selectedObjectVertexList(True)
    return cmds.skinPercent(skinClusterHandle, vertexHandle, q=True, v=True)

def selectVertices(meshVertexPairs):
    cmds.select([v for m, v in meshVertexPairs])

    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    mel.eval('doMenuComponentSelection("%s", "%s");' % (meshVertexPairs[0][0].split('.')[0], "vertex"))


def _eventFilterTargets():
    # We must return all widgets that receive strong focus that we want to tap into
    # such as the main window or 3D viewports that are not simple Qt widgets.

    from SkinningTools.UI.qt_util import wrapinstance, QMainWindow, QObject
    from maya.OpenMayaUI import MQtUtil, M3dView

    mainWin = wrapinstance(int(MQtUtil.mainWindow()), QMainWindow)

    active_view = M3dView.active3dView()
    active_view_ptr = active_view.widget()
    qt_active_view = wrapinstance(int(active_view_ptr), QObject)

    return mainWin, qt_active_view

def convertlistToOpenMayaArray(inList, arrayType):
    array = arrayType()
    for elem in inList:
        array.append(elem)
    return array

class _EventFilter(QObject):
    _singleton = None

    @staticmethod
    def singleton():
        if _EventFilter._singleton is None:
            _EventFilter._singleton = _EventFilter()
        return _EventFilter._singleton

    def eventFilter(self, obj, event):
        from SkinningTools.UI.qt_util import Qt, QEvent
        _arrows = {Qt.Key_Up: "up", Qt.Key_Down: "down"}
        if event.type() == QEvent.KeyPress and event.key() in _arrows.keys():
            return weightPaintUtils.pickWalkSkinClusterInfluenceList(_arrows[event.key()])
        return False


def dccInstallEventFilter():
    eventFilterTargets = _cleanEventFilter()
    for eventFilterTarget in eventFilterTargets:
        eventFilterTarget.installEventFilter(_EventFilter.singleton())
        eventFilterTarget.installEventFilter(MarkingMenuFilter.singleton())
    return True


def _cleanEventFilter():
    widgets = _eventFilterTargets()
    for widget in widgets:
        try:
            widget.removeEventFilter(_EventFilter.singleton())
            widget.removeEventFilter(MarkingMenuFilter.singleton())
        except Exception as e:
            if _DEBUG:
                print(e)
    return widgets


def getIds(inList):
    return shared.convertToIndexList(inList)

def textProgressBar(progress, message=''):
    barLength = 10
    status = ""
    if progress <= 0:
        progress = 0
    progress = progress / 100.0
    if progress >= 1:
        progress = 1
    block = int(round(barLength * progress))
    text = "[%s] %.1f%%, %s" % ("#" * block + "-" * (barLength - block), progress * 100, message)
    OpenMaya.MGlobal.displayInfo(text)


def displayToolTips():
    cmds.help(popupMode=True)
