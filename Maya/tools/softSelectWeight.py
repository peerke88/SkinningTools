from SkinningTools.Maya.tools import mathUtils, mesh, shared, joints
from maya import cmds, OpenMaya

'''
based on robert joosten's tool:
https://github.com/robertjoosten/maya-skinning-tools/tree/master/scripts/skinningTools/softSelectionToWeights
'''

def setSkinWeights(inMesh, meshData, influences, filler=None):
    """Calculate and set the new skin weights. If no skin cluster is attached to
    the mesh, one will be created and all weights will be set to 1 with the 
    filler influence. If a skin cluster does exist, the current weights will
    be used to blend the new weights. Maintaining of maximum influences and 
    normalization of the weights will be taken into account if these 
    attributes are set on the skin cluster.
    
    meshData = {
        mesh:{
            {index:{
                influence:weight,
                influence:weight,
            },
            {index:{
                influence:weight,
                influence:weight,
            },
        }    
    }
    
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

    # bind skin
    if not skinCluster:
        influences.append(filler)
        skinCluster = cmds.skinCluster( inMesh, influences, omi=True, mi=4, tsb=True )[0]

        # set weights with filler
        cmds.skinPercent( skinCluster, "{0}.vtx[*]".format(inMesh), transformValue=[(filler, 1)])

    # add influences
    else:
        filler = None
        joints.addCleanJoint(influences, inMesh, progressBar=None)

    # get skinCluster data
    normalizeWeights = cmds.getAttr( "{0}.normalizeWeights".format(skinCluster) )
    maxInfluences = cmds.getAttr( "{0}.maxInfluences".format(skinCluster) )
    maintainMaxInfluences = cmds.getAttr( "{0}.maintainMaxInfluences".format(skinCluster) )

    # loop indices
    for index, weights in meshData.iteritems():
        vertex = "{0}.vtx[{1}]".format(inMesh, index)
        total = sum(weights.values())

        if filler and total < 1:
            # add filler weight
            weights[filler] = 1-total
        elif not filler and total < 1:
            multiplier = 1-total

            # query existing
            transforms = cmds.skinPercent( skinCluster, vertex, query=True, transform=None )
            transforms = cmds.ls(transforms, l=True)

            values = cmds.skinPercent( skinCluster, vertex, query=True, value=True )

            # add normalized existing weights
            for t, v in zip(transforms, values):
                if t not in weights.keys():
                    weights[t] = 0

                weights[t] += v * multiplier

        if maintainMaxInfluences:
            # maintain influences, set excess influences to 0.0
            temp = zip(weights.values(), weights.keys())
            excess = sorted(temp, reverse=True)[maxInfluences:]

            for v, t in excess:
                weights[t] = 0.0

        if normalizeWeights == 1:
            # normalize all weights
            total = sum(weights.values())
            multiplier = 1/total

            for t, v in weights.iteritems():
                weights[t] = v * multiplier

        # set weights
        weights = [(t, v) for t, v in weights.iteritems()]
        cmds.skinPercent(skinCluster, vertex, transformValue=weights)
