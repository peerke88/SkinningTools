import sys, traceback, collections, itertools
from collections import defaultdict, deque
from functools import wraps
from maya import cmds, mel
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.UI.qt_util import *

_DEBUG = True
def dec_undo(func):
    '''undo decorator'''
    @wraps(func)
    def _undo_func(*args, **kwargs):
        try:
            cmds.undoInfo(ock=True)
            return func(*args, **kwargs)
        except Exception as e:
            if _DEBUG:
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc())
        finally:
            cmds.undoInfo(cck=True)
            return False

    return _undo_func

#@note check if this works later!
def dec_repeat(func):
    '''repeat last decorator'''
    @wraps(func)
    def _repeat_func(*args, **kwargs):
        ret = func(*args, **kwargs)

        try:
            modules = ''
            arguments = args
            if [x for x in ['cls', 'self'] if x in func.func_code.co_varnames]:
                arguments = args[1:]
                modules = '%s.' % args[0]

            args_string = ''
            for each in arguments:
                if isinstance(each, QWidget):
                    each = None
                args_string += '%s, ' % each

            kwargs_string = ''
            for key, item in kwargs.iteritems():
                if isinstance(item, QWidget):
                    item = None
                kwargs_string = '%s=%s, ' % (key, item)

            repeat_command = '%s%s(%s%s)' % (modules, func.__name__, args_string, kwargs_string)
            if not '' in [args_string, kwargs_string]:
                repeat_command = '%s%s(%s, %s)' % (modules, func.__name__, args_string, kwargs_string)
            
            cmds.repeatLast(addCommand='python("from SkinningTools.Maya import interface;interface.%s");' % repeat_command)
        except Exception as e:
            if _DEBUG:
                print "if this is fired the when repeating a command it means it uses MEL"
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc())
        finally:  
            return ret

    return _repeat_func

def dec_loadPlugin(plugin):
    def _loadPlugin_func(func):
        @wraps(func)
        def inner(*args, **kwargs):
            loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
            registered = cmds.pluginInfo(plugin, q=True, registered=True)

            if not registered or not loaded:
                cmds.loadPlugin(plugin)

            return func(*args, **kwargs)
        return inner
    return _loadPlugin_func

class Graph(object):
    ''' dijkstra closest path technique (for nurbs and lattice)
    implemented from: https://gist.github.com/econchick/4666413  
    basic idea: http://www.redblobgames.com/pathfinding/a-star/introduction.html'''

    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance


def dijkstra(graph, initial):
    ''' dijkstra closest path technique (for nurbs and lattice)'''
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node
        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            try:
                weight = current_weight + graph.distances[(min_node, edge)]
            except:
                continue
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path


def shortest_path(graph, origin, destination):
    ''' dijkstra closest path technique (for nurbs and lattice)'''
    visited, paths = dijkstra(graph, origin)
    full_path = deque()
    _destination = paths[destination]

    while _destination != origin:
        full_path.appendleft(_destination)
        _destination = paths[_destination]

    full_path.appendleft(origin)
    full_path.append(destination)

    return visited[destination], list(full_path)


# ------------------------------------------------------------------------------
# @note: make sure that all objects return full path
def skinCluster(inObject=None, silent=False):
    if inObject is None:
        inObject = cmds.ls(sl=1, l=1)
    if not inObject:
        return None
    print "inObject: ",inObject
    inObject = getParentShape(inObject)
    skinCluster = cmds.ls(cmds.listHistory(inObject), type="skinCluster")
    if not skinCluster:
        if silent == False:
            cmds.confirmDialog(title='Error', message='no SkinCluster found on: %s!' % inObject, button=['Ok'],
                               defaultButton='Ok', cancelButton='Ok', dismissString='Ok')
        else:
            skinCluster = None
    return skinCluster[0]


def getParentShape(object):
    if isinstance(object, list):
        object = object[0]
    objType = cmds.objectType(object)
    if objType in ['mesh', "nurbsCurve", "lattice"]:
        print object, cmds.listRelatives(object, p=True, f=True)
        object = cmds.listRelatives(object, p=True, f=True)[0]
    if cmds.objectType(object) != "transform":
        object = cmds.listRelatives(object, p=True, f=True)[0]
    return object


