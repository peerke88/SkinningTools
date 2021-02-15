# -*- coding: utf-8 -*-
'''
  @Brief: RigSystem - automated rigging system for facial rigs based on bone and guide positions
  @author Perry Leijten
  @since  05/03/2018
'''
import warnings
from maya.api.OpenMaya import MVector


class __Enumerator(object):
    """ sort of enumarators added (similar to dict)"""
    def __init__(self, x):
        """constructor Method"""
        self.__x = x

    def __str__(self):
        """ string representation
    
        :return: the representation of the enumerator 
        :rtype: string
        """
        outStr = self.__class__.__name__
        for elem in self.__x:
            outStr = '%s  \n%s' % (outStr, elem)
        return outStr

    def __setattr__(self, att, val):
        """ single attr setter possible: "_Enumerator__x" 
        
        :param att: string representation of the enumerator
        :type att: string
        :param val: object that is measured against the key
        :type val: object
        """
        if att == '_Enumerator__x':
            object.__setattr__(self, att, val)
        else:
            self.__setLocked()

    def __getattr__(self, val):
        for couple in self.__x:
            if couple[0] == val:
                return couple[1]
        warnings.warn("%s is not a valid enumerator key for %s" % (val, self.__class__.__name__))

    def __setitem__(self, i, val):
        self.__setLocked()

    @staticmethod
    def __setLocked():
        """remove attr setting functionality on object"""
        warnings.warn("Setting attributes of any kind on an enumerator is forbidden!")

    def validate(self, val):
        """validate enumarator value 

        :return: check if the value is a vector
        :rtype: bool
        """
        for couple in self.__x:
            if isinstance(couple[0], MVector):
                if couple[0] == val:
                    return True
            else:
                if couple[1] == val:
                    return True
        return False

    def getKeys(self):
        """ get current enumerator keys 

        :return: 
        :rtype: list
        """
        validKeys = []
        for pair in self.__x:
            validKeys.append(pair[0])
        return validKeys


class _AxisEnumerator(__Enumerator):
    """axis enumerator class for easy axis handling """

    def __init__(self):
        """constructor method"""
        super(_AxisEnumerator, self).__init__(
            x=(("PosAxisX", MVector(1, 0, 0)),
               ("PosAxisY", MVector(0, 1, 0)),
               ("PosAxisZ", MVector(0, 0, 1)),

               ("NegAxisX", MVector(-1, 0, 0)),
               ("NegAxisY", MVector(0, -1, 0)),
               ("NegAxisZ", MVector(0, 0, -1))))

    def invert(self, axis):
        """return the inverse value of the Vector given. 
        
        :param axis: axis to check for 
        :type axis: Vector
        :return: the opposite vector
        :rtype: Vector
        """
        axis = MVector(axis)
        if self.validate(axis):
            if axis == self.PosAxisX:
                return self.NegAxisX
            elif axis == self.NegAxisX:
                return self.PosAxisX
            elif axis == self.PosAxisY:
                return self.NegAxisY
            elif axis == self.NegAxisY:
                return self.PosAxisY
            elif axis == self.PosAxisZ:
                return self.NegAxisZ
            elif axis == self.NegAxisZ:
                return self.PosAxisZ
        else:
            warnings.warn('axis <%s> is not a valid AxisEnumerator member' % axis)

    @staticmethod
    def isPositive(axis):
        """check if current axis is positive 
        
        :param axis: axis to check for 
        :type axis: Vector
        :return: True if the axis is positive
        :rtype: bool
        """
        if sum(axis) > 0:
            return True
        return False

    @staticmethod
    def isNegative(axis):
        """ check if current axis is negative 

        :param axis: axis to check for 
        :type axis: Vector
        :return: True if the axis is negative   
        :rtype: bool
        """
        if sum(axis) < 0:
            return True
        return False

    def isX(self, axis):
        """ check if the axis is either PosAxisX or NegAxisX 
        
        :param axis: axis to check for 
        :type axis: Vector
        :return: if the vector is in the X direction
        :rtype: Vector
        """
        return axis in (self.PosAxisX, self.NegAxisX)

    def isY(self, axis):
        """ check if the axis is either PosAxisY or NegAxisY 

        :param axis: axis to check for 
        :type axis: Vector
        :return: if the vector is in the Y direction
        :rtype: Vector
        """
        return axis in (self.PosAxisY, self.NegAxisY)

    def isZ(self, axis):
        """check if the axis is either PosAxisZ or NegAxisZ 

        :param axis: axis to check for 
        :typeaxis: Vector
        :return:  if the vector is in the Z direction
        :rtype: Vector
        """
        return axis in (self.PosAxisZ, self.NegAxisZ)

    def getVector(self, axis):
        """get vector allocated to given axis 

        :param axis: axis to check for 
        :type axis: Vector
        :return
        :type: Vector
        """
        axis = MVector(axis)
        if self.validate(axis):
            if axis == self.PosAxisX:
                return MVector((1.0, 0.0, 0.0))
            elif axis == self.NegAxisX:
                return MVector((-1.0, 0.0, 0.0))
            elif axis == self.PosAxisY:
                return MVector((0.0, 1.0, 0.0))
            elif axis == self.NegAxisY:
                return MVector((0.0, -1.0, 0.0))
            elif axis == self.PosAxisZ:
                return MVector((0.0, 0.0, 1.0))
            elif axis == self.NegAxisZ:
                return MVector((0.0, 0.0, -1.0))
        else:
            warnings.warn('axis <%s> is not a valid AxisEnumerator member' % axis)


AxisEnumerator = _AxisEnumerator()


class _Space(__Enumerator):
    """simple class for space enumaration"""
    def __init__(self):
        """construction method"""
        super(_Space, self).__init__(
            x=(("Global", 0),
               ("Local", 1)))


Space = _Space()
