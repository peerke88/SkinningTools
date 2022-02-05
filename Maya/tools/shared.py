# -*- coding: utf-8 -*-
import sys, traceback, collections, itertools, cProfile, inspect, os, pstats, subprocess, random, json
from collections import defaultdict, deque
from functools import wraps
from maya import cmds, mel, OpenMaya as oldOpenMaya
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.ThirdParty import pyprof2calltree
from SkinningTools.ThirdParty.kdtree import KDTree

_DEBUG = getDebugState()


def dec_undo(func):
    """ undo decorator
    will allow the objects created and changed in maya to be part of a single chunk where possible
    the decorators is wrapped within a try except finally function to make sure everything is always undoable
    :note: object created with the use of OpenMaya will not be part of this


    :param func: function this decorator is attached to
    :type func: function()
    :return: the result of the given function
    :rtype: function()
    """
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

    return _undo_func


def dec_profile(func):
    """ profiler decorator
    run cprofile on wrapped function

    :param func: function this decorator is attached to
    :type func: function()
    :return: the result of the given function
    :rtype: function()
    """
    @wraps(func)
    def _profile_func(*args, **kwargs):
        if not _DEBUG:
            print("release: profile decorator lingering in code please remove: %s, %s" % (os.path.basename(inspect.getfile(func)), func.__name__))
            return func(*args, **kwargs)

        currentBaseFolder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        baseLocation = os.path.normpath(os.path.join(currentBaseFolder, "ThirdParty", "qcachegrind"))
        inLocation = os.path.normpath(os.path.join(currentBaseFolder, "Logs"))

        executable = os.path.normpath(os.path.join(baseLocation, "qcachegrind.exe"))
        callGrindProf = os.path.normpath(os.path.join(inLocation, 'callgrind.profile'))
        binaryData = os.path.normpath(os.path.join(inLocation, 'profiledRigSystem.profile'))

        for path in [callGrindProf, binaryData]:
            dirpath = os.path.dirname(path)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        pr.print_stats()
        pr.dump_stats(binaryData)

        pyprof2calltree.convert(pstats.Stats(binaryData), callGrindProf)
        pyprof2calltree.visualize(pstats.Stats(binaryData))
        subprocess.Popen([executable, callGrindProf])
        return result

    return _profile_func


def dec_repeat(func):
    """ repeat last decorator
    converts the given function to a command that the repeatlast command can take
    the arguments given are parsed and converted into a string that is added to a mel command.
    :todo: double check the functionality

    :param func: function this decorator is attached to
    :type func: function()
    :return: the result of the given function
    :rtype: function()
    """

    @wraps(func)
    def _repeat_func(*args, **kwargs):
        ret = func(*args, **kwargs)

        try:
            modules = ''
            arguments = args

            if sys.version_info.major == 2:
                varNames = func.func_code.co_varnames
            else:
                varNames = func.__code__.co_varnames

            if [x for x in ['cls', 'self'] if x in varNames]:
                arguments = args[1:]
                modules = '%s.' % args[0]

            args_string = ''
            for each in arguments:
                if isinstance(each, QWidget):
                    each = None
                if each == '':
                    continue
                if type(each) in [str, unicode, bytes]:
                    each = '\'{}\''.format(each)

                args_string += '%s, ' % each

            kwargs_string = ''
            for key, item in kwargs.items():
                if isinstance(item, QWidget):
                    item = None
                kwargs_string = '%s=%s, ' % (key, item)

            repeat_command = '{0}{1}({2}{3})'.format(modules, func.__name__, args_string, kwargs_string).replace(", ,", ",")
            cmds.repeatLast(addCommand='python("from SkinningTools.Maya import interface;interface.%s");' % repeat_command)

        except Exception as e:
            if _DEBUG:
                print("if this is fired the when repeating a command it means it uses MEL")
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc())
        finally:
            return ret

    return _repeat_func


