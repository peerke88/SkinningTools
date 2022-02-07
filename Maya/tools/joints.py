# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI import utils
from SkinningTools.Maya.tools import shared, mathUtils, mesh, enumerators
from maya import cmds
from maya.api.OpenMaya import MVector


# @note all functions must have connection with progressbar and sensible progress messages,
# look into warning messages later
@shared.dec_undo
def autoLabelJoints(inputLeft="L_*", inputRight="R_*", progressBar=None):
    """ joint labeling function

    :param inputLeft: search function that allocates which joints are part of the left side of the rig "*" used as a wildcard to replace part of the string
    :type inputLeft: string
    :param inputRight: search function that allocates which joints are part of the right side of the rig "*" used as a wildcard to replace part of the string
    :type inputRight: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    def SetAttrs(side, type, name):
        for attr in ["side", "type", "otherType", "drawLabel"]:
            cmds.setAttr("%s.%s" % (bone, attr), l=0)

        cmds.setAttr(bone + '.side', side)
        cmds.setAttr(bone + '.type', type)
        cmds.setAttr(bone + '.otherType', name, type="string")
        cmds.setAttr(bone + '.drawLabel', 1)

    # using short names as these will not work well with long names
    # @TODO: lets have a look if we can give a warning if there are duplicate names in the short version
    allJoints = cmds.ls(type="joint") or None
    if allJoints is None:
        return

    allFoundjoints = allJoints[::]
    percentage = 99.0 / len(allJoints)
    if not "*" in inputLeft:
        inputLeft = "*" + inputLeft + "*"
    if not "*" in inputRight:
        inputRight = "*" + inputRight + "*"

    leftJoints = cmds.ls("%s" % inputLeft, type="joint")
    rightJoints = cmds.ls("%s" % inputRight, type="joint")
    iteration1 = 0
    iteration2 = 0

    for iteration1, bone in enumerate(leftJoints):
        SetAttrs(1, 18, str(bone).replace(str(inputLeft).strip("*"), ""))
        allJoints.remove(bone)
        utils.setProgress((iteration1 + 1) * percentage, progressBar, "Setting left Side")

    for iteration2, bone in enumerate(rightJoints):
        SetAttrs(2, 18, str(bone).replace(str(inputRight).strip("*"), ""))
        allJoints.remove(bone)
        utils.setProgress((iteration1 + iteration2) * percentage, progressBar, "Setting right Side")

    for iteration3, bone in enumerate(allJoints):
        SetAttrs(0, 18, str(bone))
        utils.setProgress((iteration1 + iteration2 + iteration3) * percentage, progressBar, "Setting center")

    for bone in allFoundjoints:
        cmds.setAttr(bone + '.drawLabel', 0)

    utils.setProgress(100, progressBar, "labeling joints")
    return True

@shared.dec_undo
def resetToBindPoseobject(inObject, progressBar=None):
    """ set joints back into their bindpose using the prebind matrix of the skincluster, only works when joints are not connected (rigged)

    :param inObject: mesh object that has a skincluster attached
    :type inObject: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    skinCluster = shared.skinCluster(inObject, silent=True)
    if skinCluster is None:
        return

    infjnts = getInfluencingJoints(skinCluster)
    percentage = 99.0 / float(len(infjnts))
    for i, joint in enumerate(infjnts):
        prebindMatrix = cmds.getAttr("%s.bindPreMatrix[%s]" % (skinCluster, i))

        matrix = mathUtils.matrixToFloatList(mathUtils.floatToMatrix(prebindMatrix).inverse())
        cmds.xform(joint, ws=True, m=matrix)
        utils.setProgress(i * percentage, progressBar, "rest pose on %s" % joint)

    utils.setProgress(100, progressBar, "bindposes reset")
    return True


