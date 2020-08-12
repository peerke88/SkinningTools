from py23 import *
import math
from decimal import Decimal
from heapq import nsmallest

from Maya.tools import shared, joints
from Maya.tools.joints import comparejointInfluences, removeBindPoses
from Maya.tools.mesh import edgesToSmooth, shortestPolySurfaceCurvePathAverage
from ThirdParty.kdtree import KDTree
from UI.qt_util import *
from maya import cmds, mel
from Maya.tools.shared import convertToVertexList, dec_undo
from UI.SkinningToolsUI import SkinningTools


def getVertOverMaxInfluence(singleObject=None, MaxInfluenceValue=8, notSelect=False, progressBar=None):
    '''select all vertices that have more influences then the set Maximum'''
    if not notSelect:
        cmds.undoInfo(ock=True)
    allVerticesOverMaxInfluence = []

    cmds.select(singleObject, r=True)
    try:
        mel.eval('doPruneSkinClusterWeightsArgList 1 { "0.001" };')
    except:
        pass

    expandedVertices = convertToVertexList(singleObject)
    skinClusterName = SkinningTools.skinCluster(singleObject)
    bones = cmds.skinCluster(skinClusterName, q=True, inf=None)

    if progressBar:
        totalVertices = len(expandedVertices)
        percentage = 99.0 / totalVertices
        iteration = 1

    for vert in expandedVertices:
        # faster way then iteration over values
        numOfVertInfluences = len(cmds.skinPercent(skinClusterName, vert, q=True, value=True, ignoreBelow=0.001))
        if numOfVertInfluences > MaxInfluenceValue:
            allVerticesOverMaxInfluence.append(vert)

        if progressBar:
            progressBar.setValue(percentage * iteration)
            qApp.processEvents()
            iteration += 1

    if progressBar:
        progressBar.setValue(100)

    if not notSelect:
        cmds.undoInfo(cck=True)

    return allVerticesOverMaxInfluence


@dec_undo
def setMaxJointInfluences(objects=None, MaxInfluenceValue=8, progressBar=None):
    '''function that forces each vertex to have a maximum number of influences, pruning lowest values untill maximum is reached'''
    objectAmount = len(objects)
    fullPercentage = 99.0 / objectAmount
    for percentIteration, singleObject in enumerate(objects):
        toMuchinfls = getVertOverMaxInfluence(singleObject=singleObject, MaxInfluenceValue=MaxInfluenceValue,
                                              notSelect=True)  # returns the vertices that have too much influences
        if toMuchinfls == None or len(toMuchinfls) == 0:
            cmds.warning("no vertices over limit on: ", singleObject)
            continue

        if progressBar:
            totalVertices = len(toMuchinfls)
            percentage = fullPercentage / totalVertices
            iteration = 1;

        skin = toMuchinfls[0].split('.')[0]
        skinClusterName = SkinningTools.skinCluster(skin)
        meshShapeName = cmds.listRelatives(skin, s=True)[0]
        outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)

        infjnts = cmds.skinCluster(skinClusterName, q=True, inf=True)
        infLengt = len(infjnts)
        if outInfluencesArray == None:
            print("please check '%s' again!" % singleObject)
            continue

        lenOutInfArray = len(outInfluencesArray)

        for vertex in toMuchinfls:
            values = cmds.skinPercent(skinClusterName, vertex, q=1, v=1, ib=float(Decimal('1.0e-17')))
            curAmountValues = len(values)
            toPrune = curAmountValues - MaxInfluenceValue

            pruneFix = max(nsmallest(toPrune, values)) + 0.001
            cmds.skinPercent(skinClusterName, vertex, pruneWeights=pruneFix)

            if progressBar:
                progressBar.setValue((percentIteration * fullPercentage) + percentage * iteration)
                qApp.processEvents()
                iteration += 1;

        cmds.skinCluster(skinClusterName, e=True, fnw=1)

        cmds.setAttr("%s.maxInfluences" % skinClusterName, MaxInfluenceValue)
        cmds.setAttr("%s.maintainMaxInfluences" % skinClusterName, 1)

    if progressBar:
        progressBar.setValue(100)

    return True


