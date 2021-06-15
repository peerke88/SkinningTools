from maya import cmds
from maya.api.OpenMaya import MVector, MFloatPointArray, MFloatPoint, MIntArray, MColor, MColorArray, MFnMesh, MSelectionList, MGlobal, MItSelectionList, MFnSingleIndexedComponent
import itertools
from SkinningTools.Maya.tools import shared, mathUtils
from SkinningTools.UI import utils
from SkinningTools.UI.fallofCurveUI import BezierFunctions
from SkinningTools.py23 import *
from collections import OrderedDict, defaultdict


def getRootPath(path):
    return path.split("|")[-1]

def getShellFaces(inMesh):
    """ convert the selection of vertices to face group selections

    :param inMesh: object to evaluate
    :type inMesh: string
    :return: list of grouped faces
    :rtype: list
    """
    shells = []
    faces = set()
    total = cmds.polyEvaluate(s=True)

    for f in range(cmds.polyEvaluate(inMesh, f=True)):

        if len(shells) >= total:
            break
        if f in faces:
            continue

        shell = cmds.polySelect(inMesh, q=1, extendToShell=f)
        faces.update(shell)

        val = ".f[%d:%d]" % (min(shell), max(shell))
        shells.append(val)

    return shells


def shortestPathVertex(start, end):
    """ get the shortest path walking over the edges between 2 selected vertices

    :param start: vertex to start from
    :type start: string
    :param end: vertex to end with
    :type end: string
    :return: list of vertices to walk in order
    :rtype: list

    """
    curMesh = start.split('.')[0]

    firstExtendedEdges = cmds.polyListComponentConversion(start, te=True)
    firstExtended = cmds.filterExpand(firstExtendedEdges, sm=32, fp=1)
    secondExtendedEdges = cmds.polyListComponentConversion(end, te=True)
    secondExtended = cmds.filterExpand(secondExtendedEdges, sm=32, fp=1)

    found = []
    combinations = list(itertools.product(firstExtended, secondExtended))
    for e1, e2 in combinations:
        e1n = int(e1[e1.index("[") + 1: -1])
        e2n = int(e2[e2.index("[") + 1: -1])
        edgeSel = cmds.polySelect(curMesh, elp=[e1n, e2n], ns=True)
        if edgeSel == None:
            continue
        found.append(edgeSel)

    if found == []:
        vertexNumber1 = int(start[start.index("[") + 1: -1])
        vertexNumber2 = int(end[end.index("[") + 1: -1])
        edgeSelection = cmds.polySelect(curMesh, shortestEdgePath=[vertexNumber1, vertexNumber2])
    else:
        edgeSelection = min(found, key=len)

    if edgeSelection is None:
        cmds.error("selected vertices are not part of the same polyShell!")

    newVertexSelection = []
    for edge in edgeSelection:
        midexpand = shared.convertToVertexList("%s.e[%s]" % (curMesh, edge))
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

    inOrder = shared.convertToCompList(inOrder, curMesh)
    return [start] + inOrder + [end]


def shortestPathNurbsSurface(start, end, diagonal=False):
    """ get the shortest path walking over the edges between 2 selected control vertices

    :param start: control vertex to start from
    :type start: string
    :param end: control vertex to end with
    :type end: string
    :param diagonal: if `True` the shortest path can cross cv's diagonally, if `False` it can only go straight
    :type diagonal: bool
    :return: list of control vertices to walk in order
    :rtype: list
    """
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
    """ get the shortest path walking over the edges between 2 selected control vertices

    :param start: control vertex to start from
    :type start: string
    :param end: control vertex to end with
    :type end: string
    :return: list of control vertices to walk in order
    :rtype: list
    """
    startIndex = int(start[start.index("[") + 1: -1])
    endIndex = int(end[end.index("[") + 1: -1])
    numbers = [startIndex, endIndex]
    rangeList = range(min(numbers), max(numbers) + 1)

    inOrder = []
    for i, num in enumerate(rangeList):
        cv = "%s.cv[%s]" % (surface, num)
        inOrder.append(cv)
    if numbers[0] == endindex:
        inOrder.reverse()
    return inOrder