@shared.dec_undo
def resetSkinnedJoints(inJoints=None, inSkinCluster=None, progressBar=None):
    """ force recalculate the prebindmatrices in the skinclsuter based on current joint positions

    :param inJoints: list of joints to recalculate
    :type inJoints: list
    :param inSkinCluster: the skincluster that will receive new prebind matrices
    :type inSkinCluster: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    jnts = inJoints
    if jnts == None:
        jnts = cmds.ls(sl=0, type="joint", l=1)

    percentage = 99.0 / len(jnts)
    for i, joint in enumerate(jnts):
        skinClusterPlugs = cmds.listConnections("%s.worldMatrix[0]" % joint, type="skinCluster", p=1)
        if inSkinCluster is not None and skinClusterPlugs is not None:
            _notFound = True
            for sc in skinClusterPlugs:
                if inSkinCluster in sc:
                    skinClusterPlugs = [sc]
                    _notFound = False
            if _notFound:
                skinClusterPlugs = []

        if skinClusterPlugs:
            skinCluster = None
            for skinClstPlug in skinClusterPlugs:
                index = skinClstPlug[skinClstPlug.index("[") + 1: -1]
                skinCluster = skinClstPlug[: skinClstPlug.index(".")]
                curInvMat = cmds.getAttr("%s.worldInverseMatrix" % joint)
                cmds.setAttr("%s.bindPreMatrix[%s]" % (skinCluster, index), type="matrix", *curInvMat)
            try:
                cmds.skinCluster(skinCluster, e=True, recacheBindMatrices=True)
            except RuntimeError:
                pass
        else:
            if inSkinCluster is not None and inJoints is not None:
                print("%s not attached to %s!" % (joint, inSkinCluster))
        utils.setProgress(i * percentage, progressBar, "resetting %s" % joint)
    utils.setProgress(100, progressBar, "joints reset")
    return True


def freezeScale(inJnts, progressBar=None):
    """ force clean joint scales per joint

    :param inJnts: list of joints that need their scales to be set to uniform (1,1,1)
    :type inJnts: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: list of joints that are cleaned
    :rtype: list
    """
    percentage = 99.0 / len(inJnts)
    wms = []
    for i, joint in enumerate(inJnts):
        wm = cmds.xform(joint, q=1, ws=1, m=1)
        mm = mathUtils.floatToMatrix(wm)
        x = mathUtils.getVectorFromMatrix(mm, 0).normal()
        y = mathUtils.getVectorFromMatrix(mm, 1).normal()
        z = x ^ y
        pos = mathUtils.getVectorFromMatrix(mm, 3)
        nm = mathUtils.vectorsToMatrix([x, y, z, pos])
        wms.append(nm)
        utils.setProgress(i * percentage, progressBar, "freeze scale on %s" % joint)

    for index, jnt in enumerate(inJnts):
        fm = mathUtils.matrixToFloatList(wms[index])
        cmds.xform(jnt, ws=1, m=fm)
    utils.setProgress(100, progressBar, "scale frozen")
    return inJnts


def freezeRotate(inJnts, progressBar=None):
    """ force clean joint rotations per joint

    :param inJnts: list of joints that need their rotations to be nulified (0,0,0)
    :type inJnts: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: list of joints that are cleaned
    :rtype: list
    """

    percentage = 99.0 / len(inJnts)
    for i, joint in enumerate(inJnts):
        if cmds.objectType(joint) != "joint":
            continue
        dup = cmds.duplicate(joint, rc=1)[0]
        ch = cmds.listRelatives(dup, children=1, f=1)
        if ch:
            cmds.delete(ch)

        cmds.makeIdentity(dup, apply=1, t=0, r=1, s=0)
        jo = cmds.getAttr(dup + '.jo')[0]

        cmds.setAttr(joint + '.jo', *jo)
        cmds.delete(dup)

        try:
            cmds.setAttr(joint + '.r', 0, 0, 0)
        except:
            pass
        utils.setProgress(i * percentage, progressBar, "freeze rotate on %s" % joint)
    utils.setProgress(100, progressBar, "rotate frozen")
    return inJnts


@shared.dec_undo
def freezeSkinnedJoints(jnts, rotate=1, scale=1, progressBar=None):
    """ clean joint rotations and scales even if they are skinned

    :note: this will not work when joints are connected through ik-handle!
    :param jnts: list of joints that need their rotations and scales to be cleaned
    :type jnts: list
    :param rotate: if `True` will clean rotations, if `False` will skip them
    :type rotate: bool
    :param scale: if `True` will clean scales, if `False` will skip them
    :type scale: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    if len(jnts) == 1:
        jnts = shared.selectHierarchy(jnts)
    if rotate:
        freezeRotate(jnts)
        utils.setProgress(33, progressBar, "freezeRotate")
    if scale:
        freezeScale(jnts)
        utils.setProgress(66, progressBar, "freezeScale")
    resetSkinnedJoints(jnts)
    utils.setProgress(100, progressBar, "freeze skinned joints")
    return True

