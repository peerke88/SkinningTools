# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
import math

_DIR = os.path.dirname(__file__)


class Visualizer(QGraphicsItem):
    """ the node items that will serve as handles for the bezier curve
    """
    pen = QPen()
    pen.setStyle(Qt.DashLine)
    pen.setWidth(1)
    pen.setColor(QColor(255, 0, 0, 255))  # outline not selected

    def __init__(self, width=4, parent=None):
        """ the constructor

        :param rect: the size of the handle
        :type rect: QRect
        :param parent: the parent widget
        :type parent: QWidget
        """
        super(Visualizer, self).__init__(parent)
        self.__width = width
        self.setRect(QRect(0, 0, int(width * 2), int(width * 2)))

    def setWidth(self, width):
        self.__width = int(width)
        self.setRect(QRect(0, 0, int(self.__width * 2), int(self.__width * 2)))

    def getWidth(self):
        return self.__width

    def setRect(self, rect):
        """ set the size for the handle

        :param rect: the new size for the handle
        :type rect: QRectF
        """
        self.rect = rect
        self.update()

    def paint(self, painter, option, widget):
        """ the painter, here we actually draw the control
        """
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def boundingRect(self):
        """ get the full size of the current widget

        :return: the bounding rect
        :rtype: QRectF
        """
        return QRectF(0, 0, self.__width * 2, self.__width * 2)


class NodeScene(QGraphicsScene):
    """ the graphics scene in which we draw everything
    """

    def __init__(self, baseRect):
        super(NodeScene, self).__init__()

        self.__undoStack = QUndoStack()

        self.baseRect = baseRect
        self.setSceneRect(baseRect)
        self.visualizingCircle = None
        self.createObjects()

    def createObjects(self):
        item = QGraphicsPixmapItem(QPixmap(":/NEX_selArrow.png"))
        position = QPointF(19.0, 22.0)
        item.setPos(position)
        self.addItem(item)

        self.visualizingCircle = Visualizer()
        position = QPointF(30 - self.visualizingCircle.getWidth(), 30.0 - self.visualizingCircle.getWidth())
        self.visualizingCircle.setPos(position)
        self.addItem(self.visualizingCircle)

    def changeCircleSize(self, inSize):
        self.visualizingCircle.setWidth(inSize)
        position = QPointF(30 - self.visualizingCircle.getWidth(), 30.0 - self.visualizingCircle.getWidth())
        self.visualizingCircle.setPos(position)

    def setBaseSize(self, inSize):
        """ set the size of the grid

        :param inSize: the size of the grid
        :type inSize: int
        """
        self.baseSize = inSize


class NodeView(QGraphicsView):
    """ simple graphics view with some default settings
    """

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget
        :type parent: QWidget
        """
        super(NodeView, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        windowCss = '''background-color: rgb(60,60,60); border: 1px solid rgb(90,70,30);'''
        self.setStyleSheet(windowCss)


class MmSearchDisplay(QWidget):
    """ the bezier graph windo which allows us to manipulate the curve
    """
    toolName = "mmSearchDisplay"

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget
        :type parent: QWidget
        """
        super(MmSearchDisplay, self).__init__(parent=parent)
        self.setLayout(nullVBoxLayout())

        self.baseSize = 60
        baseRect = QRect(0, 0, self.baseSize, self.baseSize)
        self.scene = NodeScene(baseRect)

        self.view = NodeView(self)
        self.view.setScene(self.scene)
        self.view.setGeometry(baseRect)
        self.view.setFixedSize(QSize(self.baseSize, self.baseSize))
        self.layout().addWidget(self.view)

    def changeCircleSize(self, inSize):
        self.scene.changeCircleSize(inSize)


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    from SkinningTools.Maya import interface
    mainWindow = interface.get_maya_window()
    mwd = QMainWindow(mainWindow)
    mwd.setWindowTitle("mm search Test window")
    wdw = MmSearchDisplay(parent=mainWindow)
    mwd.resize(QSize(70, 70))
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