def shortestPathLattice(start, end):
    """ get the shortest path walking over the edges between 2 selected points

    :param start: points to start from
    :type start: string
    :param end: points to end with
    :type end: string
    :return: list of points to walk in order
    :rtype: list
    """
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
    """ use the component selection for pathfinding, to make sure that any skinnable mesh can be walked over

    :param selection: 2 component objects that indicate the start and end of a possible path
    :type selection: list
    :param useDistance: if `True` will use the lenght of the path to define the weight , if `False` will use the amount of points as weight
    :type useDistance: bool
    :param diagonal: if `True` the shortest path can cross cv's diagonally, if `False` it can only go straight
    :type diagonal: bool
    :param weightWindow: the window that has control over a bezier curveto define the fallof of weight
    :type weightWindow: fallofCurveUI
    :return: map of vertices in order and the weight applied to them
    :rtype: list
    """
    start = selection[0]
    end = selection[-1]

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
            lengths.append(mathUtils.measureLength(inOrder[index - 1], vertex))
            continue
        lengths.append(1)

    fullLength = sum(lengths)
    percentage = 1.0 / len(lengths)
    currentLength = 0.0
    _vertMap = OrderedDict()
    for index, vertex in enumerate(inOrder):
        currentPercentage = index * percentage
        currentLength = sum(lengths[:index + 1])
        if weightWindow is None:
            currentPercentage = (currentLength / fullLength)
        elif type(weightWindow) in [list, tuple]:
            currentPercentage = BezierFunctions.getDataOnPercentage(currentPercentage, weightWindow)
        else:
            currentPercentage = weightWindow.getDataOnPerc(currentPercentage)
        _vertMap[vertex] = currentPercentage

    return _vertMap


def edgesToSmooth(inEdges):
    """ use 2 edgeloops to find the relation of the vertices on opposite sides

    :param inEdges: list of 2 edgeloops
    :type inEdges: list
    :return: list of vertices that are closely connected together based on the edgeselection
    :rtype: list
    """
    curMesh = inEdges[0].split('.')[0]
    convertToVerts = shared.convertToIndexList(shared.convertToVertexList(inEdges))

    selectionLists = shared.getConnectedVerts(curMesh, convertToVerts)
    list1 = shared.convertToCompList(selectionLists[0], curMesh)
    list2 = shared.convertToCompList(selectionLists[1], curMesh)

    baseList = []
    edgeLengths = []
    combinations = list(itertools.product(list1, list2))
    for vert, vtx in combinations:
        loopSize = shared.checkEdgeLoop(curMesh, vert, vtx)
        if not loopSize:
            continue
        baseList.append([vert, vtx])
        edgeLengths.append(loopSize)
    
    minSize = min(edgeLengths)
    maxSize = max(edgeLengths)

    _testSize = (minSize * 1.5)  # <- might need to change this to get accurate reading of edgelengths in list
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
    """ convert the current selected skeleton to a polygonal object 
    this can be beneficial to show how the skeleton looks in other dcc tools, like zbrush

    :param radius: the radius to give each joint in the output
    :type radius: float
    """
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
    """ convert the soft selection in the scene to vertices and weights

    :return: list of vertices in the soft selection range and the weight of that vertex
    :rtype: list, list
    """
    _sel = cmds.ls(sl=1) or None
    if _sel is None or not '.' in _sel[0]:
        print("no components selected to get information from, current selection: %s" % _sel)
        return [], []

    richSelection = MGlobal.getRichSelection()
    selection = richSelection.getSelection()

    iter = MItSelectionList(selection)

    elements, weights = [], []
    while not iter.isDone():
        dagPath, component = iter.getComponent()
        node = dagPath.fullPathName()

        fnComp = MFnSingleIndexedComponent(component)
        # selectedIndex = fnComp.getElements()

        getWeight = lambda i: fnComp.weight(i).influence if fnComp.hasWeights else 1.0

        for i in range(fnComp.elementCount):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i))
        iter.next()

    return elements, weights

