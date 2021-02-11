:mod:`SkinningTools.UI.utils`
=============================

.. py:module:: SkinningTools.UI.utils


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.utils.LineEdit
   SkinningTools.UI.utils.SimplePopupSpinBox



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.utils.FalseFolderCharacters
   SkinningTools.UI.utils.FalseFolderCharactersJapanese
   SkinningTools.UI.utils.QuickDialog
   SkinningTools.UI.utils.addChecks
   SkinningTools.UI.utils.addContextToMenu
   SkinningTools.UI.utils.arrowButton
   SkinningTools.UI.utils.buttonsToAttach
   SkinningTools.UI.utils.checkStringForBadChars
   SkinningTools.UI.utils.clamp
   SkinningTools.UI.utils.compare_vec3
   SkinningTools.UI.utils.convertImageToString
   SkinningTools.UI.utils.convertStringToImage
   SkinningTools.UI.utils.findMissingItems
   SkinningTools.UI.utils.gDriveDownload
   SkinningTools.UI.utils.getClosestVector
   SkinningTools.UI.utils.getDebugState
   SkinningTools.UI.utils.getNumericName
   SkinningTools.UI.utils.incrementName
   SkinningTools.UI.utils.invLerp
   SkinningTools.UI.utils.lerp
   SkinningTools.UI.utils.loadLanguageFile
   SkinningTools.UI.utils.nullGridLayout
   SkinningTools.UI.utils.nullHBoxLayout
   SkinningTools.UI.utils.nullVBoxLayout
   SkinningTools.UI.utils.onContextMenu
   SkinningTools.UI.utils.pushButton
   SkinningTools.UI.utils.remap
   SkinningTools.UI.utils.remapClosestPoints
   SkinningTools.UI.utils.round_compare
   SkinningTools.UI.utils.saveResponseContent
   SkinningTools.UI.utils.setProgress
   SkinningTools.UI.utils.similarString
   SkinningTools.UI.utils.smart_round
   SkinningTools.UI.utils.smart_roundVec
   SkinningTools.UI.utils.storeLanguageFile
   SkinningTools.UI.utils.svgButton
   SkinningTools.UI.utils.toolButton
   SkinningTools.UI.utils.vLerp
   SkinningTools.UI.utils.veclength
   SkinningTools.UI.utils.widgetsAt


.. data:: UIDIRECTORY
   

   

.. py:class:: LineEdit



   override the focus steal on the lineedit

   .. method:: keyPressEvent(self, event)



.. py:class:: SimplePopupSpinBox(parent=None, value=0.5)



   spinbox delegate that is able to display as its own window
       

   .. attribute:: closed
      

      

   .. method:: closeEvent(self, e)



.. function:: FalseFolderCharacters(inString)

   checking a string for characters that are not allowed in folder structures

   :param inString: the string to check
   :type inString: string
   :return: if the string has bad characters
   :rtype: bool


.. function:: FalseFolderCharactersJapanese(self, inString)

   checking a string for characters that are not allowed in folder structures

   :param inString: the string to check
   :type inString: string
   :return: if the string has bad characters
   :rtype: bool


.. function:: QuickDialog(title)

   convenience Quick dialog for simple accept and reject functions

   :param title: title for the dialog
   :type title: string
   :return: the window to be created
   :rtype: QDialog


.. function:: addChecks(cls, button, checks=None)

   add checkboxes to a button for extra functionality

   :param cls: parent class
   :type cls: <class>
   :param button: the button to add the checkboxes to
   :type button: QPushButton
   :param checks: names of all the checkboxes to add
   :type checks: list


.. function:: addContextToMenu(cls, actionNames, btn)

   add context menu to button based on the checkboxes

   :param cls: parent class
   :type cls: <class>
   :param actionNames: names of all the checkboxes
   :type actionNames: list
   :param button: the button to add context menu to
   :type button: QPushButton
   :return: functions dictionary, Qmenu
   :rtype: list


.. function:: arrowButton(arrowType, sizePolicy)

   toolbutton function with arrows

   :param arrowType: Arrow, arrow type to add to the button
   :type arrowType: Qt.Arrow
   :param sizePolicy: list of sizepolicy information for width and height
   :type sizePolicy: QSizePolicy
   :return: the button  
   :rtype: QToolButton


.. function:: buttonsToAttach(name, command, *_)

   convenience function to attach signal command to qpushbutton on creation

   :param name: text to add to the button
   :type name: string
   :param command: python command to attach to the current button on clicked signal
   :type command: <function>
   :return: the button  
   :rtype: QPushButton


