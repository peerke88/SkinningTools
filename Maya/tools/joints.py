from SkinningTools.py23 import *
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI import utils 
from SkinningTools.Maya.tools import shared
from SkinningTools.Maya.tools import mathUtils
from maya import cmds, mel

# @note all functions must have connection wiuth progressbar and sensible progress messages, 
# look into warning messages later
@shared.dec_undo
def autoLabelJoints(inputLeft, inputRight, progressBar=None):
    def SetAttrs(side, type, name):
        for attr in [ "side", "type", "otherType", "drawLabel"]:
            cmds.setAttr("%s.%s"%(bone, attr), l=0)
        
        cmds.setAttr(bone + '.side', side)
        cmds.setAttr(bone + '.type', type)
        cmds.setAttr(bone + '.otherType', name, type="string")
        cmds.setAttr(bone + '.drawLabel', 1)

    allJoints = cmds.ls(type="joint") or None
    if allJoints == None:
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
    iteration3 = 0

    for iteration1, bone in enumerate(leftJoints):
        SetAttrs(1, 18, str(bone).replace(str(inputLeft).strip("*"), ""))
        allJoints.remove(bone)
        utils.setprogress((iteration1 + 1) * percentage, progressBar, "Setting left Side")

    for iteration2, bone in enumerate(rightJoints):
        SetAttrs(2, 18, str(bone).replace(str(inputRight).strip("*"), ""))
        allJoints.remove(bone)
        utils.setprogress((iteration1 + iteration2) * percentage, progressBar, "Setting right Side")

    for iteration3, bone in enumerate(allJoints):
        SetAttrs(0, 18, str(bone))
        utils.setprogress((iteration1 + iteration2 + iteration3) * percentage, progressBar, "Setting center")

    for bone in allFoundjoints:
        cmds.setAttr(bone + '.drawLabel', 0)

    utils.setprogress(100, progressBar, "labeling joints")
    return True

@shared.dec_undo
def resetToBindPoseobject(inObject, progressBar = None):
    skinCluster = shared.skinCluster(inObject, silent=True)
    if skinCluster == None:
        return
    
    percentage = 99.0/len(infjnts)
    infjnts = cmds.listConnections("%s.matrix"%skinCluster, source=True)
    for i, joint in enumerate(infjnts):
        prebindMatrix = cmds.getAttr("%s.bindPreMatrix[%s]"%(skinCluster, i))

        matrix = mathUtils.matrixToFloatList(mathUtils.floatToMatrix(prebindMatrix).inverse())
        cmds.xform(joint, ws=True, m=matrix)
        utils.setprogress(i * percentage, progressBar, "rest pose on %s"%joint)
    
    utils.setprogress(100, progressBar, "bindposes reset")
    return True

@shared.dec_undo
def resetSkinnedJoints(inJoints = None, inSkinCluster=None, progressBar = None):
    joints = inJoints
    if joints == None:
        joints = cmds.ls(sl=0, type= "joint")

    percentage = 99.0/len(joints)
    for i, joint in enumerate(joints):
        skinClusterPlugs = cmds.listConnections("%s.worldMatrix[0]"%joint, type="skinCluster", p=1)
        if inSkinCluster is not None and skinClusterPlugs is not None:
            _notFound = True
            for sc in skinClusterPlugs:
                if inSkinCluster in sc:
                    skinClusterPlugs = [sc]
                    _notFound = False
            if _notFound:
                skinClusterPlugs = []

        if skinClusterPlugs:
            for skinClstPlug in skinClusterPlugs:
                index = skinClstPlug[skinClstPlug.index("[") + 1: -1]
                skinCluster = skinClstPlug[: skinClstPlug.index(".")]
                curInvMat = cmds.getAttr("%s.worldInverseMatrix"%joint)
                cmds.setAttr("%s.bindPreMatrix[%s]"%(skinCluster, index), type="matrix", *curInvMat)
            try:
                cmds.skinCluster(skinCluster, e=True, recacheBindMatrices=True)
            except RuntimeError:
                pass
        else:
            if inSkinCluster is not None and inJoints is not None:
                print("%s not attached to %s!" %(joint, inSkinCluster))
        utils.setprogress(i * percentage, progressBar, "resetting %s"%joint)
    utils.setprogress(100, progressBar, "joints reset")
    return True

