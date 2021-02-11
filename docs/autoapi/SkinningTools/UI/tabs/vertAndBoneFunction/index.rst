:mod:`SkinningTools.UI.tabs.vertAndBoneFunction`
================================================

.. py:module:: SkinningTools.UI.tabs.vertAndBoneFunction


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.vertAndBoneFunction.VertAndBoneFunction



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.vertAndBoneFunction.testUI


.. data:: _DEBUG
   

   

.. data:: _DIR
   

   

.. py:class:: VertAndBoneFunction(inGraph=None, inProgressBar=None, parent=None)



   the widget that holds all custom single button / buttongroup functions for authoring in the dcc tools
       

   .. attribute:: checkValues
      

      

   .. attribute:: favSettings
      

      

   .. attribute:: toolName
      :annotation: = VertAndBoneFunction

      

   .. method:: _AvgWght_func(self, sender)

      average weight connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: __addVertNBoneFunc(self)

      here we will create and modify all the seperate buttons that work with the dcc tool
              


   .. method:: __favTools(self)

      favourite tools button, this button will allow the user to choose their favourite tools and display them
              


   .. method:: _bindFix_func(self, sender, *args)

      fix the bind map connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _clearLayout(self)

      make sure that the buttons are unparented but not destroyed
              


   .. method:: _connections(self)

      signal connections
              


   .. method:: _convertStyleSheet(self, inStyleSheet)

      stylesheet change for display if the object is being selected
              


   .. method:: _convertToJoint_func(self, sender)

      convert selection to joint connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _cutMesh_func(self, sender)

      cut mesh by influences connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _delBone_func(self, sender)

      delete bone connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _growsel_func(self, *args)

      grow the current selection
              


   .. method:: _nghbors_func(self, sender)

      neighbours smoothing connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _pruneOption(self, btn, value)


   .. method:: _pruneSel_func(self, sender)

      prune influences connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _setBtnLayout(self)

      populate the current widget with all objects
              


   .. method:: _setFavLayout(self)

      repopulate the current widget with only buttons that are assigned as favourite
              


   .. method:: _shrinks_func(self, *args)

      shrink the current selection
              


   .. method:: _smoothBrs_func(self, sender, *args)

      smooth brush connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _storesel_func(self, *args)

      store the current component selection and alter the connected buttons
              


   .. method:: _trsfrSK_func(self, sender, inPlace)

      transfer skin connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton
      :param inPlace: differentiates between skin and pose functionality
      :type inPlace: bool


   .. method:: _unifyBn_func(self, sender)

      unify influence map connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _updateBrush_func(self, sender, *args)

      update smooth brush connection function using the extra attributes

      :param sender: button object on which the checkbox is attached
      :type sender: QPushButton


   .. method:: _vtexMax_func(self, query)

      maximum influences per vertex connection function using the extra attributes

      :param query: if `True` will return the vertices, if `False` sets the max influences
      :type query: bool


   .. method:: active(self, *_)

      the settings to actively assign the favourite toolsets
              


   .. method:: changeLayout(self, *_)

      change layout function based on the state of the favourit settings
              


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: eventFilter(self, obj, event)

      event filter,
      this event filter listens to the mouse events on certain buttons to figure out if they can be chosen as favourite
      the event filter will display the current elements and groups as favourite when possible


   .. method:: filter(self, *_)

      install the eventfilter for assigning fouvourite settings
              


   .. method:: getButtonSetup(self, btn)

      convenience function to figure out which buttons are connected to the layout
      this will check for layouts

      :param btn: the widget with seperate attribute to check if its part of a group
      :type btn: QWidget
      :return: list of attached objects
      :rtype: list


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: getCheckValues(self)

      get the values fo all checkable attributes in the current tool

      :return: list of all checked values
      :rtype: list


   .. method:: getFavSettings(self)

      get the current settings on which elements are targeted as favourite

      :return: list of all elements that are set as favourite
      :rtype: list


   .. method:: getGroup(self, inBtn)

      convenience function to figure out which layouts the buttons are connected to

      :param btn: the widget with seperate attribute to check if its part of a group
      :type btn: QWidget
      :return: the layout the objects are attached to
      :rtype: QLayout


   .. method:: getGroupedLayout(self, inBtn)

      convenience function to figure out which buttons are connected to the layout

      :param btn: the widget with seperate attribute to check if its part of a group
      :type btn: QWidget
      :return: list of attached objects
      :rtype: list


   .. method:: setCheckValues(self, values)

      set the values of the buttons to be checked based on the given settings

      :param values: list of values from settings to set the checked state of button attributes
      :type values: list


   .. method:: setFavSettings(self, inSettings)

      set the favourite objects from given settings

      :param inSettings: list of elements that are set as favourite
      :type inSettings: list


   .. method:: showTools(self)

      switch function to show or hide elements
              


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


