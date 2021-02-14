:mod:`SkinningTools.UI.tabs.weightsUI`
======================================

.. py:module:: SkinningTools.UI.tabs.weightsUI


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.weightsUI.WeightsUI



Functions
~~~~~~~~~

.. autoapisummary::

   SkinningTools.UI.tabs.weightsUI.testUI


.. data:: _DEBUG
   

   

.. data:: _DIR
   

   

.. data:: _LOCALFOLDER
   

   

.. py:class:: WeightsUI(settings=None, inProgressBar=None, parent=None)



   weights manager
   allows to save skinning information from given objects and to load it onto the same object or even others

   .. attribute:: toolName
      :annotation: = weightUI

      

   .. method:: __addButtons(self)

      simple convenience function to add the buttons to the current ui
              


   .. method:: _changeMeshInfo(self, curFile, *_)

      chagne the information based on the current weight file selection

      :param curFile: the weight file to gather data from
      :type curFile: string


   .. method:: _checkJoints(self, joints, sender)

      check if the objects joints inputs are similar

      :param joints: input information on the joints stored on file
      :type joints: list
      :param sender: the check button used to trigger this function
      :type sender: QPushButton


   .. method:: _checkUvs(self, uvs, currentMesh, sender, checkBox)

      check if the object has uvs and if the uvs are similar

      :param uvs: input information on the uvs stored on file
      :type uvs: list
      :param currentMesh: the current objects to check for uvs
      :type currentMesh: list
      :param sender: the check button used to trigger this function
      :type sender: QPushButton
      :param checkBox: the checkbox to set if it can be used in stead of positions
      :type checkBox: QCheckBox


   .. method:: _checkVerts(self, verts, currentMesh, sender)

      check if the objects vertices are similar

      :todo: make sure that the scale values are used

      :param verts: input information on the verts stored on file
      :type verts: list
      :param currentMesh: the current object to check for verts
      :type currentMesh: string
      :param sender: the check button used to trigger this function
      :type sender: QPushButton


   .. method:: _getData(self, binary=False, *args)

      get the date from the current selection

      :param binary: if `True` stores the json information as binary to save space, if `False` stores the data as ascii
      :type binary: bool


   .. method:: _infoTextOptions(self)

      seperate text labels to be used for translation
              


   .. method:: _loadExternalFiles(self)

      load external weight files, 
      this can be used to load skinweights files that are not listed from settings.
      this will add the folder to the settignsfile so it can be found from now, but will not set skinning info


   .. method:: _loadFiles(self, *args)

      convenience function to make sure to load files from known location
              


   .. method:: _makeBB(self, bbox, mesh)

      create a cube that uses the infromation of the skinweights file bounding box, 
      to identify possible problems when loading the skincluster information


   .. method:: _savePath(self, binary=False)

      save the current information to the default path

      :param binary: if `True` stores the json information as binary to save space, if `False` stores the data as ascii
      :type binary: bool
      :return: the path the information is saved to
      :rtype: string


   .. method:: _scaleBBox(self, inValue)


   .. method:: _setSkinInfo(self)

      set the skinning info from current object to selected or multiple
      :todo: need to make sure this only allows the user to check
      :todo: or if it actually has a meaningfull relationship to the weights manager 


   .. method:: _updateInfo(self, sender, *args)

      widget to hold extra information read fromt he current weight file

      :param sender: the item object that holds the information on the weight files
      :type sender: QWidget 


   .. method:: clearInfo(self)

      clear the current information widget on the selected weights file
              


   .. method:: doTranslate(self)

      seperate function that calls upon the translate widget to help create a new language
      we use the english language to translate from to make sure that translation doesnt get lost


   .. method:: getButtonText(self)

      convenience function to get the current items that need new locale text
              


   .. method:: hideEvent(self, event)

      make sure we don't have any lingering data
              


   .. method:: translate(self, localeDict={})

      translate the ui based on given dictionary

      :param localeDict: the dictionary holding information on how to translate the ui
      :type localeDict: dict



.. function:: testUI()

   test the current UI without the need of all the extra functionality
       


