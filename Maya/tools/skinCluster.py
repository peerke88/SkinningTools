import math
from decimal import Decimal
from heapq import nsmallest

from SkinningTools.py23 import *
from SkinningTools.Maya.tools import shared, joints
from SkinningTools.Maya.tools.mesh import edgesToSmooth, shortestPolySurfaceCurvePathAverage
from SkinningTools.Maya.tools.shared import convertToVertexList
from SkinningTools.Maya.tools import shared 
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.UI.qt_util import *
from SkinningTools.UI import utils 

from maya import cmds, mel

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
        # if not utils.round_compare(prebind, curInvMat):
            return False
    return True

def getVertOverMaxInfluence(inObject, maxInfValue = 8, notSelect=False, progressBar=None ):
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
        utils.setprogress(i * percentage, progressBar, "checking vertices")
    utils.setprogress(100, progressBar, "vertices checked on %s"%inObject)
    return namedIndex, indexOverMap

@shared.dec_undo
def setMaxJointInfluences(inObject=None, maxInfValue=8, progressBar=None):
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
        utils.setprogress(index * percentage, progressBar, "removing influences")

    cmds.skinCluster(skinClusterName, e=True, fnw=1)

    cmds.setAttr("%s.maxInfluences" % skinClusterName, maxInfValue)
    cmds.setAttr("%s.maintainMaxInfluences" % skinClusterName, 1)

    utils.setprogress(100, progressBar, "set maximum influences")

    return True

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
                                button=['Yes', 'No'],
                                defaultButton='Yes',
                                cancelButton='No',
                                dismissString='No')
    if result == "Yes":
        joints.comparejointInfluences(meshes)
        return True
    return False
    
@shared.dec_undo
def execCopySourceTarget(TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection, smoothValue=1, progressBar=None):
    '''copy skincluster information from 1 object to another using closest amount of vertices based on selection'''

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
    
    allVerticesSource = convertToVertexList(sourceMesh)
    allVerticesTarget = convertToVertexList(targetMesh)

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

        utils.setprogress(tIndex * percentage, progressBar, "copy source > target vtx")

    index = 0
    for vertex in TargetSelection:
        number = allVerticesTarget.index(vertex)
        for jointIndex in xrange(jointAmount):
            weightindex = (number * jointAmount) + jointIndex
            targetInflArray[weightindex] = weightlist[index]
            index += 1

    cmds.SkinWeights([targetMesh, TargetSkinCluster], nwt=targetInflArray)

    utils.setprogress(100, progressBar, "copy from Source to Target")

    return succeeded

@shared.dec_undo
def transferClosestSkinning(objects, smoothValue, progressBar):
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

        execCopySourceTarget(newSkinCluster, origSkinCluster, convertToVertexList(object), convertToVertexList(object1), smoothValue, progressBar)
      
    return True

@shared.dec_undo
def transferSkinning(baseSkin, otherSkins, inPlace=True, sAs=True, uvSpace=False):
    '''using native maya copyskinweight to generate similar weight values
    @param baseSkin: mesh to copy skinning information from
    @param otherSkins: all other meshes that will gather weight information from the baseSkin
    @param inPlace: if True will make sure to cleanup the mesh and apply the skinning (also to be used for freezin the mesh in pose),
                    when false it assumes skinning is already applied to otherSkins and just copies the weights'''
    skinclusterBase = shared.skinCluster(baseSkin, silent=False)
    if skinclusterBase == None:
        return

    surfaceAssociation = "closestPoint"
    if sAs:
        surfaceAssociation = "closestComponent"
    
    for toSkinMesh in otherSkins:
        if inPlace:
            cmds.delete(toSkinMesh, ch=True)
        else:
            skincluster = shared.skinCluster(toSkinMesh, silent=False)
            if skincluster == None:
                continue
            cmds.skinCluster(skincluster, e=True, ub=True)

        
        jointInfls = cmds.listConnections("%s.matrix"%skinClusterBase, source=True)
        maxInfls = cmds.skinCluster(skinclusterBase, q=True, mi=True)
        joints.removeBindPoses()
        newSkinCl = cmds.skinCluster(jointInfls, toSkinMesh, mi=maxInfls)
        if uvSpace:
            cmds.copySkinWeights(ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 uv=["map1", "map1"], influenceAssociation=["label", "oneToOne", "name"],
                                 normalize=True)
        else:
            cmds.copySkinWeights(ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation=surfaceAssociation,
                                 influenceAssociation=["label", "oneToOne", "name"], normalize=True)
    return True

