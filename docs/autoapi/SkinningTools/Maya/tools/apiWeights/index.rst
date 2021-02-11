:mod:`SkinningTools.Maya.tools.apiWeights`
==========================================

.. py:module:: SkinningTools.Maya.tools.apiWeights


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.apiWeights.ApiWeights



.. py:class:: ApiWeights(extraInfo=False)

   this class handles all the management of a skincluster on a mesh
   mutliple meshes can be handled at once

   the default information gathered is:
   meshes
   vertices as indices
   joints influences as list
   all joint influences from all meshes at the same time as list
   skincluster names
   skinweights as a list of floats

   extra info can be gathered for matching skincluster information to a new mesh:
   vertex positions in bindpose
   joint positions in bindpose
   the bounding box of a mesh to check if the closest positions are going to work
   the uv coordinates of the mesh if applicable

   .. method:: doInit(self)

      init of all the data that we want to gather
      seperated as we might want to clear the values when necessary


   .. method:: getData(self, inNodes=None, progressBar=None)

      this function gathers all the data for the given nodes

      :param inNodes: list of mesh nodes to gather skinning information from
      :type inNodes: list
      :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
      :type progressBar: QProgressBar


   .. method:: getSkinFn(self, dagPath=None)

      get the openmaya skinFn from the current object or skincluster

      :param dagPath: dagpath to search skincluster
      :type dagPath: OpenMaya.MFnDagpath
      :return: the openmaya version of the skincluster
      :rtype: OpenMayaAnim.MFnSkinCluster


   .. method:: selectedVertIds(self, node)

      get the current selection of vertices, if mesh is seleced we take all vertices, if node is given we take information from that node
      seperated as we might want to clear the values when necessary

      :param node: a node specified to get vertex information from
      :type node: string
      :return: list of vertex ids
      :rtype: list



