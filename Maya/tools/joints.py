from SkinningTools.UI.utils import remap
from SkinningTools.py23 import *
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI import utils
from SkinningTools.Maya.tools import shared, mathUtils, mesh
from maya import cmds, mel
from maya.api.OpenMaya import MSpace, MFnTransform, MVector, MFnMesh


# @note all functions must have connection wiuth progressbar and sensible progress messages,
# look into warning messages later
@shared.dec_undo
def autoLabelJoints(inputLeft="L_*", inputRight="R_*", progressBar=None):
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


def freezeRotate(inJnts, progressBar=None):
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
    # @note: this will not work when joints are connected through ik-handle!
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


@shared.dec_undo
def removeBindPoses(progressBar=None):
    dagPoses = cmds.ls(type="dagPose")
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
    sc = shared.skinCluster(inMesh, silent=True)
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
def BoneMove(joint1, joint2, skin, progressBar=None):
    sc = shared.skinCluster(skin, True)
    infjnts = getInfluencingJoints(sc)
    addCleanJoint([joint1, joint2], skin)

    meshShapeName = cmds.listRelatives(skin, s=True, f=1)[0]
    outInfluencesArray = shared.getWeights(skin)

    infLengt = len(infjnts)
    pos1 = infjnts.index(joint1)
    pos2 = infjnts.index(joint2)

    lenOutInfArray = len(outInfluencesArray)
    amountToLoop = (lenOutInfArray / infLengt)
    percentage = 99.0 / amountToLoop
    for j in range(amountToLoop):
        newValue = outInfluencesArray[(j * infLengt) + pos2] + outInfluencesArray[(j * infLengt) + pos1]
        outInfluencesArray[(j * infLengt) + pos2] = newValue
        outInfluencesArray[(j * infLengt) + pos1] = 0.0
        utils.setProgress(j * percentage, progressBar, "moving joint influences")

    shared.setWeigths(skin, outInfluencesArray)
    utils.setProgress(100, progressBar, "moved joint influences")
    return True