@dec_undo
def execCopySourceTarget(TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection, smoothValue=1,
                         progressBar=None, amount=1):
    '''copy skincluster information from 1 object to another using closest amount of vertices based on selection'''
    sourcePoints = []
    sourcePointPos = []
    succeeded = True
    try:
        # make sure that both objects have the same joints
        mesh1 = TargetSelection[0].split('.')[0]
        mesh2 = SourceSelection[0].split('.')[0]
        joint = cmds.skinCluster(SourceSkinCluster, q=True, inf=True)
        joint1 = cmds.skinCluster(TargetSkinCluster, q=True, inf=True)
        jointAmount = len(joint)
        skinClusterName = SkinningTools.skinCluster(mesh1, True)
        bindPoseNode = cmds.dagPose(joint[0], q=True, bindPose=True)
        if bindPoseNode:
            outOfPose = cmds.dagPose(bindPoseNode, q=True, atPose=True)

        sourceInflArray = cmds.SkinWeights([mesh2, SourceSkinCluster], q=True)
        targetInflArray = cmds.SkinWeights([mesh1, TargetSkinCluster], q=True)

        sameMesh = True
        if mesh1 != mesh2:
            sameMesh = False
            compared = comparejointInfluences([mesh1, mesh2], True)
            if compared != None:
                if outOfPose != None:
                    result = cmds.confirmDialog(title='Confirm',
                                                message='object is not in BindPose,\ndo you want to continue out of bindpose?\npressing "No" will exit the operation! ',
                                                button=['Yes', 'No'],
                                                defaultButton='Yes',
                                                cancelButton='No',
                                                dismissString='No')
                    if result == "Yes":
                        comparejointInfluences([mesh1, mesh2])
                    else:
                        return
                else:
                    comparejointInfluences([mesh1, mesh2])

        allVerticesSource = convertToVertexList(mesh2)
        allVerticesTarget = convertToVertexList(mesh1)

        for sourceVert in SourceSelection:
            pos = cmds.xform(sourceVert, q=True, ws=True, t=True)
            sourcePoints.append(pos)
            sourcePointPos.append([sourceVert, pos])
        sourceKDTree = KDTree.construct_from_data(sourcePoints)

        if progressBar:
            oldValue = progressBar.value()
            if oldValue == 100:
                oldValue = 0
            totalVertices = len(TargetSelection)
            percentage = (99.0 / totalVertices) / amount
            iteration = 1;

        weightlist = []
        for targetVertex in TargetSelection:
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
            for jnt in joint1:
                for count, skinJoint in enumerate(joint):
                    if jnt != skinJoint:
                        continue
                    weightsCreation.append((newWeights[count] / divider))
            weightlist.extend(weightsCreation)

            if progressBar:
                progressBar.setValue(oldValue + (percentage * iteration))
                qApp.processEvents()
                iteration += 1;

        index = 0
        for vertex in TargetSelection:
            number = allVerticesTarget.index(vertex)
            for jointIndex in xrange(jointAmount):
                weightindex = (number * jointAmount) + jointIndex
                targetInflArray[weightindex] = weightlist[index]
                index += 1

        cmds.SkinWeights([mesh1, TargetSkinCluster], nwt=targetInflArray)
    except Exception as e:
        succeeded = False
        cmds.warning(e)
    finally:
        if progressBar:
            if amount == 1:
                progressBar.setValue(100)

    return succeeded


@dec_undo
def transferClosestSkinning(objects, smoothValue, progressBar):
    '''copy skincluster information from 1 object to another using closest amount of vertices'''
    object1 = objects[0]
    skinCluster = shared.skinCluster(object1)
    baseJoints = cmds.skinCluster(skinCluster, q=True, inf=True)
    amount = len(objects) - 1

    percentage = 100.0 / amount
    for iteration, object in enumerate(objects):
        if object == object1:
            continue

        skinCluster1 = skinCluster(object, silent=True)
        if skinCluster1 == None:
            skinCluster1 = cmds.skinCluster(object, baseJoints)[0]
        else:
            comparejointInfluences([object1, object])

        execCopySourceTarget(skinCluster1, skinCluster, convertToVertexList(object), convertToVertexList(object1),
                             smoothValue, progressBar, amount)
        if progressBar:
            progressBar.setValue(percentage * iteration)
            qApp.processEvents()

    if progressBar:
        progressBar.setValue(100)

    return True


