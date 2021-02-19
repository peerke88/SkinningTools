:mod:`SkinningTools.Maya.tools.mathUtils`
=========================================

.. py:module:: SkinningTools.Maya.tools.mathUtils


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.mathUtils.clamp
   SkinningTools.Maya.tools.mathUtils.closestPointOnLine
   SkinningTools.Maya.tools.mathUtils.easeInOutCircular
   SkinningTools.Maya.tools.mathUtils.easeInOutCubic
   SkinningTools.Maya.tools.mathUtils.easeInOutExponential
   SkinningTools.Maya.tools.mathUtils.easeInOutQuadratic
   SkinningTools.Maya.tools.mathUtils.easeInOutQuartic
   SkinningTools.Maya.tools.mathUtils.easeInOutQuintic
   SkinningTools.Maya.tools.mathUtils.easeInOutSinusoidal
   SkinningTools.Maya.tools.mathUtils.floatToMatrix
   SkinningTools.Maya.tools.mathUtils.getCenterPosition
   SkinningTools.Maya.tools.mathUtils.getSceneUp
   SkinningTools.Maya.tools.mathUtils.getTweeningMethod
   SkinningTools.Maya.tools.mathUtils.getTweeningMethods
   SkinningTools.Maya.tools.mathUtils.getVectorFromMatrix
   SkinningTools.Maya.tools.mathUtils.laplacianSmoothing
   SkinningTools.Maya.tools.mathUtils.lookAt
   SkinningTools.Maya.tools.mathUtils.matrixToFloatList
   SkinningTools.Maya.tools.mathUtils.measureLength
   SkinningTools.Maya.tools.mathUtils.parameterOfPointOnLine
   SkinningTools.Maya.tools.mathUtils.setMatPos
   SkinningTools.Maya.tools.mathUtils.sortByDistance
   SkinningTools.Maya.tools.mathUtils.toPoint
   SkinningTools.Maya.tools.mathUtils.toVec3
   SkinningTools.Maya.tools.mathUtils.toVec3List
   SkinningTools.Maya.tools.mathUtils.vectorsToMatrix


.. function:: clamp(value, minValue, maxValue)


.. function:: closestPointOnLine(a, b, point)

   Get the closest point on a line. The line is defined by the provided a
   and b point. The point is the point in space that is used to find the
   closest point on the line.

   :param a: point a of the line
   :type a: MVector
   :param b:  point b of the line
   :type b: MVector
   :param point: the point gather the information from
   :type point: MVector
   :return: Closest point on line
   :rtype: MVector


.. function:: easeInOutCircular(n)


.. function:: easeInOutCubic(n)


.. function:: easeInOutExponential(n)


.. function:: easeInOutQuadratic(n)


.. function:: easeInOutQuartic(n)


.. function:: easeInOutQuintic(n)


.. function:: easeInOutSinusoidal(n)


.. function:: floatToMatrix(floatList)

   convert list of 16 floats to an OpenMaya MMatrix

   :param floatList: list of at least 16 floats/ints to convert to a matrix
   :type floatList: list
   :return: the OpenMaya MMatrix to be used in matrix calculations
   :rtype: MMatrix


.. function:: getCenterPosition(inPositions)

   get the center position from all input positions

   :param inPositions: list of vectors that represent a cluster of positions
   :type inPositions: list
   :return: center position of current given positions
   :rtype: MVector


.. function:: getSceneUp(asIndex=True)

   function to get current scene up axis

   :param asIndex: if `True` will return the index of current upvector, if `False` will return string representation
   :type asIndex: bool
   :return: scene up axis
   :rtype: int,string


.. function:: getTweeningMethod(method)

   Get the tweening method from a string, if the function doesn't exists
   None will be returned.

   :return: Tweening function
   :rtype: func/None


.. function:: getTweeningMethods()

   Get all of the available tweening methods.

   :return: Tweening methods
   :rtype: dict


