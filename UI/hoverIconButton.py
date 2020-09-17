from SkinningTools.UI.qt_util import *

class HoverIconButton(QToolButton):
    def __init__(self, icon = QIcon(), hoverIcon = QIcon(), orientation = 0, parent = None):
        super(HoverIconButton, self).__init__(parent)
        self.__icon = QIcon()
        self.__hoverIcon = QIcon()
        self.__disabled = QPixmap()
        self.setCustomIcon(icon, hoverIcon, orientation)

    def setDisabledPixmap(self, pixmap):
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        self.__disabled = pixmap

    def setCustomIcon(self, pixmap, hover_pixmap, orientation=0):
        if isinstance(pixmap, str):
            pixmap = QPixmap(pixmap)
        if orientation != 0:
            transform = QTransform().rotate(orientation, Qt.Axis.ZAxis)
            pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.__icon = QIcon(pixmap)
        if isinstance(hover_pixmap, str):
            hover_pixmap = QPixmap(hover_pixmap)
        if orientation != 0:
            transform = QTransform().rotate(orientation, Qt.Axis.ZAxis)
            hover_pixmap = hover_pixmap.transformed(transform, Qt.SmoothTransformation)
        self.__hoverIcon = QIcon(hover_pixmap)
        if not self.__disabled.isNull():
            self.__icon.addPixmap(self.__disabled, QIcon.Disabled)
            self.__hoverIcon.addPixmap(self.__disabled, QIcon.Disabled)
        self.setIcon(self.__icon)

    def enterEvent(self, event):
        if not self.__hoverIcon.isNull():
            self.setIcon(self.__hoverIcon)
            self.update()
        super(HoverIconButton, self).enterEvent(event)

    def leaveEvent(self, event):
        if not self.__icon.isNull():
            self.setIcon(self.__icon)
            self.update()
        super(HoverIconButton, self).leaveEvent(event)