def dec_loadPlugin(plugin):
    """ load plugin decorator
    loads the given plugin in the current maya scene, should be attached to functions that rely on plugins

    :param func: plugin this decorator is attached to
    :type func: string
    :return: the result of the given function
    :rtype: function()
    """
    def _loadPlugin_func(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if not os.path.exists(plugin) and _DEBUG:
                print("could not locate: %s" % plugin)
                return None
            loaded = cmds.pluginInfo(plugin, q=True, loaded=True)
            registered = cmds.pluginInfo(plugin, q=True, registered=True)

            if not registered or not loaded:
                cmds.loadPlugin(plugin)

            _ret = func(*args, **kwargs)
            return _ret

        return inner

    return _loadPlugin_func

# @note: add this for debugging?


def dec_timer(func):
    """ debug timer decorator
    times the function for how long it takes to run everything in the function

    :param func: plugin this decorator is attached to
    :type func: string
    :return: the result of the given function
    :rtype: function()
    """

    @wraps(func)
    def _timer_func(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('Execution time :', func.__name__, end - start)

        return result
    return _timer_func


class Graph(object):
    """ dijkstra closest path technique (for nurbs and lattice)
    implemented from: https://gist.github.com/econchick/4666413
    basic idea: http://www.redblobgames.com/pathfinding/a-star/introduction.html
    """

    def __init__(self):
        """ constructorMethod
        """
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        """ add the node which we will later search for the shortest path

        :param value:  key value to identify the node position
        :type value: string
        """
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        """ add the edge information from which we will later search for the shortest path

        :param from_node: node that will be used as a start position on the segment
        :type from_node: string
        :param to_node: node that will be used as the end position on the segment
        :type to_node: string
        :param distance: length between the given nodes
        :type distance: float
        """
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance


def dijkstra(graph, initial):
    """ dijkstra closest path technique (for nurbs and lattice)

    :param graph: dictionary information on positions and length for the path to search
    :type graph: Graph()
    :param initial: start index to work from
    :type initial: int
    :return: objects passed and the full list of the nodes that create the path
    :rtype: list
    """
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
    """ shortest path technique (for nurbs and lattice)

    :param graph: dictionary information on positions and length for the path to search
    :type graph: Graph()
    :param origin: start index to work from
    :type origin: int
    :param destination: end index to work from
    :type destination: int
    :return: visited objects on the way, ordered list that represents the shortest path
    :rtype: list
    """
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

def skinCluster(inObject=None, silent=False):
    """ get the skincluster from the given mesh

    :param inObject: the object to search for a skincluster attachment
    :type inObject: string
    :param silent: if `True` will return None, if `False` will open a warning dialog to tell the user no skincluster was found
    :type silent: bool
    :return: name of the skincluster node
    :rtype: string
    """
    if inObject is None:
        inObject = cmds.ls(sl=1, l=1)
    if not inObject:
        return None

    if type(inObject) in [list, tuple] and len(inObject) != 0:
        inObject = inObject[0]
    if '.' in inObject:
        inObject = inObject.split('.')[0]

    inObject = getParentShape(inObject)
    sc = cmds.ls(cmds.listHistory(inObject), type="skinCluster")
    if not sc:
        if not silent:
            cmds.confirmDialog(title='Error', message='no SkinCluster found on: %s!' % inObject, button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok')
        return None
    return sc[0]


def getParentShape(inObject):
    """ get the parent object of given object if the current given object is a shape

    :param inObject: the object to search for a parent
    :type inObject: string
    :return: name of the parent transform
    :rtype: string
    """
    if isinstance(object, list):
        inObject = inObject[0]

    objType = cmds.objectType(inObject)
    if objType in ['mesh', "nurbsCurve", "lattice"]:
        inObject = cmds.listRelatives(inObject, p=True, f=True)[0]
    if cmds.objectType(inObject) != "transform":
        inObject = cmds.listRelatives(inObject, p=True, f=True)[0]
    return inObject


def doCorrectSelectionVisualization(skinMesh):
    """ convert the given objects selection to represent the right visualisation in maya
    :todo: check if this can be converted to OpenMaya so we can get rid of mel.eval

    :param skinMesh: the object to search for a parent
    :type skinMesh: string
    """
    objType = cmds.objectType(skinMesh)
    if objType == "transform":
        shape = cmds.listRelatives(skinMesh, c=1, s=1, fullPath=1)[0]
        objType = cmds.objectType(shape)

    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    if objType in ["nurbsSurface", "nurbsCurve"]:
        mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");' % skinMesh)
    elif objType == "lattice":
        mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");' % skinMesh)
    elif objType == "mesh":
        mel.eval('doMenuComponentSelection("%s", "vertex");' % skinMesh)


def convertToVertexList(inObject):
    """ convert the given input to a represented point selection for the type of object that is selected:
    polygons : vertices
    Nurbs : control vertices
    lattice : points

    :param skinMesh: the object to search for a parent
    :type skinMesh: string
    :return: for polygons a list of vertices, for Nurbs a list of control vertices, for lattice a list of points
    :rtype: list
    """
    checkObject = inObject
    if isinstance(inObject, list):
        checkObject = inObject[0]
    objType = cmds.objectType(checkObject)
    checkType = checkObject
    if objType == "transform":
        shapes = cmds.listRelatives(inObject, ad=1, s=1, fullPath=1)
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
    return []


def getComponents(meshDag, component):
    """ convert the given input to a list of component indices

    :param meshDag: the object to search through
    :type meshDag: OpenMaya.MDagPath
    :param component: the depend node to check for component flags
    :type component: OpenMaya.MDependNode
    :return: indices of all the components on the current object
    :rtype: OpenMaya.MIntArray
    """
    vtxArray = OpenMaya.MIntArray()
    meshFn = OpenMaya.MFnMesh(meshDag)
    if component.hasFn(OpenMaya.MFn.kMeshVertComponent):
        compFn = OpenMaya.MFnSingleIndexedComponent(component)
        vtxArray = compFn.getElements()
    elif component.hasFn(OpenMaya.MFn.kMeshEdgeComponent):
        compFn = OpenMaya.MFnSingleIndexedComponent(component)
        edges = compFn.getElements()
        verts = []
        for edge in edges:
            edgeVtx = meshFn.getEdgeVertices(edge)
            verts.extend(edgeVtx)
        [vtxArray.append(i) for i in list(set(verts))]
    elif component.hasFn(OpenMaya.MFn.kMeshPolygonComponent):
        compFn = OpenMaya.MFnSingleIndexedComponent(component)
        faces = compFn.getElements()
        verts = []
        for f in faces:
            faceVtx = meshFn.getPolygonVertices(f)
            verts.extend(faceVtx)
        [vtxArray.append(i) for i in list(set(verts))]
    else:
        [vtxArray.append(i) for i in range(meshFn.numVertices)]
    return vtxArray


def selectHierarchy(node):
    """ get the hierarchy of the current given object

    :param node: the object to search through
    :type node: string
    :return: list of the objects children and current object included
    :rtype: list
    """
    ad = cmds.listRelatives(node, ad=1, f=1) or []
    ad.append(node[0])
    return ad[::-1]


def getJointIndexMap(inSkinCluster):
    """ get a map of how the joints are connected to the skincluster at which index

    :param inSkinCluster: the skincluster to use as base
    :type inSkinCluster: string
    :return: map of all the joints and how they are conencted to the skincluster
    :rtype: dict
    """
    inConns = cmds.listConnections('%s.matrix' % inSkinCluster, s=1, d=0, c=1, type="joint")
    indices = []
    _connectDict = {}
    for i in inConns[::2]:
        indices.append(int(i[i.index("[") + 1: -1]))
    for index, conn in enumerate(inConns[1::2]):
        _connectDict[cmds.ls(conn, sl=0, l=1)[0]] = indices[index]
    return _connectDict


def convertToIndexList(vertList):
    """ convert components given to a list of indices

    :param vertList: list of components
    :type vertList: list
    :return: list of integers representing the components values
    :rtype: list
    """
    indices = []
    for i in vertList:
        index = int(i[i.index("[") + 1: -1])
        indices.append(index)
    return indices


def convertToCompList(indices, inMesh, comp="vtx"):
    """ convert indices to a list of the given component

    :param indices: list of integers representing the components values
    :type indices: list
    :param inMesh: the name of the mesh
    :type inMesh: string
    :param comp: the component type
    :type comp: string
    :return: list of components
    :rtype: list
    """
    return ["%s.%s[%s]" % (inMesh, comp, i) for i in list(indices)]


def toToEdgeNumber(vtx):
    """ convert vertex to a list of connected edge numbers

    :param vtx: the vertex to gather data from
    :type vtx: string
    :return: list of all connected edges
    :rtype: list
    """
    toEdges = cmds.polyListComponentConversion(vtx, te=True)
    edges = cmds.filterExpand(toEdges, sm=32, fp=1)
    en = []
    for e in edges:
        en.append(int(e[e.index("[") + 1: -1]))
    return en


def checkEdgeLoop(inMesh, vtx1, vtx2, first=True, maxLength=40):
    """ check relations between 2 vertices if they are on the same loop

    :param inMesh: the mesh on which the vertices are placed
    :type inMesh: string
    :param vtx1: the first vertex to gather data from
    :type vtx1: string
    :param vtx2: the second vertex to gather data from
    :type vtx2: string
    :param first: if `True` it will only return the first loop found, if `False` it will return any loop found
    :type first: bool
    :param maxLength:  maximum amount of edges to search between before giving up
    :type maxLength: int
    :return: list of edges between the 2 vertices
    :rtype: list
    """
    e1n = toToEdgeNumber(vtx1)
    e2n = toToEdgeNumber(vtx2)
    combinations = list(itertools.product(e1n, e2n))
    for e1, e2 in combinations:
        edgeSel = cmds.polySelect(inMesh, elp=[e1, e2], ns=True)
        if edgeSel == None:
            continue
        loopSize = len(edgeSel)
        if loopSize > maxLength and first:
            continue
        return loopSize


def getDagpath(node, extendToShape=False):
    """ get openmaya data from given object

    :param node: the object to get the openmaya data from
    :type node: string
    :param extendToShape: if `True` will return the path of the shape, if `False` it will return the path of the transform
    :type extendToShape: bool
    :return: the openmaya object (returns dependnode if the object is not a dagnode)
    :rtype: MDagPath, MDependNode
    """
    sellist = OpenMaya.MGlobal.getSelectionListByName(node)
    try:
        if extendToShape:
            return sellist.getDagPath(0).extendToShape()
        return sellist.getDagPath(0)
    except:
        return sellist.getDependNode(0)


def getMfnSkinCluster(mDag):
    """ get openmaya skincluster data from given object

    :param node: the object to get the skinclusterdata from
    :type node: MDagPath
    :return: the skincluster object
    :rtype: MFnSkinCluster
    """
    if isinstance(mDag, OpenMaya.MDagPath):
        skinNode = skinCluster(mDag.fullPathName())
    else:
        skinNode = skinCluster(mDag)
    return OpenMayaAnim.MFnSkinCluster(getDagpath(skinNode))


def traverseHierarchy(inObject):
    """ traverse the hierarchy of the current object to gahter all mesh nodes

    :param inObject: the topnode to search from
    :type inObject: string
    :return: list of all transforms holding mesh shape data
    :rtype: list
    """
    if not isinstance(inObject, list):
        inObject = [inObject]
    polygonMesh = []

    parentNodes = inObject
    for node in parentNodes:
        nodes = cmds.listRelatives(node, ad=True, c=True, typ='transform', fullPath=True, s=False) or None
        if nodes is not None:
            inObject.extend(nodes)

    for node in inObject:
        meshnode = cmds.listRelatives(node, s=True, pa=True, type='mesh', fullPath=True) or None
        if meshnode:
            polygonMesh.append(node)

    return polygonMesh

# --- vertex island functions ---


def getConnectedVerts(inMesh, vtxSelectionSet):
    """ get seperate groups of vertices that are connected by edges

    :param inMesh: the mesh to use for gathering data
    :type inMesh: string
    :param vtxSelectionSet: list of all vertices in our current selection to convert to island groups
    :type vtxSelectionSet: list
    :return: dictionary holding information of all gathered islands
    :rtype: dict
    """
    mObject = OpenMaya.MGlobal.getSelectionListByName(inMesh).getDependNode(0)
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
    """ get the direct neighbors of current vertex index connected by edge

    :param mVtxItter: the iterator that goes over all vertices
    :type mVtxItter: MItMeshVertex
    :param index: index of the vertex to get neighbor data from
    :type index: int
    :return: set of all neighbours of current index
    :rtype: set
    """
    mVtxItter.setIndex(index)
    intArray = mVtxItter.getConnectedVertices()
    return set(int(x) for x in intArray)


def getPoints(dag):
    """Get the position in world space of each vertex on the provided mesh.

    :param dag:
    :type dag: MDagPath
    :return: Points
    :rtype: list
    """
    points = OpenMaya.MPointArray()
    mesh = OpenMaya.MFnMesh(dag)
    points = mesh.getPoints(OpenMaya.MSpace.kWorld)

    return [OpenMaya.MVector(points[i]) for i in range(len(points))]


def getNormals(meshName):
    """Get the average normal in world space of each vertex on the provided mesh.
    The reason why OpenMaya.MItMeshVertex function has to be used is that the
    MFnMesh class returns incorrect normal results.

    :note: using old open maya here as maya 2019.3.1 has a hard crash when gathering normals with new openmaya
    :param dag:
    :type dag: MDagPath
    :return: Normals
    :rtype: list
    """
    normals = []

    selectionList = oldOpenMaya.MSelectionList()
    selectionList.add(meshName)
    obj = oldOpenMaya.MObject()
    selectionList.getDependNode(0, obj)
    dag = oldOpenMaya.MDagPath.getAPathTo(obj)

    meshVerItFn = oldOpenMaya.MItMeshVertex(dag)
    while not meshVerItFn.isDone():
        normal = oldOpenMaya.MVector()
        meshVerItFn.getNormal(normal, oldOpenMaya.MSpace.kWorld)
        normals.append(OpenMaya.MVector(normal[0], normal[1], normal[2]))

        meshVerItFn.next()

    return normals


def getConnectedVerticesMapper(dag):
    """Create a dictionary where the keys are the indices of the vertices and the
    values a list of indices of the connected vertices.

    :param dag:
    :type dag: MDagPath
    :return: Connected vertices mapper
    :rtype: dict
    """
    data = {}
    connected = OpenMaya.MIntArray()
    iter = OpenMaya.MItMeshVertex(dag)

    while not iter.isDone():
        connected = iter.getConnectedVertices()
        data[iter.index()] = [c for c in connected]
        iter.next()

    return data


def growLatticePoints(points):
    """ get all neighbours of a point on a lattice

    :param points: point on a lattice
    :type points: string
    :return: list of neighbouring points
    :rtype: list
    """
    base = points[0].split('.')[0]
    allPoints = cmds.ls("%s.pt[*]" % base, l=1, fl=1)

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


def getWeights(inMesh):
    """ get the complete weight data of a given mesh
    weightData = [[value]* joints] * vertices

    :param inMesh: the object to get the data from
    :type inMesh: string
    :return: list of all weights
    :rtype: list
    """
    if cmds.objectType(inMesh) == "skinCluster":
        sc = inMesh
        inMesh = cmds.listConnections(inMesh, s=0, d=1, type="shape")
    else:
        sc = skinCluster(inMesh)
    inMesh = getParentShape(inMesh)

    shape = cmds.listRelatives(inMesh, s=1, fullPath=1)[0]

    skinNode = getDagpath(sc)
    skinFn = OpenMayaAnim.MFnSkinCluster(skinNode)
    meshPath = getDagpath(shape)
    meshNode = meshPath.node()

    meshVerItFn = OpenMaya.MItMeshVertex(meshNode)
    indices = range(meshVerItFn.count())

    singleIdComp = OpenMaya.MFnSingleIndexedComponent()
    vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
    singleIdComp.addElements(indices)

    infDags = skinFn.influenceObjects()
    infIndexes = OpenMaya.MIntArray(len(infDags), 0)
    for x in range(len(infDags)):
        infIndexes[x] = int(skinFn.indexForInfluenceObject(infDags[x]))

    weightData = skinFn.getWeights(meshPath, vertexComp, infIndexes)
    return weightData


def setWeights(inMesh, weightData):
    """ set the complete weight data of a given mesh

    :param inMesh: the object to set the data to
    :type inMesh: string
    :param weightData: full list of weight data [[value]* joints] * vertices
    :type weightData: list/MDoubleArray
    """
    if cmds.objectType(inMesh) == "skinCluster":
        sc = inMesh
        inMesh = cmds.listConnections(inMesh, s=0, d=1, type="shape")
    else:
        sc = skinCluster(inMesh)
    inMesh = getParentShape(inMesh)
    shape = cmds.listRelatives(inMesh, s=1, fullPath=1)[0]

    skinNode = getDagpath(sc)
    skinFn = OpenMayaAnim.MFnSkinCluster(skinNode)
    meshPath = getDagpath(shape)
    meshNode = meshPath.node()

    meshVerItFn = OpenMaya.MItMeshVertex(meshNode)
    indices = range(meshVerItFn.count())

    singleIdComp = OpenMaya.MFnSingleIndexedComponent()
    vertexComp = singleIdComp.create(OpenMaya.MFn.kMeshVertComponent)
    singleIdComp.addElements(indices)

    infDags = skinFn.influenceObjects()
    infIndexes = OpenMaya.MIntArray(len(infDags), 0)
    for x in range(len(infDags)):
        infIndexes[x] = int(skinFn.indexForInfluenceObject(infDags[x]))

    if not isinstance(weightData, OpenMaya.MDoubleArray):
        newWeightData = OpenMaya.MDoubleArray(len(weightData), 0)
        for i, w in enumerate(weightData):
            newWeightData[i] = w
    else:
        newWeightData = weightData

    skinFn.setWeights(meshPath, vertexComp, infIndexes, newWeightData)


# -------------

def getPolyOnMesh(point, inMesh):
    """ sget polygonal mesh data of a point on the surface

    :param point: point in space
    :type point: list
    :param inMesh: the object to get the data form
    :type inMesh: string
    :return: all elements close to given point
    :rtype: faceId, triangleID, u coordinate, v coordinate
    """
    meshDag = getDagpath(inMesh, extendToShape=True)

    meshIntersector = OpenMaya.MMeshIntersector()
    meshIntersector.create(meshDag.node(), meshDag.inclusiveMatrix())

    _point = OpenMaya.MPoint(*point)
    meshPoint = meshIntersector.getClosestPoint(_point)

    u, v = meshPoint.barycentricCoords
    return meshPoint.face, meshPoint.triangle, u, v


def getTriIndex(inMesh, polygonIndex, triangleIndex):
    """ get the points that create the current triangle

    :param inMesh: the object to get the data form
    :type inMesh: string
    :param polygonIndex: index of the current polygon( quad / ngon)
    :type polygonIndex: int
    :param triangleIndex: index of the triangle within current polygon
    :type triangleIndex: int
    :return: list of vertices that cover current triangle
    :rtype: list
    """
    meshDag = getDagpath(inMesh, extendToShape=True)
    polyIt = OpenMaya.MItMeshPolygon(meshDag)

    polyIt.setIndex(polygonIndex)
    points, verts = polyIt.getTriangle(triangleIndex, OpenMaya.MSpace.kWorld)

    return (verts[0], verts[1], verts[2])


def getTriWeight(inMesh, polygonIndex, triangleIndex, u, v):
    """ get the weight of the current coordinate based on the triangles position

    :param inMesh: the object to get the data form
    :type inMesh: string
    :param polygonIndex: index of the current polygon( quad / ngon)
    :type polygonIndex: int
    :param triangleIndex: index of the triangle within current polygon
    :type triangleIndex: int
    :param u: u coordinate on the texture map
    :type u: float
    :param v: v coordinate on the texture map
    :type v: flaot
    :return: list of joint influences and the weights necessary to attach the point to the triangle
    :rtype: list
    """
    skinClusterName = skinCluster(inMesh)
    influences = cmds.listConnections("%s.matrix" % skinClusterName, source=True)

    vtxIndex = getTriIndex(inMesh, polygonIndex, triangleIndex)
    barycentricCoords = [u, v, 1.0 - u - v]

    weights = [0.0 for _ in range(len(influences))]
    for i, vertId in enumerate(vtxIndex):
        vtxWeights = cmds.skinPercent(skinClusterName, '%s.vtx[%s]' % (inMesh, vertId), query=True, value=True)
        weights = [weights[j] + weight * barycentricCoords[i] for j, weight in enumerate(vtxWeights)]

    return influences, weights


def skinConstraint(inMesh, transform, floatPrecision=3):
    """ attach a transform to mesh based on the transforms position

    :param inMesh: the object to get the data form
    :type inMesh: string
    :param transform: transorm object to attach to the skincluster
    :type transform: string
    :param floatPrecision: amount of decimals used to calculate the weight information
    :type floatPrecision: int
    """
    floatPrecision = max(floatPrecision, 1)
    point = cmds.xform(transform, q=True, t=True, ws=True)
    faceId, triangleID, u, v = getPolyOnMesh(point, inMesh)

    transforms, weights = getTriWeight(inMesh, faceId, triangleID, u, v)
    matrixNode = createWeightedMM(transforms, weights, floatPrecision=floatPrecision)

    vec1 = cmds.createNode('vectorProduct')
    vec2 = cmds.createNode('vectorProduct')
    decNode = cmds.createNode('decomposeMatrix')

    cmds.setAttr('%s.operation' % vec1, 4)
    cmds.setAttr('%s.operation' % vec2, 4)

    cmds.setAttr('%s.input1' % vec1, *point)
    cmds.connectAttr('%s.output' % vec1, '%s.input1' % vec2)
    cmds.connectAttr('%s.parentInverseMatrix' % transform, '%s.matrix' % vec2)

    cmds.connectAttr('%s.matrixSum' % matrixNode, '%s.matrix' % vec1)
    cmds.connectAttr('%s.matrixSum' % matrixNode, '%s.inputMatrix' % decNode)

    cmds.connectAttr('%s.output' % vec2, '%s.translate' % transform, force=True)
    cmds.connectAttr('%s.outputRotate' % decNode, '%s.rotate' % transform, force=True)


def createWeightedMM(transforms, weights, floatPrecision):
    """ creat matrix multiple based on the weights of the current triangle

    :param transforms: list of joints that will drive the matrix
    :type transforms: list
    :param weights: list of weights on how much the matrix needs to be driven
    :type weights: list
    :param floatPrecision: amount of decimals used to calculate the weight information
    :type floatPrecision: int
    :return: the matrix which holds the positional information
    :rtype: wtAddMatrix node
    """
    Trs = []
    Wgth = []

    wgthTotal = 0.0
    for trsNode, weight in zip(transforms, weights):
        weight = float('%.{}f'.format(floatPrecision) % weight)
        if weight > 1e-6:
            wgthTotal += weight
            Trs.append(trsNode)
            Wgth.append(weight)

    for i, weight in enumerate(Wgth):
        Wgth[i] *= 1.0 / max(wgthTotal, 1e-6)

    addMM = cmds.createNode('wtAddMatrix')

    for i, (trsNode, weight) in enumerate(zip(Trs, Wgth)):
        mmNode = cmds.createNode('multMatrix')
        mmInv = cmds.getAttr('%s.worldInverseMatrix' % trsNode)
        cmds.setAttr('%s.matrixIn[0]' % mmNode, mmInv, type='matrix')
        cmds.connectAttr('%s.worldMatrix' % trsNode, '%s.matrixIn[1]' % mmNode)

        cmds.connectAttr('%s.matrixSum' % mmNode, '%s.wtMatrix[%s].matrixIn' % (addMM, i))
        cmds.setAttr('%s.wtMatrix[%s].weightIn' % (addMM, i), weight)

        cmds.addAttr(addMM, ln=trsNode, dv=weight, at='double', k=True)
        cmds.setAttr('%s.%s' % (addMM, trsNode), lock=True)

    return addMM


def getHierarchy(selection1, selection2):
    long1 = cmds.ls(selection1, l=1)[0]
    long2 = cmds.ls(selection2, l=1)[0]
    if selection1 in long2:
        parent = long1
        child = long2
    elif selection2 in long1:
        parent = long2
        child = long1
    else:
        return [long1, long2]

    def getParentRecursively(child, stop):
        parent = cmds.listRelatives(child, parent=1, f=1)[0]
        parents = [parent]
        if parent == stop:
            return parents
        parents.extend(getParentRecursively(parent, stop))
        return parents

    return getParentRecursively(child, parent)[::-1] + [child]


def getHierarchySelection(inType="transform"):
    selection = cmds.ls(sl=1, fl=1, l=1)
    hierarchy = selection
    amountSelected = len(selection)
    if amountSelected == 0:
        hierarchy = cmds.ls(sl=0, l=1)
    elif amountSelected == 1:
        hierarchy = [selection[0]] + cmds.listRelatives(selection[0], ad=1, f=1, type=inType)
    elif amountSelected == 2:
        hierarchy = getHierarchy(*cmds.ls(sl=1, fl=1))
    hierarchy.sort(key=len)

    if inType == []:
        return hierarchy

    return cmds.ls(hierarchy, type=inType, l=1)


def closestPosCheck(sourceVerts, targetVerts, progressBar=None):
    sourcePoints = []
    sourcePointPos = []
    for sourceVert in targetVerts:
        pos = cmds.xform(sourceVert, q=True, ws=True, t=True)
        sourcePoints.append(pos)
        sourcePointPos.append([sourceVert, pos])

    _targetVerts = []
    sourceKDTree = KDTree.construct_from_data(sourcePoints)

    percentage = 99.0 / len(sourceVerts)
    for iteration, source in enumerate(sourceVerts):
        pos = cmds.xform(source, q=1, ws=1, t=1)
        val = sourceKDTree.query(query_point=pos, t=1)[0]
        for positionList in sourcePointPos:
            if val != positionList[1]:
                continue
            _targetVerts.append(positionList[0])
        setProgress(percentage * iteration, progressBar, "gathering closest vertex data")
    return _targetVerts