@shared.dec_undo
def removeBindPoses(progressBar=None):
    """ remove bindpose nodes from the scene so the prebindmatrices in the skinclusters can do their work, this also makes it easier to add new joints to the skinclusters

    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    dagPoses = cmds.ls(type="dagPose")
    if dagPoses == []:
        return

    percentage = 99.0 / len(dagPoses)
    for index, dagPose in enumerate(dagPoses):
        if not cmds.getAttr("%s.bindPose" % dagPose):
            continue
        cmds.delete(dagPose)
        utils.setProgress(index * percentage, progressBar, "delete bindposes")
    utils.setProgress(100, progressBar, "delete bindposes")
    return True


@shared.dec_undo
def addCleanJoint(jnts, inMesh, progressBar=None):
    """ add a new joint to the skincluster

    :param jnts: list of joints that need to be added to the current skinCluster
    :type jnts: list
    :param rotate: name of the mesh the joint should be added to
    :type rotate: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    sc = shared.skinCluster(inMesh, silent=True)
    if jnts == []:
        return
    percentage = 99.0 / len(jnts)
    if sc != None:
        jointInfls = getInfluencingJoints(sc)
        for index, joint in enumerate(jnts):
            if joint in jointInfls:
                continue
            cmds.skinCluster(sc, e=True, lw=False, wt=0.0, ai=joint)
            utils.setProgress(index * percentage, progressBar, "adding joints")
    utils.setProgress(100, progressBar, "adding joints")
    return True


