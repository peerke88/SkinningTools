# -*- coding: utf-8 -*-
import sys
from SkinningTools.UI.utils import *
from SkinningTools.UI.qt_util import *


class TearoffTabBar(QTabBar):
    """ tab bar for the QTabwidget that allows the widget to be removed from the tab and parent to a new window
    """

    tearOff = pyqtSignal(int, QPoint)
    def __init__(self, parent=None):
        """ the constructor

        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        QTabBar.__init__(self, parent)
        self.setCursor(Qt.ArrowCursor)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.setIconSize(QSize(12, 12))
        self.__pressedIndex = -1
        self.__isWest = False
        self.__size = 30
        self.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")

    def mousePressEvent(self, event):
        """ the mouse press event that checks if the conditions are met to detach the window
        it will change the control cursors image to display the action
        """
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
        """ make sure the image of the hand is still conveiying the correct action
        """
        if self.__pressedIndex > -1:
            pass
        else:
            if event.modifiers() == Qt.ControlModifier:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            QTabBar.mouseMoveEvent(self, event)

    def enterEvent(self, event):
        """ use the correct keyboard focus when the arrow is in the tab
        """
        self.grabKeyboard()
        QTabBar.enterEvent(self, event)

    def leaveEvent(self, event):
        """ use the correct keyboard focus when the arrow is in the tab
        """
        self.releaseKeyboard()
        QTabBar.leaveEvent(self, event)

    def keyPressEvent(self, event):
        """ make sure the correct arrow cursor is present when inside the headerview
        """
        if event.modifiers() == Qt.ControlModifier:
            self.setCursor(Qt.OpenHandCursor)
        QTabBar.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """ make sure the correct arrow cursor is present when inside the headerview
        """
        if self.cursor().shape() != Qt.ArrowCursor:
            self.setCursor(Qt.ArrowCursor)
        QTabBar.keyReleaseEvent(self, event)

    def event(self, event):
        """ make sure that the tear off event is triggered when all conditions are met
        """
        if event is None or QEvent is None:
            return
        if event.type() == QEvent.MouseButtonRelease:
            if self.__pressedIndex > -1:
                self.tearOff.emit(self.__pressedIndex, event.globalPos())
                self.__pressedIndex = -1
                self.setCursor(Qt.ArrowCursor)
        return QTabBar.event(self, event)

    def setWest(self):
        """ set the orientation of the tab widgets header
        """
        self.__isWest = True

    def tabSizeHint(self, index=0):
        """ get the size hint of the current tab
        this way we can make sure that when we detach the widget we have a correct size to work with

        :param index: index if the tab
        :type index: int
        :return: the size of the widget
        :rtype: Qsize
        """
        height = QTabBar.tabSizeHint(self, index).height()
        width = QTabBar.tabSizeHint(self, index).width()
        if index == self.count() - 1:
            if self.__isWest:
                return QSize(self.__size, height)
            else:
                return QSize(width, self.__size)
        else:
            return QTabBar.tabSizeHint(self, index)
