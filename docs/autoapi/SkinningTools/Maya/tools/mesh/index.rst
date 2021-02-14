:mod:`SkinningTools.Maya.tools.mesh`
====================================

.. py:module:: SkinningTools.Maya.tools.mesh


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.mesh.componentPathFinding
   SkinningTools.Maya.tools.mesh.cutCharacterFromSkin
   SkinningTools.Maya.tools.mesh.edgesToSmooth
   SkinningTools.Maya.tools.mesh.extractFacesByVertices
   SkinningTools.Maya.tools.mesh.getShellFaces
   SkinningTools.Maya.tools.mesh.polySkeleton
   SkinningTools.Maya.tools.mesh.setOrigShapeColor
   SkinningTools.Maya.tools.mesh.shortestPathLattice
   SkinningTools.Maya.tools.mesh.shortestPathNurbsCurve
   SkinningTools.Maya.tools.mesh.shortestPathNurbsSurface
   SkinningTools.Maya.tools.mesh.shortestPathVertex
   SkinningTools.Maya.tools.mesh.softSelection
   SkinningTools.Maya.tools.mesh.toggleDisplayOrigShape


.. function:: componentPathFinding(selection, useDistance, diagonal=False, weightWindow=None)

   use the component selection for pathfinding, to make sure that any skinnable mesh can be walked over

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


.. function:: cutCharacterFromSkin(inObject, internal=False, maya2020=False, progressBar=None)

   split the character into multiple meshes based on the skinning information

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


.. function:: edgesToSmooth(inEdges)

   use 2 edgeloops to find the relation of the vertices on opposite sides

   :param inEdges: list of 2 edgeloops
   :type inEdges: list
   :return: list of vertices that are closely connected together based on the edgeselection
   :rtype: list


.. function:: extractFacesByVertices(vertices, internal=False)

   use the given components to create a new mesh with the same skinning information

   :param vertices: the components to use as information to generate the new mesh
   :type vertices: list
   :param internal: if `True` will only convert the the inner selection, if `False` will grow the selection once to cover more ground
   :type internal: bool
   :return: new created mesh
   :rtype: string


.. function:: getShellFaces(inMesh)

   convert the selection of vertices to face group selections

   :param inMesh: object to evaluate
   :type inMesh: string
   :return: list of grouped faces
   :rtype: list


.. function:: polySkeleton(radius=5)

   convert the current selected skeleton to a polygonal object 
   this can be beneficial to show how the skeleton looks in other dcc tools, like zbrush

   :param radius: the radius to give each joint in the output
   :type radius: float


.. function:: setOrigShapeColor(inShape, inColor=(0.8, 0.2, 0.2))

   set a new vertex color to the given shape

   :param inShape: shape to add vertex colors to
   :type inShape: string
   :param inColor: the color to give the object
   :type inColor: tuple


.. function:: shortestPathLattice(start, end)

   get the shortest path walking over the edges between 2 selected points

   :param start: points to start from
   :type start: string
   :param end: points to end with
   :type end: string
   :return: list of points to walk in order
   :rtype: list


.. function:: shortestPathNurbsCurve(start, end)

   get the shortest path walking over the edges between 2 selected control vertices

   :param start: control vertex to start from
   :type start: string
   :param end: control vertex to end with
   :type end: string
   :return: list of control vertices to walk in order
   :rtype: list


.. function:: shortestPathNurbsSurface(start, end, diagonal=False)

   get the shortest path walking over the edges between 2 selected control vertices

   :param start: control vertex to start from
   :type start: string
   :param end: control vertex to end with
   :type end: string
   :param diagonal: if `True` the shortest path can cross cv's diagonally, if `False` it can only go straight
   :type diagonal: bool
   :return: list of control vertices to walk in order
   :rtype: list


.. function:: shortestPathVertex(start, end)

   get the shortest path walking over the edges between 2 selected vertices

   :param start: vertex to start from
   :type start: string
   :param end: vertex to end with
   :type end: string
   :return: list of vertices to walk in order
   :rtype: list


.. function:: softSelection()

   convert the soft selection in the scene to vertices and weights

   :return: list of vertices in the soft selection range and the weight of that vertex
   :rtype: list, list


.. function:: toggleDisplayOrigShape(inMesh, inColor=(0.8, 0.2, 0.2), both=False, progressBar=None)

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


