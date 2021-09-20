from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya import interface
from functools import partial
from math import *
from maya import cmds

_DEBUG = getDebugState()
_DIR = os.path.dirname(__file__)


class MarkingMenuFilter(QObject):
    """ the marking menu filter
    this eventfilter will grab mouse inputs and when the conditions are met it will spawn a popup window at the mouse location
    """
    _singleton = None

    def __init__(self, name="MarkingMenu", isDebug=False, parent=None):
        """ the constructor

        :param name: name for the object to be spawned
        :type name: string
        :param isDebug: if `True` will act as if most conditions are met, if `False` will work as intended
        :type isDebug: bool
        :param parent: the object to attach the popup menu too
        :type parent: QWidget
        """
        super(MarkingMenuFilter, self).__init__(parent)

        self.MMenu = radialMenu(interface.get_maya_window())
        self.__debug = isDebug
        self._storedValue = .5
        self.MenuName = name
        self.getBoneUnderMouse = False

    @staticmethod
    def singleton():
        """ singleton method
        making sure that this object can only exist once and cannot be instantiated more then once
        """
        if MarkingMenuFilter._singleton is None:
            MarkingMenuFilter._singleton = MarkingMenuFilter()
        return MarkingMenuFilter._singleton

    def eventFilter(self, obj, event):
        """ the event filter
        here we check if all conditions necessary for the widget to spawn are met
        """
        if MarkingMenuFilter is None:
            return False
        super(MarkingMenuFilter, self).eventFilter(obj, event)
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.getBoneUnderMouse = False
            return False

        if event.type() == QEvent.MouseButtonPress and event.button() == 4:
            sel = interface.getSelection()
            if sel == [] or not '.' in sel[0]:
                return False
            _selectMode = cmds.selectMode(q=True, component=True)
            if _selectMode:
                cmds.selectMode(object=True)
            _ini = os.path.join(_DIR, 'settings.ini')
            _settings = QSettings(_ini, QSettings.IniFormat)
            foundObjects = interface.objectUnderMouse(margin=int(_settings.value("mm_margin", 4)))
            if self.__debug:
                foundObjects = (True, "testBone")

            if foundObjects == (False, '') or foundObjects is False:
                return False
            if _selectMode:
                cmds.selectMode(component=True)
                cmds.select(sel, r=1)
            self.MMenu.setName(foundObjects[1])
            self.MMenu.showAtMousePos()
            return True

        self.MMenu.updateLine(QCursor.pos())

        if event.type() == QEvent.MouseButtonRelease and event.button() == 4:
            _curItem = self.MMenu.getActiveItem()
            if _curItem is not None:
                _curItem.runFunction()

            self._storedValue = self.MMenu.value
            self.MMenu.hide()
        return False