@shared.dec_undo
def extractFacesByVertices(vertices, internal=False):
    """ use the given components to create a new mesh with the same skinning information
    
    :param vertices: the components to use as information to generate the new mesh
    :type vertices: list
    :param internal: if `True` will only convert the the inner selection, if `False` will grow the selection once to cover more ground
    :type internal: bool
    :return: new created mesh
    :rtype: string
    """
    vertices = cmds.filterExpand(vertices, sm=31)
    if not vertices:
        return None

    curMesh = vertices[0].rsplit('.',1)[0]
    dup = cmds.duplicate(curMesh)[0]
    if cmds.listRelatives(dup, p=1):
        cmds.parent(dup, w=True)
    
    dup = '|' + dup
    for i, vert in enumerate(vertices):
        vertices[i] = dup + '.' + vert.rsplit('.',1)[-1]
    
    cmds.polyTriangulate(dup)

    faces = cmds.polyListComponentConversion(vertices, tf=True, internal=internal)
    faces = cmds.filterExpand(faces, sm=34)
    if not faces:
        cmds.delete(dup)
        return None

    if not internal:
        vertices = cmds.filterExpand(cmds.polyListComponentConversion(faces, tv=True), sm=31)

    vertexPositions = MFloatPointArray()
    vertexMap = {}
    normals = []
    for i, vertex in enumerate(vertices):
        vertexPositions.append(MFloatPoint(*cmds.xform(vertex, q=True, ws=True, t=True)))
        vertexMap[vertex.rsplit('[',1)[-1].split(']',1)[0]] = i
        normals.append( cmds.polyNormalPerVertex(vertex, q=1, xyz=1 )[:3] )
        
    ids = MIntArray()
    counts = MIntArray()
    for face in faces:
        faceVertices = cmds.filterExpand(cmds.polyListComponentConversion(face, tv=True), sm=31)
        counts.append(len(faceVertices))
        for vertex in faceVertices:
            ids.append(vertexMap[vertex.rsplit('[',1)[-1].split(']',1)[0]])

    m = MFnMesh()
    m.create(vertexPositions, counts, ids)

    path = m.fullPathName()
    if cmds.ls(path, type='mesh'):
        path = cmds.listRelatives(path, parent=True, f=True)
    cmds.transferAttributes(dup, path, transferPositions = 0, transferNormals =  1, transferUVs = 2, sampleSpace = 0, sourceUvSpace = "map1", targetUvSpace = "map1", searchMethod = 3 ,flipUVs = 0)
    cmds.delete(path, ch=1)
    cmds.sets(path, edit=True, forceElement="initialShadingGroup")
    cmds.delete(dup)
    return path

