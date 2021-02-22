# -*- coding: utf-8 -*-
from SkinningTools.Maya.tools import mathUtils, mesh, shared, joints
from SkinningTools.UI import utils 
from maya import cmds
from maya.api import OpenMaya

'''
based on robert joosten's tool:
https://github.com/robertjoosten/maya-skinning-tools/tree/master/scripts/skinningTools/softSelectionToWeights
'''

def setSkinWeights(inMesh, meshData, influences, filler=None, progressBar = None):
    """Calculate and set the new skin weights. If no skin cluster is attached to
    the mesh, one will be created and all weights will be set to 1 with the 
    filler influence. If a skin cluster does exist, the current weights will
    be used to blend the new weights. Maintaining of maximum influences and 
    normalization of the weights will be taken into account if these 
    attributes are set on the skin cluster.

    :param inMesh:
    :type inMesh: str
    :param meshData: skinning data for the mesh
    :type meshData: dict
    :param influences: list of (new) influences
    :type influences: list
    :param filler: Filler joint if no skin cluster is detected
    :type filler: str
    """

    skinCluster = shared.skinCluster(inMesh, True)

    if not skinCluster:
        skinCluster = cmds.skinCluster( inMesh, filler, omi=True, mi=4, tsb=True )[0]
        joints.addCleanJoint(influences, inMesh, progressBar=None)
        influences.append(filler)
    else:
        filler = None
        joints.addCleanJoint(influences, inMesh, progressBar=None)

    normalizeWeights = cmds.getAttr( "{0}.normalizeWeights".format(skinCluster) )
    maxInfluences = cmds.getAttr( "{0}.maxInfluences".format(skinCluster) )
    maintainMaxInfluences = cmds.getAttr( "{0}.maintainMaxInfluences".format(skinCluster) )

    utils.setProgress(0, progressBar, "building weights for %s"%inMesh )

    percentage = len(meshData.keys())/99.0
    for index, weights in meshData.iteritems():
        vertex = "{0}.vtx[{1}]".format(inMesh, index)
        total = sum(weights.values())

        if filler and total < 1:
            weights[filler] = 1-total
        elif not filler and total < 1:
            multiplier = 1-total

            transforms = cmds.skinPercent( skinCluster, vertex, query=True, transform=None )
            transforms = cmds.ls(transforms, l=True)

            values = cmds.skinPercent( skinCluster, vertex, query=True, value=True )

            for t, v in zip(transforms, values):
                if t not in weights.keys():
                    weights[t] = 0

                weights[t] += v * multiplier

        if maintainMaxInfluences:
            temp = zip(weights.values(), weights.keys())
            excess = sorted(temp, reverse=True)[maxInfluences:]

            for v, t in excess:
                weights[t] = 0.0

        if normalizeWeights == 1:
            total = sum(weights.values())
            multiplier = 1/total

            for t, v in weights.iteritems():
                weights[t] = v * multiplier

        weights = [(t, v) for t, v in weights.iteritems()]
        cmds.skinPercent(skinCluster, vertex, transformValue=weights)
        utils.setProgress(index * percentage, progressBar, "set skinning info: %s"%vertex )
    utils.setProgress(100, progressBar, "build skin info with soft selextion" )
