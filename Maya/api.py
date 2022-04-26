"""
Maya stub of imports used in the UI library.

The idea is to make this file as short as possible
while leaving room for other packages to implement features.
"""
import functools, os, sys, platform
from SkinningTools.Maya.tools import shared, joints
from SkinningTools.Maya.tools import weightPaintUtils
from SkinningTools.UI.qt_util import QObject, QApplication
from maya import cmds, mel, OpenMayaUI
from maya.api import OpenMaya

from SkinningTools.UI.utils import *

_DEBUG = getDebugState()


def get_maya_window():
    """ get the current maya window as a qt widget

    :return: the widget or none
    :rtype: QWidget
    """
    _widget = None
    for widget in QApplication.allWidgets():
        if widget.objectName() == "MayaWindow":
            _widget = widget
    if _widget is None:
        _widget = wrapinstance(long(OpenMayaUI.MQtUtil.mainWindow()))

    return _widget


def selectedObjectVertexList(includeObjects=False):
    """ get the current object/component selection

    :param includeObjects: if `True` will return the name of the object from which the vertex comes from, if `False` will only return the vertices
    :type includeObjects: bool
    :return: list of vertices 
    :rtype: list
    """
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
skinClusterForObject = shared.skinCluster
skinClusterForObjectHeadless = functools.partial(shared.skinCluster, silent=True)
dec_undo = shared.dec_undo


def selectedSkinnedShapes():
    """ get the shapes of skinned objects

    :return: list of shapes
    :rtype: list
    """
    selectedShapes = set(cmds.ls(sl=True, l=True, o=True, type='shape') or [])
    t = cmds.ls(sl=True, l=True, o=True, type='transform')
    if t:
        selectedShapes = selectedShapes | set(cmds.listRelatives(t, c=True, f=True, type='shape') or [])

    result = []
    for skinCluster in cmds.ls(type='skinCluster'):
        for skinnedShape in cmds.ls(cmds.skinCluster(skinCluster, q=True, g=True) or [], l=True) or []:
            if skinnedShape in selectedShapes:
                result.append(skinnedShape)

    return result


def loadPlugin(plugin):
    loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
    registered = cmds.pluginInfo(plugin, q=True, registered=True)

    if not registered or not loaded:
        try:
            cmds.loadPlugin(plugin)
        except Exception as e:
            print(e)


def getMayaVersion():
    """ get the current general mayaversion in which this tool is launched

    :return: maya version number as string
    :rtype: string
    """
    mayaVersion = str(cmds.about(apiVersion=True))[:-2]
    if "maya" in sys.executable and platform.system() == "Windows":
        mayaVersion = sys.executable.split("Maya")[-1].split(os.sep)[0]
    elif platform.system() != "Windows":
        mayaVersion = cmds.about(version=1)
    return mayaVersion


def getPluginSuffix():
    """ get the current plugin suffix based on the os that we are running

    :return: suffix for plugin files specific to a particular os
    :rtype: string
    """
    pluginSuffix = ".mll"
    if platform.system() == "Darwin":
        pluginSuffix = ".bundle"
    if platform.system() == "Linux":
        pluginSuffix = ".so"
    return pluginSuffix


def getPlugin():
    """ get the smoothbrush plugin based on information gathered on how maya is run

    :return: the path of the plugin to load
    :rtype: string
    """
    mayaVersion = getMayaVersion()
    suffix = getPluginSuffix()
    currentPath = os.path.dirname(__file__)
    _plugin = os.path.join(currentPath, "plugin/skinToolWeightsCpp/comp/Maya%s/plug-ins/SkinCommands%s" % (mayaVersion, suffix))
    return _plugin


def connectSelectionChangedCallback(callback):
    """ connect a callback to a selection changed event

    :param callback: the callback to connect
    :type callback: function
    :return: scriptjob that holds the callback
    :rtype: string
    """
    return cmds.scriptJob(e=('SelectionChanged', callback))


def disconnectCallback(handle):
    """ disconnect a callback present in the scene

    :param handle: the name of the scriptjob to remove
    :type handle: string
    """
    if isinstance(handle, int):  # in the future we can also handle MCallbackId from API callbacks here
        cmds.scriptJob(kill=handle, force=True)
    else:
        print("Unrecognized handle")


def getApiDir():
    """ get the path to the current file

    :return: path of the api file
    :rtype: string
    """
    return os.path.dirname(os.path.abspath(__file__))


def dec_loadPlugin(input):
    """ forwarded decorator function to load plugins

    :note: maybe remove this? too many similar functions? combine them all together
    :param input: name of the (python)plugin to load
    :type input: string
    """
    return shared.dec_loadPlugin(os.path.join(getApiDir(), "plugin/%s" % input))


def skinClusterInfluences(skinCluster):
    """ forwarded function to get joint information from skincluster

    :param skinCluster: skincluster to gather data from
    :type skinCluster: string
    :return: list of all joints(fullpath) connected to the skincluster
    :rtype: list
    """
    return cmds.ls(cmds.listConnections("%s.matrix" % skinCluster, source=True), l=1)


def getSkinWeights(geometry):
    """ forwarded function to get the skinning data of a mesh

    :param geometry: mesh to get data from
    :type geometry: string
    :return: list of all weights on the mesh
    :rtype: list
    """
    return shared.getWeights(geometry)