@dec_undo
def transferSkinning(baseSkin, otherSkins, inPlace=True, sAs=True, uvSpace=False):
    '''using native maya copyskinweight to generate similar weight values
    @param baseSkin: mesh to copy skinning information from
    @param otherSkins: all other meshes that will gather weight information from the baseSkin
    @param inPlace: if True will make sure to cleanup the mesh and apply the skinning (also to be used for freezin the mesh in pose),
                    when false it assumes skinning is already applied to otherSkins and just copies the weights'''
    skinclusterBase = shared.skinCluster(baseSkin, silent=False)
    if skinclusterBase == None:
        return

    if sAs:
        surfaceAssociation = "closestComponent"
    else:
        surfaceAssociation = "closestPoint"

    for skin in otherSkins:
        if inPlace:
            cmds.delete(skin, ch=True)
        else:
            skincluster = shared.skinCluster(skin, silent=False)
            if skincluster == None:
                continue
            cmds.skinCluster(skincluster, e=True, ub=True)

        jointInfls = cmds.skinCluster(skinclusterBase, q=True, inf=True)
        maxInfls = cmds.skinCluster(skinclusterBase, q=True, mi=True)
        joints.removeBindPoses()
        newSkinCl = cmds.skinCluster(jointInfls, skin, mi=maxInfls)
        if uvSpace:
            cmds.copySkinWeights(ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 uv=["map1", "map1"], influenceAssociation=["label", "oneToOne", "name"],
                                 normalize=True)
        else:
            cmds.copySkinWeights(ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 influenceAssociation=["label", "oneToOne", "name"], normalize=True)
    return True


def AvarageVertex(selection, useDistance, weightAverageWindow=None, progressBar=None):
    '''generate an average weigth from all selected vertices to apply to the last selected vertice'''
    cmds.undoInfo(ock=True)
    vertexAmount = len(selection)
    if vertexAmount < 2:
        cmds.undoInfo(cck=True)
        cmds.error("not enough vertices selected! select a minimum of 2")

    objectSel = selection[0]
    if "." in selection[0]:
        objectSel = selection[0].split('.')[0]

    isEdgeSelection = False
    if ".e[" in selection[0]:
        isEdgeSelection = True

    skinClusterName = SkinningTools.skinCluster(objectSel, True)
    succeeded = True
    cmds.setAttr("%s.envelope" % skinClusterName, 0)
    try:
        cmds.skinCluster(objectSel, e=True, nw=1)
        if vertexAmount == 2 or isEdgeSelection:
            baseList = [selection]
            if isEdgeSelection:
                baseList = edgesToSmooth(selection)

            percentage = 99.0 / len(baseList)
            for iteration, vertlist in enumerate(baseList):
                shortestPolySurfaceCurvePathAverage(vertlist, skinClusterName, useDistance,
                                                    weightWindow=weightAverageWindow)

                if progressBar != None:
                    cmds.setAttr("%s.envelope" % skinClusterName, 1)
                    cmds.select(vertlist, r=1)
                    cmds.refresh()
                    progressBar.setValue(percentage * iteration)
                    QApplication.processEvents()
                    cmds.setAttr("%s.envelope" % skinClusterName, 0)

            if progressBar != None:
                cmds.setAttr("%s.envelope" % skinClusterName, 1)
                progressBar.setValue(100)
                QApplication.processEvents()

        else:
            lastSelected = selection[-1]
            pointList = [x for x in selection if x != lastSelected]
            meshName = lastSelected.split('.')[0]

            listBoneInfluences = cmds.skinCluster(meshName, q=True, weightedInfluence=True)
            influenceSize = len(listBoneInfluences)

            TemporaryVertexJoints = []
            TemporaryVertexWeights = []
            for point in pointList:
                for bone in xrange(influenceSize):
                    pointWeights = cmds.skinPercent(skinClusterName, point, transform=listBoneInfluences[bone], q=True,
                                                    value=True)
                    if pointWeights < 0.000001:
                        continue
                    TemporaryVertexJoints.append(listBoneInfluences[bone])
                    TemporaryVertexWeights.append(pointWeights)

            totalValues = 0.0
            AvarageValues = []
            CleanList = []
            for i in TemporaryVertexJoints:
                if i not in CleanList:
                    CleanList.append(i)

            for i in xrange(len(CleanList)):
                WorkingValue = 0.0
                for j in xrange(len(TemporaryVertexJoints)):
                    if not TemporaryVertexJoints[j] == CleanList[i]:
                        continue
                    WorkingValue += TemporaryVertexWeights[j]
                numberOfPoints = len(pointList)
                AvarageValues.append((WorkingValue / numberOfPoints))
                totalValues += AvarageValues[i];

            summary = 0
            for Value in xrange(len(AvarageValues)):
                temporaryValue = AvarageValues[Value] / totalValues
                AvarageValues[Value] = temporaryValue
                summary += AvarageValues[Value]

            command = cStringIO.StringIO()
            command.write('cmds.skinPercent("%s","%s", transformValue=[' % (skinClusterName, lastSelected))

            for count, skinJoint in enumerate(CleanList):
                command.write('("%s", %s)' % (skinJoint, AvarageValues[count]))
                if not count == len(CleanList) - 1:
                    command.write(', ')
            command.write('])')
            eval(command.getvalue())

    except Exception as e:
        cmds.warning(e)
        succeeded = False
    finally:
        cmds.setAttr("%s.envelope" % skinClusterName, 1)
        cmds.undoInfo(cck=True)

    return succeeded


