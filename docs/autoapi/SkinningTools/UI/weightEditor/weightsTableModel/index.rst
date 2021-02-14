:mod:`SkinningTools.UI.weightEditor.weightsTableModel`
======================================================

.. py:module:: SkinningTools.UI.weightEditor.weightsTableModel


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.UI.weightEditor.weightsTableModel.WeightsTableModel



.. py:class:: WeightsTableModel(data, parent=None, window=None, meshIndex=[], jointNames=[], vtxSideBar=[], jointColorList=[])



   .. attribute:: _baseColor
      

      

   .. attribute:: cell_vertex_copy_color
      :annotation: = [70, 120, 120]

      

   .. attribute:: copyCellColor
      :annotation: = [90, 120, 90]

      

   .. attribute:: default
      

      

   .. attribute:: lockedBG
      

      

   .. attribute:: lockedTXT
      

      

   .. attribute:: notNormalizedColor
      :annotation: = [235, 52, 52]

      

   .. attribute:: overMaxInfColor
      :annotation: = [235, 110, 52]

      

   .. attribute:: vertex_copy_color
      :annotation: = [90, 90, 120]

      

   .. method:: columnCount(self, parent=None)

      amount of columns in current table model

      :return: amount of columns
      :rtype: int


   .. method:: data(self, index, role=Qt.DisplayRole)

      get specific data from the current given header

      :param index: index of the header
      :type index: int
      :param role: qt role on how to display the element
      :type role: Qt.DisplayRole
      :return: data gathered from the object
      :rtype: QColor/Qt.alignment


   .. method:: flags(self, index)

      get the flags of given cell

      :param index: index of the cell
      :type index: cellindex
      :return: flags used on the current cell
      :rtype: Qt.flags


   .. method:: getCellData(self, index=None, row=0, col=0)

      get the value from the given cell

      :param index: index of the cell data if given
      :type index: cellindex
      :param row: index of the row
      :type row: int
      :param col: index of the column
      :type col: int
      :return: the value of the cell
      :rtype: float


   .. method:: headerData(self, index, orientation, role)

      set up the header data for all joint objects

      :param index: index of the header
      :type index: int
      :param orientation: the Qt orientation role on how to place the current header
      :type orientation: QT.orientation
      :param role: qt role on how to display the element
      :type role: Qt.DisplayRole
      :return: the color of the object
      :rtype: QColor


   .. method:: rowCount(self, parent=None)

      amount of rows in current table model

      :return: amount of rows
      :rtype: int


   .. method:: setData(self, index, value, role=Qt.EditRole)

      set the data on the given cell

      :param index: index of the cell
      :type index: cellindex
      :param value: value to give to the cell
      :type value: float
      :param role: role of current edit
      :type role: Qt.role
      :return: if setting was succesfull
      :rtype: bool



