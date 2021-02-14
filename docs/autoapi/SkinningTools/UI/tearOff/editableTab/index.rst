:mod:`SkinningTools.UI.tearOff.editableTab`
===========================================

.. py:module:: SkinningTools.UI.tearOff.editableTab


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tearOff.editableTab.TabWidget



.. py:class:: TabWidget(parent=None)



   the tab widget that allows the user to unparent tabs in seperate dialogs
       

   .. attribute:: tabAdded
      

      

   .. attribute:: tearOff
      

      

   .. method:: addGraphicsTab(self, text='NewTAB', changeCurrent=True, useIcon=None)

      add a new tab with the correcet name and items attached

      :param text: the title used in the tab
      :type text: string
      :param changeCurrent: if `True` will override the current index, if `False` will append the tab
      :type changeCurrent: bool
      :param useIcon: if given will use an icon to display when the object is torn off
      :type useIcon: string
      :return: the widget that can be thrown around
      :rtype: QWidget


   .. method:: addView(self, text, index, inWidget)

      add the new widget to the tab

      :param text: the title used in the tab
      :type text: string
      :param index: the index onto which the view should be added
      :type index: int
      :param inWidget: the widget to attach
      :type inWidget: QWidget


   .. method:: clear(self)

      make sure that the entire widget is cleared
              


   .. method:: setCustomTabBar(self)

      set the custom tab bar that has correct orientations and tear off signals
              


   .. method:: viewAtIndex(self, index)

      get the widget attached at current index

      :return: the current tabs widget
      :rtype: QWidget



