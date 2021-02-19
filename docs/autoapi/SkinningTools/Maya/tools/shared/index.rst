:mod:`SkinningTools.Maya.tools.shared`
======================================

.. py:module:: SkinningTools.Maya.tools.shared


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.shared.Graph



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.shared.checkEdgeLoop
   SkinningTools.Maya.tools.shared.convertToCompList
   SkinningTools.Maya.tools.shared.convertToIndexList
   SkinningTools.Maya.tools.shared.convertToVertexList
   SkinningTools.Maya.tools.shared.createWeightedMM
   SkinningTools.Maya.tools.shared.dec_loadPlugin
   SkinningTools.Maya.tools.shared.dec_profile
   SkinningTools.Maya.tools.shared.dec_repeat
   SkinningTools.Maya.tools.shared.dec_timer
   SkinningTools.Maya.tools.shared.dec_undo
   SkinningTools.Maya.tools.shared.dijkstra
   SkinningTools.Maya.tools.shared.doCorrectSelectionVisualization
   SkinningTools.Maya.tools.shared.getComponents
   SkinningTools.Maya.tools.shared.getConnectedVerticesMapper
   SkinningTools.Maya.tools.shared.getConnectedVerts
   SkinningTools.Maya.tools.shared.getDagpath
   SkinningTools.Maya.tools.shared.getJointIndexMap
   SkinningTools.Maya.tools.shared.getMfnSkinCluster
   SkinningTools.Maya.tools.shared.getNeighbours
   SkinningTools.Maya.tools.shared.getNormals
   SkinningTools.Maya.tools.shared.getParentShape
   SkinningTools.Maya.tools.shared.getPoints
   SkinningTools.Maya.tools.shared.getPolyOnMesh
   SkinningTools.Maya.tools.shared.getTriIndex
   SkinningTools.Maya.tools.shared.getTriWeight
   SkinningTools.Maya.tools.shared.getWeights
   SkinningTools.Maya.tools.shared.growLatticePoints
   SkinningTools.Maya.tools.shared.selectHierarchy
   SkinningTools.Maya.tools.shared.setWeights
   SkinningTools.Maya.tools.shared.shortest_path
   SkinningTools.Maya.tools.shared.skinCluster
   SkinningTools.Maya.tools.shared.skinConstraint
   SkinningTools.Maya.tools.shared.toToEdgeNumber
   SkinningTools.Maya.tools.shared.traverseHierarchy


.. data:: _DEBUG
   

   

.. py:class:: Graph



   dijkstra closest path technique (for nurbs and lattice)
   implemented from: https://gist.github.com/econchick/4666413  
   basic idea: http://www.redblobgames.com/pathfinding/a-star/introduction.html

   .. method:: add_edge(self, from_node, to_node, distance)

      add the edge information from which we will later search for the shortest path

      :param from_node: node that will be used as a start position on the segment
      :type from_node: string
      :param to_node: node that will be used as the end position on the segment 
      :type to_node: string
      :param distance: length between the given nodes
      :type distance: float


   .. method:: add_node(self, value)

      add the node which we will later search for the shortest path

      :param value:  key value to identify the node position
      :type value: string



.. function:: checkEdgeLoop(inMesh, vtx1, vtx2, first=True, maxLength=40)

   check relations between 2 vertices if they are on the same loop

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


.. function:: convertToCompList(indices, inMesh, comp='vtx')

   convert indices to a list of the given component

   :param indices: list of integers representing the components values
   :type indices: list
   :param inMesh: the name of the mesh
   :type inMesh: string
   :param comp: the component type
   :type comp: string
   :return: list of components
   :rtype: list


.. function:: convertToIndexList(vertList)

   convert components given to a list of indices

   :param vertList: list of components
   :type vertList: list
   :return: list of integers representing the components values
   :rtype: list


.. function:: convertToVertexList(inObject)

   convert the given input to a represented point selection for the type of object that is selected:
   polygons : vertices
   Nurbs : control vertices
   lattice : points

   :param skinMesh: the object to search for a parent
   :type skinMesh: string
   :return: for polygons a list of vertices, for Nurbs a list of control vertices, for lattice a list of points
   :rtype: list


