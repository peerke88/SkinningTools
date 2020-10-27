# -*- coding: utf-8 -*-
import sys
from SkinningTools.UI.utils import *
from SkinningTools.UI.qt_util import *


class TearoffTabBar(QTabBar):
    selectMapNode = pyqtSignal(int)
    tearOff = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        QTabBar.__init__(self, parent)
        self.setCursor(Qt.ArrowCursor)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.setIconSize(QSize(12, 12))
        self.__pressedIndex = -1
        self.__isWest = False
        self.__size = 30

    def mousePressEvent(self, event):
        button = event.button()
        modifier = event.modifiers()
        if not (button == Qt.LeftButton and (modifier == Qt.NoModifier or modifier == Qt.ControlModifier)):
            return
        if modifier == Qt.ControlModifier:
            pos = event.pos()
            self.__pressedIndex = self.tabAt(pos)
            rect = self.tabRect(self.__pressedIndex)
            pixmap = QPixmap.grabWidget(self, rect)
            painter = QPainter(pixmap)
            cursorPm = QPixmap(':/closedHand')
            cursorPos = QPoint(*[(x - y) / 2 for x, y in zip(rect.size().toTuple(), QSize(32, 24).toTuple())])
            painter.drawPixmap(cursorPos, cursorPm)
            painter.end()
            cursor = QCursor(pixmap)
            self.setCursor(cursor)
        QTabBar.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.__pressedIndex > -1:
            pass
        else:
            if event.modifiers() == Qt.ControlModifier:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            QTabBar.mouseMoveEvent(self, event)

    def enterEvent(self, event):
        self.grabKeyboard()
        QTabBar.enterEvent(self, event)

    def leaveEvent(self, event):
        self.releaseKeyboard()
        QTabBar.leaveEvent(self, event)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.setCursor(Qt.OpenHandCursor)
        QTabBar.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if self.cursor().shape() != Qt.ArrowCursor:
            self.setCursor(Qt.ArrowCursor)
        QTabBar.keyReleaseEvent(self, event)

    def event(self, event):
        if event.type() == QEvent.MouseButtonRelease:
            if self.__pressedIndex > -1:
                self.tearOff.emit(self.__pressedIndex, event.globalPos())
                self.__pressedIndex = -1
                self.setCursor(Qt.ArrowCursor)
        return QTabBar.event(self, event)

    def setWest(self):
        self.__isWest = True

    def tabSizeHint(self, index=0):
        height = QTabBar.tabSizeHint(self, index).height()
        width = QTabBar.tabSizeHint(self, index).width()
        if index == self.count() - 1:
            if self.__isWest:
                return QSize(self.__size, height)
            else:
                return QSize(width, self.__size)
        else:
            return QTabBar.tabSizeHint(self, index)


class EditableTabBar(TearoffTabBar):
    tabLabelRenamed = pyqtSignal(str, str)
    requestRemove = pyqtSignal(int)
    tabChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        TearoffTabBar.__init__(self, parent)
        self.__editor = QLineEdit(self)
        self.__editor.setWindowFlags(Qt.Popup)
        self.__editor.setFocusProxy(self)
        self.__editor.setFocusPolicy(Qt.StrongFocus)
        self.__editor.editingFinished.connect(self.handleEditingFinished)
        self.__editor.installEventFilter(self)
        self.__editor.setValidator(QRegExpValidator(nameRegExp))
        self.__editIndex = -1

    def eventFilter(self, widget, event):
        if event is None or QEvent is None:
            return False
        if event.type() == QEvent.MouseButtonPress and not self.__editor.geometry().contains(event.globalPos()) or event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.__editor.hide()
            return False
        return QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.selectMapNode.emit(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self.__editor.setFixedSize(rect.size())
        self.__editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.__editor.setText(self.tabText(index))
        if not self.__editor.isVisible():
            self.__editor.show()
            self.__editIndex = index

    def handleEditingFinished(self):
        if self.__editIndex >= 0:
            self.__editor.hide()
            oldText = self.tabText(self.__editIndex)
            newText = self.__editor.text()
            if oldText != newText:
                names = [self.tabText(i) for i in range(self.count())]
                newText = getNumericName(newText, names)
                self.setTabText(self.__editIndex, newText)
                self.tabLabelRenamed.emit(oldText, newText)
                self.__editIndex = -1
            return oldText, newText
