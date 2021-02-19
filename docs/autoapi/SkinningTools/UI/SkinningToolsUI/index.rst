:mod:`SkinningTools.UI.SkinningToolsUI`
=======================================

.. py:module:: SkinningTools.UI.SkinningToolsUI


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.SkinningToolsUI.SkinningToolsUI



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.SkinningToolsUI.showUI


.. data:: _DEBUG
   

   

.. data:: _DIR
   

   

.. data:: __VERSION__
   :annotation: = 5.0.20210219

   

.. py:class:: SkinningToolsUI(newPlacement=False, parent=None)



   main skinningtools UI class
       

   .. attribute:: toolName
      

      

   .. method:: __addBrushTools(self)

      simple brush tools that enable Rodolphes relax weight tools
      :note: only for debug as this has been converted into a single button


   .. method:: __addCopyRangeFunc(self)

      mutliple tools that require more inpute, mostly to remap certain elements in the scene
              


   .. method:: __addSimpleTools(self)

      this part of the ui will gather the information from dcc directly, 
      most of the settings attached to these buttons and windows are set to a default that would work wel in most cases


   .. method:: __addVertNBoneFunc(self)

      button layout gahtering lots of different tools that make editting weights 
              


   .. method:: __componentEditSetup(self)

      revamped component editor with a lot of extra functionalities, based on the Maya component editor but build from scratch to make it more powerfull
              


   .. method:: __connections(self)

      connection to a callback filter to make sure that the seperate marking menu is created
              


   .. method:: __defaults(self)

      some default local variables for the current UI    
              


   .. method:: __mayaToolsSetup(self)

      the main tab, this will hold all the dcc tool information
      all vertex and bone manipulating contexts will be placed here  

      :note: this needs to change when we move over to different dcc


   .. method:: __menuSetup(self)

      the menubar
      this will hold information on language, simple copy/paste(hold fetch) functionality and all the documentation/settings
      documentation will open specifically for the current open tab, next to that we also have a markingmenu button as this is available all the time


   .. method:: __skinSliderSetup(self)

      skinslider tab, the functionality of tweaking the weights on the selected components by changing the corresponding bone values
              


   .. method:: __tabsSetup(self)

      main tab widget which will hold all other widget information
              


   .. method:: __uiElements(self)

      several general UI elements that should be visible most of the times
      also loads the settings necessary for storing and retrieving information


   .. method:: __weightManagerSetup(self)

      weight manager function, save and load skinweights to seperate files
              


   .. method:: _callbackFilter(self, *args)

      callbacks for both the skinsliders and the component editor to update after the mouse has left the window and has returned
      this to make sure that the user is always working with the latest setup


   .. method:: _changeLanguage(self, lang=None)

      change the ui language

      :param lang: the shortname of the language to change the ui to
      :type lang: string


   .. method:: _displayToolTip(self)

      the tooltip function, allows the tooltip to spawn a seperate window above the current object
      the tooltip wil spawn based on a timer and will remove itself when the cursor moves away
      :note: tooltips are currently disabled as there are no images to show or text to display


   .. method:: _mouseTracking(self, event)

      the event at which to display the tooltip windows

      :param event: the event that is triggerd
      :type event: QEvent


   .. method:: _openApiHelp(self)

      open the web page with the help documentation and api information
              


   .. method:: _openDocHelp(self, isMarkingMenu=False)

      open the corresponding pdf page with the help documentation tool information
              


   .. method:: _tabName(self, index=-1, mainTool=None)

      get the name of the tab at given index

      :param index: the index at which to get the tab name
      :type index: int 
      :param mainTool: the parent object to request tabnames from
      :type maintool: Qwidget
      :return: name of the current tab
      :rtype: string


   .. method:: _tooltipsCheck(self)


   .. method:: childMouseMoveEvent(self, child, event)

      the overloaded function to track mouse movements on children

      :param child: the child object at which to set mouse tracking
      :type child: QWidget
      :param event: the event that is triggerd
      :type event: QEvent


   .. method:: closeEvent(self, event)

      the close event, 
      we save the state of the ui but we also force delete a lot of the skinningtool elements,
      normally python would do garbage collection for you, but to be sure that nothing is stored in memory that does not get deleted we 
      force the deletion here as well. somehow this avoids crashes in maya!


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: enterEvent(self, event)

      the event at which to reload both the skinsliders and the component editor

      :param event: the event that is triggerd
      :type event: QEvent
      :return: the output of the inherited functions
      :rtype: superclass


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: hideEvent(self, event)

      the hide event is something that is triggered at the same time as close,
      sometimes the close event is not handled correctly by maya so we add the save state in here to make sure its always triggered
      :note: its only storing info so it doesnt break anything


   .. method:: loadUIState(self)

      load the previous set information from the ini file where possible, if the ini file is not there it will start with default settings
              


   .. method:: mouseMoveEvent(self, event)

      the move event

      :param event: the event that is triggerd
      :type event: QEvent


   .. method:: recurseMouseTracking(self, parent, flag)

      convenience function to add mousetracking to all elements that are part of the current tool this way we can attach tooltips to everything

      :param parent: the parent object that can hold moustracking events and from which to search all possible children in the hierarchy
      :type parent: Qwidget
      :param flag: if `True` turns mouse tracking on, if `False` turns mousetracking off
      :type flag: bool


   .. method:: saveUIState(self)

      save the current state of the ui in a seperate ini file, this should also hold information later from a seperate settings window

      :todo: instead of only geometry also store torn of tabs for each posssible object
      :todo: save the geometries of torn of tabs as well


   .. method:: showEvent(self, event)


   .. method:: storeTearOffInfo(self, dialog)


   .. method:: tearOff(self, index, pos=QPoint())

      get the name of the tab at given index

      :param index: the index of the tab that needs to be torn off
      :type index: int 
      :param pos: the position at which to place the torn off tabe
      :type pos: Qwidget


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict



.. function:: showUI(newPlacement=False)

   convenience function to show the current user interface in maya,

   :param newPlacement: if `True` will force the tool to not read the ini file, if `False` will open the tool as intended
   :type newPlacement: bool