@shared.dec_undo
def cutCharacterFromSkin( inObject, internal=False, maya2020 = False,  progressBar = None):  
    """ split the character into multiple meshes based on the skinning information
    
    :param inObject: object to seperate in multiple meshes
    :type inObject: string
    :param internal: if `True` will only convert the the inner selection, if `False` will grow the selection once to cover more ground
    :type internal: bool
    :param maya2020: if `True` will use the offsetparent matrix to connect the mesh to joints , if `False` will use a decompose matrix to connect the meshes
    :type maya2020: bool
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return: group object that holds all the meshes
    :rtype: string
    """  
    skinClusterName = shared.skinCluster( inObject, silent=True )
    
    if skinClusterName == None:
        return
    
    utils.setProgress(0, progressBar, "processing: %s"%inObject )
    expandedList = shared.convertToVertexList(inObject)
    
    objList = []    
    indexConns = defaultdict(lambda : [])
    
    percentage = 19.0 / len(expandedList)    
    for vId, vtx in enumerate(expandedList):
        val = cmds.skinPercent(skinClusterName, vtx, q=1, v = True)
        index = val.index(max(val))
        joint = cmds.skinPercent(skinClusterName, vtx, q=1, t = None)[index]
        indexConns[joint].append(vtx)
        utils.setProgress((vId * percentage), progressBar, "getting vtx data: %s"%(vId))

    utils.setProgress(20, progressBar, "data gathered: %s"%inObject )

    percentage = 79.0 / len(indexConns)
    for index, (shortJointName, val) in enumerate(indexConns.items()):
        obj = extractFacesByVertices(val, internal = internal)
        if obj is None:
            continue

        newObj = cmds.rename(obj[0], "%s_%s_Proxy"%(shortJointName, inObject.split("|")[-1]))

        grp = cmds.group(n= "%s_%s_ProxyGrp"%(shortJointName, inObject.split("|")[-1]), em=1)

        if not maya2020:
            decomp = cmds.createNode("decomposeMatrix", n = "%s_%s_ProxyDCP"%(shortJointName, inObject) )
            cmds.connectAttr( "%s.worldMatrix[0]"%shortJointName, "%s.inputMatrix"%decomp )
            cmds.connectAttr( "%s.outputTranslate"%decomp, "%s.translate"%grp )
            cmds.connectAttr( "%s.outputRotate"%decomp, "%s.rotate"%grp )
        else:
            cmds.connectAttr( "%s.worldMatrix[0]"%shortJointName, "%s.offsetParentMatrix"%grp )

        cmds.parent(newObj, grp)
        objList.append(grp)
        utils.setProgress(20.0 + (index * percentage), progressBar, "%s > %s proxy created"%(inObject, shortJointName))

    utils.setProgress(100, progressBar, "%s proxys generated"%inObject)
    return cmds.group(objList, n="LowRez_%s"%inObject.split("|")[-1])

def setOrigShapeColor(inShape, inColor = (.8, 0.2, 0.2)):
    """ set a new vertex color to the given shape
    
    :param inShape: shape to add vertex colors to
    :type inShape: string
    :param inColor: the color to give the object
    :type inColor: tuple
    """  
    cmds.sets(inShape, edit=True, forceElement='initialShadingGroup')
    sList = MSelectionList()
    sList.add(inShape)
    meshPath, component = sList.getComponent(0)

    vtxArry = shared.getComponents(meshPath, component)
    colors = MColorArray()
    for __ in vtxArry:
        colors.append(MColor(inColor))
    mfnMesh = MFnMesh(meshPath)
    mfnMesh.setVertexColors(colors, vtxArry)
    cmds.setAttr("%s.displayColors" % inShape, 1)

def toggleDisplayOrigShape(inMesh, inColor =(.8, 0.2, 0.2), both = False, progressBar=None):
    """
    toggle the display of the mesh beteen the output and the input shape of the skincluster. the input shape will receive default lamber + vertex colors to make sure there is a big distinction between the 2
    :todo: maybe instead of lambert shader we can use the original shader + red vertex color overlay to make sure the textures can still be viewed
    :todo: add an option that shows both shapes? so we can display 1 in movement and one in default pose

    :param inMesh: the object that has a skincluster attached which we want to toggle
    :type inMesh: string
    :param inColor: the color in RGB values from 0to1 used as color value
    :type inColor: tuple/list
    :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
    :type progressBar: QProgressBar
    :return:  `True` if the function is completed
    :rtype: bool
    """
    for shape in cmds.listRelatives(inMesh, s=1, ni=0):
        if both and cmds.listConnections(shape, s=1, d=1, type= "skinCluster"):
            continue    
        cmds.setAttr("%s.intermediateObject" % shape, not cmds.getAttr("%s.intermediateObject" % shape))
        
        if not cmds.listConnections(shape, s=0, d=1, type="shadingEngine"):
            setOrigShapeColor(shape, inColor)