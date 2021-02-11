:mod:`SkinningTools.UI.weightEditor.vertHeaderView`
===================================================

.. py:module:: SkinningTools.UI.weightEditor.vertHeaderView


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.weightEditor.vertHeaderView.VertHeaderView



.. py:class:: VertHeaderView(parent=None)



   header view that displays text in a vertical manner
       

   .. attribute:: _font
      

      

   .. attribute:: _margin
      :annotation: = 3

      

   .. attribute:: _metrics
      

      

   .. attribute:: _selectedFont
      

      

   .. attribute:: rightClicked
      

      

   .. method:: _getData(self, index)

      get the current data of the header view

      :param index: the index of the header
      :type index: int
      :return: the header data of the model
      :rtype: QVariant


   .. method:: _getWidth(self)

      get the width of the current headerview

      :return: the total width of all the headers
      :rtype: float


   .. method:: checkSelected(self, index)

      check if the current object is selected

      :param index: the index of the header
      :type index: int
      :return: if the current header is selected
      :rtype: bool


   .. method:: mouseReleaseEvent(self, event)

      mouse event to emit when mouse is right clicked
              


   .. method:: paintSection(self, painter, rect, index)

      painter that will set the text in the correct scale and oriented vertically

      :param painter: painter class to override to make sure everything is drawn correctly
      :type painter: QPainter
      :param rect: the size of the current header
      :type rect: Qrect
      :param index: the index of the header that needs to be drawn
      :type index: int 


   .. method:: rotate(self, index, rect)

      convenience function to rotate the current header from horizontal to vertical

      :param index: index of the header to change
      :type index: int
      :param rect: the horizontally placed rect
      :type rect: QRect
      :return: the vertically placed rect
      :rtype: QRect


   .. method:: sizeHint(self)

      returns the size hint 

      :return: the size hint of the current headerview
      :rtype: QSize



