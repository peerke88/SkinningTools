# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *

from functools import partial
from SkinningTools.UI.ControlSlider.abstractControl import AbstractControl
from SkinningTools.UI.ControlSlider.slider import Slider


class SliderControl(AbstractControl):
    editModeRequested = pyqtSignal()
    editModeEnded = pyqtSignal()

    startScrub = pyqtSignal()
    endScrub = pyqtSignal()

    def __init__(self, name, label='slider control', mn=-100.0, mx=100.0, rigidRange=False, parent=None, labelOnSlider=False):
        AbstractControl.__init__(self, name, parent)
        self.editModeLock = False

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(6, 4, 3, 3)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.hide()
        self.lineEdit.installEventFilter(self)

        if labelOnSlider:
            self.slider = Slider(mn, mx, self, label)
        else:
            self.slider = Slider(mn, mx, self)
        self.slider.rigidRange = rigidRange
        self.slider.installEventFilter(self)

        self.startScrub.connect(partial(self.slider.setPaintLabel, False))
        self.endScrub.connect(partial(self.slider.setPaintLabel, True))

        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.slider)
        if not labelOnSlider:
            self.label = QLabel(label, self)
            self.layout.addWidget(self.label)

        self.slider.valueChanged.connect(self.evaluateLogic)

    def editBegin(self, value):
        self.editModeRequested.emit()
        self.slider.hide()
        self.lineEdit.setText(value)
        self.lineEdit.setFocus(Qt.MouseFocusReason)
        self.lineEdit.deselect()
        self.lineEdit.show()
        self.repaint()

    def editEnd(self):
        if self.editModeLock:
            return
        self.lineEdit.hide()
        strValue = str(self.lineEdit.text())
        try:
            newValue = eval(strValue)
            self.slider.setValue(newValue)
        except:
            pass
        self.slider.show()
        self.slider.setFocus(Qt.MouseFocusReason)

        self.editModeEnded.emit()

    def eventFilter(self, obj, event):
        if obj == self.slider:
            if event.type() == QEvent.MouseButtonPress:
                self.startScrub.emit()
                self.slider.setFocus(Qt.MouseFocusReason)
            elif event.type() == QEvent.MouseButtonRelease:
                self.endScrub.emit()
                self.mouseReleaseEvent(event)
            elif event.type() == QEvent.MouseButtonDblClick:
                self.editBegin(self.slider.getValueAsString())
            elif event.type() == QEvent.KeyPress:
                if event.key() in (Qt.Key_Asterisk, Qt.Key_Plus, Qt.Key_Comma, Qt.Key_MinusQt.Key_Period, Qt.Key_Slash, Qt.Key_Colon,
                                   Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9):
                    self.editBegin(event.text())
            elif event.type() == QEvent.Enter:
                self.slider.setPaintLabel(False)
            elif event.type() == QEvent.Leave:
                self.slider.setPaintLabel(True)
            return False

        if obj != self.lineEdit:
            return AbstractControl.eventFilter(self, obj, event)

        if not obj.isEnabled():
            return False

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return:  # return key
                self.editEnd()
                obj.setStyleSheet('')
        elif event.type() == QEvent.FocusOut:
            self.editEnd()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)


    def logic1():
        print('hey hey')
        pippo = 2 + 3
        print('pippo', pippo)
        print(sys)


    def logic2(who):
        print('hello from %s' % who)


    w = QWidget()
    w.setWindowTitle('Slider Controls')
    l = QVBoxLayout(w)
    s1 = SliderControl('slider_1', mn=-10, mx=10, parent=w)
    s1.setLogicFunction(logic1)
    s2 = SliderControl('slider_2', mn=-100, mx=100, parent=w)
    s2.setLogicFunction(logic2, s2)
    l.addWidget(s1)
    l.addWidget(s2)
    w.show()

    sys.exit(app.exec_())