.. function:: checkStringForBadChars(self, inText, button, option=1, *args)

   checking a string for characters that are not allowed in folder structures

   :param inText: the text to check
   :type inText: string
   :param option: the type of structure to check for
   :type option: int

   :return: if the string has bad characters
   :rtype: bool


.. function:: clamp(val, minVal=0.0, maxVal=1.0)

   clamp value between min and max

   :param val: value to clamp
   :type val: float 
   :param minVal: minimum value 
   :type minVal: float
   :param maxVal: maximum value
   :type maxVal: float
   :return: the clamped value
   :rtype: float


.. function:: compare_vec3(a, b, epsilon=1e-05)

   compare 2 vectors if they are close enough to eahother, rounding the values as we dont want precision to interfere

   :param a: the value to compare
   :type a: list
   :param b: the value to compare
   :type b: list
   :param epsilon: the precision allowance that the vectors can have between them
   :type epsilon: double
   :return: if the objects are the same or not
   :rtype: bool


.. function:: convertImageToString(inPath)

   convenience function to save an image as a string format so the image does not have to be placed with the file

   :param inPath: the path the the image
   :type inPath: string
   :return: encoded string and extension type
   :rtype: list


.. function:: convertStringToImage(inString)

   convenience function to restore an image from an encoded string

   :param inString: encoded string and extension type
   :type inString: list
   :return: the path the the image
   :rtype: string


.. function:: findMissingItems(inList)

   find the numbers in the list that are not identified

   :param inList: list of names to check
   :type inList: list
   :return: list of missing numbers
   :rtype: list


.. function:: gDriveDownload(urlinfo, destination, progressBar=None)

   google download functionality

   :param urlinfo: dict of  filenames and corresponding files to download 
   :type urlinfo: dict
   :param destination: the folder to place downloaded files
   :type destination: string
   :param progressBar: the progressbar to show how much is downloaded
   :type progressBar: QProgressbar


.. function:: getClosestVector(inList, currentPos, amountTosearch=1)

   get the closest position in the given list from current position

   :param inList: list of positions to choose from
   :type inList: list
   :param currentPos: the position to search from
   :type currentPos: vector
   :param amountToSearch: the amoutn of closest positions to return
   :type amountToSearch: int
   :return: list of closest positions
   :rtype: list


.. function:: getDebugState()

   convenience function to work with debug mode 
   this gets turned to False when packaged using the package creator

   :return: the debug state
   :rtype: boolean


.. function:: getNumericName(text, names)

   get unique identifiers for names that are created
   if the name already exists, add a number at the end to make it unique again

   :param text: the text to check for unique names
   :type text: string
   :param names: the names that already exist
   :type names: list
   :return: a unique name
   :rtype: string


.. function:: incrementName(name)

   simple version of adding new trailing number

   :param name: object to add trailing number to
   :type name: string
   :return: objects name with new trailing number
   :rtype: string


.. function:: invLerp(a, b, v)

   lerp the other way around, use the end product to get the weigth

   :param a: start value
   :type a: float 
   :param b: end value 
   :type b: float
   :param v: middle value
   :type v: float
   :return: the weight
   :rtype: float


.. function:: lerp(a, b, t)

   blend the value from start to end based on the weight

   :param a: start value
   :type a: float 
   :param b: end value 
   :type b: float
   :param t: the weight
   :type t: float
   :return: the value in between
   :rtype: float


.. function:: loadLanguageFile(language, widgetName)

   load the language file based on given inputs

   :param language: the language used in the dictionary
   :type language: string
   :param widgetName: name of the widget used to link the language file with
   :type widgetName: string
   :return: the translation dictionary
   :rtype: dict


.. function:: nullGridLayout(parent=None, size=0)

   convenience function for the QGridLayout

   :param parent: the possible parent for the layout
   :type parent: QWidget
   :param size: the size of the margins
   :type size: int
   :return: the layout
   :rtype: QGridLayout


.. function:: nullHBoxLayout(parent=None, size=0)

   convenience function for the QHBoxLayout

   :param parent: the possible parent for the layout
   :type parent: QWidget
   :param size: the size of the margins
   :type size: int
   :return: the layout
   :rtype: QHBoxLayout


.. function:: nullVBoxLayout(parent=None, size=0)

   convenience function for the QVBoxLayout

   :param parent: the possible parent for the layout
   :type parent: QWidget
   :param size: the size of the margins
   :type size: int
   :return: the layout
   :rtype: QVBoxLayout