def doCorrectSelectionVisualization(skinMesh):
    objType = cmds.objectType(skinMesh)
    if objType == "transform":
        shape = cmds.listRelatives(skinMesh, c=1, s=1)[0]
        objType = cmds.objectType(shape)

    # @todo: convert this to openmaya?
    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    if objType in ["nurbsSurface", "nurbsCurve"]:
        mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");' % skinMesh)
    elif objType == "lattice":
        mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");' % skinMesh)
    elif objType == "mesh":
        mel.eval('doMenuComponentSelection("%s", "vertex");' % skinMesh)


def convertToVertexList(inObject):
    checkObject = inObject
    if isinstance(inObject, list):
        checkObject = inObject[0]
    objType = cmds.objectType(checkObject)
    checkType = checkObject
    if objType == "transform":
        shapes = cmds.listRelatives(inObject, ad=1, s=1)
        if not shapes == []:
            checkType = inObject
        checkType = shapes[0]

    objType = cmds.objectType(checkType)
    if objType == 'mesh':
        convertedVertices = cmds.polyListComponentConversion(inObject, tv=True)
        return cmds.filterExpand(convertedVertices, sm=31, fp=1)

    if objType == "nurbsCurve" or objType == "nurbsSurface":
        if isinstance(inObject, list) and ".cv" in inObject[0]:
            return cmds.filterExpand(inObject, sm=28, fp=1)
        elif isinstance(inObject, list):
            return cmds.filterExpand('%s.cv[*]' % inObject[0], sm=28, fp=1)
        elif ".cv" in inObject:
            return cmds.filterExpand(inObject, sm=28, fp=1)
        else:
            return cmds.filterExpand('%s.cv[*]' % inObject, sm=28, fp=1)

    if objType == "lattice":
        if isinstance(inObject, list) and ".pt" in inObject[0]:
            return cmds.filterExpand(inObject, sm=46, fp=1)
        elif isinstance(inObject, list):
            return cmds.filterExpand('%s.pt[*]' % inObject[0], sm=46, fp=1)
        elif ".pt" in inObject:
            return cmds.filterExpand(inObject, sm=46, fp=1)
        else:
            return cmds.filterExpand('%s.pt[*]' % inObject, sm=46, fp=1)

def selectHierarchy(node):
    ad = cmds.listRelatives(node, ad=1, f=1)
    ad.append(node[0])
    return ad[::-1]

def getJointIndexMap(inSkinCluster):
    inConns = cmds.listConnections('%s.matrix'%inSkinCluster, s=1, d=0,c=1, type="joint")
    indices =[]
    _connectDict = {}
    for i in inConns[::2]:
        indices.append(int(i[i.index("[") + 1: -1]))
    for index, conn in enumerate(inConns[1::2]):
        _connectDict[cmds.ls(conn,sl=0, l=1)[0]] = indices[index]
    return _connectDict

def convertToIndexList(vertList):
    indices = []
    for i in vertList:
        index = int(i[i.index("[") + 1: -1])
        indices.append(index)
    return indices

def convertToCompList(indices, mesh, comp = "vtx"):
    vertices = []
    for i in list(indices):
        vrt = "%s.%s[%s]" % (mesh,comp, i)

        vertices.append(vrt)
    return vertices

def toToEdgeNumber(vtx):
    toEdges = cmds.polyListComponentConversion(vtx, te=True)
    edges = cmds.filterExpand(toEdges, sm=32, fp=1)
    en = []
    for e in edges:
        en.append(int(e[e.index("[") + 1: -1]))
    return en

def checkEdgeLoop(mesh, vtx1, vtx2, first=True, maxLength = 40):
    e1n = toToEdgeNumber(vtx1)
    e2n = toToEdgeNumber(vtx2)
    found = []
    combinations = list(itertools.product(e1n, e2n))
    for e1, e2 in combinations:
        edgeSel = cmds.polySelect(mesh, elp=[e1, e2], ns=True)
        if edgeSel == None:
            continue
        loopSize = len(edgeSel)
        if loopSize > maxLength and first:
            continue
        return loopSize

def getDagpath(node, extendToShape=False):
    sellist = OpenMaya.MGlobal.getSelectionListByName( node )
    try:
        if extendToShape:
            return sellist.getDagPath(0).extendToShape()
        return sellist.getDagPath(0)
    except:
        return sellist.getDependNode(0)

def getMfnSkinCluster(mDag):
    if isinstance(mDag, OpenMaya.MDagPath):
        skinNode = skinCluster(mDag.fullPathName())
    else:
        skinNode = skinCluster(mDag)
    return OpenMayaAnim.MFnSkinCluster( getDagpath(skinNode) )

# --- vertex island functions ---

