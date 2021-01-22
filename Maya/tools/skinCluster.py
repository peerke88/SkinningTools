# -*- coding: utf-8 -*-
import math, itertools
from decimal import Decimal
from heapq import nsmallest

from SkinningTools.py23 import *
from SkinningTools.Maya.tools import shared, joints, mesh
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *

from maya.api import OpenMaya
from maya import cmds

_DEBUG = getDebugState()

def checkBasePose(skinCluster):
    """ check if the current object is in bindpose, using the prebind matrices and the worldmatrices of the joints
    :note: only compare worldspace translate values as precision might be difficult here

    :param skinCluster: the current skincluster to check
    :type skinCluster: string
    :return: `True` if the setup is in bindpose, `False` if not
    :rtype: bool
    """
    bp = cmds.listConnections("%s.bindPose" % skinCluster, source=True) or None
    if bp:
        return cmds.dagPose(bp[0], q=True, atPose=True) is not None
    jointMap = shared.getJointIndexMap(skinCluster)

    for key, val in jointMap.items():
        prebind = cmds.getAttr("%s.bindPreMatrix[%s]" % (skinCluster, val))[-4:-1]
        curInvMat = cmds.getAttr("%s.worldInverseMatrix" % key)[-4:-1]
        if not compare_vec3(prebind, curInvMat):
            return False
    return True


@shared.dec_undo
def forceCompareInfluences(meshes):
    """ force the joints on the current meshes to be shared, this to make sure we cannot apply weights to joints that dont exist on the skincluster

    :param meshes: the meshes on which all joints need to be shared
    :type meshes: list
    :return: `True` if the joints are the same for all meshes, `False` if not
    :rtype: bool
    """
    compared = joints.comparejointInfluences(meshes, True)
    outOfPose = False
    for inMesh in meshes:
        shared.skinCluster(inMesh, True)
        if checkBasePose(skinClusterName):
            continue
        outOfPose = True

    if compared is None:
        return True

    if not outOfPose:
        joints.comparejointInfluences(meshes)
        return True

    result = cmds.confirmDialog(title='Confirm',
                                message='object is not in BindPose,\ndo you want to continue out of bindpose?\npressing "No" will exit the operation! ',
                                button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
    if result == "Yes":
        joints.comparejointInfluences(meshes)
        return True
    return False


def getVertOverMaxInfluence(inObject, maxInfValue=8, progressBar=None):
    """ get the information of the objects skincluster on if there are too many joints driving a single vertex

    :param inObject: the object to gather information from
    :type inObject: string
    :param maxInfValue: the amount of joints that are allowed to deform a vertex at once
    :type maxInfValue: int 
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: vertices that have too much influences, dictionary on the specific vertex on how many influences are present
    :rtype: list
    """
    setProgress(0, progressBar, "get max info")
    sc = shared.skinCluster(inObject, True)
    vtxWeights = cmds.getAttr("%s.weightList[:]" % sc)
    vtxCount = len(vtxWeights)

    percentage = 99.0 / vtxCount
    indexOverMap = {}
    namedIndex = []
    for i in range(vtxCount):
        amount = len(cmds.getAttr("%s.weightList[%i].weights" % (sc, i))[0])
        if amount > maxInfValue:
            indexOverMap[i] = amount
            namedIndex.append("%s.vtx[%i]" % (inObject, i))
        setProgress(i * percentage, progressBar, "checking vertices")
    setProgress(100, progressBar, "vertices checked on %s" % inObject)
    return namedIndex, indexOverMap


@shared.dec_undo
def setMaxJointInfluences(inObject=None, maxInfValue=8, progressBar=None):
    """ set the information of the objects skincluster if there are too many joints driving a single vertex to be under that limit

    :param inObject: the object to gather information from
    :type inObject: string
    :param maxInfValue: the amount of joints that are allowed to deform a vertex at once
    :type maxInfValue: int 
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed, 
    :rtype: bool
    """
    toMuchinfls, indexOverMap = getVertOverMaxInfluence(inObject=inObject, maxInfValue=maxInfValue, progressBar = progressBar)
    if toMuchinfls == []:
        return
    setProgress(0, progressBar, "get max info")

    inObject = shared.getParentShape(inObject)
    sc = shared.skinCluster(inObject, True)
    shape = cmds.listRelatives(inObject, s=True)[0]

    outInfluencesArray = shared.getWeights(inObject)

    infjnts = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)
    infLengt = len(infjnts)

    lenOutInfArray = len(outInfluencesArray)

    percentage = 99.0 / len(toMuchinfls)
    for index, vertex in enumerate(toMuchinfls):
        values = cmds.skinPercent(sc, vertex, q=1, v=1)
        curAmountValues = len(values)
        toPrune = curAmountValues - maxInfValue

        pruneFix = max(nsmallest(toPrune, values)) + 0.001
        cmds.skinPercent(sc, vertex, pruneWeights=pruneFix)
        setProgress(index * percentage, progressBar, "removing influences")

    cmds.skinCluster(sc, e=True, fnw=1)

    cmds.setAttr("%s.maxInfluences" % sc, maxInfValue)
    cmds.setAttr("%s.maintainMaxInfluences" % sc, 1)

    setProgress(100, progressBar, "set maximum influences")

    return True


