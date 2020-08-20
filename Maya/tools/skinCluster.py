# -*- coding: utf-8 -*-
import math, itertools
from decimal import Decimal
from heapq import nsmallest

from SkinningTools.py23 import *
from SkinningTools.Maya.tools import shared, joints, mesh
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI.qt_util import *
from SkinningTools.UI import utils 

from maya import cmds

def checkBasePose(skinCluster):
    bp = cmds.listConnections("%s.bindPose"%skinCluster, source=True) or None
    if bp:
        return cmds.dagPose(bp[0], q=True, atPose=True) is not None
    jointMap = shared.getJointIndexMap(skinCluster)

    for key, val in jointMap.iteritems():
        #@note: only compare worldspace translate values as precision might be difficult here
        prebind = cmds.getAttr("%s.bindPreMatrix[%s]"%(skinCluster, val))[-4:-1]
        curInvMat = cmds.getAttr("%s.worldInverseMatrix"%key)[-4:-1]
        if not utils.compare_vec3(prebind, curInvMat):
            return False
    return True

@shared.dec_undo
def forceCompareInfluences(meshes):
    compared = joints.comparejointInfluences(meshes, True)
    outOfPose = False
    for mesh in meshes:
        shared.skinCluster(mesh, True)
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

def getVertOverMaxInfluence(inObject, maxInfValue = 8, notSelect=False, progressBar=None ):
    utils.setProgress(0, progressBar, "get max info")
    sc = shared.skinCluster(inObject, True)
    vtxWeights = cmds.getAttr("%s.weightList[:]"%sc)
    vtxCount = len(vtxWeights)

    percentage = 99.0/vtxCount
    indexOverMap={}
    namedIndex= []
    for i in xrange(vtxCount):
        amount = len(cmds.getAttr("%s.weightList[%i].weights"%(sc, i))[0])
        if  amount > maxInfValue:
            indexOverMap[i] = amount
            namedIndex.append("%s.vtx[%i]"%(inObject, i))
        utils.setProgress(i * percentage, progressBar, "checking vertices")
    utils.setProgress(100, progressBar, "vertices checked on %s"%inObject)
    return namedIndex, indexOverMap

@shared.dec_undo
def setMaxJointInfluences(inObject=None, maxInfValue=8, progressBar=None):
    utils.setProgress(0, progressBar, "get max info")
    toMuchinfls, indexOverMap = getVertOverMaxInfluence(inObject=inObject, maxInfValue=maxInfValue) or None
    if toMuchinfls is None:
        return

    sc = shared.skinCluster(inObject, True)
    shape = cmds.listRelatives(inObject, s=True)[0]

    outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)

    infjnts = cmds.listConnections("%s.matrix"%sc, source=True)
    infLengt = len(infjnts)

    lenOutInfArray = len(outInfluencesArray)

    percentage = 99.0/len(toMuchinfls)
    for index, vertex in enumerate(toMuchinfls):
        values = cmds.skinPercent(skinClusterName, vertex, q=1, v=1, ib=float(Decimal('1.0e-17')))
        curAmountValues = len(values)
        toPrune = curAmountValues - maxInfValue

        pruneFix = max(nsmallest(toPrune, values)) + 0.001
        cmds.skinPercent(skinClusterName, vertex, pruneWeights=pruneFix)
        utils.setProgress(index * percentage, progressBar, "removing influences")

    cmds.skinCluster(skinClusterName, e=True, fnw=1)

    cmds.setAttr("%s.maxInfluences" % skinClusterName, maxInfValue)
    cmds.setAttr("%s.maintainMaxInfluences" % skinClusterName, 1)

    utils.setProgress(100, progressBar, "set maximum influences")

    return True
    
