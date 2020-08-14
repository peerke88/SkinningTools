from maya import cmds
from maya.OpenMaya import MVector
from shared import *

from SkinningTools.Maya.tools import shared
from SkinningTools.Maya.tools.shared import convertToVertexList, Graph, shortest_path
from SkinningTools.UI.fallofCurveUI import BezierFunctions


def shortestPolySurfaceCurvePathAverage(selection, skinClusterName, useDistance, diagonal=False, weightWindow=None):
    ''' method to find a path between 2 given points (vertex and cv)
    polygons uses edges to find shortes path (loops and shortest edgepath functions)
    nurbs surface uses dijkstra algorythim (both diagonally and u/v based)
    nurbs curve uses simple indexing'''

    def measureLength(object1, object2):
        pos1 = MVector(*cmds.xform(object1, q=True, ws=True, t=True))
        pos2 = MVector(*cmds.xform(object2, q=True, ws=True, t=True))
        return (pos1 - pos2).length()

    start = selection[0]
    end = selection[-1]
    surface = start.split('.')[0]

    objType = cmds.objectType(start)
    poly = False
    if objType == 'mesh':
        poly = True
        added = 0.0
        firstExtendedEdges = cmds.polyListComponentConversion(start, te=True)
        firstExtended = cmds.filterExpand(firstExtendedEdges, sm=32)
        secondExtendedEdges = cmds.polyListComponentConversion(end, te=True)
        secondExtended = cmds.filterExpand(secondExtendedEdges, sm=32)

        found = []
        for e1 in firstExtended:
            for e2 in secondExtended:
                e1n = int(e1.split(".e[")[-1].split("]")[0])
                e2n = int(e2.split(".e[")[-1].split("]")[0])
                edgeSel = cmds.polySelect(surface, elp=[e1n, e2n], ns=True)
                if edgeSel == None:
                    continue
                found.append(edgeSel)
        amountFound = len(found)
        if amountFound != 0:
            # first choice:
            if amountFound == 1:
                edgeSelection = found[0]
            else:
                edgeSelection = found[0]
                for sepList in found:
                    if not len(sepList) < len(edgeSelection):
                        continue
                    edgeSelection = sepList
        else:
            # second choice:
            vertexNumber1 = int(start.split('vtx[')[-1].split("]")[0])
            vertexNumber2 = int(end.split('vtx[')[-1].split("]")[0])
            edgeSelection = cmds.polySelect(surface, shortestEdgePath=[vertexNumber1, vertexNumber2])
            if edgeSelection == None:
                cmds.error("selected vertices are not part of the same polyShell!")

        allEdges = []
        newVertexSelection = []
        for edge in edgeSelection:
            allEdges.append("%s.e[%s]" % (surface, edge))
            midexpand = convertToVertexList("%s.e[%s]" % (surface, edge))
            newVertexSelection.append(midexpand)

        start = selection[0]
        end = selection[-1]

        if start in newVertexSelection[0]:
            reverse = False
        else:
            reverse = True

        inOrder = []
        lastVertex = None
        for listVerts in newVertexSelection:
            if start in listVerts:
                listVerts.remove(start)
            if lastVertex != None:
                listVerts.remove(lastVertex)
            if end in listVerts:
                listVerts.remove(end)
            if len(listVerts) != 0:
                lastVertex = listVerts[0]
                inOrder.append(lastVertex)

        amount = len(inOrder) + 1
        if reverse:
            inOrder.reverse()

        totalDistance = measureLength(inOrder[-1], end)

    elif objType == "nurbsSurface":
        allCvs = cmds.filterExpand("%s.cv[*][*]" % surface, sm=28)
        graph = Graph()  # implemented from above (dijkstra algorithm)
        added = -2.0
        recomputeDict = {}
        for node in allCvs:
            base = (node)
            graph.add_node(base)
            recomputeDict[base] = node

        for node in allCvs:
            cmds.select(cl=1)
            cmds.nurbsSelect(node, gs=1)
            gro = cmds.ls(sl=1)[0]

            if diagonal == False:
                # rough implementation to not cross U and V at the same time (2 implementation only)
                workString = node.split("][")
                groString = gro.split("][")
                gro = ["%s][%s" % (workString[0], groString[-1]), "%s][%s" % (groString[0], workString[-1])]

            gro = cmds.filterExpand(gro, sm=28)

            gro.remove(node)
            basePos = MVector(*cmds.xform(node, q=1, ws=1, t=1))
            for f in gro:
                fPos = MVector(*cmds.xform(f, q=1, ws=1, t=1))
                fLen = (fPos - basePos).length()
                graph.add_edge((node), (f), fLen)

        shortest = shortest_path(graph, (start), (end))

        inOrder = []
        for sh in shortest[-1]:
            inOrder.append(recomputeDict[sh])
        amount = len(inOrder) + 1
        totalDistance = shortest[0]

    elif objType == "lattice":
        allCvs = cmds.filterExpand("%s.pt[*]" % surface, sm=46)
        graph = Graph()  # implemented from above (dijkstra algorithm)
        added = -2.0
        recomputeDict = {}
        for node in allCvs:
            base = (node)
            graph.add_node(base)
            recomputeDict[base] = node

        for node in allCvs:
            gro = growLatticePoints([node])
            gro.remove(node)
            basePos = MVector(*cmds.xform(node, q=1, ws=1, t=1))
            for f in gro:
                fPos = MVector(*cmds.xform(f, q=1, ws=1, t=1))
                fLen = (fPos - basePos).length()
                graph.add_edge((node), (f), fLen)

        shortest = shortest_path(graph, (start), (end))

        inOrder = []
        for sh in shortest[-1]:
            inOrder.append(recomputeDict[sh])
        amount = len(inOrder) + 1
        totalDistance = shortest[0]

    else:
        numbers = [int(start.split("[")[-1].split("]")[0]), int(end.split("[")[-1].split("]")[0])]
        added = -1.0
        rangeList = range(min(numbers), max(numbers) + 1)
        amount = len(rangeList)
        inOrder = []
        totalDistance = 0.0
        for i, num in enumerate(rangeList):
            cv = "%s.cv[%s]" % (surface, num)
            inOrder.append(cv)
            if i == 0:
                continue
            totalDistance += measureLength(inOrder[i - 1], cv)

    listBoneInfluences = cmds.skinCluster(surface, q=True, inf=True)
    weights1 = cmds.skinPercent(skinClusterName, start, q=True, v=True)
    weights2 = cmds.skinPercent(skinClusterName, end, q=True, v=True)

    lengths = []
    if useDistance:
        for index, vertex in enumerate(inOrder):
            if index == 0:
                length = measureLength(start, vertex)
            else:
                length = measureLength(inOrder[index - 1], vertex)
            if poly:
                totalDistance += length
            lengths.append(length)

    percentage = float(1.0) / (amount + added)
    currentLength = 0.0
    for index, vertex in enumerate(inOrder):
        if not useDistance:
            currentPercentage = (index) * percentage
            if poly:
                currentPercentage = (index + 1) * percentage

            if weightWindow == None:
                continue
            if type(weightWindow) == types.ListType or type(weightWindow) == types.TupleType:
                currentPercentage = BezierFunctions.getDataOnPercentage(currentPercentage, weightWindow)
            else:
                currentPercentage = weightWindow.getDataOnPerc(currentPercentage)

        else:
            currentLength += lengths[index]
            currentPercentage = (currentLength / totalDistance)
            if weightWindow == None:
                continue
            if type(weightWindow) == types.ListType or type(weightWindow) == types.TupleType:
                currentPercentage = BezierFunctions.getDataOnPercentage(currentPercentage, weightWindow)
            else:
                currentPercentage = weightWindow.getDataOnPerc(currentPercentage)

        newWeightsList = []
        for idx, weight in enumerate(weights1):
            value1 = weights2[idx] * currentPercentage
            value2 = weights1[idx] * (1 - currentPercentage)
            newWeightsList.append((listBoneInfluences[idx], value1 + value2))

        cmds.skinPercent(skinClusterName, vertex, transformValue=newWeightsList)

    cmds.select([start, end], r=1)


