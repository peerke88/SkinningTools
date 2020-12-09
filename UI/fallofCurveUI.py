# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
import math, re


class BezierFunctions(object):
    """ collection object for all functions that help create bezier curves
    https://en.wikipedia.org/wiki/B%C3%A9zier_curve
    """
    @staticmethod
    def binomial(i, n):
        """ binomial function 

        :param i: current 2d point to calculate from
        :type i: list
        :param n: total amount of points 
        :type n: int
        :return: weight
        :rtype: float
        """
        return math.factorial(n) / float(
            math.factorial(i) * math.factorial(n - i))

    @staticmethod
    def bernstein(t, i, n):
        """bernstein function

        :param t: position in 2d space based on the weight of current given point i
        :type t: float
        :param i: current 2d point to calculate from
        :type i: list
        :param n: total amount of points 
        :type n: int
        :return: weight
        :rtype: float
        """
        return BezierFunctions.binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))

    @staticmethod
    def bezier(t, points):
        """bezier function

        :param t: parameter on the curve to get the positional information (range is from 0 to 1)
        :type t: float
        :param points:control points that are used to generate the curve
        :type points: list
        :return: 2d point in space
        :rtype: list
        """
        n = len(points) - 1
        x = y = 0
        for i, pos in enumerate(points):
            bern = BezierFunctions.bernstein(t, i, n)
            x += pos[0] * bern
            y += pos[1] * bern
        return x, y

    @staticmethod
    def bezierCurveYfromX(inX, points):
        """ get the y position on the curve by giving the x
        :note: the amount of points used here to generate the curve is 101, this way its easier to get percentage data

        :param inX: the x position on the graph
        :type inX: float
        :param point: list of points generated by the bezier functions
        :type points: list
        :return: y value represented by X
        :rtype: float
        """
        fullList = {}
        for i in range(101):
            x, y = BezierFunctions.bezier(i * 0.01, points)

            fullList[x] = y

        if inX in fullList.keys():
            return fullList[inX]

        takeClosest = lambda num, collection: min(collection, key=lambda x: abs(x - num))
        nv = takeClosest(inX, fullList.keys())
        return fullList[nv]

    @staticmethod
    def bezier_curve_range(n, points):
        """ bezier point generator

        :param n: amount of points to generate
        :type n: int
        :param points: control points that are used to generate the curve
        :type points: list
        :return: list of bezier points the size of the given amount
        :rtype: list
        """
        for i in range(n):
            t = i / float(n - 1)
            yield BezierFunctions.bezier(t, points)

    @staticmethod
    def getDataOnPercentage(percentage, npts):
        """ get the data of the curve based on the percentage on the curve itself

        :param percentage: percentage on the curve
        :type percentage: float
        :param npts: control points that are used to generate the curve
        :type npts: list 
        :return: 2d point in space for given data
        :rtype: list
        """
        baseSize = npts[-1][0]
        # t, v = BezierFunctions.bezier(percentage, npts)
        return (BezierFunctions.bezierCurveYfromX(percentage * baseSize, npts) / baseSize)


class BezierCurve(QGraphicsPathItem):
    """ painterpath class to help draw the bezier curve
    """
    pen = QPen(Qt.green, 2, Qt.SolidLine)

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(BezierCurve, self).__init__(parent)
        self.setZValue(-1)
        self._rect = QRectF()
        self._boundingRect = None
        self.points = []

    def _updatePath(self, points):
        """ the update path function, given the points it will calculate the new path

        :param points: list of 2d points
        :type points: list
        """
        self.points = points
        path = QPainterPath()
        path.moveTo(points[0])
        path.cubicTo(*points[1:])
        self._rect = path.boundingRect()
        self.setPath(path)

    def boundingRect(self):
        """  get the current bounding box of the path

        :return: the bounding box
        :rtype: QRectF
        """
        return QRectF(self._boundingRect or self._rect)

    def paint(self, painter, option, widget):
        """ the painter, here we actually draw the curve
        """
        painter.setPen(self.pen)
        painter.drawPath(self.path())