class radialMenu(QMainWindow):
    """ marking menu popup window
    this window will spawn without frame or background
    we draw everything in this window with QGraphicsScene items
    the window should remove itself when the mouse button is released returning info on the object that is under the mouse

    :todo: make a connection with the main widget to override certain values in the setup
    """
    _red = QColor(208, 52, 52, 255)
    _green = QColor(80, 230, 80, 255)

    pen = QPen()
    brush = QBrush()
    brush.setStyle(Qt.SolidPattern)
    brush.setColor(_green)

    __borders = {"default": "border: 1px solid black;",
                 "hilite": "border: 2px solid #50E650;"}
    __geoSize = 800
    __radius = 80
    _availableSpaces = 8

    def __init__(self, parent=None, flags=Qt.FramelessWindowHint):
        """ the constructor

        :param parent: the window to attach this ui to
        :type parent: QWidget
        :param flags: this flags default is to make sure we dont spawn a window, this could be overwritten for debug purposes
        :type flags: Qt.window flags
        """
        super(radialMenu, self).__init__(parent, flags)
        # @note: clean this part up!!

        self.OrigPos = QPoint()
        self.mappingPos = QPoint(self.__geoSize * .5, self.__geoSize * .5)
        self.uiObjects = []
        self.__ActiveItem = None
        self.setFixedSize(self.__geoSize, self.__geoSize)
        self.checkState = interface.getSmoothAware()
        self.inputObject = ''
        self._value = .5

        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)
        self.view.setScene(self.scene)
        self.view.setSceneRect(self.frameGeometry())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setMouseTracking(True)

        self.setCentralWidget(self.view)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QWidget{background-color: rgba(100,0, 0, 50);background : transparent; border : none}")
        self.__drawUI()
        self._buildButtons()

    def _setValue(self, value):
        if not type(value) in [int, float]:
            return
        self._value = value
        self.remitem.setText("rem weight: %s" % self._value)
        self.additem.setText("add weight: %s" % self._value)

    def _getValue(self):
        return self._value

    value = property(_getValue, _setValue)

    def _setPen(self, color, width, style):
        """ override function to change the pen style of the widget

        :param color: the color to be used in drawing
        :type color: QColor
        :param width: widht of the pen stroke
        :type width: int
        :param style: style of the stroke (single line/ dash pattern)
        :type style: Qt.penStyle
        """
        self.pen.setStyle(style)
        self.pen.setWidth(width)
        self.pen.setColor(color)

    def __drawUI(self):
        """ build the ui, 
        the main ui is a circle on which we can spawn the necessary buttons
        """
        self._setPen(self._red, 2, Qt.DotLine)
        backgroundCircle = QGraphicsEllipseItem(-self.__radius + self.mappingPos.x(), -self.__radius + self.mappingPos.y(), self.__radius * 2, self.__radius * 2)
        backgroundCircle.setPen(self.pen)

        self._setPen(self._green, 5, Qt.SolidLine)
        self.itemToDraw = QGraphicsLineItem()
        circles = []
        for _ in range(2):
            circle = QGraphicsEllipseItem(-2.5 + self.mappingPos.x(), -2.5 + self.mappingPos.y(), 5, 5)
            circle.setPen(self.pen)
            circle.setBrush(self.brush)
            circles.append(circle)

        self.itemToDraw.startCircle = circles[0]
        self.itemToDraw.endCircle = circles[1]

        self.itemToDraw.setPen(self.pen)
        self.itemToDraw.setPos(QPoint(0, 0))

        for item in [backgroundCircle, circles[0], circles[1], self.itemToDraw]:
            self.scene.addItem(item)

    def updateLine(self, pos):
        """ a line from the center of the circle to the position of the mouse
        this to display which element will be chosen on mouse release
        the collision of the line with any of the buttons will show an outline on the object to highlite the selection

        :param pos: position of the mouse
        :type pos: QPos
        """
        if not self.isVisible():
            return

        line = self.mappingPos.x(), self.mappingPos.y(), pos.x() - self.OrigPos.x() + self.mappingPos.x(), pos.y() - self.OrigPos.y() + self.mappingPos.y()
        self.itemToDraw.setLine(*line)
        # old = line
        line = QLineF(*line)

        self.itemToDraw.endCircle.setPos(QPoint(pos.x() - self.OrigPos.x(), pos.y() - self.OrigPos.y()))

        self.__ActiveItem = None
        for item in self.uiObjects:
            rect = item.geometry()
            item.setStyleSheet(self.__borders["default"])
            if self.__ActiveItem:
                continue
            if QLineF.BoundedIntersection == QLineF(rect.topLeft(), rect.topRight()).intersect(line)[0] or \
                    QLineF.BoundedIntersection == QLineF(rect.topRight(), rect.bottomRight()).intersect(line)[0] or \
                    QLineF.BoundedIntersection == QLineF(rect.bottomLeft(), rect.bottomRight()).intersect(line)[0] or \
                    QLineF.BoundedIntersection == QLineF(rect.topLeft(), rect.bottomLeft()).intersect(line)[0]:
                item.setStyleSheet(self.__borders["hilite"])
                self.__ActiveItem = item

    def getActiveItem(self):
        """ return the activated item that is in collision with the mouse

        :return: widget under mouse
        :rtype: QWidget
        """
        return self.__ActiveItem

    @staticmethod
    def rotateVec(origin, point, angle):
        """ angular math to get the correct positions on a circle based on center, length and angle

        :param origin: center of the circle
        :type origin: QPos
        :param point: top point of the circle (12 o`clock)
        :type point: QPos
        :param angle: the angle at wich to rotate the point clockwise
        :type angle: QPos
        :return: position on the circle at the given angle
        :rtype: QPos
        """
        qx = origin.x() + cos(angle) * (point.x() - origin.x()) - sin(angle) * (point.y() - origin.y())
        qy = origin.y() + sin(angle) * (point.x() - origin.x()) + cos(angle) * (point.y() - origin.y())
        return QPointF(qx, qy)

    def setName(self, inName):
        self.inputObject = inName
        self.mainItem.setText(inName)
        self.mainItem.setStyleSheet(self.__borders["default"])
        self.mainItem.setAlignment(Qt.AlignCenter)
        w = QPainter().fontMetrics().width(self.mainItem.text()) + 10
        position = self.mainItem.curPos
        self.mainItem.setGeometry(position.x() - (w * .5), position.y() - 10.5, w, 21)

    def __MMButton(self, inText, position, inValue=None, inFunction=None, operation=1):
        """ single marking menu button

        :param inText: the text to display
        :type inText: string
        :param position: position on the circle
        :type position: QPos
        :param inValue: the value it will represent
        :type inValue: float
        :param inFunction: the function to run once triggered
        :type inFunction: <function>
        :param operation: the operation on how to treat the weight
        :type operation: int
        :note operation: { 0:removes the values, 1:sets the values, 2: adds the values}
        :return: the widget with all functionality
        :rtype: QLabel
        """
        item = QLabel(inText)
        item.setStyleSheet(self.__borders["default"])
        item.setAlignment(Qt.AlignCenter)
        w = QPainter().fontMetrics().width(item.text()) + 10
        item.setGeometry(position.x() - (w * .5), position.y() - 10.5, w, 21)
        if inFunction is not None:
            item.runFunction = partial(inFunction, item, inValue, operation)
        return item

    def __MMCheck(self, inText, position, inValue=True, inFunction=None):
        """ single marking menu checkbox 

        :param inText: the text to display
        :type inText: string
        :param position: position on the circle
        :type position: QPos
        :param inValue: the value it will represent
        :type inValue: float
        :param inFunction: the function to run once triggered
        :type inFunction: <function>
        :return: the widget with all functionality
        :rtype: QCheckBox
        """
        item = QCheckBox(inText)
        item.setChecked(inValue)
        item.setStyleSheet(self.__borders["default"])
        w = QPainter().fontMetrics().width(item.text()) + 20
        item.setGeometry(position.x() - (w * .5) - 2, position.y() - 11.5, w + 4, 21)
        if inFunction is not None:
            item.runFunction = partial(inFunction, item)
        return item

    def _buildButtons(self):
        """ build up the marking menu based on given bone and all elements necessary
        """
        angle = pi / self._availableSpaces
        angle += angle
        origin = QPointF(0, 0)
        basePos = QPointF(0, -self.__radius)
        offset = QPointF(self.mappingPos.x(), self.mappingPos.y())

        positionList = []
        [positionList.append(self.rotateVec(origin, basePos, i * angle) + offset) for i in range(self._availableSpaces)]

        # ---- label -----
        self.mainItem = self.__MMButton('test', positionList[0], self._value, self._changeVal)
        self.mainItem.curPos = positionList[0]
        self.scene.addWidget(self.mainItem)
        self.uiObjects.append(self.mainItem)

        # ---- surfaceAware -----
        item = self.__MMCheck("surface aware", positionList[4], self.checkState, self._setCheckState)
        self.scene.addWidget(item)
        self.uiObjects.append(item)

        # ----- setVal -----
        _dict = {2: 1, 3: .5, 6: 0}
        for key, val in _dict.items():
            item = self.__MMButton("set weight: %s" % val, positionList[key], val, self.__funcPressed)
            self.scene.addWidget(item)
            self.uiObjects.append(item)

        # ------ remove val -----
        item = self.__MMButton("rem weight: 1", positionList[5], 1, self.__funcPressed, 0)
        self.scene.addWidget(item)
        self.uiObjects.append(item)

        self.remitem = self.__MMButton("rem weight: %s" % self._value, positionList[7], self._value, self.__funcPressed, 0)
        self.scene.addWidget(self.remitem)
        self.uiObjects.append(self.remitem)

        # ------ add val -----
        self.additem = self.__MMButton("add weight: %s" % self._value, positionList[1], self._value, self.__funcPressed, 2)
        self.scene.addWidget(self.additem)
        self.uiObjects.append(self.additem)

        return True

    def _changeVal(self, item, value, operation=0):
        _popup = SimplePopupSpinBox(parent=interface.get_maya_window(), value=self._value)
        self._setValue(_popup.input.value())

    def __funcPressed(self, _, value, operation=0):
        """ function that will run when a button is clicked

        :param value: the value that will be set on the selection
        :type value: float
        :param operation: the operation on how to treat the weight
        :type operation: int
        :note operation: { 0:removes the values, 1:sets the values, 2: adds the values}
        :note: we check for selection again just to make sure it only works on the component level
        """

        sel = interface.getSelection()
        if sel == [] or not '.' in sel[0]:
            return False

        if operation != 1 and value != 1:
            value = self._value
        interface.doSkinPercent(self.inputObject, value, operation=operation)

    def _setCheckState(self, item, *_):
        """ function that will run once the checkbox state has changed
        in this case it will change soft selection settings 

        :param item: the checkbox
        :type item: QCheckbox
        """
        self.checkState = not item.isChecked()
        interface.setSmoothAware(self.checkState)

    def showAtMousePos(self):
        """ show the current setup at the position on screen where the mouse is located, 
        the center of the circle is positioned directly on the mouse
        """
        self.OrigPos = QCursor.pos()
        self.move(self.OrigPos.x() - (self.width() * .5), self.OrigPos.y() - (self.height() * 0.5))
        self.show()
        return True


class testWidget(QMainWindow):
    """simple widget to install the eventfilter on to test the markingmenu
    this will not use the dcc application but a seperate window, where debug is forced so it will always draw the popup window
    """

    def __init__(self, parent=None):
        super(testWidget, self).__init__(parent)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        self.setWindowFlags(Qt.Tool)

        _MMfilter = MarkingMenuFilter(isDebug=True, parent=self)
        self.installEventFilter(_MMfilter)


def testUI():
    """ convenience function to display and build the testing application
    """
    window_name = 'testWidget'
    from SkinningTools.Maya import api
    mainWindow = api.get_maya_window()

    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == window_name:
                child.close()
                child.deleteLater()
    window = testWidget(mainWindow)
    window.setObjectName(window_name)
    window.setWindowTitle(window_name)
    window.show()

    return window