@shared.dec_undo
def Copy2MultVertex(selection, lastSelected):
    index = int(lastSelected.split("[")[-1].split("]")[0])
    mesh = lastSelected.split('.')[0]
    sc = shared.skinCluster(mesh, True)

    infJoints =  cmds.listConnections("%s.matrix"%sc, source=True)
    currentValues = cmds.skinPercent(sc, "%s.vtx[%i]"%(mesh, index), q=1, value=1)
    
    transformValueList = []
    for i, jnt in enumerate(infJoints):
        transformValueList.append([jnt, currentValues[i]])

    cmds.skinPercent(sc, selection, transformValue=transformValueList, normalize = 0,zeroRemainingInfluences = True )

    return True

@shared.dec_undo
def hammerVerts(inSelection, needsReturn=True):
    mesh = inSelection[0].split('.')[0]
    sc = shared.skinCluster(mesh, True)
    maxInfls = cmds.skinCluster(sc, q=True, mi=True)

    cmds.skinCluster(sc, e=1, sw = 0.0, swi= 5, omi = True, forceNormalizeWeights = True)
    if needsReturn:
        return convertToVertexList(inSelection)
    return True

@shared.dec_undo
def switchVertexWeight(vertex1, vertex2):
    mesh = vertex1.split('.')[0]
    sc = shared.skinCluster(mesh)
    cmds.skinCluster(mesh, e=True, nw=1)
    listBoneInfluence =  cmds.listConnections("%s.matrix"%sc, source=True)

    pointWeights1 = cmds.skinPercent(skinClusterName, vertex1, q=True, value=True)
    pointWeights2 = cmds.skinPercent(skinClusterName, vertex2, q=True, value=True)

    pointsWeightsList1 = []
    pointsWeightsList2 = []
    for j, bone in enumerate(listBoneInfluence):
        pointsWeightsList1.append(bone, pointWeights1[j])
        pointsWeightsList2.append(bone, pointWeights2[j])

    cmds.skinPercent(skinClusterName, vertex1, transformValue=pointsWeightsList2)
    cmds.skinPercent(skinClusterName, vertex2, transformValue=pointsWeightsList1)
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





@shared.dec_undo
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




@shared.dec_undo
def smoothAndSmoothNeighbours(input, both=False, growing=False):
    '''will hammer the weights of the selected region and then also hammer the edge of the selected region'''
    vertices = convertToVertexList(input)
    mesh = vertices[0].split('.')[0]
    
    sc = shared.skinCluster(mesh)
    if both:
        cmds.select(vertices, r=1)
        cmds.skinCluster(sc, geometry=vertices, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)
    
    grown = convertToVertexList(cmds.polyListComponentConversion(vertices, tf=True))
    fixedList = list(set(grown) ^ set(vertices))
    cmds.select(fixedList, r=1)
    cmds.skinCluster(sc, geometry=fixedList, e=True, sw=0.000001, swi=5, omi=0, forceNormalizeWeights=1)

    if not growing or both == False:
        return expandedVertices

    return fixedList

# @note: different ways to grow selection:
'''
from maya.api import OpenMaya
from maya import cmds
import time

# possible quick qay to get neighbours??

start = time.time()
vertices = cmds.ls(sl=1, fl=1)
mesh  = vertices[0].split(".")[0]

def convertToVertexList(inObject):
    convertedVertices = cmds.polyListComponentConversion(inObject, tv=True)
    return cmds.filterExpand(convertedVertices, sm=31)
grown = convertToVertexList(cmds.polyListComponentConversion(vertices, tf=True))
fixedList = list(set(grown) ^ set(vertices))
cmds.select(fixedList)
print time.time() -start


start = time.time()
vertices = cmds.ls(sl=1, fl=1)
mesh  = vertices[0].split(".")[0]

def n( name ):
    sellist = OpenMaya.MGlobal.getSelectionListByName( name )
    try:
        return sellist.getDagPath(0)
    except:
        return sellist.getDependNode(0)
shape = cmds.listRelatives(mesh, s=1)[0]
meshPath = n( shape )
meshNode = meshPath.node()

meshVerItFn = OpenMaya.MItMeshVertex( meshNode )

nbs = []
for vert in vertices:
    index = int(vert.split("[")[-1].split("]")[0])
    meshVerItFn.setIndex(index)
    nbs.extend(meshVerItFn.getConnectedVertices())
    
sel = []
for nb in nbs:
    sel.append("%s.vtx[%i]"%(mesh,nb))
cmds.select(sel)
print time.time() -start
'''


@shared.dec_undo
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


@shared.dec_undo
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


@shared.dec_undo
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


@shared.dec_undo
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


@shared.dec_undo
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


@shared.dec_undo
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


@shared.dec_undo
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