@shared.dec_undo
def execCopySourceTarget(TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection, smoothValue=1, progressBar=None):
    """ copy skincluster information from one vertex group to another based on closest proximity

    :param TargetSkinCluster: the skincluster to gather information from
    :type TargetSkinCluster: string
    :param SourceSkinCluster: the skincluster to send information to
    :type SourceSkinCluster: string
    :param TargetSelection: the vertex selection to copy from
    :type TargetSelection: list
    :param SourceSelection: the vertex selection to copy to
    :type SourceSelection: list
    :param smoothValue: amount of closest positions to gather data from
    :type smoothValue: int
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed, vertices if requested
    :rtype: bool
    """
    setProgress(0, progressBar, "get source info")

    targetMesh = TargetSelection[0].split('.')[0]
    sourceMesh = SourceSelection[0].split('.')[0]

    if targetMesh != sourceMesh:
        result = forceCompareInfluences([targetMesh, sourceMesh])
        if not result:
            return

    targetJoints = joints.getInfluencingJoints(targetMesh)
    sourceJoints = joints.getInfluencingJoints(sourceMesh)
    jointAmount = len(sourceJoints)
    skinClusterName = shared.skinCluster(targetMesh, True)

    targetInflArray = shared.getWeights(targetMesh)
    sourceInflArray = shared.getWeights(sourceMesh)

    allVerticesSource = shared.convertToVertexList(sourceMesh)
    allVerticesTarget = shared.convertToVertexList(targetMesh)

    sourcePoints = []
    sourcePointPos = []
    for sourceVert in SourceSelection:
        pos = cmds.xform(sourceVert, q=True, ws=True, t=True)
        sourcePoints.append(pos)
        sourcePointPos.append([sourceVert, pos])
    sourceKDTree = KDTree.construct_from_data(sourcePoints)

    percentage = 99.0 / len(TargetSelection)
    weightlist = []
    for tIndex, targetVertex in enumerate(TargetSelection):
        pos = cmds.xform(targetVertex, q=True, ws=True, t=True)
        pts = sourceKDTree.query(query_point=pos, t=smoothValue)

        weights = []
        distanceWeightsArray = []
        totalDistanceWeights = 0
        for positionList in sourcePointPos:
            for index in range(smoothValue):
                if pts[index] != positionList[1]:
                    continue
                length = math.sqrt(pow((pos[0] - pts[index][0]), 2) +
                                   pow((pos[1] - pts[index][1]), 2) +
                                   pow((pos[2] - pts[index][2]), 2))

                distanceWeight = (1.0 / (1.0 + length))
                distanceWeightsArray.append(distanceWeight)
                totalDistanceWeights += distanceWeight

                weight = []
                indexing = allVerticesSource.index(positionList[0])
                for i in range(jointAmount):
                    weight.append(sourceInflArray[(indexing * jointAmount) + i])
                weights.append(weight)

        newWeights = []
        for index in range(smoothValue):
            for i, wght in enumerate(weights[index]):
                # distance/totalDistance is weight of the distance caluclated
                weights[index][i] = (distanceWeightsArray[index] / totalDistanceWeights) * wght

            if len(newWeights) == 0:
                newWeights = list(range(len(weights[index])))
                for j in range(len(newWeights)):
                    newWeights[j] = 0.0

            for j in range(len(weights[index])):
                newWeights[j] = newWeights[j] + weights[index][j]

        divider = 0.0
        for wght in newWeights:
            divider = divider + wght
        weightsCreation = []
        for jnt in targetJoints:
            for count, skinJoint in enumerate(sourceJoints):
                if jnt != skinJoint:
                    continue
                if divider == 0.0:
                    weightsCreation.append(newWeights[count])
                    continue
                weightsCreation.append((newWeights[count] / divider))
        weightlist.extend(weightsCreation)

        setProgress(tIndex * percentage, progressBar, "copy source > target vtx")

    index = 0
    for vertex in TargetSelection:
        number = allVerticesTarget.index(vertex)
        for jointIndex in range(jointAmount):
            weightindex = (number * jointAmount) + jointIndex
            targetInflArray[weightindex] = weightlist[index]
            index += 1

    shared.setWeights(targetMesh, targetInflArray)

    setProgress(100, progressBar, "copy from Source to Target")

    return True


