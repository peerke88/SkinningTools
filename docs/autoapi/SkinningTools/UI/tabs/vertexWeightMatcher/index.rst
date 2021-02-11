:mod:`SkinningTools.UI.tabs.vertexWeightMatcher`
================================================

.. py:module:: SkinningTools.UI.tabs.vertexWeightMatcher


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.vertexWeightMatcher.AssignWeightsWidget
   SkinningTools.UI.tabs.vertexWeightMatcher.ClosestVertexWeightWidget
   SkinningTools.UI.tabs.vertexWeightMatcher.TransferUvsWidget
   SkinningTools.UI.tabs.vertexWeightMatcher.TransferWeightsWidget



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.vertexWeightMatcher.testUI


.. py:class:: AssignWeightsWidget(parent=None, progressBar=None)



   .. attribute:: toolName
      :annotation: = AssignWeightsWidget

      #@note: untested!

      idea:

      add all joints in a list + a select button next to it
      all buttons are gray from the start

      once the button next to the joint is selected it will store vertex selection into the button and make it green (selection can be soft selection)
      maybe add a second button to analize the current vertices already inluenced by that given joint (turn buttons red?)

      make sure all weights are normalized in the end
      if the joints are not pre-analized we do an add influence command
      otherwise we do a full override(maybe with apiweights functions)


   .. method:: _JointSoftGroup(self, joint)


   .. method:: __defaults(self)


   .. method:: __setButtons(self)


   .. method:: _addData(self, joint)


   .. method:: _cleardData(self, joint)


   .. method:: _viewData(self, joint)


   .. method:: addBone(self)


   .. method:: addBones(self)


   .. method:: build(self)


   .. method:: clearUI(self)


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
              


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: searchJointName(self)


   .. method:: translate(self, localeDict={})



.. py:class:: ClosestVertexWeightWidget(parent=None)



   .. attribute:: toolName
      :annotation: = ClosestVertexWeightWidget

      

   .. method:: __checkEnabled(self)


   .. method:: __defaults(self)


   .. method:: __setButtons(self)


   .. method:: __setValue(self, inLineEdit)


   .. method:: __storeVerts(self, inputVerts)


   .. method:: _transferComp(self)


   .. method:: addLoadingBar(self, loadingBar)


   .. method:: clearUI(self)


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
              


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: translate(self, localeDict={})



.. py:class:: TransferUvsWidget(parent=None)



   .. attribute:: toolName
      :annotation: = TransferUvsWidget

      

   .. method:: __checkEnabled(self)


   .. method:: __defaults(self)


   .. method:: __setButtons(self)


   .. method:: __setValue(self, inLineEdit, inCombo)


   .. method:: _transferUV(self)


   .. method:: addLoadingBar(self, loadingBar)


   .. method:: clearUI(self)


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
              


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: translate(self, localeDict={})



.. py:class:: TransferWeightsWidget(parent=None)



   .. attribute:: toolName
      :annotation: = TransferWeightsWidget

      

   .. method:: __addItem(self, name, pyData)


   .. method:: __applySelectionCB(self)


   .. method:: __clearSelectionCB(self)


   .. method:: __copySkinDataCB(self)


   .. method:: __defaults(self)


   .. method:: __deleteItemCB(self, item)


   .. method:: __grabSkinCl(self, toSet=None)


   .. method:: __restoreSettings(self)


   .. method:: __skinClusterFunc(self)


   .. method:: __storeSelectionCB(self)


   .. method:: __vertexFunc(self)


   .. method:: addLoadingBar(self, loadingBar)


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
              


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: translate(self, localeDict={})



.. function:: testUI(widgetIndex=0)

   test the current UI without the need of all the extra functionality
       


