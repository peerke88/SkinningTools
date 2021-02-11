:mod:`SkinningTools.Maya.tools.weightsManager`
==============================================

.. py:module:: SkinningTools.Maya.tools.weightsManager


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.weightsManager.WeightsManager



.. py:class:: WeightsManager(inProgressBar=None)



   this is the manager class, maybe make a different ui class to attach these elements to
   when loading there are 4 scenarios:

   1. 1 to 1 the mesh and joints are exactly the same ( need to find a way to double check the vertex order to make sure)

   2. mesh is not the same, joints are (we need to find the best possible match using closest vertex/uvs) try baricentric coordinates where possible

   3. mesh is the same but joints are not (remap joints with the remapper, this can be closest joint, joint naming etc.) 

   4. mesh and joints are total mismatch (double check if joints are somewhate in a similar position and bounding box of the mesh is within range, maybe also do a check on joint hierarchy)

   -------------------------------

   allow files to be stored anywhere on the pc, maybe keep track on where its placed using qsettings
   also have a folder structure tree and file window next to each other for this
   place a base file setup where these files can be stored by default for quick save and load

   .. method:: _getPosAndUvCoords(self, inMesh)

      get positional data of the current mesh's components

      :param inMesh: the mesh to gather data from
      :type inMesh: string
      :return: list of positions and uv coordinates
      :rtype: list


   .. method:: checkNeedsClosestVtxSearch(self, data, fromMesh, toMesh)

      check the current mesh's positional data with the stored data

      :param data: data from the stored meshes
      :type data: dict
      :param fromMesh: the direct mesh to compare with that was stored
      :type fromMesh: string
      :param toMesh: the mesh that will get the information
      :type toMesh: string
      :return: `True` if object data does not match
      :rtype: bool


   .. method:: gatherData(self)

      gather the data from current selection of objects

      :return: data from current selected objects
      :rtype: dict


   .. method:: importData(self, jsonFile, workMesh=None, scale=1.0, closestNPoints=3, uvBased=False)

      import data from a json file 
      this setup tries to make it possible to load skinning information that does not match the original object

      :todo: make sure it works only on the workmesh if given
      :todo: fix the setup in a way that it works with the given scale

      :param jsonFile: the file that holds all the skinning information
      :type jsonFile: string
      :param closestNPoints: closest amount of positions to search from
      :type closestNPoints: int
      :param uvBased: if `True` will try to search information based on UV's, if `False`  will use the points in the 3d scene
      :type uvBased: bool


   .. method:: readData(self, jsonFile)

      read the data from a json file

      :return: data from the json file
      :rtype: dict



