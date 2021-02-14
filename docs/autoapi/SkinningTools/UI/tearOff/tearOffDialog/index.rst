:mod:`SkinningTools.UI.tearOff.tearOffDialog`
=============================================

.. py:module:: SkinningTools.UI.tearOff.tearOffDialog


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tearOff.tearOffDialog.TearOffDialog



.. py:class:: TearOffDialog(tabName, parent=None)



   the dialog that holds tab that is torn off
       

   .. attribute:: closed
      

      

   .. attribute:: tabName
      

      

   .. method:: addwidget(self, inWidget)

      the widget to add to the current dialogs layout

      :param inWidget: the widget to use for extracted dialog
      :type inWidget: QWidget


   .. method:: closeEvent(self, event)

      management function to reset the current widgets position and parent when the dialog is closed
              


   .. method:: gettabName(self)

      get the current name of the tab

      :return: the original name of the tab
      :rtype: string


   .. method:: resize(self, *args)

      convenience function to resize the current dialog
              


   .. method:: setOriginalState(self, index, tabWidget)

      override for the original state of the tab
      sets the new widget and index

      :param index: the index on which the tab should be placed when the widget is closed
      :type index: int
      :param tabWidget: the new widget to use for the tabs
      :type tabWidget: QWidget


   .. method:: settabName(self, inTabName)

      set the new name for the tab

      :param inTabName: the new name for the tab
      :type inTabName: string



