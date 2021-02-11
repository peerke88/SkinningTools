:mod:`SkinningTools.Maya.tools.holdFetch`
=========================================

.. py:module:: SkinningTools.Maya.tools.holdFetch


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.holdFetch.cleanupFetch
   SkinningTools.Maya.tools.holdFetch.fetch
   SkinningTools.Maya.tools.holdFetch.hold
   SkinningTools.Maya.tools.holdFetch.removeSelectionFromAttrs
   SkinningTools.Maya.tools.holdFetch.saveSelectionToAttrs
   SkinningTools.Maya.tools.holdFetch.selectFromAttrs


.. function:: cleanupFetch(topLevelDagObjects, remainingTopDagNodes)

   clean the connections and objects fetched

   :param topLevelDagObjects: all objects that are part of the root of the scene before fetch
   :type topLevelDagObjects: list
   :param remainingTopDagNodes: all objects that are part of the root of the scene after fetch
   :type remainingTopDagNodes: list
   :return: newly added top level nodes
   :rtype: list


.. function:: fetch()

   fetch the holded objects
   this is an override function for the paste (ctrl+v) function
   it forces only clean connections to be pasted in the current scene without making a mess out of it

   :return: created nodes
   :rtype: list


.. function:: hold(Force=False)

   hold the current selected objects
   this is an override function for the copy (ctrl+c) function
   it forces only clean connections to be copied and stored somewhere else so when pasted the scene isn't a mess

   :param Force: if `True` forces the export of selected object to take place ,if `False` it will not force the action (might break in some cases)
   :type Force: bool


.. function:: removeSelectionFromAttrs(nodes)

   cleanup identifying attributes to the objects about to be stored

   :param nodes: the nodes that are imported into the new scene will have their attribute removed
   :type nodes: list


.. function:: saveSelectionToAttrs()

   add identifying attributes to the objects about to be stored

   :return: the current selection we want to hold
   :rtype: list


.. function:: selectFromAttrs(topNodes)

   based on top nodes imported we are going to check what is added to the scene

   :param topNodes: the topnodes that are imported into the new scene
   :type topNodes: list
   :return: all new added nodes
   :rtype: list


