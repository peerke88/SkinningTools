from maya import cmds
from maya.OpenMaya import MVector
from shared import *
import itertools
from SkinningTools.Maya.tools import shared, mathUtils
from SkinningTools.UI.fallofCurveUI import BezierFunctions
from collections import OrderedDict

def getShellFaces(poly):
    shells = []
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


def shortestPathVertex(start, end):
    def measureLength(object1, object2):
        pos1 = MVector(*cmds.xform(object1, q=True, ws=True, t=True))
        pos2 = MVector(*cmds.xform(object2, q=True, ws=True, t=True))
        return (pos1 - pos2).length()

    mesh = start.split('.')[0]
    
    firstExtendedEdges = cmds.polyListComponentConversion(start, te=True)
    firstExtended = cmds.filterExpand(firstExtendedEdges, sm=32, fp=1)
    secondExtendedEdges = cmds.polyListComponentConversion(end, te=True)
    secondExtended = cmds.filterExpand(secondExtendedEdges, sm=32, fp=1)

    found = []
    combinations = list(itertools.product(firstExtended, secondExtended))
    for e1, e2 in combinations:
        e1n = int(e1[e1.index("[") + 1: -1])
        e2n = int(e2[e2.index("[") + 1: -1])
        edgeSel = cmds.polySelect(mesh, elp=[e1n, e2n], ns=True)
        if edgeSel == None:
            continue
        found.append(edgeSel)

    if found == []:
        vertexNumber1 = int(start[start.index("[") + 1: -1])
        vertexNumber2 = int(end[end.index("[") + 1: -1])
        edgeSelection = cmds.polySelect(mesh, shortestEdgePath=[vertexNumber1, vertexNumber2])
    else:
        edgeSelection = min(found, key=len)

    if edgeSelection is None:
        cmds.error("selected vertices are not part of the same polyShell!")

    newVertexSelection = []
    for edge in edgeSelection:
        midexpand = shared.convertToVertexList("%s.e[%s]" % (mesh, edge))
        newVertexSelection.append(midexpand)

    startIndex = int(start[start.index("[") + 1: -1])
    endIndex = int(end[end.index("[") + 1: -1])

    inOrder = []
    lastVertex = None
    for listVerts in newVertexSelection:
        indexList = shared.convertToIndexList(listVerts)
        if startIndex in indexList:
            indexList.remove(startIndex)
        if lastVertex != None:
            indexList.remove(lastVertex)
        if endIndex in indexList:
            indexList.remove(endIndex)
        if indexList == []:
            continue
        lastVertex = indexList[0]
        inOrder.append(lastVertex)

    if not startIndex in shared.convertToIndexList(newVertexSelection[0]):
        inOrder.reverse()

    # totalDistance = measureLength(inOrder[-1], end)
    inOrder = shared.convertToCompList(inOrder, mesh)
    return [start] + inOrder + [end]

def shortestPathNurbsSurface(start, end, diagonal=False):
    surface = start.split('.')[0]
    allCvs = cmds.filterExpand("%s.cv[*][*]" % surface, sm=28, fp=1)
    graph = shared.Graph()
    
    recomputeDict = {}
    for node in allCvs:
        base = (node)
        graph.add_node(base)
        recomputeDict[base] = node

    for node in allCvs:
        cmds.select(cl=1)
        cmds.nurbsSelect(node, gs=1)
        gro = cmds.ls(sl=1, l=1)[0]

        if diagonal == False:
            # rough implementation to not cross U and V at the same time (2 implementation only)
            workString = node.split("][")
            groString = gro.split("][")
            gro = ["%s][%s" % (workString[0], groString[-1]), "%s][%s" % (groString[0], workString[-1])]

        gro = cmds.filterExpand(gro, sm=28, fp=1)

        gro.remove(node)
        basePos = MVector(*cmds.xform(node, q=1, ws=1, t=1))
        for f in gro:
            fPos = MVector(*cmds.xform(f, q=1, ws=1, t=1))
            fLen = (fPos - basePos).length()
            graph.add_edge((node), (f), fLen)

    shortest = shared.shortest_path(graph, (start), (end))

    inOrder = []
    for sh in shortest[-1]:
        inOrder.append(recomputeDict[sh])
    return inOrder

def shortestPathNurbsCurve(start, end):
    startIndex = int(start[start.index("[") + 1: -1])
    endIndex = int(end[end.index("[") + 1: -1])
    numbers = [startIndex, endIndex]
    rangeList = xrange(min(numbers), max(numbers) + 1)

    inOrder = []
    for i, num in enumerate(rangeList):
        cv = "%s.cv[%s]" % (surface, num)
        inOrder.append(cv)
    if numbers[0] == endindex:
        inOrder.reverse()
    return inOrder