.. function:: createWeightedMM(transforms, weights, floatPrecision)

   creat matrix multiple based on the weights of the current triangle

   :param transforms: list of joints that will drive the matrix
   :type transforms: list
   :param weights: list of weights on how much the matrix needs to be driven
   :type weights: list
   :param floatPrecision: amount of decimals used to calculate the weight information
   :type floatPrecision: int
   :return: the matrix which holds the positional information
   :rtype: wtAddMatrix node


.. function:: dec_loadPlugin(plugin)

   load plugin decorator
   loads the given plugin in the current maya scene, should be attached to functions that rely on plugins

   :param func: plugin this decorator is attached to 
   :type func: string
   :return: the result of the given function
   :rtype: function()


.. function:: dec_profile(func)

   profiler decorator
   run cprofile on wrapped function 

   :param func: function this decorator is attached to 
   :type func: function()
   :return: the result of the given function
   :rtype: function()


.. function:: dec_repeat(func)

   repeat last decorator
   converts the given function to a command that the repeatlast command can take
   the arguments given are parsed and converted into a string that is added to a mel command.
   :todo: double check the functionality

   :param func: function this decorator is attached to 
   :type func: function()
   :return: the result of the given function
   :rtype: function()


.. function:: dec_timer(func)

   debug timer decorator
   times the function for how long it takes to run everything in the function

   :param func: plugin this decorator is attached to 
   :type func: string
   :return: the result of the given function
   :rtype: function()


.. function:: dec_undo(func)

   undo decorator
   will allow the objects created and changed in maya to be part of a single chunk where possible 
   the decorators is wrapped within a try except finally function to make sure everything is always undoable
   :note: object created with the use of OpenMaya will not be part of this


   :param func: function this decorator is attached to 
   :type func: function()
   :return: the result of the given function
   :rtype: function()


.. function:: dijkstra(graph, initial)

   dijkstra closest path technique (for nurbs and lattice)

   :param graph: dictionary information on positions and length for the path to search
   :type graph: Graph()
   :param initial: start index to work from
   :type initial: int
   :return: objects passed and the full list of the nodes that create the path
   :rtype: list


.. function:: doCorrectSelectionVisualization(skinMesh)

   convert the given objects selection to represent the right visualisation in maya
   :todo: check if this can be converted to OpenMaya so we can get rid of mel.eval

   :param skinMesh: the object to search for a parent
   :type skinMesh: string


.. function:: getComponents(meshDag, component)

   convert the given input to a list of component indices

   :param meshDag: the object to search through
   :type meshDag: OpenMaya.MDagPath
   :param component: the depend node to check for component flags
   :type component: OpenMaya.MDependNode
   :return: indices of all the components on the current object
   :rtype: OpenMaya.MIntArray


.. function:: getConnectedVerticesMapper(dag)

   Create a dictionary where the keys are the indices of the vertices and the
   values a list of indices of the connected vertices.

   :param dag:
   :type dag: MDagPath
   :return: Connected vertices mapper
   :rtype: dict


.. function:: getConnectedVerts(inMesh, vtxSelectionSet)

   get seperate groups of vertices that are connected by edges

   :param inMesh: the mesh to use for gathering data
   :type inMesh: string
   :param vtxSelectionSet: list of all vertices in our current selection to convert to island groups
   :type vtxSelectionSet: list
   :return: dictionary holding information of all gathered islands
   :rtype: dict


.. function:: getDagpath(node, extendToShape=False)

   get openmaya data from given object

   :param node: the object to get the openmaya data from
   :type node: string
   :param extendToShape: if `True` will return the path of the shape, if `False` it will return the path of the transform
   :type extendToShape: bool
   :return: the openmaya object (returns dependnode if the object is not a dagnode)
   :rtype: MDagPath, MDependNode


.. function:: getJointIndexMap(inSkinCluster)

   get a map of how the joints are connected to the skincluster at which index

   :param inSkinCluster: the skincluster to use as base
   :type inSkinCluster: string
   :return: map of all the joints and how they are conencted to the skincluster
   :rtype: dict


.. function:: getMfnSkinCluster(mDag)

   get openmaya skincluster data from given object

   :param node: the object to get the skinclusterdata from
   :type node: MDagPath
   :return: the skincluster object
   :rtype: MFnSkinCluster