def Copy2MultVertex(selection, secondSelection=False):
    ''' copy vertex informaton from 1 vetex to the rest of the selection, making sure all weights are the same'''
    if not len(selection) >= 2:
        cmds.error("please select more then 2 components!")
    lastSelected = selection[-1]
    if secondSelection:
        lastSelected = selection[1]
    pointList = [x for x in selection if x != lastSelected]
    baseMesh = lastSelected.split('.')[0]
    meshShapeName = cmds.listRelatives(baseMesh, s=True)[0]
    skinClusterName = SkinningTools.skinCluster(baseMesh, True)

    SkinWeightCopyInfluences = cmds.skinCluster(skinClusterName, q=True, inf=True)
    SkinWeightCopyWeights = cmds.skinPercent(skinClusterName, lastSelected, query=True, value=True)

    # using selection is faster then going through for loop ... thank you maya!
    cmds.select(pointList)
    command = cStringIO.StringIO()
    command.write('cmds.skinPercent("%s", transformValue=[' % (skinClusterName))

    for count, skinJoint in enumerate(SkinWeightCopyInfluences):
        command.write('("%s", %s)' % (skinJoint, SkinWeightCopyWeights[count]))
        if not count == len(SkinWeightCopyInfluences) - 1:
            command.write(', ')
    command.write('], normalize=False, zeroRemainingInfluences=True)')
    eval(command.getvalue())

    return True


@dec_undo
def neighbourAverage(components, warningPopup=True):
    '''similar to hammer skinweights, more brute force, smooths current weights according to nearest neighbour'''
    expandedVertices = convertToVertexList(components)
    if warningPopup and len(expandedVertices) > 1000:
        result = cmds.confirmDialog(title='warning',
                                    message='current selection can take a long time to process, continue?',
                                    button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if result == "No":
            cmds.undoInfo(cck=True)
            return

    meshes = {}
    for expandedVert in expandedVertices:
        mesh = expandedVert.split('.')[0]
        if not mesh in meshes:
            meshes[mesh] = [expandedVert]
        else:
            meshes[mesh].append(expandedVert)

    for mesh in meshes:
        skinClusterName = SkinningTools.skinCluster(mesh)

        for vertex in meshes[mesh]:
            cmds.AverageVtxWeight(vertex, sc=skinClusterName, wt=1)

    return True


@dec_undo
def hammerVerts(input, needsReturn=True):
    ''' simple call for the weight hammer mel command + added functionality to return vertices'''
    cmds.select(input, r=1)
    mel.eval("weightHammerVerts")
    if needsReturn:
        return convertToVertexList(input)
    return True


@dec_undo
def BoneMove(bone1, bone2, skin):
    '''transfer weights between 2 joints using the selected mesh'''
    skinClusterName = SkinningTools.skinCluster(skin, True)
    infjnts = cmds.skinCluster(skinClusterName, q=True, inf=True)

    if not bone1 in infjnts:
        cmds.skinCluster(skinClusterName, e=True, lw=False, wt=0.0, ai=bone1)
    if not bone2 in infjnts:
        cmds.skinCluster(skinClusterName, e=True, lw=False, wt=0.0, ai=bone2)

    meshShapeName = cmds.listRelatives(skin, s=True)[0]
    outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)

    # get bone1 position and bone2 position in list
    infLengt = len(infjnts)
    bone1Pos = 0
    bone2Pos = 0
    for i in xrange(infLengt):
        if infjnts[i] == bone1:
            bone1Pos = i
        if infjnts[i] == bone2:
            bone2Pos = i

    lenOutInfArray = len(outInfluencesArray)
    amountToLoop = (lenOutInfArray / infLengt)

    for j in xrange(amountToLoop):
        newValue = outInfluencesArray[(j * infLengt) + bone2Pos] + outInfluencesArray[(j * infLengt) + bone1Pos]
        outInfluencesArray[(j * infLengt) + bone2Pos] = newValue
        outInfluencesArray[(j * infLengt) + bone1Pos] = 0.0

    cmds.SkinWeights([meshShapeName, skinClusterName], nwt=outInfluencesArray)
    return True


