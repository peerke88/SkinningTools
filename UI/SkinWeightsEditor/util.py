# -*- coding: utf-8 -*-

from maya import cmds


def skinClusterFor(geometry):
    geometry = cmds.ls(geometry, l=True)[0]
    for cl in cmds.ls(type='skinCluster') or []:
        for g in cmds.skinCluster(cl, q=True, geometry=True):
            g = cmds.ls(g, l=True)[0]
            if g == geometry:
                return cl
    return None