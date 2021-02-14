:mod:`SkinningTools.Maya.interface`
===================================

.. py:module:: SkinningTools.Maya.interface


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.interface.NeighborSelection
   SkinningTools.Maya.interface.skinWeight
   SkinningTools.Maya.interface.vertexWeight



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.interface.addNewJoint
   SkinningTools.Maya.interface.avgVtx
   SkinningTools.Maya.interface.convertToJoint
   SkinningTools.Maya.interface.copySkin
   SkinningTools.Maya.interface.copySkinWeightsOptions
   SkinningTools.Maya.interface.copyVtx
   SkinningTools.Maya.interface.createPolySkeleton
   SkinningTools.Maya.interface.cutMesh
   SkinningTools.Maya.interface.dccToolButtons
   SkinningTools.Maya.interface.deleteBindPoses
   SkinningTools.Maya.interface.doSelect
   SkinningTools.Maya.interface.fetch
   SkinningTools.Maya.interface.forceLoadPlugin
   SkinningTools.Maya.interface.freezeJoint
   SkinningTools.Maya.interface.getAllJoints
   SkinningTools.Maya.interface.getCurrentMeshJoints
   SkinningTools.Maya.interface.getInterfaceDir
   SkinningTools.Maya.interface.getLockData
   SkinningTools.Maya.interface.getMaxInfl
   SkinningTools.Maya.interface.getMayaVersion
   SkinningTools.Maya.interface.getMeshFromJoints
   SkinningTools.Maya.interface.getNeightbors
   SkinningTools.Maya.interface.getPluginSuffix
   SkinningTools.Maya.interface.getSelection
   SkinningTools.Maya.interface.getSmoothAware
   SkinningTools.Maya.interface.getUVInfo
   SkinningTools.Maya.interface.hammerVerts
   SkinningTools.Maya.interface.hold
   SkinningTools.Maya.interface.initBpBrush
   SkinningTools.Maya.interface.keepOnlyJoints
   SkinningTools.Maya.interface.labelJoints
   SkinningTools.Maya.interface.mirrorSkinOptions
   SkinningTools.Maya.interface.moveBones
   SkinningTools.Maya.interface.neighbors
   SkinningTools.Maya.interface.objectUnderMouse
   SkinningTools.Maya.interface.paintSmoothBrush
   SkinningTools.Maya.interface.pathToPlugin
   SkinningTools.Maya.interface.pinToSurface
   SkinningTools.Maya.interface.prebindFixer
   SkinningTools.Maya.interface.removeJoint
   SkinningTools.Maya.interface.removeUnused
   SkinningTools.Maya.interface.resetPose
   SkinningTools.Maya.interface.resetToBindPoseobject
   SkinningTools.Maya.interface.selectJoints
   SkinningTools.Maya.interface.seperateSkinned
   SkinningTools.Maya.interface.setJointLocked
   SkinningTools.Maya.interface.setMaxInfl
   SkinningTools.Maya.interface.setSmoothAware
   SkinningTools.Maya.interface.showInfVerts
   SkinningTools.Maya.interface.showToolTip
   SkinningTools.Maya.interface.skinnedJointColors
   SkinningTools.Maya.interface.smooth
   SkinningTools.Maya.interface.switchVtx
   SkinningTools.Maya.interface.transferUV
   SkinningTools.Maya.interface.unifyShells
   SkinningTools.Maya.interface.unifySkeletons
   SkinningTools.Maya.interface.uniteSkinned


.. py:class:: NeighborSelection



   The most base type

   .. method:: __borderSel(self, *_)


   .. method:: getBorderIndex(self)


   .. method:: grow(self, *_)


   .. method:: shrink(self, *_)


   .. method:: storeSel(self, *_)



.. py:class:: skinWeight(inProgressBar=None)



   The most base type

   .. method:: calcRemap(self, remapDict)


   .. method:: getSkinWeight(self)


   .. method:: needsRemap(self)


   .. method:: setSkinWeights(self)



.. py:class:: vertexWeight(inProgressBar=None)



   The most base type

   .. method:: getVtxWeight(self)


   .. method:: setVtxWeight(self)



.. function:: addNewJoint(progressBar=None)


.. function:: avgVtx(useDistance=True, weightAverageWindow=None, progressBar=None)


.. function:: convertToJoint(inName=None, progressBar=None)


.. function:: copySkin(inplace, smooth, uvSpace, progressBar=None)


.. function:: copySkinWeightsOptions()


.. function:: copyVtx(progressBar=None)


.. function:: createPolySkeleton(radius=1)


.. function:: cutMesh(internal, maya2020, progressBar=None)


.. function:: dccToolButtons(progressBar=None)


.. function:: deleteBindPoses(progressBar=None)


.. function:: doSelect(input, replace=True)


.. function:: fetch()


.. function:: forceLoadPlugin(inPlugin)


.. function:: freezeJoint(progressBar=None)


.. function:: getAllJoints()


.. function:: getCurrentMeshJoints()


.. function:: getInterfaceDir()


.. function:: getLockData(inObject)


.. function:: getMaxInfl(amountInfluences=8, progressBar=None)


.. function:: getMayaVersion()


.. function:: getMeshFromJoints(progressBar=None)


.. function:: getNeightbors(inComps)


.. function:: getPluginSuffix()


.. function:: getSelection()


.. function:: getSmoothAware()


.. function:: getUVInfo(inMesh)


.. function:: hammerVerts(progressBar=None)


.. function:: hold()


.. function:: initBpBrush()


.. function:: keepOnlyJoints(invert=False, progressBar=None)


.. function:: labelJoints(doCheck=True, progressBar=None)


.. function:: mirrorSkinOptions()


.. function:: moveBones(swap=False, progressBar=None)


.. function:: neighbors(both, growing, full, progressBar=None)


.. function:: objectUnderMouse(margin=4, selectionType='joint')


.. function:: paintSmoothBrush()


.. function:: pathToPlugin(pluginName)


.. function:: pinToSurface()


.. function:: prebindFixer(doModel, inPose, progressBar=None)


.. function:: removeJoint(useParent=True, delete=True, fast=False, progressBar=None)


.. function:: removeUnused(progressBar=None)


.. function:: resetPose(progressBar=None)


.. function:: resetToBindPoseobject(progressBar=None)


.. function:: selectJoints(progressBar=None)


.. function:: seperateSkinned(progressBar=None)


.. function:: setJointLocked(inJoint, inValue)


.. function:: setMaxInfl(amountInfluences=8, progressBar=None)


.. function:: setSmoothAware(input)


.. function:: showInfVerts(progressBar=None)


.. function:: showToolTip(inBool)


.. function:: skinnedJointColors()


.. function:: smooth(progressBar=None)


.. function:: switchVtx(progressBar=None)


.. function:: transferUV(source, target, sMap='map1', tMap='map1', progressBar=None)


.. function:: unifyShells(progressBar=None)


.. function:: unifySkeletons(query=False, progressBar=None)


.. function:: uniteSkinned()


