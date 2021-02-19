:mod:`SkinningTools.UI.tabs.softSelectUI`
=========================================

.. py:module:: SkinningTools.UI.tabs.softSelectUI


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.softSelectUI.AddInfluenceWidget
   SkinningTools.UI.tabs.softSelectUI.FillerInfluenceWidget
   SkinningTools.UI.tabs.softSelectUI.InfluenceWidget
   SkinningTools.UI.tabs.softSelectUI.SoftSelectionToWeightsWidget



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.softSelectUI.testUI


.. py:class:: AddInfluenceWidget(parent)



   Widget used to add influences. Will emit the 'addInfluence' signal when
   the add button is released.

   :param parent: the object to attach this ui to 
   :type parent: QWidget

   .. attribute:: addInfluence
      

      


.. py:class:: FillerInfluenceWidget(parent)



   Widget used to set the filler influence. 

   :param parent: the object to attach this ui to 
   :type parent: QWidget

   .. attribute:: influence
      

      

   .. method:: _getInfluence(self)


   .. method:: _setInfluence(self, influence)


   .. method:: contextMenuEvent(self, event)


   .. method:: setInfluenceFromSelection(self)

      Get all of the joints in the current selection. If no joints are 
      selected a RuntimeError will be raised and the UI reset.

      :raises RuntimeError: if no joints are selected



.. py:class:: InfluenceWidget(parent=None)



   Widget used to set the influence and soft selection. Once a new soft 
   selection is made the 'setSoftSelection' signal will be emitted.

   :param parent: the object to attach this ui to 
   :type parent: QWidget

   .. attribute:: influence
      

      

   .. attribute:: setSoftSelection
      

      

   .. attribute:: ssActive
      

      

   .. attribute:: ssData
      

      

   .. attribute:: ssSettings
      

      

   .. method:: _SetSsActive(self, value)


   .. method:: _SetSsData(self, value)


   .. method:: _getInfluence(self)


   .. method:: _getSsActive(self)


   .. method:: _getSsData(self)


   .. method:: _getSsSettings(self)


   .. method:: _setInfluence(self, influence)


   .. method:: _setSsSettings(self, value)


   .. method:: contextMenuEvent(self, event)


   .. method:: selectSoftSelection(self)

      Set the stored soft selection.
              


   .. method:: setInfluenceFromSelection(self)

      Get all of the joints in the current selection. If no joints are 
      selected a RuntimeError will be raised and the UI reset.

      :raises RuntimeError: if no joints are selected


   .. method:: setSoftSelectionFromSelection(self)

      Get the current soft selection. If no soft selection is made a 
      RuntimeError will be raised.

      :raises RuntimeError: if no soft selection is made



.. py:class:: SoftSelectionToWeightsWidget(progressBar=None, parent=None)



   Widget used to manage all of the added influences and their soft selection.

   :param parent: the object to attach this ui to
   :type parent: QWidget

   .. attribute:: toolName
      :annotation: = AssignWeightsWidget

      

   .. method:: addInfluence(self)

      Add an new influence widget to the layout, :class:`InfluenceWidget`.
              


   .. method:: addLoadingBar(self, loadingBar)


   .. method:: getInfluences(self)

      Loop over all of the content of the scroll layout and yield if the
      item is an instance of :class:`InfluenceWidget`.

      :return: All influence widgets in the scroll layout
      :rtype: iterator


   .. method:: setEnableInfluence(self)

      This function is called when a soft selection is made. All influences 
      will be checked to see if there is a mesh with no skin cluster 
      attached. If this is the case the filler joint widget 
      :class:`FillerInfluenceWidget` will be enabled.


   .. method:: skin(self)

      This function is called when the skin button is released. All of the
      influences sorted and the mesh skin weights updated. As this can be 
      a time consuming process a progress bar will be updated with every 
      mesh that gets updated.



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


