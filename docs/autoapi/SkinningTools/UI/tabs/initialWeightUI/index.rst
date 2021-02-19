:mod:`SkinningTools.UI.tabs.initialWeightUI`
============================================

.. py:module:: SkinningTools.UI.tabs.initialWeightUI


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.initialWeightUI.InitWeightUI



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.initialWeightUI.testUI


.. py:class:: InitWeightUI(inProgressBar=None, parent=None)



   the widget that holds all custom single button / buttongroup functions for authoring in the dcc tools
       

   .. attribute:: toolName
      :annotation: = InitWeightUI

      

   .. method:: __connections(self)


   .. method:: __toolsSetup(self)


   .. method:: _applySkin(self)


   .. method:: _changeSetup(self)


   .. method:: _selectJoint(self)


   .. method:: _selectMesh(self)


   .. method:: addLoadingBar(self, loadingBar)


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
              


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: translate(self, localeDict={})



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