def freezeScale(joints, progressBar = None):
    percentage = 99.0/len(joints)
    wms = []
    for i, joint in enumerate(joints):
        wm = cmds.xform(joint, q=1, ws=1, m=1)
        mm = mathUtils.floatToMatrix(wm)
        x = mathUtils.getVectorFromMatrix(mm, 0).normal()
        y = mathUtils.getVectorFromMatrix(mm, 1).normal()
        z  = x ^ y
        pos = mathUtils.getVectorFromMatrix(mm, 3)
        nm = mathUtils.vectorsToMatrix([x,y,z, pos])
        wms.append(nm)
        utils.setprogress(i * percentage, progressBar, "freeze scale on %s"%joint)
   
    for index, jnt in enumerate(joints):
        fm = mathUtils.matrixToFloatList(wms[index])
        cmds.xform(jnt, ws=1, m = fm)
    utils.setprogress(100, progressBar, "scale frozen")

def freezeRotate(joints, progressBar = None):
    percentage = 99.0/len(joints)
    for i, joint in enumerate(joints):
        if cmds.objectType(joint) != "joint":
            continue
        dup = cmds.duplicate(joint, rc=1)[0]
        ch = cmds.listRelatives(dup, children=1, f=1)
        if ch:
            cmds.delete(ch)

        cmds.makeIdentity(dup, apply=1, t=0, r=1, s=0)
        jo = cmds.getAttr(dup + '.jo')[0]

        cmds.setAttr(joint + '.jo', jo[0], jo[1], jo[2])
        cmds.delete(dup)

        try:
            cmds.setAttr(joint + '.r', 0, 0, 0)
        except:
            pass
        utils.setprogress(i * percentage, progressBar, "freeze rotate on %s"%joint)
    utils.setprogress(100, progressBar, "rotate frozen")
    return joints

@shared.dec_undo
def freezeSkinnedJoints(joints, rotate = 1, scale = 1, progressBar = None):
    #@note: this will not work when joints are connected through ik-handle!
    if len(joints) == 1:
        joints = shared.selectHierarchy(joints)
    if rotate:
        freezeRotate(joints)
        utils.setprogress(33, progressBar, "freezeRotate")
    if scale:
        freezeScale(joints)
        utils.setprogress(66, progressBar, "freezeScale")
    resetSkinnedJoints(joints)
    utils.setprogress(100, progressBar, "freeze skinned joints")

@shared.dec_undo
def removeBindPoses(progressBar = None):
    dagPoses = cmds.ls(type="dagPose")
    percentage = 99.0 / len(dagPoses)
    for index, dagPose in enumerate(dagPoses):
        if not cmds.getAttr("%s.bindPose" % dagPose):
            continue
        cmds.delete(dagPose)
        utils.setprogress(index * percentage, progressBar, "delete bindposes")
    utils.setprogress(100, progressBar, "delete bindposes")
    return True

@shared.dec_undo
def addCleanJoint(joints, mesh, progressBar = None):
    skinClusterName = shared.skinCluster(mesh, silent=True)
    percentage = 99.0 / len(joints)
    if skinClusterName != None:
        jointInfls = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
        for index, joint in enumerate(joints):
            if joint in jointInfls:
                continue
            cmds.skinCluster(skinClusterName, e=True, lw=False, wt=0.0, ai=joint)
            utils.setprogress(index * percentage, progressBar, "adding joints")
    utils.setprogress(100, progressBar, "adding joints")
    return True

@shared.dec_undo
def BoneMove(joint1, joint2, skin, progressBar = None):
    skinClusterName = shared.skinCluster(skin, True)
    infjnts = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
    addCleanJoint([joint1, joint2], skin)
    
    meshShapeName = cmds.listRelatives(skin, s=True, f=1)[0]
    outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)

    infLengt = len(infjnts)
    pos1 = infjnts.index(joint1)
    pos2 = infjnts.index(joint2)

    lenOutInfArray = len(outInfluencesArray)
    amountToLoop = (lenOutInfArray / infLengt)
    percentage = 99.0 / len(amountToLoop)
    for j in xrange(amountToLoop):
        newValue = outInfluencesArray[(j * infLengt) + pos2] + outInfluencesArray[(j * infLengt) + pos1]
        outInfluencesArray[(j * infLengt) + pos2] = newValue
        outInfluencesArray[(j * infLengt) + pos1] = 0.0
        utils.setprogress(j * percentage, progressBar, "moving joint influences")

    cmds.SkinWeights([meshShapeName, skinClusterName], nwt=outInfluencesArray)
    utils.setprogress(100, progressBar, "moved joint influences")
    return True