def getConnectedVerts(mesh, vtxSelectionSet):
    mObject = OpenMaya.MGlobal.getSelectionListByName(mesh).getDependNode(0)
    iterVertLoop = OpenMaya.MItMeshVertex(mObject)

    talkedToNeighbours = set()
    districtDict = collections.defaultdict(list)
    districtNr = 0
    for currentIndex in vtxSelectionSet:
        districtHouses = set()

        if not currentIndex in talkedToNeighbours:
            districtHouses.add(currentIndex)
            currentNeighbours = getNeighbours(iterVertLoop, currentIndex)
            while currentNeighbours:
                newNeighbours = set()
                for neighbour in currentNeighbours:
                    if neighbour in vtxSelectionSet and not neighbour in talkedToNeighbours:
                        talkedToNeighbours.add(neighbour)
                        districtHouses.add(neighbour)
                        newNeighbours = newNeighbours.union(getNeighbours(iterVertLoop, neighbour))

                currentNeighbours = newNeighbours
            districtDict[districtNr] = districtHouses
            districtNr += 1

        iterVertLoop.setIndex(currentIndex)
        iterVertLoop.next()

    return districtDict


def getNeighbours(mVtxItter, index):
    mVtxItter.setIndex(index)
    intArray = mVtxItter.getConnectedVertices()
    return set(int(x) for x in intArray)


def growLatticePoints(points):
    base = points[0].split('.')[0]
    allPoints = cmds.filterExpand("%s.pt[*]" % base, sm=46, fp=1)

    extras = []
    for j in points:
        extras.append(j)
        a = int(j.split("[")[1].split("]")[0])
        b = int(j.split("[")[2].split("]")[0])
        c = int(j.split("[")[3].split("]")[0])
        for i in [-1, 1]:
            growa = "%s.pt[%s][%s][%s]" % (base, a + i, b, c)
            growb = "%s.pt[%s][%s][%s]" % (base, a, b + i, c)
            growc = "%s.pt[%s][%s][%s]" % (base, a, b, c + i)
            if growa in allPoints:
                extras.append(growa)
            if growb in allPoints:
                extras.append(growb)
            if growc in allPoints:
                extras.append(growc)
    return extras


def getWeights(mesh):
    sc = skinCluster(mesh)
    shape = cmds.listRelatives(mesh, s=1)[0]

    skinNode = getDagpath( sc )       
    skinFn = MFnSkinCluster(skinNode)
    meshPath = getDagpath( shape )
    meshNode = meshPath.node()

    meshVerItFn = OpenMaya.MItMeshVertex( meshNode )
    indices = range( meshVerItFn.count() )

    singleIdComp = OpenMaya.MFnSingleIndexedComponent()
    vertexComp = singleIdComp.create( OpenMaya.MFn.kMeshVertComponent )
    singleIdComp.addElements( indices )

    infDags = skinFn.influenceObjects()
    infIndexes = OpenMaya.MIntArray( len( infDags ) , 0 )
    for x in xrange( len( infDags ) ):
        infIndexes[x] = int( skinFn.indexForInfluenceObject( infDags[x] ) )

    weightData = skinFn.getWeights( meshPath , vertexComp, infIndexes )
    return weightData

def setWeigths(mesh, weightData):
    sc = skinCluster(mesh)
    shape = cmds.listRelatives(mesh, s=1)[0]

    skinNode = getDagpath( sc )       
    skinFn = MFnSkinCluster(skinNode)
    meshPath = getDagpath( shape )
    meshNode = meshPath.node()

    meshVerItFn = OpenMaya.MItMeshVertex( meshNode )
    indices = range( meshVerItFn.count() )

    singleIdComp = OpenMaya.MFnSingleIndexedComponent()
    vertexComp = singleIdComp.create( OpenMaya.MFn.kMeshVertComponent )
    singleIdComp.addElements( indices )

    infDags = skinFn.influenceObjects()
    infIndexes = OpenMaya.MIntArray( len( infDags ) , 0 )
    for x in xrange( len( infDags ) ):
        infIndexes[x] = int( skinFn.indexForInfluenceObject( infDags[x] ) )

    skinFn.setWeights( meshPath , vertexComp , infIndexes , weightData ) 

# -------------