@shared.dec_undo
def BoneMove(sourceJoint, targetJoint, skin, progressBar=None):
    """ move joint influences from 1 joint to another

    :param sourceJoint: joint to get the weight information from
    :type sourceJoint: string
    :param targetJoint: joint to set the weigth information to
    :type targetJoint: string
    :param skin: the skincluster on which the weight information is based
    :type skin: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    sc = shared.skinCluster(skin, True)
    addCleanJoint([joint1, joint2], skin)
    infjnts = list(set(getInfluencingJoints(sc) + [joint1, joint2]))

    _map = {}
    for joint in infjnts:
        _map[joint] = cmds.getAttr("%s.liw"%joint)
        cmds.setAttr("%s.liw"%joint, 1)

    cmds.setAttr("%s.liw"%joint1, 0)
    cmds.setAttr("%s.liw"%joint2, 0)
    cmds.skinPercent(sc, "%s.vtx[*]"%skin, transformValue=[joint1, 0.0])
    for joint, value in _map.items():
        cmds.setAttr("%s.liw"%joint, value)
    utils.setProgress(100, progressBar, "moved joint influences")
    return True


@shared.dec_undo
def BoneSwitch(joint1, joint2, skin, progressBar=None):
    """ switch the weight information of 2 given joints
    it reconnects the indices of the joints that are used on the given skincluster

    :param joint1: joint to switch the weight information from
    :type joint1: string
    :param joint2: joint to switch the weigth information from
    :type joint2: string
    :param skin: the skincluster on which the weight information is based
    :type skin: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    sc = shared.skinCluster(skin, True)
    addCleanJoint([joint1, joint2], skin)

    _connectDict = shared.getJointIndexMap(sc)
    for jnt in [joint1, joint2]:
        cmds.disconnectAttr('%s.worldMatrix' % jnt, '%s.matrix[%i]' % (sc, _connectDict[jnt]))
        cmds.disconnectAttr("%s.lockInfluenceWeights" % jnt, "%s.lockWeights[%s]" % (sc, _connectDict[jnt]))
    utils.setProgress(33, progressBar, "get influence map")
    
    cmds.connectAttr(joint1 + '.worldMatrix', '%s.matrix[%i]' % (sc, _connectDict[joint2]), f=1)
    cmds.connectAttr(joint2 + '.worldMatrix', '%s.matrix[%i]' % (sc, _connectDict[joint1]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint1, "%s.lockWeights[%s]" % (sc, _connectDict[joint2]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint2, "%s.lockWeights[%s]" % (sc, _connectDict[joint1]), f=1)
    # @Todo: check if we need to reset the prebindmatrices of these joints as the index order might be broken for this
    utils.setProgress(66, progressBar, "switch influences")

    resetSkinnedJoints([joint1, joint2], sc)
    utils.setProgress(100, progressBar, "switched bones")
    return True


@shared.dec_undo
def ShowInfluencedVerts(inMesh, jnts, progressBar=None):
    """ show the vertices that have any weight information from current given joints (weight information above 0.0)

    :param inMesh: mesh object that is influences by a skincluster and joints that are in the given selection
    :type inMesh: string
    :param jtns: joints that influence the current given mesh
    :type jtns: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    percentage = 100.0 / len(jnts)
    sc = shared.skinCluster(inMesh, True)

    vtxWeigths = cmds.getAttr("%s.weightList[:]" % sc)
    vtxCount = len(vtxWeigths)
    _connectDict = shared.getJointIndexMap(sc)

    toSelect = []
    for index, jnt in enumerate(jnts):
        if jnt not in _connectDict.keys():
            continue
        w = cmds.getAttr("%s.weightList[0:%i].weights[%i]" % (sc, vtxCount - 1, _connectDict[jnt]))
        #@todo: do we check from 0.0 or should we check for epsilon?
        res = [idx for idx, val in enumerate(w) if val > 0.0]
        for i in res:
            toSelect.append("%s.vtx[%i]" % (inMesh, i))
        utils.setProgress(percentage * index, progressBar, "gather weight information")

    utils.setProgress(100, progressBar, "show influenced vertices")
    return toSelect


@shared.dec_undo
def removeJointBySkinPercent(skinObject, jointsToRemove, sc, progressBar=None):
    """ remove joints influences by setting them to 0.0

    :param skinObject: the mesh object from which to remove influences
    :type skinObject: string
    :param jointsToRemove: list of joints to remove from current skincluster
    :type jointsToRemove: list
    :param sc: the skincluster attached to the mesh
    :type sc: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    verts = ShowInfluencedVerts(skinObject, jointsToRemove, progressBar=None)
    if verts == None or len(verts) == 0:
        return

    jnts = []
    percentage = 99.0 / len(jointsToRemove)
    for index, jnt in enumerate(jointsToRemove):
        if jnt not in jointsAttached:
            continue
        jnts.append((jnt, 0.0))
        utils.setProgress(index * percentage, progressBar, "removing joint weights")

    cmds.select(verts, r=1)
    cmds.skinPercent(sc, tv=jnts, normalize=True)
    utils.setProgress(100, progressBar, "joint weights removed")
    return True


@shared.dec_undo
def deleteJointSmart(jointsToRemove, progressBar=None):
    """ delete joints from the current chain no matter where they are placed or how they are parented

    :param jointsToRemove: list of joints to remove from current skincluster
    :type jointsToRemove: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    percentage = 99.0 / len(jointsToRemove)
    for index, jnt in enumerate(jointsToRemove):
        childJoints = cmds.listRelatives(jnt, c=1) or None
        parent = cmds.listRelatives(jnt, p=1) or None
        if childJoints is None:
            continue
        if parent is None:
            cmds.parent(childJoints, w=1)
            continue
        cmds.parent(childJoints, parent)
        utils.setProgress(index * percentage, progressBar, "reparenting joints")
    cmds.delete(jointsToRemove)
    utils.setProgress(100, progressBar, "deleted joints")
    return True


@shared.dec_undo
def removeJoints(skinObjects, jointsToRemove, useParent=True, delete=True, fast=False, progressBar=None):
    """ delete joints from the scene/ or just the skincluster in a way that it does not break the skinweigths
    will search for surogate joints to take over the weight information of the joint that is to be deleted

    :param skinObjects: objects from which the joint influences will be removed
    :type skinObjects: list
    :param jointsToRemove: list of joints to remove from current skincluster
    :type jointsToRemove: list
    :param useParent: it `True` will give the current joints information to its direct parent.
    :type useParent: bool
    :param delete: if `True` this will make sure that the joint is deleted in the end, if `False` only removes the weight information
    :type delete: bool
    :param fast: if `True` the fast option does not take into account other joints, it will just remove the weights of the given joint and normalize, if `False` it will look for better options
    :type fast: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    
    meshes = getMeshesInfluencedByJoint(jointsToRemove)
    for _mesh in meshes:
        if _mesh in skinObjects:
            continue
        skinObjects.append(_mesh)

    skinClusters = []
    skinPercentage = 100.0 / len(skinObjects)
    for skinIter, skinObject in enumerate(skinObjects):
        sc = shared.skinCluster(skinObject, True)
        if sc == None:
            continue

        jointsAttached = getInfluencingJoints(sc)
        if fast:
            removeJointBySkinPercent(skinObject, jointsToRemove, sc, progressBar)
            skinClusters.append(sc)
            utils.setProgress(skinIter * skinPercentage, progressBar, "removing influences")
            continue

        toSearch = []
        for jnt in jointsAttached:
            if jnt in jointsToRemove:
                continue
            toSearch.append(jnt)

        sourcePositions = []
        sourceJoints = []
        for joint in toSearch:
            pos = cmds.xform(joint, q=True, ws=True, t=True)
            sourcePositions.append(pos)
            sourceJoints.append([joint, pos])

        sourceKDTree = KDTree.construct_from_data(sourcePositions)

        jntPercentage = skinPercentage / len(jointsToRemove)
        for jntIter, jnt in enumerate(jointsToRemove):
            bone1 = jnt
            bone2 = cmds.listRelatives(jnt, parent=True) or [None]
            if useParent and bone2 is not None:
                bone2 = bone2[0]
            else:
                removePos = cmds.xform(jnt, q=True, ws=True, t=True)
                pts = sourceKDTree.query(removePos, t=1)
                for index, position in enumerate(sourceJoints):
                    if position[1] != pts[0]:
                        continue
                    bone2 = position[0]

            BoneMove(bone1, bone2, skinObject)

            utils.setProgress((jntIter + 1) * jntPercentage, progressBar, "remapping joints influences")

        skinClusters.append(sc)

    for sc in skinClusters:
        jointsAttached = getInfluencingJoints(sc)
        for jnt in jointsToRemove:
            if not jnt in jointsAttached:
                continue
            cmds.skinCluster(sc, e=True, ri=jnt)

    print("removed these joints from influence: ", jointsToRemove)
    if delete:
        deleteJointSmart(jointsToRemove)

    utils.setProgress(100, progressBar, "removed joints")

    return True


def comparejointInfluences(skinObjects, query=False, progressBar=None):
    """ compare the list of influences between several skinned objects

    :param skinObjects: skinned objects to compary influence lists
    :type skinObjects: list
    :param query: it `True` return the joints that are not present in all of the given objects, if `False` will make sure that all joints are present in all given objects
    :type query: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed, list of joints in query mode, None if there are no joints to be found in query
    :rtype: bool, list
    """
    jnts = []
    for obj in skinObjects:
        sc = shared.skinCluster(obj, True)
        jnt = getInfluencingJoints(sc)
        jnts.append(jnt)
    utils.setProgress(33, progressBar, "get joint maps")

    setList = []
    for i, s in enumerate(jnts):
        setList.append(set(jnts[i]).difference(*(jnts[:i] + jnts[i + 1:])))

    utils.setProgress(66, progressBar, "find differences")

    jnts = []
    for jntSet in setList:
        jnts.extend(list(jntSet))

    if query == True:
        utils.setProgress(100, progressBar, "found missing influences")
        if jnts:
            return jnts
        return None

    for obj in skinObjects:
        addCleanJoint(jnts, obj)
    utils.setProgress(100, progressBar, "unified joint maps")
    return True


def getMeshesInfluencedByJoint(currentJoints, progressBar=None):
    """ get all meshes that are influenced by current selection of joints

    :param currentJoints: the joint to check if they are used in skinclusters 
    :type currentJoints: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: list of objects influences by the current selection of joints
    :rtype:  list
    """
    allSkinClusters = cmds.ls(type="skinCluster")
    meshes = []
    percentage = 99.0 / len(allSkinClusters)
    for index, scl in enumerate(allSkinClusters):
        jnts = getInfluencingJoints(scl)
        geo = cmds.skinCluster(scl, q=1, g=1)[0]
        for jnt in currentJoints:
            if jnt in jnts and not geo in meshes:
                meshes.append(geo)
        utils.setProgress(index * percentage, progressBar, "listing connections")
    utils.setProgress(100, progressBar, "gather mesh information")
    return meshes


def getInfluencingJoints(inObject):
    """ get all joints that are influencing the given mesh

    :param inObject: the object which is influenced by a skincluster
    :type inObject: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: list of all the joints that are currently driving the given mesh
    :rtype:  list
    """
    if cmds.objectType(inObject) != "skinCluster":
        inObject = shared.skinCluster(inObject, silent=True)
    if inObject != None:
        jointInfls = cmds.ls(cmds.listConnections("%s.matrix" % inObject, source=True), l=1)
        return jointInfls


@shared.dec_undo
def removeUnusedInfluences(inObject, progressBar=None):
    """ remove the joints that are attached to the skincluster but are not assigned any weights.
    
    :note: this will only remove the current connection with joints, check if we can remap the nodes index connections in weights, influenceColor, lockweights and matrix inputs

    :param inObject: the object which is influenced by a skincluster
    :type inObject: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return:  `True` if the function is completed
    :rtype: bool
    """
    sc = shared.skinCluster(inObject)
    jointInfls = getInfluencingJoints(sc)
    weightedInfls = cmds.ls(cmds.skinCluster(sc, q=1, wi=1), l=1)

    toRemove = list(set(jointInfls) - set(weightedInfls))

    nodeState = cmds.getAttr("%s.nodeState" % sc)
    cmds.setAttr("%s.nodeState" % sc, 1)
    percentage = 99.0 / len(toRemove)
    index = 0
    for index, jnt in enumerate(toRemove):
        cmds.skinCluster(sc, e=1, ri=jnt)
        utils.setProgress(index * percentage, progressBar, "removing joint %s from mesh" % jnt.rsplit("|")[-1])

    cmds.setAttr("%s.nodeState" % sc, nodeState)
    utils.setProgress(100, progressBar, "removed %i joints from influence" % (index + 1))
    return True

@shared.dec_undo
def convertClusterToJoint(inCluster, jointName=None, progressBar=None):
    """ convert cluster deformer to a joint using the same influences and pivot position
    
    :param inCluster: the cluster object that is deforming a mesh
    :type inCluster: string
    :param jointName: name to give the joint, if `None` will create a default name
    :type jointName: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return:  `True` if the function is completed
    :rtype: bool
    """
    utils.setProgress(0, progressBar, "gather cluster data")
    shape = cmds.listRelatives(inCluster, s=1, type="clusterHandle") or None
    if shape is None:
        return
    clusterDeformer = cmds.listConnections(shape, s=1, type="cluster")[0]
    clusterSet = cmds.listConnections(clusterDeformer, type="objectSet")
    allConnected = shared.convertToVertexList(cmds.sets(clusterSet, q=1))
    indices = shared.convertToIndexList(allConnected)

    if jointName is None:
        jnt = cmds.createNode("joint", n="temp%s" % (indices[0]))
    else:
        jnt = cmds.createNode("joint", n=jointName)

    cmds.matchTransform(jnt, inCluster, pos=1, rot=0)

    inMesh = allConnected[0].split('.')[0]

    sc = shared.skinCluster(inMesh, True)
    cmds.skinCluster(sc, e=True, lw=False, wt=0.0, ai=jnt)

    # expandedVertices = shared.convertToVertexList(inMesh)
    values = cmds.percent(clusterDeformer, inMesh, q=1, v=1)

    percentage = 99.0 / len(allConnected)
    for index, vertex in enumerate(allConnected):
        cmds.skinPercent(sc, vertex, tv=[jnt, values[indices[index]]])
        utils.setProgress(index * percentage, progressBar, "setting cluster weights")

    cmds.delete(inCluster)
    utils.setProgress(100, progressBar, "converted cluster to joint")
    return jnt


@shared.dec_undo
def convertVerticesToJoint(inComponents, jointName=None, progressBar=None):
    """ convert (soft) selection to a joint based on center of selection
    
    :param inComponents: mesh component selection to assign to the joint
    :type inComponents: list
    :param jointName: name to give the joint, if `None` will create a default name
    :type jointName: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return:  `True` if the function is completed
    :rtype: bool
    """
    
    verts, weights = mesh.softSelection()
    if verts == []:
        return

    expanded = shared.convertToVertexList(inComponents)
    inMesh = expanded[0].split(".")[0]

    indices = shared.convertToIndexList(expanded)
    cluster = cmds.cluster()[1]
    if jointName is None:
        jnt = cmds.createNode("joint", n="temp%s" % (indices[0]))
    else:
        jnt = cmds.createNode("joint", n=jointName)
    cmds.matchTransform(jnt, cluster, pos=1, rot=0)

    addCleanJoint([jnt], inMesh)
    sc = shared.skinCluster(inMesh, True)

    percentage = 99.0 / len(verts)
    for index, vert in enumerate(verts):
        cmds.skinPercent(sc, vert, tv=[jnt, weights[index]])
        utils.setProgress(index * percentage, progressBar, "set skinweights")
    utils.setProgress(100, progressBar, "converted to joint")
    return jnt



@shared.dec_undo
def toggleMoveSkinnedJoints(inMesh, inPose = False,  progressBar=None):
    """
    toggle joint bind position manipulation on or off
    :todo: visualise the mesh that is manipulated <- needs to come from mesh.toggleDisplayOrigShape
    :todo: make different objects positioned on the prebind position that manipulate the prebind matrices for the joints
    :param inMesh: mesh object manipulated through a skincluster
    :type inMesh: string
    :param inPose: if `True` will generate a skeleton to manipulate the bindpose, if `False` will use the skinned skeleton
    :type inPose: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return:  `True` if the function is completed
    :rtype: bool
    """
    _buildInfo = "created with skinnintools"
    sc = shared.skinCluster(inMesh, True)

    preConns = cmds.listConnections("%s.bindPreMatrix" % sc, s=1, d=0, c=1, p=1) or []
    if preConns:
        jnts = []
        for driver, driven in zip(preConns[1::2], preConns[::2]):
            cmds.disconnectAttr(driver, driven)
            jnt = driver.split(".")[0]
            curInvMat = cmds.getAttr("%s.worldInverseMatrix" % jnt)
            cmds.setAttr(driven, type="matrix", *curInvMat)
            if cmds.attributeQuery("notes", n=jnt,  ex=1) and cmds.getAttr("%s.notes"%jnt) == _buildInfo:
                jnts.append(jnt)
        
        cmds.delete(jnts)
        return True

    conns = cmds.listConnections("%s.matrix" % sc, s=1, d=0, c=1, p=1)
    if inPose:
        parentSettings = []
        for driver, driven in zip(conns[1::2], conns[::2]):
            jnt = driver.split('.')[0]
            getPreBind = mathUtils.matrixToFloatList(mathUtils.floatToMatrix(cmds.getAttr(driven.replace("matrix", "bindPreMatrix"))).inverse())
            nJnt = cmds.createNode("joint", n="%sPreBind"%jnt, ss=1 )
            if not cmds.attributeQuery("notes", n=nJnt,  ex=1):
                cmds.addAttr(nJnt, sn= "nts", ln= "notes", dt = "string")
            cmds.setAttr( "%s.notes"%nJnt, _buildInfo, type="string" )
            cmds.setAttr("%s.notes"%nJnt, l=1)

            cmds.xform(nJnt, ws=1, m= getPreBind)

            parent = cmds.listRelatives(jnt, p=1) or None
            if parent:
                parentSettings.append([nJnt, "%sPreBind"%parent[0]])

            driven = driven.replace("matrix", "bindPreMatrix")
            cmds.connectAttr("%s.worldInverseMatrix"%nJnt, driven)
        
        for child, parent in parentSettings:
            if not cmds.objExists(parent):
                continue
            cmds.parent(child, parent)
            ro = cmds.getAttr("%s.rotate"%child)
            cmds.setAttr("%s.jointOrient"%child, *ro[0])
            cmds.setAttr("%s.rotate"%child, 0,0,0)
        return True

    for driver, driven in zip(conns[1::2], conns[::2]):
        driver = driver.replace("worldMatrix", "worldInverseMatrix")
        driven = driven.replace("matrix", "bindPreMatrix")
        cmds.connectAttr(driver, driven)

    return True


''' extra joint tools:
5. create joint on selection (vertex position, face orientaton etc.) usin L or T shape based on selection
6. add remove joint on current chain
7. add orient to rotation, add rotation to orient, and use rotation axis (also add query)
8. parent without transform

9 allign orientation from 1 to another joint (with or without spacing) (use orientation from first to last)
10 allign orientation based on plane
11. allign orientation manually
12. place/generate joints on curve/between selection
'''

def drawStyle(inSelection, style = False, progressBar = None):
    percentage = 99.0 / len(inSelection)
    for index, jnt in enumerate(inSelection):
        if cmds.objectType(jnt) != "joint":
            continue
        cmds.setAttr("%s.drawStyle"%jnt, int(not style) * 2 )
        utils.setProgress(index * percentage, progressBar, "set drawStyle")
    utils.setProgress(100, progressBar, "set drawStyle")

def segmentScale(inSelectio, compensate = False, progressBar = None):
    percentage = 99.0 / len(inSelection)
    for index, jnt in enumerate(inSelection):
        if cmds.objectType(jnt) != "joint":
            continue
        cmds.setAttr("%s.segmentScaleCompensate"%jnt, compensate )
        utils.setProgress(index * percentage, progressBar, "set sgement scale")
    utils.setProgress(100, progressBar, "set sgement scale")

def localRotateAxis(inSelection, showAxis = False, progressBar = None):
    percentage = 99.0 / len(inSelection)
    for index, jnt in enumerate(inSelection):
        if cmds.objectType(jnt) != "joint":
            continue
        cmds.setAttr("%s.displayLocalAxis"%jnt, showAxis )
        utils.setProgress(index * percentage, progressBar, "set LRA")
    utils.setProgress(100, progressBar, "set LRA")

def mirrorJoints(inSelection, mirrorAxis = "X", behaviour = True, searchReplace =('L_', 'R_') , worldSpace = True,  progressBar = None):
    if type(mirrorAxis) == int:
        mirrorAxis = "XYZ"[ mirrorAxis ]
    _mirrorSetup = { "X" : [ False, False, True ],
                     "Y" : [ False, True, False ],
                     "Z" : [ True, False, False ]}

    percentage = 79.0 / len(inSelection)
    parentInfo = {}
    for index, jnt in enumerate(inSelection):
        if cmds.objectType(jnt) != "joint":
            continue
        parent = None
        if worldSpace:
            parent = cmds.listRelatives(jnt, p=1, f=1)[0] or None
        if parent != None:
            cmds.parent(jnt, w=1)
        parentInfo[jnt] == parent

        cmds.mirrorJoint(jnt, mxy=_mirrorSetup[mirrorAxis.upper()][0], 
                              mxz=_mirrorSetup[mirrorAxis.upper()][1], 
                              myz=_mirrorSetup[mirrorAxis.upper()][2], 
                              mirrorBehavior=behaviour,
                              searchReplace=searchReplace )
        utils.setProgress(index * percentage, progressBar, "mirror joints")
    
    percentage = 20.0/len(list(parentInfo.keys()))
    for key, value in parentInfo.items():
        _value = value.replace(*searchReplace)
        if cmds.objExists(_value):
            value = _value
        cmds.parent(key.replace(*searchReplace), value)
        utils.setProgress((index * percentage) + 79,0, progressBar, "reparent mirrored joints")

    utils.setProgress(100, progressBar, "mirrored joints")

def jointLookat(point, pointAt, normal = None, space = enumerators.Space.Global,primaryAxis =enumerators.AxisEnumerator.PosAxisX, secondaryAxis = enumerators.AxisEnumerator.PosAxisY, progressBar = None):
    point = mathUtils.toVec3(point)
    pointAt = mathUtils.toVec3(pointAt)
    if space == enumerators.Space.Local:
        pointAt = pointAt + point
    
    if not normal is None:
        normal = mathUtils.toVec3(normal)
        if space == enumerators.Space.Local:
            normal = normal + point

    matrix = mathUtils.lookAt(point, pointAt, normal, primaryAxis, secondaryAxis)
    jnt = cmds.createNode("joint")
    cmds.xform( jnt, ws=1, m = mathUtils.matrixToFloatList(matrix) )

# :Todo: update the setup here using the following methods
# orient based on every joint
# orient based on triangles                          * <  use this bone for rotation
# orient based on average normals                   / \
# orient last joint based on parent                /   \ 
#                                                 /     \
# make sure to orient based on the triangle edge 。       .
#                                                ^ if this is the first the use the same up as the second! 
def orientJointChain( average = False, primaryAxis=enumerators.AxisEnumerator.PosAxisX, secondaryAxis = enumerators.AxisEnumerator.PosAxisY, progressBar = None):
    sel = shared.getHierarchySelection("joint")

    def getWsVec(inObject):
        return MVector(*cmds.xform(inObject, q=1, ws=1, t=1))

    def getChildMatrix(inObject):
        _retDict = {}
        endChildren = cmds.listRelatives(inObject, c=1, f=1) or []
        for child in endChildren:
            _retDict[child] = cmds.xform(child, q=1, ws=1, m=1)  
        return _retDict
    
    _infoDict = {}
    _setupDict = {}
    for index, jnt in enumerate(sel):

        cur = getWsVec(jnt)
        if jnt == sel[-1]:
            aim1, up1, pos1 = _setupDict[sel[index - 1]] 
            aim = cur + (aim1 - pos1)
            up = cur + (up1 - pos1)
        elif jnt == sel[-2]:
            aim = getWsVec(sel[index + 1])
            up = getWsVec(sel[index - 1])
        else:
            aim = getWsVec(sel[index + 1])
            up = getWsVec(sel[index + 2])

        _setupDict[jnt] = [aim, up, cur]

        nDict = getChildMatrix(jnt)
        for key, val in nDict.items():
            if key in sel:
                continue
            _infoDict[key] = val 

    if average:
        _up = MVector()
        for _, up, _ in _setupDict.values():
            _up += up
        avg = _up / len(_setupDict.keys()) 
        for key, (aim, up, pos) in _setupDict.items():
            _setupDict[key]  = [aim, avg, pos]
    else:
        _prev = MVector()

        for index, (obj, (aim, up, pos)) in enumerate(_setupDict.items()):
            if index == -1:
                _prev = (up - pos).normal()
                continue
            _cur = (up - pos).normal()
            if (_prev * _cur) < 0:
                up = pos + (_cur * -1)
            _setupDict[obj] = [aim, up, pos]

    _toSetup = _setupDict.keys()
    _toSetup.sort(key=len)
    for index, obj in enumerate(_toSetup):
        aim, up, pos = _setupDict[obj]
        cur = (up - pos).normal()
        aimMatrix = mathUtils.lookAt(pos, aim, up, primaryAxis, secondaryAxis, False)
        cmds.xform(obj, ws=1, m=mathUtils.matrixToFloatList(aimMatrix))

    _toFix = _infoDict.keys()
    _toFix.sort(key=len)
    for obj in _toFix:
        cmds.xform(obj, ws=1, m=_infoDict[obj])        

class jointRotation(object):
    def __init__(self):
        self._joints = []
        self._cleanup = []
    
    def createJointRotators(self):
        _sel = cmds.ls(sl=1)
        sel = _sel[::]
        for s in _sel:
            sel.extend(cmds.listRelatives(s,ad=1, type="transform"))
        for obj in sel:
            loc = cmds.spaceLocator(n="%sGuide"%obj)[0]
            cmds.setAttr("%s.displayLocalAxis"%loc, 1)
            grp = cmds.group(loc, n="%sGuideOfst"%obj)
            cmds.matchTransform(grp, obj, pos=1, rot=1)
            pc = cmds.parentConstraint(loc, obj, mo=0)[0]
            self._cleanup.extend([grp, pc]) 
        self._joints.extend(cmds.ls(sel, type="joint"))

    def cleanupRotations(self):
        if self._joints != []:
            freezeSkinnedJoints(self._joints)
        if self._cleanup != []:
            cmds.delete(self._cleanup)
        self._cleanup=[]
        self._joints=[]