@shared.dec_undo
def transferClosestSkinning(objects, smoothValue, progressBar=None):
    """ copy skincluster information from one object to others based on closest proximity

    :param objects: objects to use for data, first selected will be used to gather data, the rest will be copied to
    :type objects: list
    :param smoothValue: amount of closest positions to gather data from
    :type smoothValue: int
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "get closest info")
    baseObject = objects[0]
    origSkinCluster = shared.skinCluster(baseObject)
    origJoints = joints.getInfluencingJoints(origSkinCluster) 

    percentage = 99.0 / len(objects)
    for iteration, currentObj in enumerate(objects):
        if currentObj == baseObject:
            continue

        newSkinCluster = shared.skinCluster(currentObj, silent=True)
        if newSkinCluster is None:
            newSkinCluster = cmds.skinCluster(currentObj, origJoints)[0]
        else:
            joints.comparejointInfluences([baseObject, currentObj])

        execCopySourceTarget(newSkinCluster, origSkinCluster, shared.convertToVertexList(object), shared.convertToVertexList(object1), smoothValue, progressBar)
        setProgress(iteration * percentage, progressBar, "copy closest skin")
    setProgress(100, progressBar, "transfered closest skin")
    return True


@shared.dec_undo
def transferSkinning(baseSkin, otherSkins, inPlace=True, sAs=True, uvSpace=False, progressBar=None):
    """ copy skincluster information from one object to others 

    :param baseSkin: objects to use for data
    :type baseSkin: string
    :param otherSkins: objects that will get the data from the baseskin
    :type otherSkins: list
    :param inPlace: if `True` will delete the history on other objects before applying the skin (building new skincluster info), if `False` will build on top of existing skincluster info
    :type inPlace: bool
    :param sAs: if `True` will use surface association method to copy over information, if `False` will use a brute force approach
    :type sAs: bool
    :param uvSpace: if `True` will use uv space information to copy skin, if `False` will use closest vertex position
    :type uvSpace: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "transfer skinning")
    
    sc = shared.skinCluster(baseSkin, silent=False)
    if sc == None:
        return False

    surfaceAssociation = "closestPoint"
    if sAs:
        surfaceAssociation = "closestComponent"

    percentage = 99.0 / len(otherSkins)
    for index, toSkinMesh in enumerate(otherSkins):
        if inPlace:
            cmds.delete(toSkinMesh, ch=True)
        else:
            skincluster = shared.skinCluster(toSkinMesh, silent=False)
            if skincluster == None:
                continue
            cmds.skinCluster(skincluster, e=True, ub=True)

        jointInfls = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)
        maxInfls = cmds.skinCluster(sc, q=True, mi=True)
        joints.removeBindPoses()
        newSkinCl = cmds.skinCluster(jointInfls, toSkinMesh, mi=maxInfls)
        if uvSpace:
            cmds.copySkinWeights(ss=sc, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 uv=["map1", "map1"], influenceAssociation=["label", "oneToOne", "name"], normalize=True)
        else:
            cmds.copySkinWeights(ss=sc, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 influenceAssociation=["label", "oneToOne", "name"], normalize=True)
        setProgress(index * percentage, progressBar, "transfer skin info")
    setProgress(100, progressBar, "transfered skin")
    return True


@shared.dec_undo
def Copy2MultVertex(selection, lastSelected, progressBar=None):
    """ copy information between vertices

    :param selection: the selection of vertices that will get the information
    :type selection: list 
    :param lastSelected: the vertex we gather information from
    :type lastSelected: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed, vertices if requested
    :rtype: bool
    """
    setProgress(0, progressBar, "start copy vertex")
    index = int(lastSelected.split("[")[-1].split("]")[0])
    currentMesh = lastSelected.split('.')[0]
    sc = shared.skinCluster(currentMesh, True)

    infJoints = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)
    currentValues = cmds.skinPercent(sc, "%s.vtx[%i]" % (currentMesh, index), q=1, value=1)

    percentage = 99.0 / len(infJoints)
    transformValueList = []
    for i, jnt in enumerate(infJoints):
        transformValueList.append([jnt, currentValues[i]])
        setProgress(i * percentage, progressBar, "gather joint info")

    cmds.skinPercent(sc, selection, transformValue=transformValueList, normalize=1, zeroRemainingInfluences=True)
    setProgress(100, progressBar, "copied vertex")
    return True


