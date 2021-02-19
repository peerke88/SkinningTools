:mod:`SkinningTools.Maya.tools.joints`
======================================

.. py:module:: SkinningTools.Maya.tools.joints


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.joints.BoneMove
   SkinningTools.Maya.tools.joints.BoneSwitch
   SkinningTools.Maya.tools.joints.ShowInfluencedVerts
   SkinningTools.Maya.tools.joints.addCleanJoint
   SkinningTools.Maya.tools.joints.autoLabelJoints
   SkinningTools.Maya.tools.joints.comparejointInfluences
   SkinningTools.Maya.tools.joints.convertClusterToJoint
   SkinningTools.Maya.tools.joints.convertVerticesToJoint
   SkinningTools.Maya.tools.joints.deleteJointSmart
   SkinningTools.Maya.tools.joints.drawStyle
   SkinningTools.Maya.tools.joints.freezeRotate
   SkinningTools.Maya.tools.joints.freezeScale
   SkinningTools.Maya.tools.joints.freezeSkinnedJoints
   SkinningTools.Maya.tools.joints.getInfluencingJoints
   SkinningTools.Maya.tools.joints.getMeshesInfluencedByJoint
   SkinningTools.Maya.tools.joints.jointLookat
   SkinningTools.Maya.tools.joints.localRotateAxis
   SkinningTools.Maya.tools.joints.mirrorJoints
   SkinningTools.Maya.tools.joints.removeBindPoses
   SkinningTools.Maya.tools.joints.removeJointBySkinPercent
   SkinningTools.Maya.tools.joints.removeJoints
   SkinningTools.Maya.tools.joints.removeUnusedInfluences
   SkinningTools.Maya.tools.joints.resetSkinnedJoints
   SkinningTools.Maya.tools.joints.resetToBindPoseobject
   SkinningTools.Maya.tools.joints.segmentScale
   SkinningTools.Maya.tools.joints.toggleMoveSkinnedJoints


.. function:: BoneMove(joint1, joint2, skin, progressBar=None)

   move joint influences from 1 joint to another

   :param joint1: joint to get the weight information from
   :type joint1: string
   :param joint2: joint to set the weigth information to
   :type joint2: string
   :param skin: the skincluster on which the weight information is based
   :type skin: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: BoneSwitch(joint1, joint2, skin, progressBar=None)

   switch the weight information of 2 given joints
   it reconnects the indices of the joints that are used on the given skincluster

   :param joint1: joint to switch the weight information from
   :type joint1: string
   :param joint2: joint to switch the weigth information from
   :type joint2: string
   :param skin: the skincluster on which the weight information is based
   :type skin: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: ShowInfluencedVerts(inMesh, jnts, progressBar=None)

   show the vertices that have any weight information from current given joints (weight information above 0.0)

   :param inMesh: mesh object that is influences by a skincluster and joints that are in the given selection
   :type inMesh: string
   :param jtns: joints that influence the current given mesh
   :type jtns: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: addCleanJoint(jnts, inMesh, progressBar=None)

   add a new joint to the skincluster

   :param jnts: list of joints that need to be added to the current skinCluster
   :type jnts: list
   :param rotate: name of the mesh the joint should be added to
   :type rotate: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: autoLabelJoints(inputLeft='L_*', inputRight='R_*', progressBar=None)

   joint labeling function

   :param inputLeft: search function that allocates which joints are part of the left side of the rig "*" used as a wildcard to replace part of the string
   :type inputLeft: string
   :param inputRight: search function that allocates which joints are part of the right side of the rig "*" used as a wildcard to replace part of the string
   :type inputRight: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: comparejointInfluences(skinObjects, query=False, progressBar=None)

   compare the list of influences between several skinned objects

   :param skinObjects: skinned objects to compary influence lists
   :type skinObjects: list
   :param query: it `True` return the joints that are not present in all of the given objects, if `False` will make sure that all joints are present in all given objects
   :type query: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed, list of joints in query mode, None if there are no joints to be found in query
   :rtype: bool, list


.. function:: convertClusterToJoint(inCluster, jointName=None, progressBar=None)

   convert cluster deformer to a joint using the same influences and pivot position

   :param inCluster: the cluster object that is deforming a mesh
   :type inCluster: string
   :param jointName: name to give the joint, if `None` will create a default name
   :type jointName: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return:  `True` if the function is completed
   :rtype: bool


.. function:: convertVerticesToJoint(inComponents, jointName=None, progressBar=None)

   convert (soft) selection to a joint based on center of selection

   :param inComponents: mesh component selection to assign to the joint
   :type inComponents: list
   :param jointName: name to give the joint, if `None` will create a default name
   :type jointName: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return:  `True` if the function is completed
   :rtype: bool


.. function:: deleteJointSmart(jointsToRemove, progressBar=None)

   delete joints from the current chain no matter where they are placed or how they are parented

   :param jointsToRemove: list of joints to remove from current skincluster
   :type jointsToRemove: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: drawStyle(inSelection, style=False, progressBar=None)


