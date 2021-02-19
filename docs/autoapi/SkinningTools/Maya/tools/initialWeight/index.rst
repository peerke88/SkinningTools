:mod:`SkinningTools.Maya.tools.initialWeight`
=============================================

.. py:module:: SkinningTools.Maya.tools.initialWeight


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.initialWeight.buildSkinCluster
   SkinningTools.Maya.tools.initialWeight.closestLineToPoint
   SkinningTools.Maya.tools.initialWeight.jointsToLines
   SkinningTools.Maya.tools.initialWeight.setInitialWeights


.. function:: buildSkinCluster(inMesh, inJoints)

   This function will check if the provided mesh has a skin cluster attached
   to it. If it doesn't a new skin cluster will be created with the provided
   joints as influences. No additional arguments are used to setup the skin
   cluster. This is something that needs to be done afterwards by the user.
   If a skin cluster already exists all provided joints will be added to the
   skin cluster as an influence.

   :param str mesh:
   :param list inJoints:
   :return: Skin cluster
   :rtype: str


.. function:: closestLineToPoint(lines, point)

   Loop over all lines and find the closest point on the line from the
   provided point. After this is done the list of lines is sorted based on
   closest distance to the line.

   :param lines:
   :type lines: dict
   :param point:
   :type point: MVector
   :return: Closest lines and points ordered on distance
   :rtype: tuple


.. function:: jointsToLines(inJoints)

   Filter the provided joints list and loop its children to generate lines
   between the parent and its children. It is possible that multiple children
   lie on the same line thinking twister joints for example. This function
   filters those out and creates lines between the twisters rather than lines
   overlapping each other.

   :param joints:
   :type joints: list
   :return: Line data
   :rtype: dict


.. function:: setInitialWeights(inMesh, inJoints, iterations=3, projection=0, blend=False, blendMethod=None, progressBar=None)

   The set initial weights function will set the skin weights on a mesh and
   the isolate only the provided components of any. Each vertex will only
   have one influence, the best influence is determined by generating lines
   for each of the joints and determining the line closest to the vertex. The
   vertex points can be altered as well using laplacian smoothing operations
   to details or overlapping and the project can be used to project the point
   along its normal to get it closer to the preferred joints.

   :param mesh:
   :type mesh:str
   :param joints:
   :type joints:list
   :param iterations: Number of smoothing iterations
   :type iterations:int
   :param projection: Value between 0-1
   :type projection:float