class NodeMoveCommand(QUndoCommand):
    """ simple undo override to help with undoing movement in the qt window
    """
    def __init__(self, scene, node, oldPosition, newPosition, description=None, parent=None):
        """ the constructor

        :param scene: the scene in which we move the items
        :type scene: QGraphicsScene
        :param node: the node that will be moved
        :type node: NodeItem
        :param oldPosition: previous position
        :type oldPosition: Qpos
        :param newPosition: new position
        :type newPosition: QPos
        :param description: description to give the undo function of whats happening
        :type description: string
        :param parent: the parent widget
        :type parent: QWidget
        """
        super(NodeMoveCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)
        self.__scene = scene
        self.__node = node
        self.__oldPosition = oldPosition
        self.__newPosition = newPosition

    def redo(self):
        """ the redo function
        """
        super(NodeMoveCommand, self).redo()
        self.__node.setPos(self.__newPosition)
        self.__scene.updateCurve()

    def undo(self):
        """ the undo function
        """
        super(NodeMoveCommand, self).undo()
        self.__node.setPos(self.__oldPosition)
        self.__scene.updateCurve()


class NodeSwitchCommand(QUndoCommand):
    """ simple undo override to help with undoing curve style switch in the qt window
    """
    def __init__(self, scene, oldPositions, newPositions, description=None, parent=None):
        """ the constructor

        :param scene: the scene in which we move the items
        :type scene: QGraphicsScene
        :param node: the node that will be moved
        :type node: NodeItem
        :param oldPosition: previous position
        :type oldPosition: Qpos
        :param newPosition: new position
        :type newPosition: QPos
        :param description: description to give the undo function of whats happening
        :type description: string
        :param parent: the parent widget
        :type parent: QWidget
        """
        super(NodeSwitchCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)
        self.__scene = scene
        self.__oldPositions = oldPositions
        self.__newPositions = newPositions

    def redo(self):
        """ the redo function
        """
        super(NodeSwitchCommand, self).redo()
        self.__scene.setPointPositions(self.__newPositions)

    def undo(self):
        """ the undo function
        """
        super(NodeSwitchCommand, self).undo()
        self.__scene.setPointPositions(self.__oldPositions)


