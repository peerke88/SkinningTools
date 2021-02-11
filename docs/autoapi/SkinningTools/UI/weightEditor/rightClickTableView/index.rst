:mod:`SkinningTools.UI.weightEditor.rightClickTableView`
========================================================

.. py:module:: SkinningTools.UI.weightEditor.rightClickTableView


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.weightEditor.rightClickTableView.RightClickTableView



.. py:class:: RightClickTableView(parent=None)



   convenience setup on the table view to make sure right click connections are made
   emits signals once conditions are met

   .. attribute:: keyPressed
      

      

   .. attribute:: rightClicked
      

      

   .. method:: keyPressEvent(self, event)

      use the keypress event to make sure that keyboard inputs are caught and emitted
              


   .. method:: mousePressEvent(self, event)

      get the position on of the mouse once the mouse is pressed
              


   .. method:: mouseReleaseEvent(self, event)

      make sure that we only emit the signal if its the right mouse button
              