@shared.dec_undo
def hammerVerts(inSelection, needsReturn=True, progressBar=None):
    """ a quick and dirty way of smoothing vertex selection

    :param inSelection: the selection of vertices that will be smoothed
    :type inSelection: list 
    :param needsReturn: if `True` will return a vertex list of affected vertices, if `False` will return default value
    :type needsReturn: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed, vertices if requested
    :rtype: bool, list
    """
    setProgress(0, progressBar, "start Hammer")
    currentMesh = inSelection[0].split('.')[0]
    sc = shared.skinCluster(currentMesh, True)
    maxInfls = cmds.skinCluster(sc, q=True, mi=True)
    setProgress(50, progressBar, "gather data")

    cmds.skinCluster(sc, e=1, sw=0.0, swi=5, omi=True, forceNormalizeWeights=True)
    setProgress(100, progressBar, "Hammered Weights")
    if needsReturn:
        return shared.convertToVertexList(inSelection)
    return True


@shared.dec_undo
def switchVertexWeight(vertex1, vertex2, progressBar=None):
    """ swap information between 2 skinned vertices

    :param vertex1: the first vertex to use skin info 
    :type vertex1: string
    :param vertex2: the second vertex to use skin info
    :type vertex2: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "start switch")
    currentMesh = vertex1.split('.')[0]
    sc = shared.skinCluster(currentMesh)
    cmds.skinCluster(currentMesh, e=True, nw=1)
    infJoints = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)

    pointWeights1 = cmds.skinPercent(sc, vertex1, q=True, value=True)
    pointWeights2 = cmds.skinPercent(sc, vertex2, q=True, value=True)

    pointsWeightsList1 = []
    pointsWeightsList2 = []
    percentage = 99.0 / len(infJoints)
    for i, bone in enumerate(infJoints):
        pointsWeightsList1.append([bone, pointWeights1[i]])
        pointsWeightsList2.append([bone, pointWeights2[i]])
        setProgress(i * percentage, progressBar, "gather joint info")

    cmds.skinPercent(sc, vertex1, transformValue=pointsWeightsList2)
    cmds.skinPercent(sc, vertex2, transformValue=pointsWeightsList1)
    setProgress(100, progressBar, "switched Weights")
    return True


@shared.dec_undo
def transferUvToSkinnedObject(meshSource, meshTarget, sourceMap="map1", targetMap="map1", progressBar=None):
    """ a way to copy uv map information from a static mesh to a skinned mesh without breaking the history stack

    :param meshSource: the static mesh that holds correct uv information
    :type meshSource: string
    :param meshTarget: the skinned mesh that needs to get uv information
    :type meshTarget: string
    :param sourceMap: the uv map to get information from
    :type sourceMap: string
    :param targetMap: the uv map to send information to
    :type targetMap: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "gather shape info")
    shapes = cmds.listRelatives(meshTarget, s=1)
    mesh_orig = None
    for shape in shapes:
        if cmds.getAttr("%s.intermediateObject" % shape) == 0:
            continue
        if cmds.listConnections(shape, type="groupParts") is None:
            continue
        mesh_orig = shape

    conns = cmds.listConnections(mesh_orig, d=1, c=1, p=1)

    setProgress(22, progressBar, "transfer uv")

    cmds.setAttr("%s.intermediateObject" % mesh_orig, 0)
    transformAttrs = cmds.transferAttributes(meshSource, mesh_orig,
                                             transferPositions=False,
                                             transferNormals=False,
                                             transferUVs=2,
                                             transferColors=2,
                                             sampleSpace=4,
                                             sourceUvSpace=sourceMap,
                                             targetUvSpace=targetMap,
                                             searchMethod=3,
                                             flipUVs=False,
                                             colorBorders=True)
    cmds.setAttr("%s.intermediateObject" % mesh_orig, 1)

    setProgress(35, progressBar, "cleanup history stack")
    conns = cmds.listConnections(transformAttrs, d=1, c=1, p=1)
    indices = []
    _connectDict = {}
    for i in conns[::2]:
        indices.append(i)
    for index, conn in enumerate(conns[1::2]):
        _connectDict[indices[index]] = conn
    for key, value in _connectDict.items():
        try:
            cmds.disconnectAttr(key, value)
        except:
            pass
    cmds.delete(transformAttrs)

    setProgress(87, progressBar, "clean connections")

    shapes = cmds.listRelatives(meshTarget, s=1)
    for shape in shapes:
        connections = cmds.listConnections(shape)
        if not connections:
            cmds.delete(shape)

    setProgress(100, progressBar, "transfered UV")
    return True