def edgesToSmooth(inEdges):
    def convertToIndexList(vertList):
        indices = []
        for i in vertList:
            index = int(i.split("[")[-1].split("]")[0])
            indices.append(index)
        return indices

    def convertToVertList(indices, mesh):
        vertices = []
        for i in list(indices):
            vrt = "%s.vtx[%s]" % (mesh, i)

            vertices.append(vrt)
        return vertices

    def toToEdgeNumber(vtx):
        toEdges = cmds.polyListComponentConversion(vtx, te=True)
        edges = cmds.filterExpand(toEdges, sm=32)
        en = []
        for e in edges:
            en.append(int(e.split(".e[")[-1].split("]")[0]))
        return en

    def checkEdgeLoop(mesh, vtx1, vtx2, first=True):
        e1n = toToEdgeNumber(vtx1)
        e2n = toToEdgeNumber(vtx2)
        found = []
        for e1 in e1n:
            for e2 in e2n:
                edgeSel = cmds.polySelect(mesh, elp=[e1, e2], ns=True)
                if edgeSel == None:
                    continue
                if len(edgeSel) > 40 and first:
                    continue
                return True

    mesh = inEdges[0].split('.')[0]
    convertToVerts = convertToIndexList(shared.convertToVertexList(inEdges))

    selectionLists = getConnectedVerts(mesh, convertToVerts)
    list1 = convertToVertList(selectionLists[0], mesh)
    list2 = convertToVertList(selectionLists[1], mesh)

    baseList = []
    fixed = []
    for vert in list1:
        for vtx in list2:
            if not checkEdgeLoop(mesh, vert, vtx):
                continue
            baseList.append([vert, vtx])
            fixed.extend([vert, vtx])

    # quick fix so it will not take the longest loop first
    for vert in list1:
        for vtx in list2:
            if vert in fixed or vtx in fixed:
                continue

            if not checkEdgeLoop(mesh, vert, vtx, False):
                continue
            baseList.append([vert, vtx])

    return baseList


