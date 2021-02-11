:mod:`SkinningTools.UI.tabs.skinBrushes`
========================================

.. py:module:: SkinningTools.UI.tabs.skinBrushes


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.skinBrushes.BrushMode
   SkinningTools.UI.tabs.skinBrushes.SkinBrushes



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.skinBrushes.buildSmoothBrushCommand
   SkinningTools.UI.tabs.skinBrushes.getSelectedSKinCLuster
   SkinningTools.UI.tabs.skinBrushes.pathToSmoothBrushPlugin
   SkinningTools.UI.tabs.skinBrushes.rodPaintSmoothBrush
   SkinningTools.UI.tabs.skinBrushes.updateBrushCommand


.. data:: _CTX
   :annotation: = artUserPaintContext

   

.. data:: _DEBUG
   

   

.. data:: _DIR
   

   

.. data:: dec_loadSmoothBrush
   

   

.. py:class:: BrushMode

   .. attribute:: RELAX
      :annotation: = 1

      

   .. attribute:: SMOOTH
      :annotation: = 0

      

   .. attribute:: UNDEF
      :annotation: = 2

      


.. py:class:: SkinBrushes(parent=None)



   .. method:: __addBrushFunc(self)


   .. method:: changeBrushType(self)


   .. method:: getBrushMode(self)


   .. method:: getRadius(self)


   .. method:: radiusValueChanged(self, value)


   .. method:: toggleBindPoseButton(self)


   .. method:: toggleBrushButton(self)


   .. method:: updateBrush(self)



.. function:: buildSmoothBrushCommand(context, skinClusterName, radiusExtraLinks, brushMode)


.. function:: getSelectedSKinCLuster()


.. function:: pathToSmoothBrushPlugin()


.. function:: rodPaintSmoothBrush(radiusExtraLinks=0.0, brushMode=BrushMode.SMOOTH)


.. function:: updateBrushCommand(context, skinCluster, radiusExtraLinks, brushMode)