.. function:: getVectorFromMatrix(matrix, index)

   get the vectors of which the matrix is made (index 3 will give the position)

   :param matrix: the matrix to translate
   :type matrix: MMatrix
   :param index: index of row to grab information from
   :type index: int
   :return: the MVector that represents the row of given index from the matrix
   :rtype: MVector


.. function:: laplacianSmoothing(vectors, connected, iterations=3)

   Perform a laplacian smoothing on the provided vectors based on a
   connection mapper. The position of the new vector is set based on the
   index of that vector and its connected vectors based on the connected
   indices. The new vector position is the average position of the connected
   vectors.

   :param vectors:
   :type vectors: list
   :param connected:
   :type connected: dict
   :param iterations:
   :type iterations: int
   :return: Smoothed vectors
   :rtype: list


.. function:: lookAt(base, aim, up=None, primaryAxis=toVec3((1, 0, 0)), secondaryAxis=toVec3((0, 1, 0)), invertTerz=False)

   convert a minimal of 2 positions to an aim matrix 

   :param Base: base position of the mmatrix 
   :type Base: MVector
   :param aim: position the matrix needs to point towards 
   :type aim: MVector
   :param up: poition that the matrix needs to identify the secondary lookat 
   :type up: MVector
   :param primaryAxis: vector used as the aim for current matrix 
   :type primaryAxis: MVector
   :param secondaryAxis: vector used as the up axis 
   :type secondaryAxis: MVector
   :return: the matrix created from 2 vectors
   :rtype: MMatrix


.. function:: matrixToFloatList(matrix)

   convert MMatrix to a list of 16 floats

   :param matrix: OpenMaya MMatrix to convert
   :type matrix: MMAtrix
   :return: list of 16 floats gathered from a matrix
   :rtype: list


.. function:: measureLength(object1, object2)

   get the length bewtween 2 given objects translations

   :param object1: 1st object to get transformation data from
   :type object1: string
   :param object2: 2nd object to get transformation data from
   :type object2: string
   :return: length between 2 given objects
   :rtype: float


.. function:: parameterOfPointOnLine(a, b, point)

   Get the parameter of a point on a line. For this function to give a
   correct result it is important that the provided point already lies on the
   line. The :func:`closestPointOnLine` can be used to get that point on the
   line.

   :param a: point a on the line
   :type a: MVector
   :param b: point b on the line
   :type b: MVector
   :param point: the position in space to check the parameter on the line
   :type point: MVector
   :return: Parameter of the point on the line
   :rtype: float


.. function:: setMatPos(matrix, vector)

   set the positon of a given OpenMaya MMatrix by a vector/ float list

   :param matrix: the matrix to translate
   :type matrix: MMatrix
   :param vector: the vector position to give the matrix
   :type vector: MVector
   :return: the OpenMaya MMatrix to be used in matrix calculations
   :rtype: MMatrix


.. function:: sortByDistance(nodes, point, points)

   Sort the provided nodes list based on the distance between the point and
   the points. With the nodes sorted from shortest distance to longest. It
   is expected that the order of the nodes link with the order of the points.

   :param nodes: 
   :type nodes: list
   :param point:
   :type point: MVector
   :param points:
   :type points: list
   :return: Sorted node list and sorted points list
   :rtype: tuple(list, list)


.. function:: toPoint(inObject)

   convert a list or tuple to an MPoint

   :param inObject: list of floats or ints
   :type inObject: list
   :return: point created from list
   :rtype: MPoint


.. function:: toVec3(inObject)

   convert a list or tuple to an MVector

   :param inObject: list of floats or ints
   :type inObject: list
   :return: vector created from list
   :rtype: MVector


.. function:: toVec3List(inList)

   convenience function convert a list of floatlists or intlists to a list of MVectors

   :param inList: list of lists
   :type inList: list
   :return: list of MVectors
   :rtype: list


.. function:: vectorsToMatrix(vectorList)

   convert list of OpenMaya MVector to an OpenMaya MMatrix

   :param vectorList: list of at least 3 MVectors (to make sure the rotation matrix is set)
   :type vectorList: list
   :return: the OpenMaya MMatrix to be used in matrix calculations
   :rtype: MMatrix


