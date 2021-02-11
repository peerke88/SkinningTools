:mod:`SkinningTools.UI.hoverIconButton`
=======================================

.. py:module:: SkinningTools.UI.hoverIconButton


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.hoverIconButton.HoverIconButton



.. py:class:: HoverIconButton(icon=QIcon(), hoverIcon=QIcon(), checked=None, orientation=0, parent=None)



   hover icon, custom tool button that can change if the mouse hovers over it or once clicked
       

   .. method:: _checkState(self)

      the state used when the icon is checked
      it will replace the current icon with the one used when its checked or not.


   .. method:: enterEvent(self, event)

      the mouse hover enter event

      :param event: the given event
      :type event: QEvent 


   .. method:: leaveEvent(self, event)

      the mouse hover leave event

      :param event: the given event
      :type event: QEvent 


   .. method:: setCustomIcon(self, pixmap, hover, checked=None, orientation=0)

      the function that sets the correct icons to the tool
      can be used to override the toolbutton with new icons

      :param pixmap: default icon
      :type pixmap: QIcon
      :param hover: icon used for when the mouse hovers over the button
      :type hover: QIcon
      :param checked: icon used for when the object is checked
      :type checked: QIcon
      :param orientation: orientation in degrees clockwise for the images on the control
      :type orientation: int


   .. method:: setDisabledPixmap(self, pixmap)

      the icon used for when the object is disabled

      :param pixmap: path to icon 
      :type pixmap: string/QPixmap