.. function:: getNeighbours(mVtxItter, index)

   get the direct neighbors of current vertex index connected by edge

   :param mVtxItter: the iterator that goes over all vertices
   :type mVtxItter: MItMeshVertex
   :param index: index of the vertex to get neighbor data from
   :type index: int
   :return: set of all neighbours of current index
   :rtype: set


.. function:: getNormals(meshName)

   Get the average normal in world space of each vertex on the provided mesh.
   The reason why OpenMaya.MItMeshVertex function has to be used is that the
   MFnMesh class returns incorrect normal results.

   :note: using old open maya here as maya 2019.3.1 has a hard crash when gathering normals with new openmaya
   :param dag:
   :type dag: MDagPath
   :return: Normals
   :rtype: list


.. function:: getParentShape(inObject)

   get the parent object of given object if the current given object is a shape

   :param inObject: the object to search for a parent
   :type inObject: string
   :return: name of the parent transform
   :rtype: string


.. function:: getPoints(dag)

   Get the position in world space of each vertex on the provided mesh.

   :param dag:
   :type dag: MDagPath
   :return: Points
   :rtype: list


.. function:: getPolyOnMesh(point, inMesh)

   sget polygonal mesh data of a point on the surface 

   :param point: point in space
   :type point: list
   :param inMesh: the object to get the data form
   :type inMesh: string
   :return: all elements close to given point
   :rtype: faceId, triangleID, u coordinate, v coordinate


.. function:: getTriIndex(inMesh, polygonIndex, triangleIndex)

   get the points that create the current triangle

   :param inMesh: the object to get the data form
   :type inMesh: string
   :param polygonIndex: index of the current polygon( quad / ngon)
   :type polygonIndex: int
   :param triangleIndex: index of the triangle within current polygon
   :type triangleIndex: int
   :return: list of vertices that cover current triangle
   :rtype: list


.. function:: getTriWeight(inMesh, polygonIndex, triangleIndex, u, v)

   get the weight of the current coordinate based on the triangles position

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


.. function:: getWeights(inMesh)

   get the complete weight data of a given mesh 
   weightData = [[value]* joints] * vertices

   :param inMesh: the object to get the data from
   :type inMesh: string
   :return: list of all weights
   :rtype: list


.. function:: growLatticePoints(points)

   get all neighbours of a point on a lattice

   :param points: point on a lattice
   :type points: string
   :return: list of neighbouring points
   :rtype: list


.. function:: selectHierarchy(node)

   get the hierarchy of the current given object

   :param node: the object to search through
   :type node: string
   :return: list of the objects children and current object included
   :rtype: list


.. function:: setWeights(inMesh, weightData)

   set the complete weight data of a given mesh 

   :param inMesh: the object to set the data to
   :type inMesh: string
   :param weightData: full list of weight data [[value]* joints] * vertices
   :type weightData: list/MDoubleArray


.. function:: shortest_path(graph, origin, destination)

   shortest path technique (for nurbs and lattice)

   :param graph: dictionary information on positions and length for the path to search
   :type graph: Graph()
   :param origin: start index to work from
   :type origin: int
   :param destination: end index to work from
   :type destination: int
   :return: visited objects on the way, ordered list that represents the shortest path
   :rtype: list


.. function:: skinCluster(inObject=None, silent=False)

   get the skincluster from the given mesh

   :param inObject: the object to search for a skincluster attachment
   :type inObject: string
   :param silent: if `True` will return None, if `False` will open a warning dialog to tell the user no skincluster was found
   :type silent: bool
   :return: name of the skincluster node
   :rtype: string


.. function:: skinConstraint(inMesh, transform, floatPrecision=3)

   attach a transform to mesh based on the transforms position

   :param inMesh: the object to get the data form
   :type inMesh: string
   :param transform: transorm object to attach to the skincluster
   :type transform: string
   :param floatPrecision: amount of decimals used to calculate the weight information
   :type floatPrecision: int


.. function:: toToEdgeNumber(vtx)

   convert vertex to a list of connected edge numbers

   :param vtx: the vertex to gather data from
   :type vtx: string
   :return: list of all connected edges
   :rtype: list


.. function:: traverseHierarchy(inObject)

   traverse the hierarchy of the current object to gahter all mesh nodes

   :param inObject: the topnode to search from
   :type inObject: string
   :return: list of all transforms holding mesh shape data
   :rtype: list


