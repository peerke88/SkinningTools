:mod:`SkinningTools.UI.advancedToolTip`
=======================================

.. py:module:: SkinningTools.UI.advancedToolTip


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.advancedToolTip.AdvancedToolTip



.. data:: TOOLTIPDIRECTORY
   

   

.. py:class:: AdvancedToolTip(rect, parent=None)



   advanced tooltip window
   allows the text of any language to be displayed together with a gif image to show what the current object could do for the user

   .. method:: leaveEvent(self, event)


   .. method:: setGifImage(self, gifName)

      set the gif to the current object and play automatically

      :param gifName: the path to the gif object
      :type gifName: string


   .. method:: setTip(self, inText)

      set the text for the tooltip

      :param inText: the tooltip text
      :type inText: string


   .. method:: toolTipExists(self, imageName)

      check if the image to display exists

      :return: True or False depending on if the image exists
      :rtype: bool