def shortestPathLattice(start, end):
    allCvs = cmds.filterExpand("%s.pt[*]" % surface, sm=46, fp=1)
    graph = shared.Graph()
    recomputeDict = {}
    for node in allCvs:
        base = (node)
        graph.add_node(base)
        recomputeDict[base] = node

    for node in allCvs:
        gro = shared.growLatticePoints([node])
        gro.remove(node)
        basePos = MVector(*cmds.xform(node, q=1, ws=1, t=1))
        for f in gro:
            fPos = MVector(*cmds.xform(f, q=1, ws=1, t=1))
            fLen = (fPos - basePos).length()
            graph.add_edge((node), (f), fLen)

    shortest = shared.shortest_path(graph, (start), (end))

    inOrder = []
    for sh in shortest[-1]:
        inOrder.append(recomputeDict[sh])
    return inOrder

def componentPathFinding(selection, useDistance, diagonal=False, weightWindow=None):
    start = selection[0]
    end = selection[-1]
    surface = start.split('.')[0]

    objType = cmds.objectType(start)
    if objType == 'mesh':
        inOrder = shortestPathVertex(start, end)
    elif objType == "nurbsSurface":
        inOrder = shortestPathNurbsSurface(start, end, diagonal)
    elif objType == "lattice":
        inOrder = shortestPathLattice(start, end)
    else:
        inOrder = shortestPathNurbsCurve(start, end)
    
    lengths = []
    for index, vertex in enumerate(inOrder):
        if index == 0:
            continue
        if useDistance:
            lengths.append(mathUtils.measureLength(inOrder[index-1], vertex))
            continue
        lengths.append(1)

    fullLength = sum(lengths)
    percentage = 1.0/ len(lengths)
    currentLength = 0.0
    _vertMap = OrderedDict()
    for index, vertex in enumerate(inOrder):
        currentPercentage = index * percentage
        currentLength = sum(lengths[:index+1])
        if weightWindow is None:
            currentPercentage = (currentLength / fullLength)
        elif type(weightWindow) in [list, tuple]:
            currentPercentage = BezierFunctions.getDataOnPercentage(currentPercentage, weightWindow)
        else:
            currentPercentage = weightWindow.getDataOnPerc(currentPercentage)
        _vertMap[vertex] = currentPercentage
    
    return _vertMap


def edgesToSmooth(inEdges):
    mesh = inEdges[0].split('.')[0]
    convertToVerts = shared.convertToIndexList(shared.convertToVertexList(inEdges))
    
    selectionLists = shared.getConnectedVerts(mesh, convertToVerts)
    list1 = shared.convertToCompList(selectionLists[0], mesh)
    list2 = shared.convertToCompList(selectionLists[1], mesh)
    
    baseList = []
    edgeLengths = []
    combinations = list(itertools.product(list1, list2))
    for vert, vtx in combinations:
        loopSize = shared.checkEdgeLoop(mesh, vert, vtx)
        if not loopSize:
            continue
        baseList.append([vert, vtx])
        edgeLengths.append(loopSize)
    print edgeLengths
    minSize = min(edgeLengths)
    maxSize = max(edgeLengths)

    _testSize = (minSize*1.5) # <- might need to change this to get accurate reading of edgelengths in list
    if maxSize > _testSize:
        fixed = []
        for i, value in enumerate(edgeLengths):
            if value > _testSize:
                continue
            fixed.append(baseList[i])
        return fixed
    return baseList

@shared.dec_undo
def polySkeleton(radius=5):
    currentUnit = cmds.currentUnit(q=True, l=True)
    if currentUnit != 'cm':
        cmds.currentUnit(l='cm')

    selection = cmds.ls(type="joint", l=1)
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
        if children is None:
            continue
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


def softSelection():
    _sel = cmds.ls(sl=1) or None
    if _sel is None or not '.' in _sel[0]:
        print ("no components selected to get information from, current selection: %s"%_sel)
        return [],[]

    richSelection = OpenMaya.MGlobal.getRichSelection()
    selection = richSelection.getSelection()
    
    iter = OpenMaya.MItSelectionList( selection )

    elements, weights = [], []
    while not iter.isDone():
        dagPath, component = iter.getComponent()
        node = dagPath.fullPathName()

        fnComp = OpenMaya.MFnSingleIndexedComponent(component)
        selectedIndex = fnComp.getElements()

        getWeight = lambda i: fnComp.weight( i ).influence if fnComp.hasWeights else 1.0
        
        for i in range( fnComp.elementCount ):
            elements.append( '%s.vtx[%i]' % ( node, fnComp.element( i ) ) )
            weights.append( getWeight( i ) ) 
        iter.next()

    return elements, weights