def setSkinWeights(geometry, skinCluster, weights, influenceIndices=None):
    """ forwarded function to set the skinning data on a mesh

    :param geometry: mesh to set data to
    :type geometry: string
    :param skinCluster: skincluster attached to the current geometry
    :type skinCluster: string
    :param weights: list of weights to set
    :type weights: list
    :param influenceIndices: list of joints
    :type influenceIndices: list
    """
    if influenceIndices:
        cmds.skinPercent(skinCluster, geometry, tv=zip(influenceIndices, weights))
    else:
        cmds.SkinWeights(geometry, skinCluster, nwt=weights)


def getSingleVertexWeight(skinClusterHandle, vertexHandle, influenceHandle):
    """given a skin,  a vertex and a joint, return the weight
    skin cluster can be obtained with skinClusterForObject
    mvertex can be obtained with selectedObjectVertexList(True), joint can be obtained with skinClusterInfluences

    :param skinClusterHandle: name of the current skincluster
    :type skinClusterHandle: string
    :param vertexHandle: name of current vertex
    :type vertexHandle: string
    :param influenceHandle: name of bone to get data from
    :type influenceHandle: string
    :return: list of influences
    :rtype: list
    """
    return cmds.skinPercent(skinClusterHandle, vertexHandle, q=True, t=influenceHandle)


def getSingleVertexWeights(skinClusterHandle, vertexHandle):
    """given a skin and a vertex, return the weight
    skin cluster can be obtained with skinClusterForObject
    vertex can be obtained with selectedObjectVertexList(True)

    :param skinClusterHandle: name of the current skincluster
    :type skinClusterHandle: string
    :param vertexHandle: name of current vertex
    :type vertexHandle: string
    :return: list of influences
    :rtype: list
    """
    return cmds.skinPercent(skinClusterHandle, vertexHandle, q=True, v=True)


def selectVertices(meshVertexPairs):
    """ select vertices based on given vertex pairs

    :param meshVertexPairs: list of objects that hold a list of which the second element is a vertex
    :type meshVertexPairs: list
    """
    cmds.select([v for m, v in meshVertexPairs])

    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    skinMesh = meshVertexPairs[0][0]
    objType = cmds.objectType(skinMesh)
    if objType == "transform":
        shape = cmds.listRelatives(skinMesh, c=1, s=1, fullPath=1)[0]
        objType = cmds.objectType(shape)

    if objType == "nurbsSurface" or objType == "nurbsCurve":
        mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");' % skinMesh)
    elif objType == "lattice":
        mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");' % skinMesh)
    elif objType == "mesh":
        mel.eval('doMenuComponentSelection("%s", "vertex");' % skinMesh)


def _eventFilterTargets():
    """We must return all widgets that receive strong focus that we want to tap into
    such as the main window or 3D viewports that are not simple Qt widgets.

    :return: the maya window and the active 3d viewport
    :rtype: list
    """
    from SkinningTools.UI.qt_util import wrapinstance, QMainWindow, QWidget
    from maya.OpenMayaUI import MQtUtil, M3dView

    mainWin = wrapinstance(int(MQtUtil.mainWindow()), QMainWindow)

    active_view = M3dView.active3dView()
    active_view_ptr = active_view.widget()
    qt_active_view = wrapinstance(int(active_view_ptr), QWidget)

    return mainWin, qt_active_view


def convertlistToOpenMayaArray(inList, arrayType):
    """convert given list to an openmaya arraytype

    :param inList: list of objects to be added to arraytype
    :type inList: list
    :param arrayType: any openmaya array type
    :type arrayType: OpenMaya.<array>
    :return: the array filled with data
    :rtype: OpenMaya.<array>
    """
    array = arrayType()
    for elem in inList:
        array.append(elem)
    return array


class _EventFilter(QObject):
    """ eventfilter class to allow extra functionality to be added to the current maya qt eventfilters
    """
    _singleton = None

    @staticmethod
    def singleton():
        """ singleton of the current class for ease of identifying

        :return: the current object singleton
        :rtype: cls
        """
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
    from SkinningTools.UI.markingMenu import MarkingMenuFilter
    """ install the eventfilter on the current dcc
    
    :return: `True` if succesfull
    :rtype: bool
    """
    eventFilterTargets = _cleanEventFilter()
    for eventFilterTarget in eventFilterTargets:
        eventFilterTarget.installEventFilter(_EventFilter.singleton())
        eventFilterTarget.installEventFilter(MarkingMenuFilter.singleton())
    return True


def _cleanEventFilter():
    from SkinningTools.UI.markingMenu import MarkingMenuFilter
    """ remove the eventfilter on the current dcc
    
    :return: list of widgets from which the eventfilters where removed
    :rtype: list
    """
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
    """ forwarded function to conevert components to indices

    :param inlist: list of maya components
    :type inlist: list
    :return: list of indices
    :rtype: list
    """
    return shared.convertToIndexList(inList)


def textProgressBar(progress, message=''):
    """ set the current progress of a function using test only

    :param progress: percentage of progress 
    :type progress: float
    :param message: the message to be displayed
    :type message: string
    """
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
    """force display tool tips in maya as these are turned off by default"""
    cmds.help(popupMode=True)
