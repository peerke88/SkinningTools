:mod:`SkinningTools.UI.messageProgressBar`
==========================================

.. py:module:: SkinningTools.UI.messageProgressBar


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.messageProgressBar.MessageProgressBar



.. py:class:: MessageProgressBar(parent=None)



   the progressbar
   added functionality to the progressbar to make sure it also displays the correct message on what is currently been done

   :note: add warning messages or error messages in the progressbar? change color?
   :note: possibly make this smarter by having segmented blocks in which seperate functions can still access the progressbar but dont take up 100% just a smaller portion

   .. attribute:: message
      

      

   .. method:: _getMessage(self)

      return the current message of the progressbar
      :note: probably not really necessary, just added for the possibility, 
      could be usefull to expand with some string operations in multilayered tools

      :return: the message in the progressbar
      :rtype: string


   .. method:: _setMessage(self, inMessage)

      override the text on the progress bar with a personal message

      :param inMessage: the message to add
      :type inMessage: string


   .. method:: setValue(self, inValue)

      set the actual value of the progressbar, adds in the message as well

      :param inValue: the value to set the progressbar to
      :type inValue: float