@dec_undo
def BoneSwitch(joint1, joint2, skin):
    '''switch bone influences by reconnecting matrices in the skincluster plugs
    really fast, downside: only applicable in bindpose'''

    skinClusterName = SkinningTools.skinCluster(skin, True)
    connection1 = cmds.listConnections(joint1 + '.worldMatrix', s=0, d=1, c=1, p=1, type="skinCluster")
    connection2 = cmds.listConnections(joint2 + '.worldMatrix', s=0, d=1, c=1, p=1, type="skinCluster")

    sameCluster1 = False
    sameCluster2 = False
    currentConnection1 = ''
    currentConnection2 = ''
    for conn1 in connection1:
        if conn1.split('.')[0] == skinClusterName:
            sameCluster1 = True
            currentConnection1 = conn1
    for conn2 in connection2:
        if conn2.split('.')[0] == skinClusterName:
            sameCluster2 = True
            currentConnection2 = conn2

    if sameCluster1 == False or sameCluster2 == False:
        cmds.warning("bones not part of the same skincluster!")
    try:
        origConnection1 = currentConnection1.split('matrix')[-1]
        origConnection2 = currentConnection2.split('matrix')[-1]

        cmds.disconnectAttr(joint1 + '.worldMatrix', currentConnection1)
        cmds.disconnectAttr(joint2 + '.worldMatrix', currentConnection2)
        cmds.disconnectAttr("%s.lockInfluenceWeights" % joint1, "%s.lockWeights%s" % (skinClusterName, origConnection1))
        cmds.disconnectAttr("%s.lockInfluenceWeights" % joint2, "%s.lockWeights%s" % (skinClusterName, origConnection2))

        cmds.connectAttr(joint1 + '.worldMatrix', currentConnection2, f=1)
        cmds.connectAttr(joint2 + '.worldMatrix', currentConnection1, f=1)
        cmds.connectAttr("%s.lockInfluenceWeights" % joint1, "%s.lockWeights%s" % (skinClusterName, origConnection2),
                         f=1)
        cmds.connectAttr("%s.lockInfluenceWeights" % joint2, "%s.lockWeights%s" % (skinClusterName, origConnection1),
                         f=1)

        SkinningTools().resetSkinnedJoints([joint1, joint2], skinClusterName)
    except Exception as e:
        cmds.warning(e)
        return False
    return True


@dec_undo
def ShowInfluencedVerts(skin, bones, progressBar=None):
    ''' management to show and select all vertices that are influenced by the given bones. 
    even a small influence (for example: "1.0e-17") will be shown '''
    selection = []
    percentage = 100.0 / len(bones)

    skinClusterName = SkinningTools.skinCluster(skin, True)
    for iteration, bone in enumerate(bones):
        # pymel version is cleaner as it doesnt do unecesary selections in between
        if _pymel:
            jointsAttached = cmds.skinCluster(skinClusterName, q=True, inf=True)
            if not bone in jointsAttached:
                continue
            skinNode = PyNode(skinClusterName)
            vert_list, values = skinNode.getPointsAffectedByInfluence(bone)
            foundVerts = vert_list.getSelectionStrings()
            if len(foundVerts) == 0:
                continue
            expandedVertices = convertToVertexList(foundVerts)
        else:
            cmds.select(cl=True)
            cmds.skinCluster(skin, e=True, nw=1)
            cmds.select(bone, d=True)
            SkinningTools.doCorrectSelectionVisualization(skin)
            cmds.select(cl=True)
            cmds.skinCluster(skinClusterName, e=True, siv=bone)
            expandedVertices = cmds.ls(sl=True, fl=True)
        if expandedVertices == None or len(expandedVertices) == 0:
            continue
        for select in expandedVertices:
            if not "." in select:
                continue
            selection.append(select)

        if progressBar != None:
            progressBar.setValue(percentage * iteration)
            QApplication.processEvents()
    if progressBar != None:
        progressBar.setValue(100)
        QApplication.processEvents()

    SkinningTools.doCorrectSelectionVisualization(skin)
    return selection


@dec_undo
def switchVertexWeight(vertex1, vertex2):
    '''switches weight infromation between 2 vertices'''
    mesh = vertex1.split('.')[0]
    skinClusterName = SkinningTools.skinCluster(mesh)
    cmds.skinCluster(mesh, e=True, nw=1)
    listBoneInfluence = cmds.skinCluster(mesh, q=True, influence=True)

    boneAmount = len(listBoneInfluence)

    pointWeights1 = cmds.skinPercent(skinClusterName, vertex1, q=True, value=True)
    pointWeights2 = cmds.skinPercent(skinClusterName, vertex2, q=True, value=True)

    pointsWeightsList1 = [None] * boneAmount
    pointsWeightsList2 = [None] * boneAmount
    for j, bone in enumerate(listBoneInfluence):
        pointsWeightsList1[j] = (bone, pointWeights1[j])
        pointsWeightsList2[j] = (bone, pointWeights2[j])

    cmds.skinPercent(skinClusterName, vertex1, transformValue=pointsWeightsList2)
    cmds.skinPercent(skinClusterName, vertex2, transformValue=pointsWeightsList1)
    return True