@shared.dec_undo
def BoneSwitch(joint1, joint2, skin, progressBar = None):
    skinClusterName = shared.skinCluster(skin, True)
    addCleanJoint([joint1, joint2], skin)

    _connectDict = shared.getJointIndexMap(skinClusterName)
    for key, val in _connectDict.iteritems():
        cmds.disconnectAttr('%s.worldMatrix'%key, '%s.matrix[%i]'%(skinClusterName,val))
        cmds.disconnectAttr("%s.lockInfluenceWeights"%key, "%s.lockWeights[%s]" % (skinClusterName, val))
    utils.setprogress(33, progressBar, "get influence map")

    cmds.connectAttr(joint1 + '.worldMatrix', '%s.matrix[%i]'%(skinClusterName,_connectDict[joint2]), f=1)
    cmds.connectAttr(joint2 + '.worldMatrix', '%s.matrix[%i]'%(skinClusterName,_connectDict[joint1]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint1, "%s.lockWeights[%s]" % (skinClusterName, _connectDict[joint2]), f=1)
    cmds.connectAttr("%s.lockInfluenceWeights" % joint2, "%s.lockWeights[%s]" % (skinClusterName, _connectDict[joint1]), f=1)
    utils.setprogress(66, progressBar, "switch influences")

    resetSkinnedJoints([joint1, joint2], skinClusterName)
    utils.setprogress(100, progressBar, "switched bones")
    return True

@shared.dec_undo
def ShowInfluencedVerts(inMesh, joints, progressBar=None):
    percentage = 100.0 / len(joints)
    sc = shared.skinCluster(inMesh, True)
    
    vtxWeigths = cmds.getAttr("%s.weightList[:]"%sc)
    vtxCount = len(vtxWeigths )
    _connectDict = shared.getJointIndexMap(sc)

    toSelect = []
    for index, jnt in enumerate(joints): 
        if jnt not in _connectDict.keys():
            continue
        w = cmds.getAttr("%s.weightList[0:%i].weights[%i]"%(sc, vtxCount - 1, _connectDict[jnt]))
        res = [idx for idx, val in enumerate(w) if val > 0.0] 
        for i in res:
            toSelect.append("%s.vtx[%i]"%("body_low", i))
        utils.setprogress(percentage * index, progressBar, "gather weight information")

    cmds.select(toSelect, r=1)
    shared.doCorrectSelectionVisualization(inMesh)
    utils.setprogress(100, progressBar, "show influenced vertices")
    return toSelect

@shared.dec_undo
def removeJointBySkinPercent(skinObject, jointsToRemove, skinClusterName, progressBar = None):
    verts = ShowInfluencedVerts(skinObject, jointsToRemove, progressBar=None)
    if verts == None or len(verts) == 0:
        return

    jnts = []
    percentage = 99.0 / len(jointsToRemove)
    for index, jnt in enumerate(jointsToRemove):
        if not jnt in jointsAttached:
            continue
        jnts.append((jnt, 0.0))
        utils.setprogress(index * percentage, progressBar, "removing joint weights")

    cmds.select(verts, r=1)
    cmds.skinPercent(skinClusterName, tv=jnts, normalize=True)
    utils.setprogress(100, progressBar, "joint weights removed")

@shared.dec_undo
def deleteJointSmart(jointsToRemove, progressBar = None):
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
        utils.setprogress(index * percentage, progressBar, "reparenting joints")
    cmds.delete(jointsToRemove)
    utils.setprogress(100, progressBar, "deleted joints")

@shared.dec_undo
def removeJoints(skinObjects, jointsToRemove, useParent=True, delete=True, fast=False, progressBar=None):
    skinClusters = []
    skinPercentage = 100.0 / len(skinObjects)

    for skinIter, skinObject in enumerate(skinObjects):
        skinClusterName = SkinningTools.skinCluster(skinObject, True)
        if skinClusterName == None:
            continue

        jointsAttached = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
        if fast:
            removeJointBySkinPercent(skinObject, jointsToRemove, skinClusterName, progressBar)
            skinClusters.append(skinClusterName)
            utils.setprogress(skinIter * skinPercentage, progressBar, "removing influences")
            continue

        if not useParent:
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
            if useParent:
                bone2 = cmds.listRelatives(jnt, parent=True)[0] or None
                if bone2 == None:
                    removePos = cmds.xform(jnt, q=True, ws=True, t=True)
                    pts = sourceKDTree.query(query_point=removePos, t=1)
                    for index, position in enumerate(sourceJoints):
                        if position[1] != pts[0]:
                            continue
                        bone2 = position[0]
            else:
                removePos = cmds.xform(jnt, q=True, ws=True, t=True)
                pts = sourceKDTree.query(query_point=removePos, t=1)
                for index, position in enumerate(sourceJoints):
                    if position[1] != pts[0]:
                        continue
                    bone2 = position[0]

            BoneMove(bone1, bone2, skinObject)

            utils.setprogress((jntIter + 1) * jntPercentage, progressBar, "remapping joints influences")

        skinClusters.append(skinClusterName)

    for skinClusterName in skinClusters:
        jointsAttached = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
        for jnt in jointsToRemove:
            if not jnt in jointsAttached:
                continue
            cmds.skinCluster(skinClusterName, e=True, ri=jnt)

    print("removed these joints from influence: ", jointsToRemove)
    if delete:
        deleteJointSmart(jointsToRemove)

    utils.setprogress(100, progressBar, "removed joints")
    
    return True

def comparejointInfluences(skinObjects, query=False, progressBar=None):
    objs = cmds.ls(sl=1)
    joints = []
    for obj in skinObjects:
        skinClusterName = shared.skinCluster(obj, True)
        jnt = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
        joints.append(jnt)
    utils.setprogress(33, progressBar, "get joint maps")

    setList = []
    for i, s in enumerate(joints):
        setList.append(set(joints[i]).difference(*(joints[:i] + joints[i+1:])))

    utils.setprogress(66, progressBar, "find differences")
    
    joints = []
    for jntSet in setList:
        joints.extend(list(jntSet))

    if query == True:
        utils.setprogress(100, progressBar, "found missing influences")
        if joints:
            return joints
        return None

    for obj in skinObjects:
        addCleanJoint(joints, obj)
    utils.setprogress(100, progressBar, "unified joint maps")
    return True

def getMeshesInfluencedByJoint(currentJoints, progressBar=None):
    allSkinClusters = cmds.ls(type="skinCluster")
    meshes = []
    percentage = 99.0 / len(allSkinClusters)
    for index, scl in enumerate(allSkinClusters):
        joints = cmds.listConnections("%s.matrix"%scl, source=True)
        geo = cmds.skinCluster(scl, q=1, g=1)[0]
        for jnt in currentJoints:
            if jnt in joints and not geo in meshes:
                meshes.append(geo)
        utils.setprogress(index * percentage, progressBar, "listing connections")
    utils.setprogress(100, progressBar, "gather mesh information")
    return meshes

def getInfluencingJoints(object, progressBar=None):
    skinClusterName = SkinningTools.skinCluster(object, silent=True)
    if skinClusterName != None:
        jointInfls = cmds.listConnections("%s.matrix"%skinClusterName, source=True)
        utils.setprogress(100, progressBar, "get influencing joints")
        return jointInfls

@shared.dec_undo
def removeUnusedInfluences(inObject, progressBar = None):
    # @note: this will only remove the current connection with joints
    # check if we can remap the nodes index connections in weights, influenceColor, lockweights and matrix inputs
    sc = shared.skinCluster(inObject)
    jointInfls = cmds.listConnections("%s.matrix"%sc, source=True)
    weightedInfls = cmds.skinCluster(sc, q=1, wi=1)

    toRemove = list(set(jointInfls)-set(weightedInfls))

    nodeState= cmds.getAttr("%s.nodeState"%sc)
    cmds.setAttr("%s.nodeState"%sc, 1)
    percentage = 99.0 / len(toRemove)
    for index, jnt in enumerate(toRemove):
        cmds.skinCluster(sc, e=1, ri = jnt)
        utils.setprogress(index * percentage, progressBar, "removing joint %s from mesh"%jnt)

    cmds.setAttr("%s.nodeState"%sc, nodeState)
    utils.setprogress(100, progressBar, "removed %i joints from influence"%(index+1))

