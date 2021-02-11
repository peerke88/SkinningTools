:mod:`SkinningTools.Maya.tools.mathUtils`
=========================================

.. py:module:: SkinningTools.Maya.tools.mathUtils


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.mathUtils.floatToMatrix
   SkinningTools.Maya.tools.mathUtils.getCenterPosition
   SkinningTools.Maya.tools.mathUtils.getVectorFromMatrix
   SkinningTools.Maya.tools.mathUtils.matrixToFloatList
   SkinningTools.Maya.tools.mathUtils.measureLength
   SkinningTools.Maya.tools.mathUtils.setMatPos
   SkinningTools.Maya.tools.mathUtils.toPoint
   SkinningTools.Maya.tools.mathUtils.toVec3
   SkinningTools.Maya.tools.mathUtils.toVec3List
   SkinningTools.Maya.tools.mathUtils.vectorsToMatrix


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


.. function:: getVectorFromMatrix(matrix, index)

   get the vectors of which the matrix is made (index 3 will give the position)

   :param matrix: the matrix to translate
   :type matrix: MMatrix
   :param index: index of row to grab information from
   :type index: int
   :return: the MVector that represents the row of given index from the matrix
   :rtype: MVector


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


.. function:: setMatPos(matrix, vector)

   set the positon of a given OpenMaya MMatrix by a vector/ float list

   :param matrix: the matrix to translate
   :type matrix: MMatrix
   :param vector: the vector position to give the matrix
   :type vector: MVector
   :return: the OpenMaya MMatrix to be used in matrix calculations
   :rtype: MMatrix


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