@dec_undo
def smoothAndSmoothNeighbours(input, both=False, growing=False):
    '''will hammer the weights of the selected region and then also hammer the edge of the selected region'''
    expandedVertices = convertToVertexList(input)
    meshes = {}
    for expandedVert in expandedVertices:
        mesh = expandedVert.split('.')[0]
        if not mesh in meshes:
            meshes[mesh] = [expandedVert]
        else:
            meshes[mesh].append(expandedVert)

    for mesh in meshes:
        skinClusterName = shared.skinCluster(mesh)
        if both:
            cmds.select(meshes[mesh], r=1)
            cmds.skinCluster(skinClusterName, geometry=meshes[mesh], e=True, sw=0.000001, swi=5, omi=0,
                             forceNormalizeWeights=1)
        convertedFaces = cmds.polyListComponentConversion(meshes[mesh], tf=True)
        expandedVertices1 = convertToVertexList(convertedFaces)
        fixedList = list(set(expandedVertices1) ^ set(meshes[mesh]))
        cmds.select(fixedList, r=1)
        cmds.skinCluster(skinClusterName, geometry=fixedList, e=True, sw=0.000001, swi=5, omi=0,
                         forceNormalizeWeights=1)

    if not growing or both == False:
        return expandedVertices
    return fixedList


@dec_undo
def removeUnusedInfluences(objects, progressBar=None):
    percentage = 100.0 / len(objects)
    for index, obj in enumerate(objects):
        skinClusterName = SkinningTools.skinCluster(obj, True)
        if not skinClusterName:
            shape = cmds.listRelatives(obj, s=1) or None
            if progressBar:
                progressBar.setValue(percentage * (index + 1))
                qApp.processEvents()
            if shape != None:
                cmds.warning("mesh object: %s has no skincluster attached!" % obj)
            continue
        attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)
        weightedJoints = cmds.skinCluster(skinClusterName, q=True, wi=True)

        nonInfluenced = []
        for attached in attachedJoints:
            if attached in weightedJoints:
                continue
            nonInfluenced.append(attached)

        for joint in nonInfluenced:
            cmds.skinCluster(skinClusterName, e=True, ri=joint)

        cmds.flushUndo()
        if progressBar:
            progressBar.setValue(percentage * (index + 1))
            qApp.processEvents()

    if progressBar:
        progressBar.setValue(100.0)
        qApp.processEvents()
    return True


@dec_undo
def transferUvToSkinnedObject(mesh_source, mesh_target):
    '''transfer uv's to intermediate shape instead of final shape. clean and no deformation with bind movement'''
    shapes = cmds.listRelatives(mesh_target, ad=True, type="mesh")
    mesh_orig = None
    for shape in shapes:
        if cmds.getAttr("%s.intermediateObject" % shape) == 0:
            continue
        mesh_orig = shape

    if mesh_orig == None:
        cmds.error("no intermediate shape found!")

    cmds.setAttr("%s.intermediateObject" % shape, 0)
    cmds.transferAttributes(mesh_source, mesh_orig,
                            transferPositions=False,
                            transferNormals=False,
                            transferUVs=2,
                            transferColors=2,
                            sampleSpace=4,
                            sourceUvSpace="map1",
                            targetUvSpace="map1",
                            searchMethod=3,
                            flipUVs=False,
                            colorBorders=True
                            )
    cmds.setAttr("%s.intermediateObject" % shape, 1)
    cmds.delete(mesh_orig, ch=1)

    return mesh_target


