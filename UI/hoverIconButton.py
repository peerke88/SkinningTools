from SkinningTools.UI.qt_util import *

class HoverIconButton(QToolButton):
    """ hover icon, custom tool button that can change if the mouse hovers over it or once clicked
    """
    def __init__(self, icon = QIcon(), hoverIcon = QIcon(), checked = None, orientation = 0, parent = None):
        """ the constructor

        :param icon: default icon
        :type icon: QIcon
        :param hoverIcon: icon used for when the mouse hovers over the button
        :type hoverIcon: QIcon
        :param checked: icon used for when the object is checked
        :type checked: QIcon
        :param orientation: orientation in degrees clockwise for the images on the control
        :type orientation: int
        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(HoverIconButton, self).__init__(parent)
        self.__icon = QIcon()
        self.__hoverIcon = QIcon()
        if checked is not None:
            self.setCheckable(True)
            self.clicked.connect(self._checkState)
            self.setStyleSheet( "selection-background-color: rgba(0,0,0,0);")
        self.__checked = QIcon()
        self.__disabled = QPixmap()
        self.setCustomIcon(icon, hoverIcon, checked, orientation)

    def setDisabledPixmap(self, pixmap):
        """ the icon used for when the object is disabled

        :param pixmap: path to icon 
        :type pixmap: string/QPixmap
        """
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        self.__disabled = pixmap

    def setCustomIcon(self, pixmap, hover, checked = None, orientation=0):
        """ the function that sets the correct icons to the tool
        can be used to override the toolbutton with new icons

        :param pixmap: default icon
        :type pixmap: QIcon
        :param hover: icon used for when the mouse hovers over the button
        :type hover: QIcon
        :param checked: icon used for when the object is checked
        :type checked: QIcon
        :param orientation: orientation in degrees clockwise for the images on the control
        :type orientation: int
        """
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        if isinstance(hover, str):
            hover = QPixmap(hover)
        if isinstance(checked, str):
            checked = QPixmap(checked)
        if orientation != 0:
            transform = QTransform().rotate(orientation, Qt.Axis.ZAxis)
            pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
            hover = hover.transformed(transform, Qt.SmoothTransformation)
            checked = checked.transformed(transform, Qt.SmoothTransformation)
        self.__icon = QIcon(pixmap)
        self.__hoverIcon = QIcon(hover)
        self.__checked = QIcon(checked)
        
        if not self.__disabled.isNull():
            self.__icon.addPixmap(self.__disabled, QIcon.Disabled)
            self.__hoverIcon.addPixmap(self.__disabled, QIcon.Disabled)
            self.__checked.addPixmap(self.__disabled, QIcon.Disabled)
        self.setIcon(self.__icon)

    def enterEvent(self, event):
        """ the mouse hover enter event

        :param event: the given event
        :type event: QEvent 
        """
        if not self.__hoverIcon.isNull() and not self.isChecked():
            self.setIcon(self.__hoverIcon)
            self.update()
        super(HoverIconButton, self).enterEvent(event)

    def leaveEvent(self, event):
        """ the mouse hover leave event

        :param event: the given event
        :type event: QEvent 
        """
        if not self.__icon.isNull() and not self.isChecked():
            self.setIcon(self.__icon)
            self.update()
        super(HoverIconButton, self).leaveEvent(event)

    def _checkState(self):
        """ the state used when the icon is checked
        it will replace the current icon with the one used when its checked or not.
        """
        if self.isChecked():
            self.setIcon(self.__checked)
        else:
            self.setIcon(self.__icon)