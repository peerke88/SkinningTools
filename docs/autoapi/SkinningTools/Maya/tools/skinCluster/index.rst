:mod:`SkinningTools.Maya.tools.skinCluster`
===========================================

.. py:module:: SkinningTools.Maya.tools.skinCluster


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.skinCluster.SoftSkinBuilder



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.skinCluster.AvarageVertex
   SkinningTools.Maya.tools.skinCluster.Copy2MultVertex
   SkinningTools.Maya.tools.skinCluster.avgVertex
   SkinningTools.Maya.tools.skinCluster.checkBasePose
   SkinningTools.Maya.tools.skinCluster.combineSkinnedMeshes
   SkinningTools.Maya.tools.skinCluster.doSkinPercent
   SkinningTools.Maya.tools.skinCluster.execCopySourceTarget
   SkinningTools.Maya.tools.skinCluster.extractSkinnedShells
   SkinningTools.Maya.tools.skinCluster.forceCompareInfluences
   SkinningTools.Maya.tools.skinCluster.freezeSkinnedMesh
   SkinningTools.Maya.tools.skinCluster.getVertOverMaxInfluence
   SkinningTools.Maya.tools.skinCluster.hammerVerts
   SkinningTools.Maya.tools.skinCluster.hardSkinSelectionShells
   SkinningTools.Maya.tools.skinCluster.keepOnlySelectedInfluences
   SkinningTools.Maya.tools.skinCluster.neighbourAverage
   SkinningTools.Maya.tools.skinCluster.seperateSkinnedObject
   SkinningTools.Maya.tools.skinCluster.setMaxJointInfluences
   SkinningTools.Maya.tools.skinCluster.smoothAndSmoothNeighbours
   SkinningTools.Maya.tools.skinCluster.switchVertexWeight
   SkinningTools.Maya.tools.skinCluster.transferClosestSkinning
   SkinningTools.Maya.tools.skinCluster.transferSkinning
   SkinningTools.Maya.tools.skinCluster.transferUvToSkinnedObject


.. data:: _DEBUG
   

   

.. py:class:: SoftSkinBuilder(progressBar=None)



   this class handles the buildup of a skincluster using selections
   the base of the infromation is gathered from the object itself

   the user can then alter the weights using direct selection and assiging the values
   or it can use the soft selection to define a bigger selection and smooth weights

   .. method:: addSoftSkinInfo(self, bone)

      add skinning info to the bone based on current selection

      :param bone: name of the bone to assign data too
      :type bone: string


   .. method:: analyzeSkin(self, inMesh, pre=True)

      analyze the current skin, get information from the given mesh and fill the constructor

      :param inMesh: the mesh to analyze
      :type inMesh: string
      :param pre: if `True` will set the current info to be pre-analyzed, if `False` will leave the function alone
      :type pre: bool
      :note pre: unused, this one will be used later to check if we are going to add, replace or create weights from scratch
      :return: list of current joints influencing the mesh
      :rtype: list


   .. method:: getVerts(self, bone)

      get the vertices currently influenced by the given bone

      :param bone: name of the bone to get information from
      :type bone: string
      :return: list of vertices influenced
      :rtype: list


   .. method:: removeData(self, bone)

      remove the data associated with given bone

      :Todo: figure out what to do with the original weights!
      :param bone: name of the bone to clear the date off
      :type bone: string


   .. method:: setSoftSkinInfo(self, inMesh, add=True)

      set the skinning info to the mesh

      :param inMesh: name of the mesh to assignt the data to
      :type inMesh: string
      :param add: if `True` will add the info to the existing information, if `False` will override the information
      :type add: bool