def freezeSkinnedMesh(meshes, progressBar=None):
    '''freeze transformations and delete history on skinned mesh 
    @param meshes: all meshes that need to be cleaned'''
    if len(meshes) == 0:
        cmds.error("nothing selected please select a mesh")

    cmds.undoInfo(stateWithoutFlush=0)
    try:
        percentage = 100.0 / len(meshes)
        for index, mesh in enumerate(meshes):
            skinClusterName = SkinningTools.skinCluster(mesh, True)
            attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)

            meshShapeName = cmds.listRelatives(mesh, s=True)[0]
            outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)

            cmds.skinCluster(meshShapeName, e=True, ub=True)
            cmds.delete(mesh, ch=1)
            cmds.makeIdentity(mesh, apply=True)

            newSkinClusterName = cmds.skinCluster(attachedJoints, mesh, tsb=True, bm=0, nw=1)
            cmds.SkinWeights([meshShapeName, newSkinClusterName], nwt=outInfluencesArray)

            if progressBar:
                progressBar.setValue(percentage * (index + 1))
                qApp.processEvents()
    except Exception as e:
        cmds.warning(e)
        meshes = None
    finally:
        if progressBar:
            progressBar.setValue(100.0)
            qApp.processEvents()

    cmds.undoInfo(stateWithoutFlush=1)
    return meshes


@dec_undo
def seperateSkinnedObject(meshes, progressBar=None):
    '''seperates mesh by polyshells and keeps skinning information intact
    @param meshes: all meshses that need to be seperated'''

    def getShellFaces(poly):
        shells = []
        shells1 = []
        faces = set()
        total = cmds.polyEvaluate(s=True)

        for f in xrange(cmds.polyEvaluate(poly, f=True)):

            if len(shells) >= total:
                break
            if f in faces:
                continue

            shell = cmds.polySelect(poly, q=1, extendToShell=f)
            faces.update(shell)

            val = ".f[%d:%d]" % (min(shell), max(shell))
            shells.append(val)

        return shells

    objectAmount = len(meshes)
    fullPercentage = 99.0 / objectAmount

    for percentIteration, mesh in enumerate(meshes):
        shape = cmds.listRelatives(mesh, ad=True, s=True)
        shells1 = getShellFaces(mesh)

        if progressBar:
            total = len(shells1)
            percentage = fullPercentage / total
            iteration = 1

        newMeshes = []
        for i, shell in enumerate(shells1):

            dup = cmds.duplicate(mesh)[0]
            newShells = []
            for obj in shells1:
                newShells.append(dup + obj)
            newShells.pop(i)
            cmds.delete(newShells)
            cmds.flushUndo()
            newMeshes.append(dup)

            if progressBar:
                progressBar.setValue((percentIteration * fullPercentage) + percentage * iteration)
                qApp.processEvents()
                iteration += 1

        transferSkinning(mesh, newMeshes, inPlace=True)
        cmds.delete(shape)
        cmds.parent(newMeshes, mesh)

    if progressBar:
        progressBar.setValue(100)
        qApp.processEvents()
    return True


@dec_undo
def extractSkinnedShells(components):
    '''extracts selected components as a new mesh but keeps skininfo
    @param components: components needed to extract to include skinning, if no skincluster found only extracts mesh'''

    def convertToFaces(components):
        convertedFaces = cmds.polyListComponentConversion(components, tf=True)
        expandedFaces = cmds.filterExpand(convertedFaces, sm=34)
        return expandedFaces

    if len(components) > 0:
        mesh = components[0]
    else:
        mesh = components

    if "." in mesh:
        mesh = mesh.split(".")[0]

    faces = convertToFaces(components)
    dup = cmds.duplicate(mesh)[0]
    allFaces = convertToFaces(dup)

    newSel = []
    for face in faces:
        newSel.append("%s.%s" % (dup, face.split(".")[-1]))

    cmds.delete(list(set(allFaces) ^ set(newSel)))
    cmds.delete(dup, ch=1)
    if SkinningTools.skinCluster(mesh, True) == None:
        return
    transferSkinning(mesh, [dup], inPlace=True)
    return dup