@shared.dec_undo
def seperateSkinnedObject(inMesh, progressBar=None):
    """ seperate a skinned mesh that has different polygroups combined into multiple objects with skinning information intact

    :param inMesh: the skinned mesh to split in multiple
    :type inMesh: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "start seperate")
    shape = cmds.listRelatives(inMesh, ad=True, s=True)
    shells = mesh.getShellFaces(inMesh)

    total = len(shells)
    percentage = 99.0 / total

    newMeshes = []
    for i, shell in enumerate(shells):

        dup = cmds.duplicate(inMesh)[0]
        newShells = []
        for obj in shells:
            newShells.append(dup + obj)
        newShells.pop(i)
        cmds.delete(newShells)
        cmds.flushUndo()
        newMeshes.append(dup)

        setProgress(percentage * i, progressBar, "extracting shells")

    transferSkinning(inMesh, newMeshes, inPlace=True)
    cmds.delete(shape)
    cmds.parent(newMeshes, inMesh)

    setProgress(100, progressBar, "seperated object shells")
    return True


@shared.dec_undo
def extractSkinnedShells(components, progressBar=None):
    """ extract a selection of components as a new mesh with the same skinning info

    :param components: list of components that define the new mesh
    :type components: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: the mesh that is created
    :rtype: string
    """
    def _convertToFaces(components):
        convertedFaces = cmds.polyListComponentConversion(components, tf=True)
        return cmds.filterExpand(convertedFaces, sm=34)

    setProgress(0, progressBar, "get shell info")
    faces = _convertToFaces(components)
    inMesh = faces[0].split(".")[0]

    dup = cmds.duplicate(inMesh)[0]
    allFaces = _convertToFaces(dup)

    newSel = []
    percentage = 80.0 / len(faces)
    for i, face in enumerate(faces):
        newSel.append("%s.%s" % (dup, face.split(".")[-1]))
        setProgress(i * percentage, progressBar, "construct shells")

    cmds.delete(list(set(allFaces) ^ set(newSel)))
    cmds.delete(dup, ch=1)
    if shared.skinCluster(inMesh, True) == None:
        return
    transferSkinning(inMesh, [dup], inPlace=True)
    setProgress(100, progressBar, "extracted shells")
    return dup


@shared.dec_undo
def combineSkinnedMeshes(meshes, progressBar=None):
    """ combine multiple skinned meshes into 1 single skinned mesh

    :param meshes: list of meshes to combine
    :type meshes: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: the mesh that is created
    :rtype: string
    """
    setProgress(0, progressBar, "start Merge")
    cmds.polyUniteSkinned(meshes, ch=0, mergeUVSets=1)
    setProgress(100, progressBar, "merged skins")
    return newMesh


@shared.dec_undo
def keepOnlySelectedInfluences(fullSelection, jointOnlySelection, inverse=False, progressBar=None):
    """ use the selection of joints and components to tell which joints are allowed to drive the current components

    :param fullSelection: list of meshes and joints
    :type fullSelection: list
    :param fullSelection: list of only joints
    :type fullSelection: list
    :param fullSelection: if `True` will remove the current joints from the selection, if `False` will make sure only these joints drive the components
    :type fullSelection: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "get joint influences")
    polySelection = list(set(fullSelection) ^ set(jointOnlySelection))
    vertices = shared.convertToVertexList(polySelection)
    inMesh = vertices[0].split(".")[0]
    skinCluster = shared.skinCluster(inMesh, True)

    attachedJoints = joints.getInfluencingJoints(skinCluster) 
    jointsToRemove = jointOnlySelection
    if not inverse:
        jointsToRemove = list(set(attachedJoints) - set(jointOnlySelection))

    jointsToRemoveValues = []
    percentage = 99.0 / len(jointsToRemove)
    for index, jnt in enumerate(jointsToRemove):
        jointsToRemoveValues.append((jnt, 0))
        setProgress(index * percentage, progressBar, "get joints to remove")

    cmds.skinPercent(skinCluster, vertices, tv=jointsToRemoveValues, normalize=True)
    setProgress(100, progressBar, "removed unselected influences")
    return True


@shared.dec_undo
def smoothAndSmoothNeighbours(input, both=False, growing=False, full=True, progressBar=None):
    """ a function that can walk over a mesh selection smooth the mesh gradually

    :param input: list components
    :type input: list
    :param both: if `True` will smooth both the inner and outer part of the selection, if `False` will only smooth outside of the current selection
    :type both: bool
    :param growing: if `True` smooth and convert the selection to the outer shell of current selection, if `False` will keep the same selection
    :type growing: bool
    :param full: if `True` will get any component in the outer selection that is close to the current vertex, if `False` will only select vertices connected by an edge
    :type full: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: list of vertices in the new selection
    :rtype: list
    """
    setProgress(0, progressBar, "start smooth")
    vertices = shared.convertToVertexList(input)
    inMesh = vertices[0].split('.')[0]
    meshNode = OpenMaya.MGlobal.getSelectionListByName(inMesh).getDependNode(0)
    meshVerItFn = OpenMaya.MItMeshVertex(meshNode)

    sc = shared.skinCluster(inMesh)
    if both:
        cmds.select(vertices, r=1)
        cmds.skinCluster(sc, geometry=vertices, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)
    if full:
        grown = shared.convertToVertexList(cmds.polyListComponentConversion(vertices, tf=True))
    else:
        indices = []
        for vert in vertices:
            index = int(vert[vert.index("[") + 1: -1])
            indices.extend(shared.getNeighbours(meshVerItFn, index))
        grown = shared.convertToCompList(indices, inMesh)

    fixedList = list(set(grown) ^ set(vertices))
    setProgress(67, progressBar, "gathered smooth data")
    cmds.skinCluster(sc, geometry=fixedList, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)

    setProgress(100, progressBar, "smoothed neighbors")
    if False in [growing, both]:
        cmds.select(vertices, r=1)
        return vertices
    cmds.select(fixedList, r=1)
    return fixedList