class NodeItem(QGraphicsItem):
    """ the node items that will serve as handles for the bezier curve
    """
    width = 10
    gradient = QRadialGradient(width * .75, width * .75, width * .75, width * .75, width * .75)
    gradient.setColorAt(0, QColor.fromRgbF(1, .5, .01, 1))
    gradient.setColorAt(1, QColor.fromRgbF(1, .6, .06, 1));

    brush = QBrush(gradient)
    brush.setStyle(Qt.RadialGradientPattern)

    pen = QPen()
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(2)
    pen.setColor(QColor(104, 104, 104, 255))  # outline not selected

    selPen = QPen()
    selPen.setStyle(Qt.SolidLine)
    selPen.setWidth(2)
    selPen.setColor(QColor(67, 255, 163, 255))  # outline selected

    def __init__(self, rect=None, parent=None):
        """ the constructor

        :param rect: the size of the handle
        :type rect: QRect
        :param parent: the parent widget
        :type parent: QWidget
        """
        super(NodeItem, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        if rect != None:
            self.setRect(rect)
        else:
            self.setRect(QRect(0, 0, 10, 10))
        self.lockXPos = False

        self.snap = False

    def setSnap(self, snapValue):
        """ set the node to be able to snap to a certain grid

        :param snapValue: size of the grid
        :type snapValue: int
        """
        self.snap = snapValue

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
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def boundingRect(self):
        """ get the full size of the current widget

        :return: the bounding rect
        :rtype: QRectF
        """
        return QRectF(0, 0, 20, 20)

    def setLockXPos(self, inPos):
        """ make sure that the object cannot move away from the locked position

        :param inPos: the position in x to lock the control to
        :type inPos: float
        """
        self.lockXPos = inPos

    def mousePressEvent(self, event):
        """ starting position to be captured on first mouse press

        :param event: event to trigger
        :type event: QEvent
        """
        self.currentPos = self.pos()
        super(NodeItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ drag event to take place and update the drawing of elements

        :param event: event to trigger
        :type event: QEvent
        """
        super(NodeItem, self).mouseMoveEvent(event)
        curOffset = -self.width * .5
        scX = min(max(event.scenePos().x(), curOffset), self.scene().baseSize + curOffset)
        scY = min(max(event.scenePos().y(), curOffset), self.scene().baseSize + curOffset)
        if self.lockXPos != False:
            scX = self.lockXPos

        if self.snap != False:
            def convert(input, snapValue):
                return round((float(input) / snapValue)) * snapValue

            scX = convert(scX, self.snap)
            scY = convert(scY, self.snap)

        self.newPos = QPointF(scX, scY)
        self.setPos(self.newPos)
        self.scene().updateCurve()

    def mouseReleaseEvent(self, event):
        """ final position of the nodehandle to cover

        :param event: event to trigger
        :type event: QEvent
        """
        super(NodeItem, self).mouseReleaseEvent(event)

        if self.newPos == None:
            return
        self.scene().getUndoStack().push(NodeMoveCommand(self.scene(), self, self.currentPos, self.newPos))
        self.newPos = None


class NodeScene(QGraphicsScene):
    """ the graphics scene in which we draw everything
    """
    def __init__(self, baseRect):
        """ the constructor

        :param baseRect: the size of the scene to work with
        :type baseRect: QRect
        """
        super(NodeScene, self).__init__()

        self.__undoStack = QUndoStack()

        self.pointObjects = []
        self.bezier = None
        self.baseSize = 300
        self.baseRect = baseRect
        self.setSceneRect(baseRect)

        self.undoAction = self.getUndoStack().createUndoAction(self)
        self.redoAction = self.getUndoStack().createRedoAction(self)

        self.createGrid()
        self.createGrid(10, Qt.black, Qt.DotLine)
        self.createControls()

    def createGrid(self, divider=4, color=Qt.darkGray, line=Qt.DashLine):
        """ create a grid based on the current size and the divider

        :param divider: draw a line based on the divider to create the grid
        :type divider: int
        :param color: the color of the line to use
        :type color: QColor
        :param line: the linepattern to use while drawing the grid
        :type line: Qt.linestyle
        """
        pos = float(self.baseSize) / divider
        for div in range(divider):
            if div == 0:
                continue
            lineItem = QGraphicsLineItem(0, pos * div, self.baseSize, pos * div)
            lineItem.setZValue(-1)
            lineItem.setPen(QPen(color, 1, line))
            self.addItem(lineItem)

            lineItem = QGraphicsLineItem(pos * div, 0, pos * div, self.baseSize)
            lineItem.setZValue(-1)
            lineItem.setPen(QPen(color, 1, line))
            self.addItem(lineItem)

        pen = QPen(Qt.black, 1, Qt.SolidLine)
        rect = QGraphicsRectItem(self.baseRect)
        rect.setZValue(-1)
        self.addItem(rect)

    def createControls(self):
        """ create the nodeitem controls to spawn the curve
        """
        self.controlPoints = []
        pts = [QPoint(0, 0), QPoint(self.baseSize / 4.0, 0), QPoint(self.baseSize - (self.baseSize / 4.0), self.baseSize), QPoint(self.baseSize, self.baseSize)]
        for point in pts:
            controlPoint = NodeItem()
            self.addItem(controlPoint)
            controlPoint.setPos(point - QPoint(5, 5))
            self.controlPoints.append(controlPoint)
            self.addPoints(controlPoint)
        self.controlPoints[0].setLockXPos(-5.0)
        self.controlPoints[-1].setLockXPos(self.baseSize - 5.0)
        self.bCurve = BezierCurve()
        self.bCurve._updatePath(pts)
        self.setBezier(self.bCurve)
        self.addItem(self.bCurve)

    def setSnap(self, snapValue):
        """ set the snap value to all of the controls

        :param snapValue: size of the grid
        :type snapValue: int
        """
        for pt in self.controlPoints:
            pt.setSnap(snapValue)

    def keyPressEvent(self, event):
        """ triggers from keyboard presses

        :param event: event to trigger
        :type event: QEvent
        """
        modifiers = QApplication.keyboardModifiers()
        if type(event) == QKeyEvent:
            if modifiers != Qt.ControlModifier:
                return

            if event.key() == Qt.Key_Z:
                self.undoAction.trigger()
            elif event.key() == Qt.Key_Y:
                self.redoAction.trigger()

    def getUndoStack(self):
        """ get the object that handles the undo setup of this scene

        :return: the current undostack function
        :rtype: QUndoStack
        """
        return self.__undoStack

    def setPoints(self, inPointObjects):
        """ set the list of objects that will drive the curve

        :param inPointObjects: list of nodeitems
        :ytpe inPointObjects: list
        """
        self.pointObjects = inPointObjects

    def setPointPositions(self, inpts):
        """ function to override handle positions at once, this to make sure we can switch the curve

        :param inpts: list of 2d space positions
        :type inpts: list
        """
        for i, pt in enumerate(inpts):
            self.pointObjects[i].setPos(pt - QPoint(5, 5))
        self.updateCurve()

    def getPoints(self):
        """ get the current positions of all the handles

        :return: the positions of the handles
        :rtype: list
        """
        pts = []
        for obj in self.pointObjects:
            pt = QPointF(obj.pos().x() + 5, obj.pos().y() + 5)
            pts.append(pt)
        return pts

    def addPoints(self, inPointObject):
        """ add new control objects for the curve

        :param inPointObject: the new item to add for control
        :type inPointObject: NodeItem
        """
        self.pointObjects.append(inPointObject)

    def setBezier(self, inBezier):
        """ set the bezier QPainterPath

        :param inBezier: the curve to draw
        :type inBezier: QPainterPath
        """
        self.bezier = inBezier

    def updateCurve(self):
        """ update the curve path with the positions of the control handles
        """
        pts = self.getPoints()
        self.bezier._updatePath(pts)

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


class BezierGraph(QMainWindow):
    """ the bezier graph windo which allows us to manipulate the curve
    """
    closed = pyqtSignal()
    def __init__(self, parent =None):
        """ the constructor

        :param parent: the parent widget
        :type parent: QWidget
        """
        super(BezierGraph, self).__init__()
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        layout = QVBoxLayout(self.widget)
        self.BezierDict = {'bezier': [QPoint(0, 0), QPoint(75, 0), QPoint(225, 300), QPoint(300, 300)],
                           'linear': [QPointF(0.000000, 0.000000), QPointF(75.000000, 75.000000), QPointF(225.000000, 225.000000), QPointF(300.000000, 300.000000)]}

        self.settings = QSettings("bezierGraph", "graphPoints")

        self.baseSize = 300
        baseRect = QRect(0, 0, self.baseSize, self.baseSize)
        self.scene = NodeScene(baseRect)
        self.scene.setBaseSize(self.baseSize)

        self.view = NodeView(self)
        self.view.setScene(self.scene)
        self.view.setGeometry(baseRect)
        layout.addWidget(self.view)

        self.setMenuBar(QMenuBar())
        undo = self.menuBar().addAction(self.scene.undoAction)
        redo = self.menuBar().addAction(self.scene.redoAction)

        lay1 = QHBoxLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        self.cbox = QComboBox()
        self.cbox.setMinimumWidth(80)
        self.cbox.currentIndexChanged.connect(self.changeCurve)
        self.line1 = QLineEdit()
        self.line1.textEdited[unicode].connect(self.__lineEdit_FieldEditted)
        self.but1 = QPushButton("store")
        self.but2 = QPushButton("del")
        self.but1.clicked.connect(self.storeValues)
        self.but2.clicked.connect(self.delValues)

        check = QCheckBox("snap")
        check.toggled.connect(self.setSnap)
        check.setChecked(True)
        for qb in [self.cbox, self.line1, self.but1, self.but2]:
            qb.setMinimumHeight(23)
            lay1.addWidget(qb)

        lay1.addWidget(check)
        layout.addLayout(lay1)

        self.__qt_normal_color = QPalette(self.line1.palette()).color(QPalette.Base)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.updateView()
        self.__lineEdit_FieldEditted()
        self._loadCBox()

    def updateView(self):
        """ always scale the objects to fit the window
        """
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def setSnap(self):
        """ set the snap value for all the handles
        """
        self.scene.setSnap(False)
        if self.sender().isChecked():
            self.scene.setSnap(5)

    def __lineEdit_Color(self, inLineEdit, inColor):
        """ change the lineedit color 

        :param inLineEdit: the lineedit to change
        :type inLineEdit: QlineEdit
        :param inColor: color to set the line edit to
        :type inColor: QColor
        """
        PalleteColor = QPalette(inLineEdit.palette())
        PalleteColor.setColor(QPalette.Base, QColor(inColor))
        inLineEdit.setPalette(PalleteColor)

    def __lineEdit_FieldEditted(self, *args):
        """ check the edit of the current text field, block information if wrong characters are used
        """
        Controller_name_text = self.line1.displayText()
        if FalseFolderCharacters(Controller_name_text) != None:
            self.__lineEdit_Color(self.line1, 'red')
            self.but1.setEnabled(False)
        elif Controller_name_text == "":
            self.but1.setEnabled(False)
        else:
            self.__lineEdit_Color(self.line1, self.__qt_normal_color)
            self.but1.setEnabled(True)

    def delValues(self):
        """ remove created curves form the settings when no longer necessary
        """
        if self.cbox.currentText() in ['bezier', 'linear']:
            return
        del self.BezierDict[self.cbox.currentText()]
        self.settings.setValue("graphPos", self.BezierDict)
        self._loadCBox()

    def storeValues(self):
        """ store user made curves into the combobox
        """
        pts = self.scene.bCurve.points
        self.BezierDict[self.line1.displayText()] = pts

        self.settings.setValue("graphPos", self.BezierDict)
        self._loadCBox()

    def _loadCBox(self):
        """ load different curves into the combobox for ease of access
        """
        self.cbox.clear()
        inDict = self.settings.value("graphPos", {})
        if len(inDict) > 2:
            self.BezierDict = inDict
        for key, value in self.BezierDict.items():
            self.cbox.addItem(key)

        self.scene.getUndoStack().clear()

    def changeCurve(self):
        """ change the current curve visual to one that has been stored before
        """
        if self.cbox.currentText() == '':
            return
        self.but2.setEnabled(not (self.cbox.currentText() in ['bezier', 'linear']))

        cp = self.BezierDict[self.cbox.currentText()]
        self.scene.getUndoStack().push(NodeSwitchCommand(self.scene, self.scene.getPoints(), cp))

    def curveAsPoints(self):
        """ get the generated curve as a list of 2d points

        :return: the curve as points
        :rtype: list
        """
        pts = self.scene.bCurve.points
        npts = []
        for pt in pts:
            npts.append([pt.x(), pt.y()])
        return npts

    def getDivisionData(self, divisions=11):
        """ get the data on the curve based on divisions

        :param divisions: amount of points to divide the curve with
        :type divisions: int
        :return: list of curve positions
        :rtype: list
        """
        percentage = 1 / (divisions - 1.0)
        l = []
        for i in range(divisions):
            l.append(i * percentage)
        return self.getDataOnPoints(l)

    def getDataOnPerc(self, percentage, npts=None):
        """ get the data on the curve based on divisions

        :param percentage: percentage on the curve
        :type percentage: float
        :param npts: points on the curve
        :type npts: list
        :return: position on the curve based on percentage of the parameter
        :rtype: list
        """
        if npts == None:
            npts = self.curveAsPoints()

        return BezierFunctions.getDataOnPercentage(percentage, npts)

    def getDataOnPoints(self, inList=(0.0, 0.2, 0.25, 0.5, 0.6, 0.66, 0.8, 1.0)):
        """ get the data of the curve based on different parameters
        
        :param inList: points on the curve based on parameters
        :type inList: list
        :return: positions on the curve based on the different parameters
        :rtype: list
        """
        percentageList = []
        for i in inList:
            percentageList.append(self.getDataOnPerc(i))
        return percentageList

    def resizeEvent(self, event):
        """ resize the grid and elements based on the resize of the window
        """
        super(BezierGraph, self).resizeEvent(event)
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def hideEvent(self, event):
        """ if this graph is hidden its save to call it closed
        """
        self.closed.emit()
        super(BezierGraph, self).hideEvent(event)
