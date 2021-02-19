:mod:`averageWeightPlugin`
==========================

.. py:module:: averageWeightPlugin


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   averageWeightPlugin.AverageWghtCtx
   averageWeightPlugin.AverageWghtCtxInitialize
   averageWeightPlugin.AverageWghtCtxUpdate



Functions
~~~~~~~~~

.. autoapisummary::

   averageWeightPlugin.creatorInit
   averageWeightPlugin.creatorUpdate
   averageWeightPlugin.initialize
   averageWeightPlugin.initializePlugin
   averageWeightPlugin.maya_useNewAPI
   averageWeightPlugin.syntaxUpdate
   averageWeightPlugin.uninitializePlugin


.. data:: CONTEXT_INIT
   :annotation: = paintAverageWghtCtxInitialize

   

.. data:: CONTEXT_UPDATE
   :annotation: = paintAverageWghtCtxUpdate

   

.. data:: kCreator
   :annotation: = Trevor van Hoof & Perry Leijten

   

.. data:: kVersion
   :annotation: = 1.0.20200831

   

.. data:: smoothWeights
   

   

.. py:class:: AverageWghtCtx



   .. method:: calcWeights(self, value, origWeights, nbWeigths, influences, amountComps)


   .. method:: initialize(self, obj)


   .. method:: reset(self)


   .. method:: setWeights(self, index, value)



.. py:class:: AverageWghtCtxInitialize



   .. method:: doIt(self, args)



.. py:class:: AverageWghtCtxUpdate



   .. method:: doIt(self, args)


   .. method:: isUndoable(self)


   .. method:: redoIt(self)


   .. method:: undoIt(self)



.. function:: creatorInit()


.. function:: creatorUpdate()


.. function:: initialize()


.. function:: initializePlugin(mObject)


.. function:: maya_useNewAPI()


.. function:: syntaxUpdate()


.. function:: uninitializePlugin(mObject)


