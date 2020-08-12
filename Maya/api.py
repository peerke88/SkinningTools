"""
Maya stub of imports used in the UI library.

The idea is to make this file as short as possible
while leaving room for other packages to implement features.
"""
from Maya.tools import shared
from maya import cmds


def selectedObjectVertexList():
    step = cmds.ls(sl=True, l=True)
    if step:
        return shared.convertToVertexList(step[0]) or []
    return []


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


def skinClusterInfluences(skinCluster):
    return cmds.skinCluster(skinCluster, q=True, inf=True)


def getSkinWeights(geometry, skinCluster):
    return cmds.SkinWeights(geometry, skinCluster, q=True)


def setSkinWeights(geometry, skinCluster, weights, influenceIndices=None):
    if influenceIndices:
        cmds.skinPercent(skinCluster, geometry, tv=zip(influenceIndices, weights))
    else:
        cmds.SkinWeights(geometry, skinCluster, nwt=weights)
