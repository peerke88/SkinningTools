:mod:`SkinningTools.UI.translator`
==================================

.. py:module:: SkinningTools.UI.translator


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.translator.SearchableComboBox
   SkinningTools.UI.translator.TranslatorDialog



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.translator.showUI
   SkinningTools.UI.translator.testUI


.. py:class:: SearchableComboBox(parent=None)



   combobox that adds functionality to search for the object necessary out of the list of items
       

   .. method:: _sync(self)

      sync the current text with the text of give item at the index
              



.. py:class:: TranslatorDialog(inDict=None, defaultLanguage='japanese', widgetName=None, parent=None)



   simple dialog with google translate connections
   making sure that we can translate any given text to any language
   the items displayed will always have the english text to the left to compare

   .. method:: _createDict(self)

      create the dictionary using the information of the widget

      :return: the translated dictionary
      :rtype: dict


   .. method:: _doTranslate(self)

      seperate function to translate elements when the dialog is already build
              


   .. method:: _populateDialog(self)

      populate the dialog using the given dictionary and auto translate the necessary pieces of information
              


   .. method:: _recreateDialog(self)

      create the dialog with all the information of the given dictionary
              


   .. method:: getLangValue(self)

      convenience function to get the name of the language we are translating to

      :return: the language to translate to
      :rtype: string


   .. method:: storeTranslation(self)

      build the translation json file 
              


   .. method:: translateConnection(self, key, inText, doTranslate=True)

      create layout with the setup using a label and a lineedit to make sure we can change the translation if necessary

      :param key: key value of the original dictionary to use for later
      :type key: string
      :param inText: the text to translate or use as the input to change
      :type inText: string
      :param doTranslate: if `True` the text given will be translated, if `False` we use the text for asjustments
      :type doTranslate: bool
      :return: the layout holding the widgets
      :rtype: QLayout



.. function:: showUI(inDict, widgetName)

   function to show the widget blocking other functionality

   :param inDict: the dictionary to translate
   :type inDict: dict
   :param widgetName: the name of the widget to use to store the file
   :type widgetName: string
   :return: the current widget
   :rtype: QWidget


.. function:: testUI(inDict, widgetName)

   convenience function to show the current widget without it being part of the system

   :param inDict: the dictionary to translate
   :type inDict: dict
   :param widgetName: the name of the widget to use to store the file
   :type widgetName: string
   :return: the current widget
   :rtype: QWidget