@shared.dec_undo
def execCopySourceTarget(TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection, smoothValue=1, progressBar=None):
    utils.setProgress(0, progressBar, "get source info")

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
    
    targetInflArray = cmds.SkinWeights([targetMesh, TargetSkinCluster], q=True)
    sourceInflArray = cmds.SkinWeights([sourceMesh, SourceSkinCluster], q=True)
    
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
            for index in xrange(smoothValue):
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
                for i in xrange(jointAmount):
                    weight.append(sourceInflArray[(indexing * jointAmount) + i])
                weights.append(weight)

        newWeights = []
        for index in xrange(smoothValue):
            for i, wght in enumerate(weights[index]):
                # distance/totalDistance is weight of the distance caluclated
                weights[index][i] = (distanceWeightsArray[index] / totalDistanceWeights) * wght

            if len(newWeights) == 0:
                newWeights = list(range(len(weights[index])))
                for j in xrange(len(newWeights)):
                    newWeights[j] = 0.0

            for j in xrange(len(weights[index])):
                newWeights[j] = newWeights[j] + weights[index][j]

        divider = 0.0
        for wght in newWeights:
            divider = divider + wght
        weightsCreation = []
        for jnt in targetJoints:
            for count, skinJoint in enumerate(sourceJoints):
                if jnt != skinJoint:
                    continue
                weightsCreation.append((newWeights[count] / divider))
        weightlist.extend(weightsCreation)

        utils.setProgress(tIndex * percentage, progressBar, "copy source > target vtx")

    index = 0
    for vertex in TargetSelection:
        number = allVerticesTarget.index(vertex)
        for jointIndex in xrange(jointAmount):
            weightindex = (number * jointAmount) + jointIndex
            targetInflArray[weightindex] = weightlist[index]
            index += 1

    cmds.SkinWeights([targetMesh, TargetSkinCluster], nwt=targetInflArray)

    utils.setProgress(100, progressBar, "copy from Source to Target")

    return True

@shared.dec_undo
def transferClosestSkinning(objects, smoothValue, progressBar = None):
    utils.setProgress(0, progressBar, "get closest info")
    baseObject = objects[0]
    origSkinCluster = shared.skinCluster(baseObject)
    origJoints = cmds.listConnections("%s.matrix"%origSkinCluster, source=True)

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
        utils.setProgress(iteration * percentage, progressBar, "copy closest skin")
    utils.setProgress(100, progressBar, "transfered closest skin")
    return True

@shared.dec_undo
def transferSkinning(baseSkin, otherSkins, inPlace=True, sAs=True, uvSpace=False, progressBar = None):
    utils.setProgress(0, progressBar, "transfer skinning")
    sc = shared.skinCluster(baseSkin, silent=False)
    if sc == None:
        return False

    surfaceAssociation = "closestPoint"
    if sAs:
        surfaceAssociation = "closestComponent"
    
    percentage = 99.0/ len(otherSkins)
    for index, toSkinMesh in enumerate(otherSkins):
        if inPlace:
            cmds.delete(toSkinMesh, ch=True)
        else:
            skincluster = shared.skinCluster(toSkinMesh, silent=False)
            if skincluster == None:
                continue
            cmds.skinCluster(skincluster, e=True, ub=True)

        
        jointInfls = cmds.listConnections("%s.matrix"%sc, source=True)
        maxInfls = cmds.skinCluster(sc, q=True, mi=True)
        joints.removeBindPoses()
        newSkinCl = cmds.skinCluster(jointInfls, toSkinMesh, mi=maxInfls)
        if uvSpace:
            cmds.copySkinWeights(ss=sc, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 uv=["map1", "map1"], influenceAssociation=["label", "oneToOne", "name"], normalize=True)
        else:
            cmds.copySkinWeights(ss=sc, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 influenceAssociation=["label", "oneToOne", "name"], normalize=True)
        utils.setProgress(index * percentage, progressBar, "transfer skin info")
    utils.setProgress(100, progressBar, "transfered skin")
    return True

