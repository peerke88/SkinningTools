# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
from ..qtUtil import *

from maya import cmds
from maya.OpenMaya import MEventMessage

from sliderControl import SliderControl


class NumericAttribute(QHBoxLayout):
    '''
    Represents a maya attribute as a fancy slider.
    Double click to turn it into a l ne edit that even supports basic math (uses python parse)
    '''
    valueChanged = pyqtSignal(str)

    def __init__(self, attribPath, *args, **kwargs):
        super(NumericAttribute, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignmentFlag(Qt.AlignRight))

        self.__attributes = [attribPath]
        tooltip = self.__nsFreeAttribPath(0)

        attribRange = self.__fittedValueRange
        self.gripSlider = SliderControl(str(attribPath), label=attribPath.attribute,  min=attribRange[0], max = attribRange[1], rigidRange=attribRange[2])
        self.gripSlider.slider.setValue(self.__value(0))
        self.addWidget(self.gripSlider)

        #automatic attribute setting
        self.gripSlider.slider.valueChanged.connect(self.__setValue)

    def __nsFreeAttribPath(self, id):
        parts = str(self.__attributes[id]).split('|')
        for i in range(len(parts)):
            if not parts[i]: continue
            parts[i] = parts[i].split(':', 1)[-1]
        return '|'.join(parts)

    @property
    def __fittedValueRange(self):
        #range fitted around all attributes
        out = None
        for i in range(len(self.__attributes)):
            r = self.__valueRange(i)
            if out is None:
                out = r
            else:
                out[0] = min(out[0], r[0])
                out[1] = max(out[1], r[1])
                out[2] = (out[2] == True and r[2] == True)
        return out

    def __valueRange(self, id):
        #range for specific attribute
        try:
            output = cmds.attributeQuery(str(self.__attributes[id]).rsplit('.', 1)[-1],
                node = str(self.__attributes[id]).rsplit('.', 1)[0], r = True)
            output.append(True)
            return output
        except:
            if "Angle" in cmds.getAttr(str(self.__attributes[id]), type=True):
                return [-360, 360, False]
            else:
                return [-500,500, False]
    
    def __value(self, id):
        return cmds.getAttr(str(self.__attributes[id]))

    def __setValue(self, newValue):
        if AttribWidget.inUse:
            return
        for attr in self.__attributes:
            cmds.setAttr(str(attr), newValue)
            self.valueChanged.emit(str(attr))

    def addAttribute(self, attribPath):
        self.__attributes.append(attribPath)
        fittedRange = self.__fittedValueRange
        self.gripSlider.slider.setRange(*fittedRange[0:2])
        self.gripSlider.slider.rigidRange = fittedRange[2]

    def hasAttributeName(self, attribName):
        for attr in self.__attributes:
            if str(attr).rsplit('.', 1)[-1] == attribName:
                return True
        return False


class AttribWidget(QObject):
    '''
    Widget that displays an editable list of attributes.
    Attributes are derived from selection.
    Any attribute is displayed once with it's short name.
    If not all objects have the attribute it is still displayed.
    '''
    def __init__(self, destWidget):
        super(AttribWidget, self).__init__()

        self.destWidget = destWidget

        #make the layout nested
        if not self.destWidget.layout():
            self.destWidget.setLayout(QVBoxLayout())
        self.__makeLayout()
        self.__callbacks = []

        self.destWidget.installEventFilter(self)

        self.__undoID = MEventMessage.addEventCallback('Undo', self.enterEvent, None)
        self.__redoID = MEventMessage.addEventCallback('Redo', self.enterEvent, None)

    def __del__(self):
        try:
            MEventMessage.removeCallback(self.__undoID)
        except: pass
        try:
            MEventMessage.removeCallback(self.__redoID)
        except: pass

    def connectValueChanged(self, boundFunction):
        self.__callbacks.append(boundFunction)

    inUse = False
    def emitValueChanged(self, *args):
        if AttribWidget.inUse:
            return
        inUse = True
        for cb in self.__callbacks:
            cb()
        inUse = False

    def __makeLayout(self):
        self.__masterWidget = QFrame()
        self.destWidget.layout().addWidget(self.__masterWidget)
        self.__masterWidget.setLayout(QVBoxLayout())
        self.__masterWidget.layout().setAlignment(Qt.AlignTop | Qt.AlignRight)

    def __clear(self):
        try:
            self.__masterWidget.close()
            self.__masterWidget.deleteLater()
            self.__masterWidget = None
        except:
            #masterWidget is already deleted
            pass
        self.__makeLayout()

    @property
    def mainLayout(self):
        try:
            return self.__masterWidget.layout()
        except:
            return None

    def __getWidget(self, attr):
        for item in self.mainLayout.children():
            if item.hasAttributeName(attr):
                return item

    def update(self, objects):
        self.__clear()

    def __openUndoBlock(self):
        cmds.undoInfo(openChunk=True)

    def __closeUndoBlock(self):
        cmds.undoInfo(closeChunk=True)

    def enterEvent(self, object):
        cleanObjects = []
        selectedObjects = cmds.ls(sl=True, l=True)
        for selectedObject in selectedObjects:
            cleanObjects.append(str(GripPickerName(selectedObject)))

        numericAttributeWidgets = self.mainLayout.children()
        if not numericAttributeWidgets:
            return True

        changeObjects = False
        if str(GripPickerName(numericAttributeWidgets[-1].gripSlider.name.split('.')[0])) in cleanObjects:
            for child in numericAttributeWidgets:
                #update values to scene values
                #if isinstance(child, SliderControl):
                firstAttrObject =  str(GripPickerName(child.gripSlider.name))
                value = cmds.getAttr(firstAttrObject)
                child.gripSlider.slider.setValue(value)
        else:
            #update attributes to scene selection
            allchildren = object.children()
            for child in allchildren:
                sip.delete(child)
            AttribWidget(object).update(cleanObjects)

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.enterEvent(object)
            return True
        else:
            return False