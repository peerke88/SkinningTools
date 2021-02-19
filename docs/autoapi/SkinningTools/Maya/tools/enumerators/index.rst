:mod:`SkinningTools.Maya.tools.enumerators`
===========================================

.. py:module:: SkinningTools.Maya.tools.enumerators

.. autoapi-nested-parse::

   @Brief: RigSystem - automated rigging system for facial rigs based on bone and guide positions
   @author Perry Leijten
   @since  05/03/2018



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.tools.enumerators._AxisEnumerator
   SkinningTools.Maya.tools.enumerators._Space
   SkinningTools.Maya.tools.enumerators.__Enumerator



.. data:: AxisEnumerator
   

   

.. data:: Space
   

   

.. py:class:: _AxisEnumerator



   axis enumerator class for easy axis handling 

   .. method:: getVector(self, axis)

      get vector allocated to given axis 

      :param axis: axis to check for 
      :type axis: Vector
      :return
      :type: Vector


   .. method:: invert(self, axis)

      return the inverse value of the Vector given. 

      :param axis: axis to check for 
      :type axis: Vector
      :return: the opposite vector
      :rtype: Vector


   .. method:: isNegative(axis)
      :staticmethod:

      check if current axis is negative 

      :param axis: axis to check for 
      :type axis: Vector
      :return: True if the axis is negative   
      :rtype: bool


   .. method:: isPositive(axis)
      :staticmethod:

      check if current axis is positive 

      :param axis: axis to check for 
      :type axis: Vector
      :return: True if the axis is positive
      :rtype: bool


   .. method:: isX(self, axis)

      check if the axis is either PosAxisX or NegAxisX 

      :param axis: axis to check for 
      :type axis: Vector
      :return: if the vector is in the X direction
      :rtype: Vector


   .. method:: isY(self, axis)

      check if the axis is either PosAxisY or NegAxisY 

      :param axis: axis to check for 
      :type axis: Vector
      :return: if the vector is in the Y direction
      :rtype: Vector


   .. method:: isZ(self, axis)

      check if the axis is either PosAxisZ or NegAxisZ 

      :param axis: axis to check for 
      :typeaxis: Vector
      :return:  if the vector is in the Z direction
      :rtype: Vector



.. py:class:: _Space



   simple class for space enumaration


.. py:class:: __Enumerator(x)



   sort of enumarators added (similar to dict)

   .. method:: __getattr__(self, val)


   .. method:: __setLocked()
      :staticmethod:

      remove attr setting functionality on object


   .. method:: __setattr__(self, att, val)

      single attr setter possible: "_Enumerator__x" 

      :param att: string representation of the enumerator
      :type att: string
      :param val: object that is measured against the key
      :type val: object


   .. method:: __setitem__(self, i, val)


   .. method:: __str__(self)

      string representation

      :return: the representation of the enumerator 
      :rtype: string


   .. method:: getKeys(self)

      get current enumerator keys 

      :return: 
      :rtype: list


   .. method:: validate(self, val)

      validate enumarator value 

      :return: check if the value is a vector
      :rtype: bool