@shared.dec_undo
def Copy2MultVertex(selection, lastSelected, progressBar = None):
    utils.setProgress(0, progressBar, "start copy vertex")
    index = int(lastSelected.split("[")[-1].split("]")[0])
    mesh = lastSelected.split('.')[0]
    sc = shared.skinCluster(mesh, True)

    infJoints =  cmds.listConnections("%s.matrix"%sc, source=True)
    currentValues = cmds.skinPercent(sc, "%s.vtx[%i]"%(mesh, index), q=1, value=1)

    percentage = 99.0/ len(infJoints)
    transformValueList = []
    for i, jnt in enumerate(infJoints):
        transformValueList.append([jnt, currentValues[i]])
        utils.setProgress(i * percentage, progressBar, "gather joint info")

    cmds.skinPercent(sc, selection, transformValue=transformValueList, normalize = 0,zeroRemainingInfluences = True )
    utils.setProgress(100, progressBar, "copied vertex")
    return True

@shared.dec_undo
def hammerVerts(inSelection, needsReturn=True, progressBar = None):
    utils.setProgress(0, progressBar, "start Hammer")
    mesh = inSelection[0].split('.')[0]
    sc = shared.skinCluster(mesh, True)
    maxInfls = cmds.skinCluster(sc, q=True, mi=True)
    utils.setProgress(50, progressBar, "gather data")

    cmds.skinCluster(sc, e=1, sw = 0.0, swi= 5, omi = True, forceNormalizeWeights = True)
    utils.setProgress(100, progressBar, "Hammered Weights")
    if needsReturn:
        return shared.convertToVertexList(inSelection)
    return True

@shared.dec_undo
def switchVertexWeight(vertex1, vertex2, progressBar = None):
    utils.setProgress(0, progressBar, "start switch")
    mesh = vertex1.split('.')[0]
    sc = shared.skinCluster(mesh)
    cmds.skinCluster(mesh, e=True, nw=1)
    infJoints = cmds.listConnections("%s.matrix"%sc, source=True)

    pointWeights1 = cmds.skinPercent(skinClusterName, vertex1, q=True, value=True)
    pointWeights2 = cmds.skinPercent(skinClusterName, vertex2, q=True, value=True)

    pointsWeightsList1 = []
    pointsWeightsList2 = []
    percentage = 99.0/ len(infJoints)
    for j, bone in enumerate(infJoints):
        pointsWeightsList1.append(bone, pointWeights1[j])
        pointsWeightsList2.append(bone, pointWeights2[j])
        utils.setProgress(i * percentage, progressBar, "gather joint info")

    cmds.skinPercent(skinClusterName, vertex1, transformValue=pointsWeightsList2)
    cmds.skinPercent(skinClusterName, vertex2, transformValue=pointsWeightsList1)
    utils.setProgress(100, progressBar, "switched Weights")
    return True

@shared.dec_undo
def transferUvToSkinnedObject(mesh_source, mesh_target, sourceMap = "map1", targetMap = "map1", progressBar = None):
    utils.setProgress(0, progressBar, "gather shape info")
    shapes = cmds.listRelatives(mesh_target, s=1)
    mesh_orig = None
    for shape in shapes:
        if cmds.getAttr("%s.intermediateObject" % shape) == 0:
            continue
        if cmds.listConnections(shape,type = "groupParts") is None:
            continue
        mesh_orig = shape
        
    conns = cmds.listConnections(mesh_orig, d=1, c=1, p=1)
    
    utils.setProgress(22, progressBar, "transfer uv")

    cmds.setAttr("%s.intermediateObject" % mesh_orig, 0)
    transformAttrs = cmds.transferAttributes(mesh_source, mesh_orig,
                                transferPositions=False,
                                transferNormals=False,
                                transferUVs=2,
                                transferColors=2,
                                sampleSpace=4,
                                sourceUvSpace=sourceMap,
                                targetUvSpace=targetMap,
                                searchMethod=3,
                                flipUVs=False,
                                colorBorders=True )
    cmds.setAttr("%s.intermediateObject" % mesh_orig, 1)

    utils.setProgress(35, progressBar, "cleanup history stack")
    conns = cmds.listConnections(transformAttrs, d=1, c=1, p=1)
    indices =[]
    _connectDict = {}
    for i in conns[::2]:
        indices.append(i)
    for index, conn in enumerate(conns[1::2]):
        _connectDict[indices[index]] = conn
    for key, value in _connectDict.iteritems():
        try:
            cmds.disconnectAttr(key, value)
        except:
            pass
    cmds.delete(transformAttrs)

    utils.setProgress(87, progressBar, "clean connections")

    shapes = cmds.listRelatives(mesh_target, s=1)
    for shape in shapes:
        connections = cmds.listConnections(shape)
        if not connections:
            cmds.delete(shape)

    utils.setProgress(100, progressBar, "transfered UV")
    return True