def getPolyOnMesh(point, mesh):
    meshDag =getDagpath(mesh, extendToShape=True)

    meshIntersector = OpenMaya.MMeshIntersector()
    meshIntersector.create(meshDag.node(), meshDag.inclusiveMatrix())

    _point = OpenMaya.MPoint(*point)
    meshPoint = meshIntersector.getClosestPoint(_point)

    faceIndex = meshPoint.faceIndex()
    triangleIndex = meshPoint.triangleIndex()

    u, v = meshPoint.getBarycentricCoords()
    return faceIndex, triangleIndex, u, v

def getTriIndex(mesh, polygon_index, triangleIndex):
    meshDag = getDagpath(mesh, extendToShape=True)
    polyIt = OpenMaya.MItMeshPolygon(meshDag)
    
       
    prevIndexPTR = polyIt.setIndex(polygon_index )

    points, vertex_list = polyIt.getTriangle(triangleIndex, OpenMaya.MSpace.kWorld)

    return (vertex_list[0], vertex_list[1], vertex_list[2])
    
def getTriWeight(mesh, polygon_index, triangleIndex, u, v):
    skin_cluster = skinCluster(mesh)
    influences = cmds.listConnections("%s.matrix"%skinClusterName, source=True)

    vtxIndex = getTriIndex(mesh, polygon_index, triangleIndex)
    barycentric_coordinates = [u, v, 1.0-u-v]

    weights = [0.0 for _ in range(len(influences))]
    for i, vertId in enumerate(vtxIndex):
        vtxWeights = cmds.skinPercent(skin_cluster, '%s.vtx[%s]'%(mesh, vertId), query=True, value=True)
        weights = [weights[j] + weight * barycentric_coordinates[i] for j,weight in enumerate(vtxWeights)]

    return influences, weights


def skinConstraint(mesh, transform, precision=2):
    precision = max(precision, 1)
    point = cmds.xform(transform, q=True, t=True, ws=True)
    faceId, triangle_index, u, v = getPolyOnMesh(point, mesh)

    transforms, weights = getTriWeight(mesh, faceId, triangle_index, u, v)
    matrix_node = createWeightedMM(transforms, weights, precision=precision)

    vector_product_node1 = cmds.createNode('vectorProduct')
    cmds.setAttr('%s.operation'%vector_product_node1, 4)
    cmds.setAttr('%s.input1'%vector_product_node1, *point)
    cmds.connectAttr('%s.matrixSum'%matrix_node, '%s.matrix'%vector_product_node1)

    vector_product_node2 = cmds.createNode('vectorProduct')
    cmds.setAttr('%s.operation'%vector_product_node2, 4)
    cmds.connectAttr('%s.output'%vector_product_node1, '%s.input1'%vector_product_node2)
    cmds.connectAttr('%s.parentInverseMatrix'%transform, '%s.matrix'%vector_product_node2)
    cmds.connectAttr('%s.output'%vector_product_node2, '%s.translate'%transform, force=True)

    decompose_matrix_node = cmds.createNode('decomposeMatrix')
    cmds.connectAttr('%s.matrixSum'%matrix_node, '%s.inputMatrix'%decompose_matrix_node)
    cmds.connectAttr('%S.outputRotate'%decompose_matrix_node, '%s.rotate'%transform, force=True)
 

def createWeightedMM(transforms, weights, precision, epsilon=1e-6):
    Trs = []
    Wgth = []

    wgthTotal = 0.0
    for trsNode, weight in zip(transforms, weights):
        weight = float('%.{}f'.format(precision) % weight)
        if weight > epsilon:
            wgthTotal += weight
            Trs.append(trsNode)
            Wgth.append(weight)

    for i, weight in enumerate(Wgth):
        Wgth[i] *= 1.0 / max(wgthTotal, 1e-6)
    
    addMM = cmds.createNode('wtAddMatrix')

    for i, (trsNode, weight) in enumerate(zip(Trs, Wgth)):
        mmNode = cmds.createNode('multMatrix')
        mmInv = cmds.getAttr('%s.worldInverseMatrix'%trsNode)
        cmds.setAttr('%s.matrixIn[0]'%mmNode, mmInv, type='matrix')
        cmds.connectAttr('%s.worldMatrix'%trsNode, '%s.matrixIn[1]'%mmNode)

        cmds.connectAttr('%s.matrixSum'%mmNode, '%s.wtMatrix[%s].matrixIn'%(addMM, i))
        cmds.setAttr('%s.wtMatrix[%s].weightIn'%(addMM, i), weight)

        cmds.addAttr(addMM, ln=trsNode, dv=weight, at='double', k=True)
        cmds.setAttr('%s.%s'%(addMM, trsNode), lock=True)

    return addMM