"""
Maya stub of imports used in the UI library.

The idea is to make this file as short as possible
while leaving room for other packages to implement features.
"""
import functools

from Maya.tools import shared
from maya import cmds, mel

from Maya.tools.shared import mayaToolsWindow


def selectedObjectVertexList(includeObjects=False):
    step = cmds.ls(sl=True, l=True)
    if not step:
        return []
    res = shared.convertToVertexList(step[0]) or []
    if includeObjects:
        return [(r.split('.', 1)[0], r) for r in res]
    return res


skinPercent = cmds.skinPercent
meshVertexList = shared.convertToVertexList


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
    if isinstance(handle, str):  # in the future we can also handle MCallbackId from API callbacks here
        cmds.scriptJob(kill=handle, force=True)


skinClusterForObject = shared.skinCluster
skinClusterForObjectHeadless = functools.partial(shared.skinCluster, silent=True)


def skinClusterInfluences(skinCluster):
    return cmds.skinCluster(skinCluster, q=True, inf=True)


def getSkinWeights(geometry, skinCluster):
    return cmds.SkinWeights(geometry, skinCluster, q=True)


def setSkinWeights(geometry, skinCluster, weights, influenceIndices=None):
    if influenceIndices:
        cmds.skinPercent(skinCluster, geometry, tv=zip(influenceIndices, weights))
    else:
        cmds.SkinWeights(geometry, skinCluster, nwt=weights)


def dccToolButtons():
    return mayaToolsWindow()


def getSingleVertexWeight(skinClusterHandle, meshHandle, vertexHandle, influenceHandle):
    # given a skin, a skinned mesh, a vertex and a joint, return the weight
    # skin cluster can be obtained with skinClusterForObject
    # mesh and vertex can be obtained with selectedObjectVertexList(True), joint can be obtained with skinClusterInfluences
    return cmds.skinPercent(skinClusterHandle, meshHandle, vertexHandle, influenceHandle, q=True, value=True)


def selectVertices(meshVertexPairs):
    cmds.select([v for m, v in meshVertexPairs[:20]])

    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    mel.eval('doMenuComponentSelection("%s", "%s");' % (meshVertexPairs[0][0].split('.')[0], "vertex"))