@shared.dec_undo
def seperateSkinnedObject(mesh, progressBar=None):
    utils.setProgress(0, progressBar, "start seperate")
    shape = cmds.listRelatives(mesh, ad=True, s=True)
    shells = mesh.getShellFaces(mesh)

    total = len(shells)
    percentage = 99.0 / total

    newMeshes = []
    for i, shell in enumerate(shells):

        dup = cmds.duplicate(mesh)[0]
        newShells = []
        for obj in shells:
            newShells.append(dup + obj)
        newShells.pop(i)
        cmds.delete(newShells)
        cmds.flushUndo()
        newMeshes.append(dup)

        utils.setProgress(percentage * i, progressBar, "extracting shells")

    transferSkinning(mesh, newMeshes, inPlace=True)
    cmds.delete(shape)
    cmds.parent(newMeshes, mesh)

    utils.setProgress(100, progressBar, "seperated object shells")
    return True

@shared.dec_undo
def extractSkinnedShells(components, progressBar=None):
    def _convertToFaces(components):
        convertedFaces = cmds.polyListComponentConversion(components, tf=True)
        return cmds.filterExpand(convertedFaces, sm=34)

    utils.setProgress(0, progressBar, "get shell info")
    faces = _convertToFaces(components)
    mesh = faces.split(".")[0]

    dup = cmds.duplicate(mesh)[0]
    allFaces = _convertToFaces(dup)

    newSel = []
    percentage = 80.0/ len(faces)
    for i, face in enumerate(faces):
        newSel.append("%s.%s" % (dup, face.split(".")[-1]))
        utils.setProgress(i * percentage, progressBar, "construct shells")

    cmds.delete(list(set(allFaces) ^ set(newSel)))
    cmds.delete(dup, ch=1)
    if shared.skinCluster(mesh, True) == None:
        return
    transferSkinning(mesh, [dup], inPlace=True)
    utils.setProgress(100, progressBar, "extracted shells")
    return dup

@shared.dec_undo
def combineSkinnedMeshes(meshes):
    utils.setProgress(0, progressBar, "start Merge")
    cmds.polyUniteSkinned( meshes, ch= 0, mergeUVSets =1)
    utils.setProgress(100, progressBar, "merged skins")
    return newMesh

@shared.dec_undo
def keepOnlySelectedInfluences(fullSelection, jointOnlySelection):
    utils.setProgress(0, progressBar, "get joint influences")
    polySelection = list(set(fullSelection) ^ set(jointOnlySelection))
    vertices = shared.convertToVertexList(polySelection)
    mesh = vertices[0].split(".")[0]
    skinCluster = SkinningTools.skinCluster(mesh, True)

    attachedJoints = cmds.skinCluster(skinCluster, q=True, inf=True)
    jointsToRemove = list(set(attachedJoints) - set(jointOnlySelection))

    jointsToRemoveValues = []
    percentage = 99.0/len(jointsToRemove)
    for index, jnt in enumerate(jointsToRemove):
        jointsToRemoveValues.append((jnt, 0))
        utils.setProgress(index * percentage, progressBar, "get joints to remove")

    cmds.skinPercent(skinCluster, vertices, tv=jointsToRemoveValues, normalize=True)
    utils.setProgress(100, progressBar, "removed unselected influences")
    return True

