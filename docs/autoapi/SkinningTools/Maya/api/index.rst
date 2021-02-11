:mod:`SkinningTools.Maya.api`
=============================

.. py:module:: SkinningTools.Maya.api

.. autoapi-nested-parse::

   Maya stub of imports used in the UI library.

   The idea is to make this file as short as possible
   while leaving room for other packages to implement features.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.api._EventFilter



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.api._cleanEventFilter
   SkinningTools.Maya.api._eventFilterTargets
   SkinningTools.Maya.api.connectSelectionChangedCallback
   SkinningTools.Maya.api.convertlistToOpenMayaArray
   SkinningTools.Maya.api.dccInstallEventFilter
   SkinningTools.Maya.api.dec_loadPlugin
   SkinningTools.Maya.api.disconnectCallback
   SkinningTools.Maya.api.displayToolTips
   SkinningTools.Maya.api.getApiDir
   SkinningTools.Maya.api.getIds
   SkinningTools.Maya.api.getMayaVersion
   SkinningTools.Maya.api.getPlugin
   SkinningTools.Maya.api.getPluginSuffix
   SkinningTools.Maya.api.getSingleVertexWeight
   SkinningTools.Maya.api.getSingleVertexWeights
   SkinningTools.Maya.api.getSkinWeights
   SkinningTools.Maya.api.get_maya_window
   SkinningTools.Maya.api.selectVertices
   SkinningTools.Maya.api.selectedObjectVertexList
   SkinningTools.Maya.api.selectedSkinnedShapes
   SkinningTools.Maya.api.setSkinWeights
   SkinningTools.Maya.api.skinClusterInfluences
   SkinningTools.Maya.api.textProgressBar


.. data:: _DEBUG
   

   

.. data:: addCleanJoint
   

   

.. data:: dec_undo
   

   

.. data:: meshVertexList
   

   

.. data:: skinClusterForObject
   

   

.. data:: skinClusterForObjectHeadless
   

   

.. data:: skinPercent
   

   

.. py:class:: _EventFilter



   eventfilter class to allow extra functionality to be added to the current maya qt eventfilters
       

   .. attribute:: _singleton
      

      

   .. method:: eventFilter(self, obj, event)


   .. staticmethod:: singleton()

      singleton of the current class for ease of identifying

      :return: the current object singleton
      :rtype: cls



.. function:: _cleanEventFilter()


.. function:: _eventFilterTargets()

   We must return all widgets that receive strong focus that we want to tap into
   such as the main window or 3D viewports that are not simple Qt widgets.

   :return: the maya window and the active 3d viewport
   :rtype: list


.. function:: connectSelectionChangedCallback(callback)

   connect a callback to a selection changed event

   :param callback: the callback to connect
   :type callback: function
   :return: scriptjob that holds the callback
   :rtype: string


.. function:: convertlistToOpenMayaArray(inList, arrayType)

   convert given list to an openmaya arraytype

   :param inList: list of objects to be added to arraytype
   :type inList: list
   :param arrayType: any openmaya array type
   :type arrayType: OpenMaya.<array>
   :return: the array filled with data
   :rtype: OpenMaya.<array>


.. function:: dccInstallEventFilter()


.. function:: dec_loadPlugin(input)

   forwarded decorator function to load plugins

   :note: maybe remove this? too many similar functions? combine them all together
   :param input: name of the (python)plugin to load
   :type input: string


.. function:: disconnectCallback(handle)

   disconnect a callback present in the scene

   :param handle: the name of the scriptjob to remove
   :type handle: string


.. function:: displayToolTips()

   force display tool tips in maya as these are turned off by default


.. function:: getApiDir()

   get the path to the current file

   :return: path of the api file
   :rtype: string


.. function:: getIds(inList)

   forwarded function to conevert components to indices

   :param inlist: list of maya components
   :type inlist: list
   :return: list of indices
   :rtype: list


.. function:: getMayaVersion()

   get the current general mayaversion in which this tool is launched

   :return: maya version number as string
   :rtype: string


.. function:: getPlugin()

   get the smoothbrush plugin based on information gathered on how maya is run

   :return: the path of the plugin to load
   :rtype: string


.. function:: getPluginSuffix()

   get the current plugin suffix based on the os that we are running

   :return: suffix for plugin files specific to a particular os
   :rtype: string


.. function:: getSingleVertexWeight(skinClusterHandle, vertexHandle, influenceHandle)

   given a skin,  a vertex and a joint, return the weight
   skin cluster can be obtained with skinClusterForObject
   mvertex can be obtained with selectedObjectVertexList(True), joint can be obtained with skinClusterInfluences

   :param skinClusterHandle: name of the current skincluster
   :type skinClusterHandle: string
   :param vertexHandle: name of current vertex
   :type vertexHandle: string
   :param influenceHandle: name of bone to get data from
   :type influenceHandle: string
   :return: list of influences
   :rtype: list


.. function:: getSingleVertexWeights(skinClusterHandle, vertexHandle)

   given a skin and a vertex, return the weight
   skin cluster can be obtained with skinClusterForObject
   vertex can be obtained with selectedObjectVertexList(True)

   :param skinClusterHandle: name of the current skincluster
   :type skinClusterHandle: string
   :param vertexHandle: name of current vertex
   :type vertexHandle: string
   :return: list of influences
   :rtype: list


.. function:: getSkinWeights(geometry)

   forwarded function to get the skinning data of a mesh

   :param geometry: mesh to get data from
   :type geometry: string
   :return: list of all weights on the mesh
   :rtype: list


.. function:: get_maya_window()

   get the current maya window as a qt widget

   :return: the widget or none
   :rtype: QWidget


.. function:: selectVertices(meshVertexPairs)

   select vertices based on given vertex pairs

   :param meshVertexPairs: list of objects that hold a list of which the second element is a vertex
   :type meshVertexPairs: list


.. function:: selectedObjectVertexList(includeObjects=False)

   get the current object/component selection

   :param includeObjects: if `True` will return the name of the object from which the vertex comes from, if `False` will only return the vertices
   :type includeObjects: bool
   :return: list of vertices 
   :rtype: list


.. function:: selectedSkinnedShapes()

   get the shapes of skinned objects

   :return: list of shapes
   :rtype: list


.. function:: setSkinWeights(geometry, skinCluster, weights, influenceIndices=None)

   forwarded function to set the skinning data on a mesh

   :param geometry: mesh to set data to
   :type geometry: string
   :param skinCluster: skincluster attached to the current geometry
   :type skinCluster: string
   :param weights: list of weights to set
   :type weights: list
   :param influenceIndices: list of joints
   :type influenceIndices: list


.. function:: skinClusterInfluences(skinCluster)

   forwarded function to get joint information from skincluster

   :param skinCluster: skincluster to gather data from
   :type skinCluster: string
   :return: list of all joints(fullpath) connected to the skincluster
   :rtype: list


.. function:: textProgressBar(progress, message='')

   set the current progress of a function using test only

   :param progress: percentage of progress 
   :type progress: float
   :param message: the message to be displayed
   :type message: string


