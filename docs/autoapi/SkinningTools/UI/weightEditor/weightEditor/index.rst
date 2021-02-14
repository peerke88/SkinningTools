:mod:`SkinningTools.UI.weightEditor.weightEditor`
=================================================

.. py:module:: SkinningTools.UI.weightEditor.weightEditor


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.weightEditor.weightEditor.WeightEditorWindow



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.weightEditor.weightEditor.testUI


.. py:class:: WeightEditorWindow(parent=None)



   weight editor widget, 
   allows for skincluster visualisation based on the vertex selection and the joints in the skincluster

   .. attribute:: toolName
      :annotation: = WeightEditorWindow

      

   .. method:: __defaults(self)

      conveninece function to gather all the default values to be used
              


   .. method:: _uiSetup(self)

      convenience function to gather all buttons for the current UI
              


   .. method:: cellChanged(self, *args)

      cell changed signal, makes sure that the selected indices are returned and the contexts are cleared
              


   .. method:: cleanupTable(self)

      cleanup table data, forced garbage collection as this tool deals with a lot of data
              


   .. method:: clearCallback(self)

      remove selection based callback
              


   .. method:: clearCopyPaste(self)

      clear the copy paste data
              


   .. method:: closeEvent(self, event)

      close event override
              


   .. method:: copyCells(self)

      copy cell information 
              


   .. method:: copyMenu(self)

      simple popup menu with copy functions
              


   .. method:: createCallback(self)

      create callback to refresh the current table based on selection in dcc tool
              


   .. method:: directInput(self, string)

      set up popup box based on given string

      :param string: string object representing the number
      :type string: string


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: evalHeaderWidth(self, add=3)

      in here we change the size of the header based on the format of the font and amount of bones

      :param add: buffer pixels to extend the size with
      :type add: int


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: getCellValue(self)

      get and set the new cell value based on the self.inputValue from the popupbox
              


   .. method:: getClickedItemVal(self)

      get the current value of the selected cells
              


   .. method:: getIgnoreList(self, row, column, rowLen, colLen)

      get the list of items to be ignored

      :param row: the index of the row
      :type row: int
      :param column: the index of the column
      :type column: int
      :param rowLen: amoutn of rows
      :type rowLen: int
      :param colLen: amount of columns
      :type colLen: int
      :return: list of itmems to ignore
      :rtype: list


   .. method:: getRows(self)

      get the rows of selected cells

      :return: list of selected rows
      :rtype: list


   .. method:: getSkinWeights(self)

      get skinweights function,
      this is where we grab all the information from the dcc tool to populate the table
      based on either object or component selection we make sure to grab all joints and weights associated
      the selections will be listed as vertex components and will be split according to the object where they came from


   .. method:: lockJointWeight(self, jointID)

      based on joint id given we lock the joint weights so they cannot change,
      this will be represented in the table widget as well by darkening the cells

      :param jointID: the index of the joint to be locked
      :type jointID: int


   .. method:: lockWeigths(self, jointID=None, lock=True)

      function to lock or unlock weights, this will be represented in the widget as well as in the dcc tool

      :param jointID: the index of the joint to be locked
      :type jointID: int
      :param lock: if `True` will lock the weight so it cannot be changed, if `False` will unlock the weight
      :type lock: bool


   .. method:: pasteCells(self)

      paste cell information
              


   .. method:: refreshTable(self)

      force redraw the current table view
              


   .. method:: searchJointName(self)

      based on the given text we only display columns that are represted by a partial identification of the given string in the search lineedit
              


   .. method:: selectFromHeader(self)

      select the current joint we work with from the current header (based on right-click)

      :todo: needs to change when other dcc then maya will be used


   .. method:: setClose(self)

      close and cleanup the weights table
              


   .. method:: setLockedData(self, ids, inValue)

      make sure that the weights are also locked in the dcc tool


      :param ids: the list of indeces of the joints to be locked
      :type ids: list
      :param inValue: if `True` will lock the weight so it cannot be changed, if `False` will unlock the weight
      :type inValue: bool


   .. method:: setPopupValue(self, textValue=True)

      set the value for the popup menu based on the current cells

      :note: maybe make this smarter so it just checks what the input is and base it on that instead of using an arg
      :param textValue: if `True` will convert the information from string to float, if `False` expects the information to be float already 
      :type textValue: bool


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict


   .. method:: tryNormalizeWeights(self)

      force normalize the weights of the current vertex row
      making sure that all elements are adding up to a maximum of 1
      trys to make sure that the maximum influences are kept unless more cells are altered at the same time
      htis is used as the set weights function as we dont want weights that are not normalized


   .. method:: vtxPaste(self)

      paste the gathered date onto newly selected vertices
              


   .. method:: vxtCopy(self)

      copy the date of selected vertices
              



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


