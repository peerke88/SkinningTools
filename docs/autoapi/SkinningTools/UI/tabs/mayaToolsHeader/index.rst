:mod:`SkinningTools.UI.tabs.mayaToolsHeader`
============================================

.. py:module:: SkinningTools.UI.tabs.mayaToolsHeader


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.mayaToolsHeader.MayaToolsHeader



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.mayaToolsHeader.testUI


.. py:class:: MayaToolsHeader(inGraph=None, inProgressBar=None, parent=None)



   basic group object that holds all the maya Tools
   :note: this needs to change later based on the dcc tool

   .. attribute:: toolName
      :annotation: = MayaToolsHeader

      

   .. method:: __connections(self)

      signal connections
              


   .. method:: __mayaToolsSetup(self)

      convenience function to gather all buttons for the current UI
              


   .. method:: _loadSkin(self)

      load current stored object weigth information
              


   .. method:: _loadVtx(self)

      load current stored vertex weigth information
              


   .. method:: _storeSkin(self)

      visual update on storing object weigth information
              


   .. method:: _storeVtx(self)

      visual update on storing vertex weigth information
              


   .. method:: _updateGraph(self)

      convert the graph to an image 

      :return: path to the image to use as button
      :rtype: string


   .. method:: _updateGraphButton(self)

      update the button image with information of the current graph
              


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