@shared.dec_undo
def avgVertex(vertices, lastSelected, progressBar=None):
    """ smooth a vertex's skinning information based on order of selection

    :param vertices: list of vertices to gather information from
    :type vertices: list
    :param lastSelected: last selected object can get the average information
    :type lastSelected: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "get average data")
    pointList = [x for x in vertices if x != lastSelected]
    inMesh = lastSelected.split('.')[0]
    sc = shared.skinCluster(inMesh)
    jointInfls = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)

    _weights = dict.fromkeys(jointInfls, 0)
    percentage = 99.0 / len(pointList)
    for index, point in enumerate(pointList):
        for joint in jointInfls:
            pointWeights = cmds.skinPercent(sc, point, transform=joint, q=True, value=True)
            if pointWeights < 0.000001:
                continue
            _weights[joint] += pointWeights
        setProgress(index * percentage, progressBar, "gather smooth data")

    amountPts = len(pointList)
    transformValueList = []
    for key, value in _weights.items():
        transformValueList.append([key, value])

    cmds.skinPercent(sc, lastSelected, transformValue=transformValueList, normalize=1, zeroRemainingInfluences=True)
    setProgress(100, progressBar, "set average weight")
    return True


@shared.dec_undo
def freezeSkinnedMesh(inMesh, progressBar=None):
    """ 'freeze' a skinned mesh, remove construction history and transform information

    :param inMesh: name of the skinned mesh to cleanup
    :type inMesh: string
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "start freeze mesh")
    sc = shared.skinCluster(inMesh, True)
    attachedJoints = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)

    setProgress(25, progressBar, "gather current skindata")
    shape = cmds.listRelatives(inMesh, s=True)[0]
    outInfluencesArray = shared.getWeights(inMesh)

    setProgress(50, progressBar, "clean mesh")
    cmds.skinCluster(shape, e=True, ub=True)
    cmds.delete(inMesh, ch=1)
    cmds.makeIdentity(inMesh, apply=True)

    setProgress(75, progressBar, "re-apply skin")
    nsc = cmds.skinCluster(attachedJoints, inMesh, tsb=True, bm=0, nw=1)
    shared.setWeights(inMesh, outInfluencesArray)
    setProgress(100, progressBar, "freeze skinned mesh")
    return True


@shared.dec_undo
def hardSkinSelectionShells(selection, progressBar=False):
    """  use the current selection to define islands that are clustered togehter and make sure that each island shares the same skinning information

    :param selection: list of components
    :type selection: list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: the current selection
    :rtype: list
    """
    setProgress(0, progressBar, "converting to shells")
    expanded = shared.convertToVertexList(selection)
    inMesh = expanded[0].split('.')[0]

    sc = shared.skinCluster(inMesh, True)
    attachedJoints = cmds.skinCluster(sc, q=True, inf=True)

    vtxList = shared.convertToIndexList(expanded)
    foundFriendDict = shared.getConnectedVerts(inMesh, vtxList)

    iteration = 0
    percentage = 99.0 / len(foundFriendDict.keys())
    for group, entries in foundFriendDict.items():
        list1 = foundFriendDict[group]
        vertices = shared.convertToCompList(list(list1), inMesh)
        vertexWeights = dict.fromkeys(attachedJoints, 0.0)

        combinations = list(itertools.product(vertices, attachedJoints))
        for vertex, jnt in combinations:
            vertexWeights[jnt] += cmds.skinPercent(sc, vertex, transform=jnt, query=True)

        jointValueList = []
        for jnt in attachedJoints:
            newValue = vertexWeights[jnt] / float(len(vertices))
            jointValueList.append([jnt, newValue])

        cmds.skinPercent(sc, vertices, transformValue=jointValueList, normalize=1)
        setProgress(iteration * percentage, progressBar, "setting shell data")
        iteration += 1
        cmds.refresh()

    setProgress(100, progressBar, "hard skinned shells")
    return selection