@dec_undo
def combineSkinnedMeshes(meshes):
    '''combines meshes and keeps skin info in tact
    uses maya command for maya 2016+
    @param meshes: all the meshes that need to be combined, if a mesh has no skincluster it will not be included'''
    joints.comparejointInfluences(meshes)

    attachedSortedJoints = None
    sourcePos = []
    sourcePosWeight = []
    for mesh in meshes:
        meshShapeName = cmds.listRelatives(mesh, s=True)[0]
        skinClusterName = SkinningTools.skinCluster(mesh, True)
        if skinClusterName == None:
            continue
        attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)

        outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName], q=True)
        jointLen = len(attachedJoints)
        if attachedSortedJoints == None:
            attachedSortedJoints = attachedJoints

        vertices = shared.convertToVertexList(mesh)
        for index, vert in enumerate(vertices):
            position = cmds.xform(vert, q=True, ws=True, t=True)
            sourcePos.append(position)

            newList = []
            if attachedSortedJoints != attachedJoints:
                d = {}
                wList = outInfluencesArray[:jointLen]
                for ids, joint in enumerate(attachedJoints):
                    d[joint] = wList[ids]
                for jnt in attachedSortedJoints:
                    newList.append(d[jnt])

            else:
                newList = outInfluencesArray[:jointLen]

            sourcePosWeight.append([position, newList])
            del outInfluencesArray[:jointLen]

    newMesh = cmds.polyUnite(meshes, ch=1, mergeUVSets=1)[0]
    cmds.delete(newMesh, ch=1)

    sourceKDTree = KDTree.construct_from_data(sourcePos)

    skinCluster = cmds.skinCluster(newMesh, attachedJoints, tsb=True)
    attachedJoints = cmds.skinCluster(skinCluster, q=True, inf=True)

    newInfluenceArray = []
    newMeshVertices = convertToVertexList(newMesh)
    for index, vertex in enumerate(newMeshVertices):
        pos = cmds.xform(vertex, q=True, ws=True, t=True)
        pts = sourceKDTree.query(query_point=pos, t=1)

        for positionList in sourcePosWeight:
            if pts[0] != positionList[0]:
                continue
            newList = []
            d = {}
            for ids, joint in enumerate(attachedSortedJoints):
                d[joint] = positionList[1][ids]
            for jnt in attachedJoints:
                newList.append(d[jnt])
            newInfluenceArray.extend(newList)

    meshShapeName = cmds.listRelatives(newMesh, s=True)[0]
    cmds.SkinWeights([meshShapeName, skinCluster[0]], nwt=newInfluenceArray)
    return newMesh


@dec_undo
def keepOnlySelectedInfluences(fullSelection, jointOnlySelection):
    '''removes influences on selected component that are not selected in the jointsselection given
    @param fullSelection: component or mesh selection that needs te be cleaned
    @param jointOnlySelection: these are the joints that are allowed to influence the selected components/meshes'''

    onlyMesh = list(set(fullSelection) ^ set(jointOnlySelection))
    mesh = onlyMesh[0].split(".")[0]
    skinCluster = SkinningTools.skinCluster(mesh, True)

    allJoints = cmds.ls(type="joint")
    jointsToRemove = list(set(allJoints) ^ set(jointOnlySelection))
    attachedJoints = cmds.skinCluster(skinCluster, q=True, inf=True)

    expandedVertices = convertToVertexList(onlyMesh)

    cmds.select(expandedVertices, r=1)
    jointsToRemoveValues = []
    for jnt in jointsToRemove:
        if not jnt in attachedJoints:
            continue
        jointsToRemoveValues.append((jnt, 0))

    cmds.skinPercent(skinCluster, tv=jointsToRemoveValues, normalize=True)
    return True


@dec_undo
def hardSkinSelectionShells(selection, progressBar=False):
    '''converts selection to shells, gathers weights from each shell and averages it out and give each vertex of the shell the new weights
    @param selection: input selection, any component selection will do'''

    expanded = convertToVertexList(selection)

    meshName = cmds.ls(sl=1)[0].split('.')[0]
    skinClusterName = shared.skinCluster(meshName, True)
    attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)

    objType = cmds.objectType(expanded[0])
    if not objType == "mesh":
        cmds.error("selectionShells only work on polygon components")
    vtxList = set([int(x.split("[")[-1][:-1]) for x in expanded])
    foundFriendDict = getConnectedVerts(meshName, vtxList)

    if progressBar:
        percentage = 100.0 / len(foundFriendDict)
        iteration = 0

    for group, entries in foundFriendDict.iteritems():
        list1 = foundFriendDict[group]
        vertices = []
        vertexWeights = dict.fromkeys(attachedJoints, 0.0)
        for vertex in list1:

            vertexName = "%s.vtx[%s]" % (meshName, vertex)

            vertices.append(vertexName)
            for jnt in attachedJoints:
                value = cmds.skinPercent(skinClusterName, vertexName, transform=jnt, query=True)
                vertexWeights[jnt] += value

        jointValueList = []
        for jnt in attachedJoints:
            newValue = vertexWeights[jnt] / float(len(vertices))
            jointValueList.append([jnt, newValue])

        cmds.select(vertices, r=1)
        cmds.skinPercent(skinClusterName, transformValue=jointValueList, normalize=1)
        cmds.refresh()
        if progressBar:
            progressBar.setValue(percentage * iteration)
            qApp.processEvents()
            iteration += 1;
    if progressBar:
        progressBar.setValue(100.0)
    return selection
