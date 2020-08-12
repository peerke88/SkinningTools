"""
Maya stub of imports used in the UI library.
"""
from Maya.tools.shared import convertToVertexList
from maya import cmds


def selectedObjectVertexList():
    step = cmds.ls(sl=True, l=True)
    if step:
        return convertToVertexList(step[0]) or []
    return []