.. function:: AvarageVertex(selection, useDistance, weightAverageWindow=None, progressBar=None)

   grouped function that allows multiple ways of averaging vertices based on how its selected

   :param selection: list of components
   :type selection: list
   :param useDistance: if `True` the weight is measured by the distance between elements, if `False` weight is measured by the amount in the selection
   :type useDistance: bool
   :param weightAverageWindow: name of the skinned mesh to cleanup
   :type weightAverageWindow: falloffCurveUI
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: Copy2MultVertex(selection, lastSelected, progressBar=None)

   copy information between vertices

   :param selection: the selection of vertices that will get the information
   :type selection: list 
   :param lastSelected: the vertex we gather information from
   :type lastSelected: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed, vertices if requested
   :rtype: bool


.. function:: avgVertex(vertices, lastSelected, progressBar=None)

   smooth a vertex's skinning information based on order of selection

   :param vertices: list of vertices to gather information from
   :type vertices: list
   :param lastSelected: last selected object can get the average information
   :type lastSelected: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: checkBasePose(skinCluster)

   check if the current object is in bindpose, using the prebind matrices and the worldmatrices of the joints
   :note: only compare worldspace translate values as precision might be difficult here

   :param skinCluster: the current skincluster to check
   :type skinCluster: string
   :return: `True` if the setup is in bindpose, `False` if not
   :rtype: bool


.. function:: combineSkinnedMeshes(meshes, progressBar=None)

   combine multiple skinned meshes into 1 single skinned mesh

   :param meshes: list of meshes to combine
   :type meshes: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: the mesh that is created
   :rtype: string


.. function:: doSkinPercent(bone, value, operation=0)

   simple function to quickly set weights with the given value

   :param bone: joint to change the weight influence of
   :type bone: list
   :param value: value to set the weight
   :type value: float
   :param operation: the operation on how to treat the weight
   :type operation: int
   :note operation: = { 0:removes the values, 1:sets the values, 2: adds the values}
   :return: `True` if the function is completed
   :rtype: bool


.. function:: execCopySourceTarget(TargetSkinCluster, SourceSkinCluster, TargetSelection, SourceSelection, smoothValue=1, progressBar=None)

   copy skincluster information from one vertex group to another based on closest proximity

   :param TargetSkinCluster: the skincluster to gather information from
   :type TargetSkinCluster: string
   :param SourceSkinCluster: the skincluster to send information to
   :type SourceSkinCluster: string
   :param TargetSelection: the vertex selection to copy from
   :type TargetSelection: list
   :param SourceSelection: the vertex selection to copy to
   :type SourceSelection: list
   :param smoothValue: amount of closest positions to gather data from
   :type smoothValue: int
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed, vertices if requested
   :rtype: bool


.. function:: extractSkinnedShells(components, progressBar=None)

   extract a selection of components as a new mesh with the same skinning info

   :param components: list of components that define the new mesh
   :type components: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: the mesh that is created
   :rtype: string


.. function:: forceCompareInfluences(meshes)

   force the joints on the current meshes to be shared, this to make sure we cannot apply weights to joints that dont exist on the skincluster

   :param meshes: the meshes on which all joints need to be shared
   :type meshes: list
   :return: `True` if the joints are the same for all meshes, `False` if not
   :rtype: bool


.. function:: freezeSkinnedMesh(inMesh, progressBar=None)

   'freeze' a skinned mesh, remove construction history and transform information

   :param inMesh: name of the skinned mesh to cleanup
   :type inMesh: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: getVertOverMaxInfluence(inObject, maxInfValue=8, progressBar=None)

   get the information of the objects skincluster on if there are too many joints driving a single vertex

   :param inObject: the object to gather information from
   :type inObject: string
   :param maxInfValue: the amount of joints that are allowed to deform a vertex at once
   :type maxInfValue: int 
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: vertices that have too much influences, dictionary on the specific vertex on how many influences are present
   :rtype: list


.. function:: hammerVerts(inSelection, needsReturn=True, progressBar=None)

   a quick and dirty way of smoothing vertex selection

   :param inSelection: the selection of vertices that will be smoothed
   :type inSelection: list 
   :param needsReturn: if `True` will return a vertex list of affected vertices, if `False` will return default value
   :type needsReturn: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed, vertices if requested
   :rtype: bool, list


