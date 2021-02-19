:mod:`SkinningTools.Maya.tools.softSelectWeight`
================================================

.. py:module:: SkinningTools.Maya.tools.softSelectWeight


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.softSelectWeight.setSkinWeights


.. function:: setSkinWeights(inMesh, meshData, influences, filler=None, progressBar=None)

   Calculate and set the new skin weights. If no skin cluster is attached to
   the mesh, one will be created and all weights will be set to 1 with the 
   filler influence. If a skin cluster does exist, the current weights will
   be used to blend the new weights. Maintaining of maximum influences and 
   normalization of the weights will be taken into account if these 
   attributes are set on the skin cluster.

   :param inMesh:
   :type inMesh: str
   :param meshData: skinning data for the mesh
   :type meshData: dict
   :param influences: list of (new) influences
   :type influences: list
   :param filler: Filler joint if no skin cluster is detected
   :type filler: str


