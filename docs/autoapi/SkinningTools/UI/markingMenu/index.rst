:mod:`SkinningTools.UI.markingMenu`
===================================

.. py:module:: SkinningTools.UI.markingMenu


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.markingMenu.MarkingMenuFilter
   SkinningTools.UI.markingMenu.radialMenu
   SkinningTools.UI.markingMenu.testWidget



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.markingMenu.testUI


.. data:: _DEBUG
   

   

.. py:class:: MarkingMenuFilter(name='MarkingMenu', isDebug=False, parent=None)



   the marking menu filter
   this eventfilter will grab mouse inputs and when the conditions are met it will spawn a popup window at the mouse location

   .. attribute:: _singleton
      

      

   .. method:: eventFilter(self, obj, event)

      the event filter
      here we check if all conditions necessary for the widget to spawn are met


   .. staticmethod:: singleton()

      singleton method
      making sure that this object can only exist once and cannot be instantiated more then once



.. py:class:: radialMenu(parent=None, flags=Qt.FramelessWindowHint)



   marking menu popup window
   this window will spawn without frame or background
   we draw everything in this window with QGraphicsScene items
   the window should remove itself when the mouse button is released returning info on the object that is under the mouse

   :todo: make a connection with the main widget to override certain values in the setup

   .. attribute:: __borders
      

      

   .. attribute:: __geoSize
      :annotation: = 800

      

   .. attribute:: __radius
      :annotation: = 80

      

   .. attribute:: _availableSpaces
      :annotation: = 8

      

   .. attribute:: _green
      

      

   .. attribute:: _red
      

      

   .. attribute:: brush
      

      

   .. attribute:: pen
      

      

   .. attribute:: value
      

      

   .. method:: __MMButton(self, inText, position, inValue=None, inFunction=None, operation=1)

      single marking menu button

      :param inText: the text to display
      :type inText: string
      :param position: position on the circle
      :type position: QPos
      :param inValue: the value it will represent
      :type inValue: float
      :param inFunction: the function to run once triggered
      :type inFunction: <function>
      :param operation: the operation on how to treat the weight
      :type operation: int
      :note operation: { 0:removes the values, 1:sets the values, 2: adds the values}
      :return: the widget with all functionality
      :rtype: QLabel


   .. method:: __MMCheck(self, inText, position, inValue=True, inFunction=None)

      single marking menu checkbox 

      :param inText: the text to display
      :type inText: string
      :param position: position on the circle
      :type position: QPos
      :param inValue: the value it will represent
      :type inValue: float
      :param inFunction: the function to run once triggered
      :type inFunction: <function>
      :return: the widget with all functionality
      :rtype: QCheckBox


   .. method:: __drawUI(self)

      build the ui, 
      the main ui is a circle on which we can spawn the necessary buttons


   .. method:: __funcPressed(self, _, value, operation=0)

      function that will run when a button is clicked

      :param value: the value that will be set on the selection
      :type value: float
      :param operation: the operation on how to treat the weight
      :type operation: int
      :note operation: { 0:removes the values, 1:sets the values, 2: adds the values}


   .. method:: _buildButtons(self)

      build up the marking menu based on given bone and all elements necessary
              


   .. method:: _changeVal(self, item, value, operation=0)


   .. method:: _getValue(self)


   .. method:: _setCheckState(self, item, *_)

      function that will run once the checkbox state has changed
      in this case it will change soft selection settings 

      :param item: the checkbox
      :type item: QCheckbox


   .. method:: _setPen(self, color, width, style)

      override function to change the pen style of the widget

      :param color: the color to be used in drawing
      :type color: QColor
      :param width: widht of the pen stroke
      :type width: int
      :param style: style of the stroke (single line/ dash pattern)
      :type style: Qt.penStyle


   .. method:: _setValue(self, value)


   .. method:: getActiveItem(self)

      return the activated item that is in collision with the mouse

      :return: widget under mouse
      :rtype: QWidget


   .. staticmethod:: rotateVec(origin, point, angle)

      angular math to get the correct positions on a circle based on center, length and angle

      :param origin: center of the circle
      :type origin: QPos
      :param point: top point of the circle (12 o`clock)
      :type point: QPos
      :param angle: the angle at wich to rotate the point clockwise
      :type angle: QPos
      :return: position on the circle at the given angle
      :rtype: QPos


   .. method:: setName(self, inName)


   .. method:: showAtMousePos(self)

      show the current setup at the position on screen where the mouse is located, 
      the center of the circle is positioned directly on the mouse


   .. method:: updateLine(self, pos)

      a line from the center of the circle to the position of the mouse
      this to display which element will be chosen on mouse release
      the collision of the line with any of the buttons will show an outline on the object to highlite the selection

      :param pos: position of the mouse
      :type pos: QPos



.. py:class:: testWidget(parent=None)



   simple widget to install the eventfilter on to test the markingmenu
   this will not use the dcc application but a seperate window, where debug is forced so it will always draw the popup window


.. function:: testUI()

   convenience function to display and build the testing application
       


