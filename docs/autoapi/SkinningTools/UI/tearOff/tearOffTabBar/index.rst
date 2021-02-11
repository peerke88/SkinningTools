:mod:`SkinningTools.UI.tearOff.tearOffTabBar`
=============================================

.. py:module:: SkinningTools.UI.tearOff.tearOffTabBar


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tearOff.tearOffTabBar.TearoffTabBar



.. py:class:: TearoffTabBar(parent=None)



   tab bar for the QTabwidget that allows the widget to be removed from the tab and parent to a new window
       

   .. attribute:: tearOff
      

      

   .. method:: enterEvent(self, event)

      use the correct keyboard focus when the arrow is in the tab
              


   .. method:: event(self, event)

      make sure that the tear off event is triggered when all conditions are met
              


   .. method:: keyPressEvent(self, event)

      make sure the correct arrow cursor is present when inside the headerview
              


   .. method:: keyReleaseEvent(self, event)

      make sure the correct arrow cursor is present when inside the headerview
              


   .. method:: leaveEvent(self, event)

      use the correct keyboard focus when the arrow is in the tab
              


   .. method:: mouseMoveEvent(self, event)

      make sure the image of the hand is still conveiying the correct action
              


   .. method:: mousePressEvent(self, event)

      the mouse press event that checks if the conditions are met to detach the window
      it will change the control cursors image to display the action


   .. method:: setWest(self)

      set the orientation of the tab widgets header
              


   .. method:: tabSizeHint(self, index=0)

      get the size hint of the current tab
      this way we can make sure that when we detach the widget we have a correct size to work with

      :param index: index if the tab
      :type index: int
      :return: the size of the widget
      :rtype: Qsize