@shared.dec_undo
def smoothAndSmoothNeighbours(input, both=False, growing=False, full = True):
    utils.setProgress(0, progressBar, "start smooth")
    vertices = shared.convertToVertexList(input)
    mesh = vertices[0].split('.')[0]
    meshNode = OpenMaya.MGlobal.getSelectionListByName( name ).getDependNode()
    meshVerItFn = OpenMaya.MItMeshVertex( meshNode )
    
    sc = shared.skinCluster(mesh)
    if both:
        cmds.select(vertices, r=1)
        cmds.skinCluster(sc, geometry=vertices, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)
    if full:
        grown = shared.convertToVertexList(cmds.polyListComponentConversion(vertices, tf=True))
    else:
        indices =[]
        for vert in vertices:
            index = int(vert[vert.index("[") + 1: -1])
            indices.extend(shared.getNeighbours(meshVerItFn, index))
            for nb in indices:
                grown.append("%s.vtx[%i]"%(mesh,nb))
        grown = convertToCompList(indices, mesh)

    fixedList = list(set(grown) ^ set(vertices))
    utils.setProgress(67, progressBar, "gathered smooth data")
    cmds.skinCluster(sc, geometry=fixedList, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)

    utils.setProgress(100, progressBar, "smoothed neighbors")
    if not growing or both == False:
        return expandedVertices

    return fixedList

@shared.dec_undo
def avgVertex( vertices, lastSelected, progressBar = None):
    utils.setProgress(0, progressBar, "get average data")
    pointList = [x for x in vertices if x != lastSelected]
    mesh = lastSelected.split('.')[0]
    sc = shared.skinCluster(mesh)
    jointInfls = cmds.listConnections("%s.matrix"%sc, source=True)

    _weights = dict.fromkeys(jointInfls, 0)
    percentage = 99.0/len(pointList)
    for index, point in enumerate(pointList):
        for joint in jointInfls:
            pointWeights = cmds.skinPercent(sc, point, transform=joint, q=True,  value=True)
            if pointWeights < 0.000001:
                continue
            _weights[joint] += pointWeights
        utils.setProgress(index * percentage, progressBar, "gather smooth data")

    amountPts = len(pointList)
    transformValueList = []
    for key, value in _weights.iteritems():
        transformValueList.append([key, value])

    cmds.skinPercent(sc, lastSelected, transformValue=transformValueList, normalize = 1, zeroRemainingInfluences = True )
    utils.setProgress(100, progressBar, "set average weight")
    return True

@shared.dec_undo
def freezeSkinnedMesh(mesh, progressBar=None):
    utils.setProgress(0, progressBar, "start freeze mesh")
    sc = shared.skinCluster(mesh, True)
    attachedJoints = cmds.listConnections("%s.matrix"%sc, source=True)

    utils.setProgress(25, progressBar, "gather current skindata")
    shape = cmds.listRelatives(mesh, s=True)[0]
    outInfluencesArray = cmds.SkinWeights([shape, sc], q=True)

    utils.setProgress(50, progressBar, "clean mesh")
    cmds.skinCluster(shape, e=True, ub=True)
    cmds.delete(mesh, ch=1)
    cmds.makeIdentity(mesh, apply=True)

    utils.setProgress(75, progressBar, "re-apply skin")
    nsc = cmds.skinCluster(attachedJoints, mesh, tsb=True, bm=0, nw=1)
    cmds.SkinWeights([shape, nsc], nwt=outInfluencesArray)
    utils.setProgress(100, progressBar, "freeze skinned mesh")
    return True