@shared.dec_undo
def AvarageVertex(selection, useDistance, weightAverageWindow=None, progressBar=None):
    """ grouped function that allows multiple ways of averaging vertices based on how its selected

    :param selection: list of components
    :type selection: list
    :param useDistance: if `True` the weight is measured by the distance between elements, if `False` weight is measured by the amount in the selection
    :type useDistance: bool
    :param weightAverageWindow: name of the skinned mesh to cleanup
    :type weightAverageWindow: falloffCurveUI
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    setProgress(0, progressBar, "get selection data")
    vertexAmount = len(selection)
    if vertexAmount < 2:
        cmds.error("not enough vertices selected! select a minimum of 2")

    selectedMesh = selection[0].split('.')[0]

    _isEdgeSelection = False
    if ".e[" in selection[0]:
        _isEdgeSelection = True

    sc = shared.skinCluster(selectedMesh, True)
    infJoints = joints.getInfluencingJoints(sc)  # cmds.listConnections("%s.matrix"%sc, source=True)

    cmds.skinCluster(selectedMesh, e=True, nw=1)
    if vertexAmount == 2 or _isEdgeSelection:
        baseList = [selection]
        if _isEdgeSelection:
            baseList = mesh.edgesToSmooth(selection)

        percentage = 99.0 / len(baseList)
        try:
            cmds.setAttr( "%s.envelope"%sc, 0)
            for iteration, vertlist in enumerate(baseList):
                
                vertMap = mesh.componentPathFinding(vertlist, useDistance, weightWindow=weightAverageWindow)

                startWGT = cmds.skinPercent(sc, vertlist[0], q=True, v=True)
                endWGT = cmds.skinPercent(sc, vertlist[1], q=True, v=True)

                for vertex, percentage in vertMap.items():
                    newWeightsList = []
                    for idx, weight in enumerate(startWGT):
                        value1 = endWGT[idx] * percentage
                        value2 = startWGT[idx] * (1 - percentage)
                        newWeightsList.append((infJoints[idx], value1 + value2))
                    cmds.skinPercent(sc, vertex, transformValue=newWeightsList)
                setProgress(iteration * percentage, progressBar, "set path average data")
        except Exception as e:
            if _DEBUG:
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc())
        finally:
            cmds.setAttr( "%s.envelope"%sc, 1)

        setProgress(1.0, progressBar, "average skin applied to path")
        return True

    lastSelected = selection[-1]
    avgVertex(selection, lastSelected, progressBar)
    setProgress(100, progressBar, "set average weight")
    return True


@shared.dec_undo
def neighbourAverage(components, warningPopup=True, progressBar=None):
    """ force smooth skinning based on the current selection

    :param components: current list of components
    :type components: list
    :param warningPopup: if `True` will open a popup when the selection might take too long, if `False` will not use the popup
    :type warningPopup: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: `True` if the function is completed
    :rtype: bool
    """
    expandedVertices = shared.convertToVertexList(components)
    if warningPopup and len(expandedVertices) > 1000:
        result = cmds.confirmDialog(title='warning',
                                    message='current selection can take a long time to process, continue?',
                                    button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if result == "No":
            return

    setProgress(100, progressBar, "get neighbor data")
    inMesh = expandedVertices[0].split('.')[0]
    sc = shared.skinCluster(inMesh)
    percentage = 99.0 / len(expandedVertices)
    for index, vertex in enumerate(expandedVertices):
        cmds.AverageVtxWeight(vertex, sc=sc, wt=1)
        setProgress(index * percentage, progressBar, "set average weight")

    setProgress(100, progressBar, "set neighbor average")
    return True


@shared.dec_undo
def doSkinPercent(bone, value, operation=0):
    """ simple function to quickly set weights with the given value

    :param bone: joint to change the weight influence of
    :type bone: list
    :param value: value to set the weight
    :type value: float
    :param operation: the operation on how to treat the weight
    :type operation: int
    :note operation: = { 0:removes the values, 1:sets the values, 2: adds the values}
    :return: `True` if the function is completed
    :rtype: bool
    """
    _sel = cmds.ls(sl=1, fl=1)
    _softSelect = cmds.softSelect(q=True, softSelectEnabled=1)
    if _softSelect:
        vertices, weights = mesh.softSelection()
    else:
        selection = cmds.ls(sl=1, l=1)
        vertices = shared.convertToVertexList(selection)
        weights = [1.0] * len(vertices)

    if vertices == []:
        return False

    inMesh = vertices[0].split('.')[0]
    sc = shared.skinCluster(inMesh, True)
    if sc is None:
        return False

    bone = cmds.ls(bone, l=1)[0]
    allBones = joints.getInfluencingJoints(sc)
    if not bone in allBones:
        cmds.skinCluster(sc, e=True, lw=False, wt=0.0, ai=bone)

    _rel = (operation != 1)
    _mult = [-1, 1, 1]
    if _softSelect:
        for index, vert in enumerate(vertices):
            newVal = weights[index] * _mult[operation]# * value
            cmds.skinPercent(sc, vert, r = _rel, tv=[bone, weights[index]], normalize=True)
    else:
        newVal = value * _mult[operation]
        cmds.skinPercent(sc, vertices, r = _rel, tv=[bone, value * _mult[operation]], normalize=True)

    return True


class SoftSkinBuilder(object):
    """ this class handles the buildup of a skincluster using selections
    the base of the infromation is gathered from the object itself

    the user can then alter the weights using direct selection and assiging the values
    or it can use the soft selection to define a bigger selection and smooth weights
    """
    def __init__(self, progressBar = None):
        """ constructor method
        
        :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
        :type progressBar: QProgressBar
        """
        self._progressBar = progressBar

        from SkinningTools.Maya.tools.apiWeights import ApiWeights
        self.__weightInfo = ApiWeights()
        self.__currentMesh = ''
        self.boneWeights= {}
        self._newWeights = {}
        self._preAnalyzed = False

    def analyzeSkin(self, inMesh, pre = True):
        """ analyze the current skin, get information from the given mesh and fill the constructor
        
        :param inMesh: the mesh to analyze
        :type inMesh: string
        :param pre: if `True` will set the current info to be pre-analyzed, if `False` will leave the function alone
        :type pre: bool
        :note pre: unused, this one will be used later to check if we are going to add, replace or create weights from scratch
        :return: list of current joints influencing the mesh
        :rtype: list
        """
        if pre: 
            self._preAnalyzed = pre
        self.__weightInfo.getData([inMesh], self._progressBar)
        _jntLen = len(self.__weightInfo.meshInfluences[inMesh])
        for index, bone in enumerate(self.__weightInfo.meshInfluences[inMesh]):
            self.boneWeights[bone] =  self.__weightInfo.meshWeights[inMesh][index*_jntLen: (1+index) * _jntLen]

        return self.__weightInfo.meshInfluences[inMesh]

    def getVerts(self, bone):
        """ get the vertices currently influenced by the given bone
        
        :param bone: name of the bone to get information from
        :type bone: string
        :return: list of vertices influenced
        :rtype: list
        """
        _info = []
        if bone in self.boneWeights.keys():
            _info = [x for x, i in enumerate(self.boneWeights[bone]) if i >= 1e-6]
        if bone  in self._newWeights.keys():
            _info.extend(self._newWeights[bone][0])
        return _info

    def removeData(self, bone):
        """ remove the data associated with given bone
        
        :Todo: figure out what to do with the original weights!
        :param bone: name of the bone to clear the date off
        :type bone: string
        """        
        if not bone in self._newWeights.keys():
            return
        amount = len(self._newWeights[bone])
        self._newWeights[bone] = [0.0] * amount

    def addSoftSkinInfo(self, bone):
        """ add skinning info to the bone based on current selection
        
        :param bone: name of the bone to assign data too
        :type bone: string
        """   
        _softSelect = cmds.softSelect(q=True, softSelectEnabled=1)
        if _softSelect:
            vertices, weights = mesh.softSelection()
        else:
            selection = cmds.ls(sl=1, l=1)
            vertices = shared.convertToVertexList(selection)
            weights = [1.0] * len(vertices)

        _mesh = vertices[0].split('.')
        if self.__currentMesh == '':
            self.__currentMesh = _mesh

        if self.__currentMesh == _mesh:
            self._newWeights[bone] = [vertices, weights]

    def setSoftSkinInfo(self, inMesh, add = True):
        """ set the skinning info to the mesh
        
        :param inMesh: name of the mesh to assignt the data to
        :type inMesh: string
        :param add: if `True` will add the info to the existing information, if `False` will override the information
        :type add: bool
        """   
        sc = shared.skinCluster(inMesh)
        if not sc:
            sc = cmds.skinCluster(inMesh, self.boneWeights.keys(), tsb=1)

        self.analyzeSkin(inMesh, False)

        _origWeights = []
        _weigths = []
        for bone in self.__weightInfo.meshInfluences[inMesh]:
            verts, weights = self._newWeights[bone]
            indices = shared.convertToIndexList(verts)
            _origWeights.extend(self.boneWeights[bone])
            for i, wght  in enumerate(weights):
                if add:
                    self.boneWeights[bone][indices[i]] += weight
                else:
                    self.boneWeights[bone][indices[i]] = weight
            _weights.extend(self.boneWeights[bone])


        jnts = [self.__weightInfo.meshInfluences[inMesh].index(inf) for inf in self.__weightInfo.meshInfluences[inMesh]]       
            
        vertIds = self.__weightInfo.meshVerts[inMesh]
        cmds.SkinEditor(inMesh, sc, vid=vertIds, nw = _weights, jid = jnts, ow = _origWeights )

