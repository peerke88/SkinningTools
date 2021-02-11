:mod:`SkinEditPlugin`
=====================

.. py:module:: SkinEditPlugin


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinEditPlugin.SkinEditClass



Functions
~~~~~~~~~

.. autoapisummary::

   SkinEditPlugin.cmdCreator
   SkinEditPlugin.initializePlugin
   SkinEditPlugin.maya_useNewAPI
   SkinEditPlugin.syntaxCreator
   SkinEditPlugin.uninitializePlugin


.. data:: kPluginCmdName
   :annotation: = SkinEditor

   

.. py:class:: SkinEditClass



   .. method:: doIt(self, args)


   .. method:: getDagpath(self, node, extendToShape=False)


   .. method:: getMfnSkinCluster(self, mDag)


   .. method:: isUndoable(self)


   .. method:: parseArguments(self, args)


   .. method:: redoIt(self)


   .. method:: setWeight(self, inWeights)


   .. method:: undoIt(self)



.. function:: cmdCreator()


.. function:: initializePlugin(mobject)


.. function:: maya_useNewAPI()


.. function:: syntaxCreator()


.. function:: uninitializePlugin(mobject)