.. function:: hardSkinSelectionShells(selection, progressBar=False)

   use the current selection to define islands that are clustered togehter and make sure that each island shares the same skinning information

   :param selection: list of components
   :type selection: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: the current selection
   :rtype: list


.. function:: keepOnlySelectedInfluences(fullSelection, jointOnlySelection, inverse=False, progressBar=None)

   use the selection of joints and components to tell which joints are allowed to drive the current components

   :param fullSelection: list of meshes and joints
   :type fullSelection: list
   :param fullSelection: list of only joints
   :type fullSelection: list
   :param fullSelection: if `True` will remove the current joints from the selection, if `False` will make sure only these joints drive the components
   :type fullSelection: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: neighbourAverage(components, warningPopup=True, progressBar=None)

   force smooth skinning based on the current selection

   :param components: current list of components
   :type components: list
   :param warningPopup: if `True` will open a popup when the selection might take too long, if `False` will not use the popup
   :type warningPopup: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: seperateSkinnedObject(inMesh, progressBar=None)

   seperate a skinned mesh that has different polygroups combined into multiple objects with skinning information intact

   :param inMesh: the skinned mesh to split in multiple
   :type inMesh: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: setMaxJointInfluences(inObject=None, maxInfValue=8, progressBar=None)

   set the information of the objects skincluster if there are too many joints driving a single vertex to be under that limit

   :param inObject: the object to gather information from
   :type inObject: string
   :param maxInfValue: the amount of joints that are allowed to deform a vertex at once
   :type maxInfValue: int 
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed, 
   :rtype: bool


.. function:: smoothAndSmoothNeighbours(input, both=False, growing=False, full=True, progressBar=None)

   a function that can walk over a mesh selection smooth the mesh gradually

   :param input: list components
   :type input: list
   :param both: if `True` will smooth both the inner and outer part of the selection, if `False` will only smooth outside of the current selection
   :type both: bool
   :param growing: if `True` smooth and convert the selection to the outer shell of current selection, if `False` will keep the same selection
   :type growing: bool
   :param full: if `True` will get any component in the outer selection that is close to the current vertex, if `False` will only select vertices connected by an edge
   :type full: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: list of vertices in the new selection
   :rtype: list


.. function:: switchVertexWeight(vertex1, vertex2, progressBar=None)

   swap information between 2 skinned vertices

   :param vertex1: the first vertex to use skin info 
   :type vertex1: string
   :param vertex2: the second vertex to use skin info
   :type vertex2: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: transferClosestSkinning(objects, smoothValue, progressBar=None)

   copy skincluster information from one object to others based on closest proximity

   :param objects: objects to use for data, first selected will be used to gather data, the rest will be copied to
   :type objects: list
   :param smoothValue: amount of closest positions to gather data from
   :type smoothValue: int
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: transferSkinning(baseSkin, otherSkins, inPlace=True, sAs=True, uvSpace=False, progressBar=None)

   copy skincluster information from one object to others 

   :param baseSkin: objects to use for data
   :type baseSkin: string
   :param otherSkins: objects that will get the data from the baseskin
   :type otherSkins: list
   :param inPlace: if `True` will delete the history on other objects before applying the skin (building new skincluster info), if `False` will build on top of existing skincluster info
   :type inPlace: bool
   :param sAs: if `True` will use surface association method to copy over information, if `False` will use a brute force approach
   :type sAs: bool
   :param uvSpace: if `True` will use uv space information to copy skin, if `False` will use closest vertex position
   :type uvSpace: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: transferUvToSkinnedObject(meshSource, meshTarget, sourceMap='map1', targetMap='map1', progressBar=None)

   a way to copy uv map information from a static mesh to a skinned mesh without breaking the history stack

   :param meshSource: the static mesh that holds correct uv information
   :type meshSource: string
   :param meshTarget: the skinned mesh that needs to get uv information
   :type meshTarget: string
   :param sourceMap: the uv map to get information from
   :type sourceMap: string
   :param targetMap: the uv map to send information to
   :type targetMap: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