.. function:: onContextMenu(buttonObj, popMenu, functions, point)

   popup the context menu when requested

   :param buttonObj: the button to add context menu to
   :type buttonObj: QPushButton
   :param popMenu: the menu to popup
   :type popMenu: QMenu
   :param functions: names of all the checkboxes
   :type functions: list
   :param point: position to spawn the menu on screen
   :type point: Qpos


.. function:: pushButton(text='')

   simple button command with correct stylesheet

   :param text: text to add to the button
   :type text: string
   :return: the button  
   :rtype: QPushButton


.. function:: remap(iMin, iMax, oMin, oMax, v)

   remap the value from 1 range to another range

   :param iMin: new min value
   :type iMin: float 
   :param iMax: new max value
   :type iMax: float
   :param oMin: old min value
   :type oMin: float
   :param oMax: old max value
   :type oMax: float
   :param v: value to remap
   :type v: float
   :return: remapped value
   :rtype: float


.. function:: remapClosestPoints(sourceList, targetList, amount)

   map given positions to the closest positions

   :param sourceList: list of positions to search from
   :type sourceList: 
   :param targetList: list of positions to choose from
   :type targetList: list
   :param amount: the amoutn of closest positions to return
   :type amount: int
   :return: closest positions, weight values
   :rtype: list


.. function:: round_compare(vA, vB, debug=False)

   compare 2 objects if they are close enough to eahother, rounding the values as we dont want precision to interfere

   :param vA: the value to compare
   :type vA: float/ double
   :param vB: the value to compare
   :type vB: float/ double
   :param debug: if `True` prints the info, if `False` just returns the value
   :type debug: bool
   :return: if the objects are the same or not
   :rtype: bool


.. function:: saveResponseContent(response, destination)

   save the chunks of data into a file

   :param response: the information gathered from the website
   :type response: <response>
   :param destination: the folder to place downloaded files
   :type destination: string


.. function:: setProgress(inValue, progressBar=None, inText='')

   convenience function to set the progress bar value even when a qProgressbar does not exist

   :param inValue: the current percentage of the progressbar
   :type inValue: int
   :param progressbar: the progressbar to update
   :type progressbar: QProgressBar
   :param inText: additional text to show with the progressbar
   :type inText: string


.. function:: similarString(inString, inList)

   check if there is an object that resembles the given string in the list

   :param inString: string to check for
   :type inString: string
   :param inList: list of strings to choose from
   :type inList: list
   :return: the string that resembles the input the most
   :rtype: string


.. function:: smart_round(value, ndigits)

   function to cap the decimals 

   :param value: the value to cap
   :type value: float/double
   :param ndigits: amount of decimals needed
   :type ndigits: int
   :return: rounded float
   :rtype: float


.. function:: smart_roundVec(inVector, nDigits)

   function to cap the decimals of a vector

   :param inVector: the value to cap
   :type inVector: list
   :param ndigits: amount of decimals needed
   :type ndigits: int
   :return: rounded vector
   :rtype: list


.. function:: storeLanguageFile(inDict, language, widgetName)

   store the language file based on given inputs

   :param inDict: the translation dictionary
   :type inDict: dict
   :param language: the language used in the dictionary
   :type language: string
   :param widgetName: name of the widget used to link the language file with
   :type widgetName: string


.. function:: svgButton(name='', pixmap='', size=None, toolTipInfo=None)

   toolbutton function with image from svg file

   :param name: text to add to the button
   :type name: string
   :param pixmap: location of the svg file
   :type pixmap: string
   :param size: height and width of image in pixels
   :type size: int
   :return: the button  
   :rtype: QPushButton


.. function:: toolButton(pixmap='', orientation=0, size=None)

   toolbutton function with image

   :param pixmap: location of the image
   :type pixmap: string
   :param orientation: rotation in degrees clockwise
   :type orientation: int
   :param size: height and width of image in pixels
   :type size: int
   :return: the button  
   :rtype: QToolButton


.. function:: vLerp(start, end, percent)

   blend the vector from start to end based on the weight

   :param start: start vector
   :type start: vector 
   :param end: end vector 
   :type end: vector
   :param percent: the weight
   :type percent: float
   :return: the vector in between
   :rtype: vector


.. function:: veclength(inVec)

   get the length of a vector

   :param inVec: the vector to get the length of
   :type inVec: list 
   :return: length of a vector
   :rtype: float


.. function:: widgetsAt(pos)

   Qt convenience function to get the widget at given screen position

   :param pos: the position on screen
   :type pos: QPos 
   :return: widget on the position given
   :rtype: QWidget