@shared.dec_undo
def BoneSwitch(joint1, joint2, skin, progressBar=None):
    sc = shared.skinCluster(skin, True)
    addCleanJoint([joint1, joint2], skin)

    _connectDict = shared.getJointIndexMap(sc)
    for key, val in _connectDict.items():
        cmds.disconnectAttr('%s.worldMatrix' % key, '%s.matrix[%i]' % (sc, val))
        cmds.disconnectAttr("%s.lockInfluenceWeights" % key, "%s.lockWeights[%s]" % (sc, val))
    utils.setProgress(33, progressBar, "get influence map")

    cmds.connectAttr(joint1 + '.worldMatrix', '%s.matrix[%i]' % (sc, _connectDict[joint2]), f=1)
    cmds.connectAttr(joint2 + '.worldMatrix', '%s.matrix[%i]' % (sc, _connectDict[joint1]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint1, "%s.lockWeights[%s]" % (sc, _connectDict[joint2]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint2, "%s.lockWeights[%s]" % (sc, _connectDict[joint1]), f=1)
    utils.setProgress(66, progressBar, "switch influences")

    resetSkinnedJoints([joint1, joint2], sc)
    utils.setProgress(100, progressBar, "switched bones")
    return True


@shared.dec_undo
def ShowInfluencedVerts(inMesh, jnts, progressBar=None):
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
        res = [idx for idx, val in enumerate(w) if val > 0.0]
        for i in res:
            toSelect.append("%s.vtx[%i]" % (inMesh, i))
        utils.setProgress(percentage * index, progressBar, "gather weight information")

    cmds.select(toSelect, r=1)
    utils.setProgress(100, progressBar, "show influenced vertices")
    return True


@shared.dec_undo
def removeJointBySkinPercent(skinObject, jointsToRemove, sc, progressBar=None):
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


@shared.dec_undo
def deleteJointSmart(jointsToRemove, progressBar=None):
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


@shared.dec_undo
def removeJoints(skinObjects, jointsToRemove, useParent=True, delete=True, fast=False, progressBar=None):
    skinClusters = []

    # @todo: make this smarter, make it look for all skinclusters when deleting the joint to keep the joint as clean as possible
    # if delete:
    #     for joint in jointsToRemove:
    #         skinClusters.append(cmds.listConnections("%s.worldMatrix[0]"%joint, type="skinCluster", p=1))

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
    objs = cmds.ls(sl=1)
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


def getInfluencingJoints(inObject, progressBar=None):
    if cmds.objectType(inObject) == "mesh":
        inObject = shared.skinCluster(inObject, silent=True)
    if inObject != None:
        jointInfls = cmds.ls(cmds.listConnections("%s.matrix" % inObject, source=True), l=1)
        utils.setProgress(100, progressBar, "get influencing joints")
        return jointInfls


@shared.dec_undo
def removeUnusedInfluences(inObject, progressBar=None):
    # @note: this will only remove the current connection with joints
    # check if we can remap the nodes index connections in weights, influenceColor, lockweights and matrix inputs
    sc = shared.skinCluster(inObject)
    jointInfls = getInfluencingJoints(sc)
    weightedInfls = cmds.skinCluster(sc, q=1, wi=1)

    toRemove = list(set(jointInfls) - set(weightedInfls))

    nodeState = cmds.getAttr("%s.nodeState" % sc)
    cmds.setAttr("%s.nodeState" % sc, 1)
    percentage = 99.0 / len(toRemove)
    index = 0
    for index, jnt in enumerate(toRemove):
        cmds.skinCluster(sc, e=1, ri=jnt)
        utils.setProgress(index * percentage, progressBar, "removing joint %s from mesh" % jnt)

    cmds.setAttr("%s.nodeState" % sc, nodeState)
    utils.setProgress(100, progressBar, "removed %i joints from influence" % (index + 1))


@shared.dec_undo
def convertClusterToJoint(inObject, jointName=None, progressBar=None):
    utils.setProgress(0, progressBar, "gather cluster data")
    shape = cmds.listRelatives(inObject, s=1, type="clusterHandle") or None
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

    cmds.matchTransform(jnt, clusterDeformer, pos=1, rot=0)

    inMesh = allConnected[0].split('.')[0]

    sc = shared.skinCluster(inMesh, True)
    cmds.skinCluster(sc, e=True, lw=False, wt=0.0, ai=jnt)

    expandedVertices = shared.convertToVertexList(inMesh)
    values = cmds.percent(clusterDeformer, inMesh, q=1, v=1)

    percentage = 99.0 / len(allConnected)
    for index, vertex in enumerate(allConnected):
        cmds.skinPercent(sc, vertex, tv=[jnt, values[indices[index]]])
        utils.setProgress(index * percentage, progressBar, "setting cluster weights")

    cmds.delete(inObject)
    utils.setProgress(100, progressBar, "converted cluster to joint")
    return jnt


@shared.dec_undo
def convertVerticesToJoint(inComponents, jointName=None, progressBar=None):
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
    return jnt


def convertClustersToJoint(inMesh, inClusters, progressBar=True):
    meshDag = shared.getDagpath(inMesh)
    mfnMesh = MFnMesh(meshDag)
    origPos = mfnMesh.getPoints(MSpace.kObject)
    vertices = {}
    for index, vtx in enumerate(origPos):
        vertices[index] = {}

    jnts = []
    for deform in inClusters:
        deformDag = shared.getDagpath(deform)

        jnt = cmds.createNode("joint", n="temp%s" % (deform))
        cmds.matchTransform(jnt, deform, pos=1, rot=1)

        mfnTrs = MFnTransform(deformDag)
        vec = MVector(1, 0, 0)
        mfnTrs.setTranslation(vec, MSpace.kTransform)

        deformPos = mfnMesh.getPoints(MSpace.kObject)
        zero = MVector(0, 0, 0)
        mfnTrs.setTranslation(zero, MSpace.kTransform)

        weights = []
        for index, origVec in enumerate(origPos):
            deformVec = deformPos[index]
            vertices[index][jnt] = (origVec - deformVec).length()
        jnts.append(jnt)

    sc = shared.skinCluster(inMesh)
    if sc is not None:
        addCleanJoint(jnts, inMesh)
    else:
        sc = cmds.skinCluster(jnts, inMesh, tsb=1)[0]

    for key, value in vertices.items():
        vtx = "%s.vtx[%i]" % (inMesh, key)
        tv = []
        totalVal = 0
        for jnt in jnts:
            totalVal += value[jnt]
        if totalVal < 1e-6:
            continue

        for jnt in jnts:
            weight = value[jnt]
            if totalVal > 1.0:
                weight = remap(0, totalVal, 0, 1, weight)
            tv.append([jnt, weight])

        cmds.skinPercent(sc, vtx, transformValue=tv)