.. function:: freezeRotate(inJnts, progressBar=None)

   force clean joint rotations per joint

   :param inJnts: list of joints that need their rotations to be nulified (0,0,0)
   :type inJnts: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: list of joints that are cleaned
   :rtype: list


.. function:: freezeScale(inJnts, progressBar=None)

   force clean joint scales per joint

   :param inJnts: list of joints that need their scales to be set to uniform (1,1,1)
   :type inJnts: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: list of joints that are cleaned
   :rtype: list


.. function:: freezeSkinnedJoints(jnts, rotate=1, scale=1, progressBar=None)

   clean joint rotations and scales even if they are skinned

   :note: this will not work when joints are connected through ik-handle!
   :param jnts: list of joints that need their rotations and scales to be cleaned
   :type jnts: list
   :param rotate: if `True` will clean rotations, if `False` will skip them
   :type rotate: bool
   :param scale: if `True` will clean scales, if `False` will skip them
   :type scale: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: getInfluencingJoints(inObject)

   get all joints that are influencing the given mesh

   :param inObject: the object which is influenced by a skincluster
   :type inObject: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: list of all the joints that are currently driving the given mesh
   :rtype:  list


.. function:: getMeshesInfluencedByJoint(currentJoints, progressBar=None)

   get all meshes that are influenced by current selection of joints

   :param currentJoints: the joint to check if they are used in skinclusters 
   :type currentJoints: list
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: list of objects influences by the current selection of joints
   :rtype:  list


.. function:: jointLookat(point, pointAt, normal=None, space=enumerators.Space.Global, primaryAxis=enumerators.AxisEnumerator.PosAxisX, secondaryAxis=enumerators.AxisEnumerator.PosAxisY, progressBar=None)


.. function:: localRotateAxis(inSelection, showAxis=False, progressBar=None)


.. function:: mirrorJoints(inSelection, mirrorAxis='X', behaviour=True, searchReplace=('L_', 'R_'), progressBar=None)


.. function:: removeBindPoses(progressBar=None)

   remove bindpose nodes from the scene so the prebindmatrices in the skinclusters can do their work, this also makes it easier to add new joints to the skinclusters

   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: removeJointBySkinPercent(skinObject, jointsToRemove, sc, progressBar=None)

   remove joints influences by setting them to 0.0

   :param skinObject: the mesh object from which to remove influences
   :type skinObject: string
   :param jointsToRemove: list of joints to remove from current skincluster
   :type jointsToRemove: list
   :param sc: the skincluster attached to the mesh
   :type sc: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: removeJoints(skinObjects, jointsToRemove, useParent=True, delete=True, fast=False, progressBar=None)

   delete joints from the scene/ or just the skincluster in a way that it does not break the skinweigths
   will search for surogate joints to take over the weight information of the joint that is to be deleted

   :param skinObjects: objects from which the joint influences will be removed
   :type skinObjects: list
   :param jointsToRemove: list of joints to remove from current skincluster
   :type jointsToRemove: list
   :param useParent: it `True` will give the current joints information to its direct parent.
   :type useParent: bool
   :param delete: if `True` this will make sure that the joint is deleted in the end, if `False` only removes the weight information
   :type delete: bool
   :param fast: if `True` the fast option does not take into account other joints, it will just remove the weights of the given joint and normalize, if `False` it will look for better options
   :type fast: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: removeUnusedInfluences(inObject, progressBar=None)

   remove the joints that are attached to the skincluster but are not assigned any weights.

   :note: this will only remove the current connection with joints, check if we can remap the nodes index connections in weights, influenceColor, lockweights and matrix inputs

   :param inObject: the object which is influenced by a skincluster
   :type inObject: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return:  `True` if the function is completed
   :rtype: bool


.. function:: resetSkinnedJoints(inJoints=None, inSkinCluster=None, progressBar=None)

   force recalculate the prebindmatrices in the skinclsuter based on current joint positions

   :param inJoints: list of joints to recalculate
   :type inJoints: list
   :param inSkinCluster: the skincluster that will receive new prebind matrices
   :type inSkinCluster: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: resetToBindPoseobject(inObject, progressBar=None)

   set joints back into their bindpose using the prebind matrix of the skincluster, only works when joints are not connected (rigged)

   :param inObject: mesh object that has a skincluster attached
   :type inObject: string
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return: `True` if the function is completed
   :rtype: bool


.. function:: segmentScale(inSelectio, compensate=False, progressBar=None)


.. function:: toggleMoveSkinnedJoints(inMesh, inPose=False, progressBar=None)

   toggle joint bind position manipulation on or off
   :todo: visualise the mesh that is manipulated <- needs to come from mesh.toggleDisplayOrigShape
   :todo: make different objects positioned on the prebind position that manipulate the prebind matrices for the joints
   :param inMesh: mesh object manipulated through a skincluster
   :type inMesh: string
   :param inPose: if `True` will generate a skeleton to manipulate the bindpose, if `False` will use the skinned skeleton
   :type inPose: bool
   :param progressBar: progress bar instance to be used for progress display, if `None` it will print the progress instead
   :type progressBar: QProgressBar
   :return:  `True` if the function is completed
   :rtype: bool