@shared.dec_undo
def hardSkinSelectionShells(selection, progressBar=False):
    utils.setProgress(0, progressBar, "converting to shells")
    expanded = shared.convertToVertexList(selection)
    mesh = expanded[0].split('.')[0]

    sc = shared.skinCluster(mesh, True)
    attachedJoints = cmds.skinCluster(sc, q=True, inf=True)

    vtxList = shared.convertToIndexList(expanded)
    foundFriendDict = shared.getConnectedVerts(mesh, vtxList)

    iteration = 0
    percentage = 99.0/len(foundFriendDict.keys())
    for group, entries in foundFriendDict.iteritems():
        list1 = foundFriendDict[group]
        vertices = shared.convertToCompList(mesh, list1)
        vertexWeights = dict.fromkeys(attachedJoints, 0.0)

        combinations = list(itertools.product(vertices, attachedJoints))
        for vertex, jnt in combinations:
            vertexWeights[jnt] += cmds.skinPercent(sc, vertex, transform=jnt, query=True)

        jointValueList = []
        for jnt in attachedJoints:
            newValue = vertexWeights[jnt] / float(len(vertices))
            jointValueList.append([jnt, newValue])

        cmds.skinPercent(sc, vertices, transformValue=jointValueList, normalize=1)
        utils.setProgress(iteration * percentage, progressBar, "setting shell data")
        iteration += 1
        cmds.refresh()
    
    utils.setProgress(100, progressBar, "hard skinned shells")
    return selection

@shared.dec_undo
def AvarageVertex(selection, useDistance, weightAverageWindow=None, progressBar=None):
    utils.setProgress(0, progressBar, "get selection data")
    vertexAmount = len(selection)
    if vertexAmount < 2:
        cmds.error("not enough vertices selected! select a minimum of 2")

    mesh = selection[0].split('.')[0]

    _isEdgeSelection = False
    if ".e[" in selection[0]:
        _isEdgeSelection = True

    sc = shared.skinCluster(mesh, True)
    infJoints = cmds.listConnections("%s.matrix"%sc, source=True)
    
    cmds.skinCluster(mesh, e=True, nw=1)
    if vertexAmount == 2 or _isEdgeSelection:
        baseList = [selection]
        if _isEdgeSelection:
            baseList = shared.edgesToSmooth(selection)

        percentage = 99.0/len(baseList)   
        for iteration, vertlist in enumerate(baseList):
            vertMap = componentPathFinding(vertlist, useDistance, weightWindow=weightAverageWindow)

            startWGT = cmds.skinPercent( sc, vertlist[0], q=True, v=True )        
            endWGT = cmds.skinPercent( sc, vertlist[1], q=True, v=True )  

            for vertex, percentage in vertMap.iteritems():
                newWeightsList = []
                for idx, weight in enumerate(startWGT):
                    value1 = endWGT[idx] * percentage
                    value2 = startWGT[idx] * (1-percentage)
                    newWeightsList.append( (infJoints[ idx ], value1 + value2) )
                cmds.skinPercent(sc, vertex, transformValue= newWeightsList)
            utils.setProgress(iteration * percentage, progressBar, "set path average data")
        utils.setProgress(iteration * percentage, progressBar, "average skin applied to path")
        return True            

    lastSelected = selection[-1]
    avgVertex(selection, lastSelected, progressBar)
    utils.setProgress(100, progressBar, "set average weight")
    return True

@shared.dec_undo
def neighbourAverage(components, warningPopup=True, progressBar=None):
    expandedVertices = shared.convertToVertexList(components)
    if warningPopup and len(expandedVertices) > 1000:
        result = cmds.confirmDialog(title='warning',
                                    message='current selection can take a long time to process, continue?',
                                    button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if result == "No":
            return

    utils.setProgress(100, progressBar, "get neighbor data")
    mesh = expandedVertices[0].split('.')[0]
    sc = shared.skinCluster(mesh)
    percentage = 99.0/len(expandedVertices)
    for index, vertex in enumerate(expandedVertices):
        cmds.AverageVtxWeight(vertex, sc=sc, wt=1)
        utils.setProgress(index * percentage, progressBar, "set average weight")

    utils.setProgress(100, progressBar, "set neighbor average")
    return True
