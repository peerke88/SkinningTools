from collections import defaultdict, deque, OrderedDict
from functools import wraps

def dec_undo(func):
    '''undo decorator'''
    @wraps(func)
    def _undo_func(*args, **kwargs):
        try:
            cmds.undoInfo(ock=True)
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            print(e.__class__)
            print(sys.exc_info())
            cmds.warning(traceback.format_exc( )) 
        finally:
            cmds.undoInfo(cck=True)
    
    return _undo_func

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
#@note: make sure that all objects return full path

def skinCluster(object, silent=False):
    '''static function to get the skincluster from any mesh
    @param object: mesh to get the skinCluster
    @param silent: flag to display warning dialog or to silently continue the current function'''
    
    object = SkinningTools.getParentShape(object)
    skinCluster = mel.eval('findRelatedSkinCluster("%s");'%object) 
    if not skinCluster:
        if silent == False:
            cmds.confirmDialog( title='Error', message='no SkinCluster found on: %s!'%object, button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
        else:
            skinCluster = None
    return skinCluster

def getParentShape(object):
    '''static function to get the correct dagnode of a mesh which is used in other functions'''
    if isinstance(object, list):
        object = object[0]
    objType = cmds.objectType(object)
    if objType == 'mesh' or objType == "nurbsCurve" or objType == "lattice":
        object = cmds.listRelatives(object, p=True, f=True)[0]
    if cmds.objectType(object) != "transform":
        object = cmds.listRelatives(object, p=True, f=True)[0]
    return object

def doCorrectSelectionVisualization(skinMesh):
    '''static function to cleanup selection details in maya so selection is correctly visualized'''
    objType = cmds.objectType(skinMesh)
    if objType == "transform":
        shape = cmds.listRelatives(skinMesh, c=1, s=1)[0]
        objType = cmds.objectType(shape)

    mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
    if objType == "nurbsSurface" or objType == "nurbsCurve":
        mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");'%skinMesh )
    elif objType == "lattice":
        mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");'%skinMesh )
    elif objType == "mesh":
        mel.eval('doMenuComponentSelection("%s", "vertex");'%skinMesh )

def convertToVertexList(self, object):
    '''conveniently converts every polygonal selection to vertices as vertices are the components on which skin is applied
    @param object: can be either the mesh, the shape or a component based selection
    selection will be flattened so each vertix is listed without nesting (i.e. ['.vtx[0:20]'] becomes ['.vtx[0]', '.vtx[1]', .....])'''
    checkObject = object
    if isinstance(object, list):
        checkObject = object[0]
    objType = cmds.objectType(checkObject)
    checkType = checkObject
    if objType == "transform":
        shapes = cmds.listRelatives(object, ad=1, s=1)
        if not shapes == []:
            checkType = object
        checkType = shapes[0]

    objType = cmds.objectType(checkType)
    if objType == 'mesh': # or objType == "nurbsCurve" or objType == "lattice":
        convertedVertices = cmds.polyListComponentConversion(object, tv=True)
        return cmds.filterExpand(convertedVertices, sm=31)
    
    if objType == "nurbsCurve" or objType == "nurbsSurface":
        if isinstance(object, list) and ".cv" in object[0]:
            return cmds.filterExpand(object, sm=28)
        elif isinstance(object, list):
            return cmds.filterExpand('%s.cv[*]'%object[0], sm=28)
        elif ".cv" in object:
            return cmds.filterExpand(object, sm=28)
        else:
            return cmds.filterExpand('%s.cv[*]'%object, sm=28)
    
    if objType == "lattice":
        if isinstance(object, list) and ".pt" in object[0]:
            return cmds.filterExpand(object, sm =46 )
        elif isinstance(object, list):
            return cmds.filterExpand('%s.pt[*]'%object[0], sm =46 )
        elif ".pt" in object:
            return cmds.filterExpand(object, sm =46 )
        else:
            return cmds.filterExpand('%s.pt[*]'%object, sm =46 )