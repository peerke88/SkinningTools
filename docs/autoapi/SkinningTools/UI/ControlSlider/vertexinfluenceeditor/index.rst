:mod:`SkinningTools.UI.ControlSlider.vertexinfluenceeditor`
===========================================================

.. py:module:: SkinningTools.UI.ControlSlider.vertexinfluenceeditor


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.ControlSlider.vertexinfluenceeditor.VertexInfluenceEditor



.. py:class:: VertexInfluenceEditor(skinCluster, vtxLName, skinBones, weights, parent=None)



   .. attribute:: lockIcon
      

      

   .. attribute:: unlockIcon
      

      

   .. method:: __lineEdit_FieldEditted(self, *_)


   .. method:: __toggleLock(self, index)


   .. method:: __updateWeights(self, setId, newValue)

      normalize all other weights so we can cleanly inject the new value

      calculate what weight will remain after injecting the new value
      then multiply all other weights by that value, so that all other weights added together = the remainder
      this works because the sum of all weights is first made to be 1.0, then we do (1.0 * 1.0 - newValue) where each 1.0 is actually the list of weights

      these steps are optimized to 'find the total value we should divide by to normalize'
      and 'multiply by the remainder and divide by the total value at the same time', so instead of 2 steps (normalize and multiply separately)
      we just multiply by a ratio of (1.0 - newValue) / initialRemainderTotal

      the target weight can be set either at the start or at the end because it's index is otherwise ignored


   .. method:: getCurrentBones(self)


   .. method:: hideZero(self, state)


   .. method:: showBones(self, inBones)



