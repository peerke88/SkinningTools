:mod:`SkinningTools.UI.tabs.skinSliderSetup`
============================================

.. py:module:: SkinningTools.UI.tabs.skinSliderSetup


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.skinSliderSetup.SkinSliderSetup



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.skinSliderSetup.testUI


.. py:class:: SkinSliderSetup(parent=None)



   skinslider setup, 
   allows the weights to be changed with a slider widget while keeping everything normalized

   .. attribute:: toolName
      :annotation: = SkinSliderSetup

      

   .. method:: __setUI(self)

      convenience function to gather all buttons for the current UI
              


   .. method:: _showUnused(self, *args)

      setup to display the joints if they have or do not have a weight value assigned
              


   .. method:: _update(self)

      convenience function to refresh and update the current widget
              


   .. method:: clearCallback(self)

      remove selection based callback
              


   .. method:: createCallback(self)

      create callback to refresh the current widget based on selection in dcc tool
              


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: searchJointName(self)

      based on the given text we only display jointsliders that are represted by a partial identification of the given string in the search lineedit
              


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