def polySkeleton(radius=5):
    currentUnit = cmds.currentUnit(q=True, l=True)
    if currentUnit != 'cm':
        cmds.currentUnit(l='cm')

    selection = cmds.ls(type="joint")
    allGeo = []
    for joint in selection:
        sphere = cmds.polySphere()[0]
        point = cmds.pointConstraint(joint, sphere, mo=False)
        cmds.delete(point)
        cmds.setAttr(sphere + '.scaleX', radius)
        cmds.setAttr(sphere + '.scaleY', radius)
        cmds.setAttr(sphere + '.scaleZ', radius)
        allGeo.append(sphere)

        children = cmds.listRelatives(joint, type="joint")
        if children == None:
            pass
        else:
            for child in children:
                cone = cmds.polyCone()[0]
                cmds.setAttr(cone + '.translateY', 1)
                cmds.makeIdentity(cone, apply=True)
                cmds.move(0, 0, 0, cone + ".scalePivot", cone + ".rotatePivot", absolute=True)
                point = cmds.pointConstraint(joint, cone, mo=False)
                aim = cmds.aimConstraint(child, cone, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType="scene")
                cmds.delete(point, aim)
                cmds.setAttr(cone + '.scaleX', radius)
                cmds.setAttr(cone + '.scaleY', radius)
                cmds.setAttr(cone + '.scaleZ', radius)
                getPos = cmds.xform(child, q=True, ws=True, t=True)
                cmds.xform(cone + '.vtx[20]', ws=True, t=getPos)
                allGeo.append(cone)
    cmds.polyUnite(allGeo)
    cmds.DeleteHistory(allGeo)
    cmds.currentUnit(l=currentUnit)
