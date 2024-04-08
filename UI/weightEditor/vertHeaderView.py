from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *


class VertHeaderView(QHeaderView):
    """ header view that displays text in a vertical manner
    """
    rightClicked = pyqtSignal()

    _margin = 3
    _font = QFont()
    _metrics = QFontMetrics(_font)
    _selectedFont = QFont()
    # _selectedFont.setWeight(63)

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(VertHeaderView, self).__init__(Qt.Horizontal, parent)
        self._parent = parent

        if QT_VERSION not in ["pyside2", "pyside6"]:
            self.setClickable(True)
        else:
            self.setSectionsClickable(True)

        self.setHighlightSections(True)

    def mouseReleaseEvent(self, event):
        """ mouse event to emit when mouse is right clicked
        """
        self._parent.view.mouse_pos = QCursor.pos()
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(self.__class__, self).mouseReleaseEvent(event)

    def paintSection(self, painter, rect, index):
        """ painter that will set the text in the correct scale and oriented vertically

        :param painter: painter class to override to make sure everything is drawn correctly
        :type painter: QPainter
        :param rect: the size of the current header
        :type rect: Qrect
        :param index: the index of the header that needs to be drawn
        :type index: int 
        """
        painter.rotate(-90)
        data = self._getData(index)

        data = data.split(':')[-1]
        isSelected = self.checkSelected(index)

        if isSelected:
            font = self._selectedFont
        else:
            font = self._font
        painter.setFont(font)

        _color = self.model().headerData(index, Qt.Horizontal, Qt.BackgroundRole)
        _darker = QColor(*map(lambda c: c - 42, _color.getRgb()[:3]))
        _nRect = self.rotate(index, rect)
        painter.fillRect(_nRect, _color)

        painter.setPen(QPen(_darker))
        painter.drawRect(_nRect)

        painter.setPen(QColor(*[230] * 3))

        tx = -rect.height() + self._margin
        ty = rect.left() + (rect.width() + self._metrics.descent()) / 2
        painter.drawText(tx, ty, data)

    def checkSelected(self, index):
        """ check if the current object is selected

        :param index: the index of the header
        :type index: int
        :return: if the current header is selected
        :rtype: bool
        """
        sel_model = self.selectionModel()
        selected_item = sel_model.currentIndex()
        isSelected = sel_model.columnIntersectsSelection(index, selected_item)
        return isSelected

    def rotate(self, index, rect):
        """ convenience function to rotate the current header from horizontal to vertical

        :param index: index of the header to change
        :type index: int
        :param rect: the horizontally placed rect
        :type rect: QRect
        :return: the vertically placed rect
        :rtype: QRect
        """
        offset = int(index == 0)
        rect = rect.getRect()
        rect = [rect[1] - rect[3] + 1, rect[0] - 1 + offset, rect[3] - 1, rect[2] - offset]
        rect = QRect(*rect)
        return rect

    def sizeHint(self):
        """ returns the size hint 

        :return: the size hint of the current headerview
        :rtype: QSize
        """
        return QSize(0, self._getWidth() + 2 * self._margin)

    def _getWidth(self):
        """ get the width of the current headerview

        :return: the total width of all the headers
        :rtype: float
        """
        if self.model() is None:
            return 0
        width_list = [self._metrics.width(self._getData(i)) for i in range(0, self.model().columnCount())] or [0]
        max_width = max(width_list) * 1.1
        return max_width

    def _getData(self, index):
        """ get the current data of the header view

        :param index: the index of the header
        :type index: int
        :return: the header data of the model
        :rtype: QVariant
        """
        return self.model().headerData(index, self.orientation(), 0)
