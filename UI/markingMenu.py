from SkinningTools.UI.qt_util import *

from maya import cmds, mel, OpenMayaUI, OpenMaya
from functools import partial
from math import *

def objectUnderMouse(margin = 4, selectionType = "joint"):
    def selectFromScreenApi(x, y, x_rect=None, y_rect=None):
        # find object under mouse, (silently select the object using api and clear selection)
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
            
        args = [x, y]
        if x_rect!=None and y_rect!=None:
            OpenMaya.MGlobal.selectFromScreen(x, y, x_rect, y_rect, OpenMaya.MGlobal.kReplaceList)
        else:
            OpenMaya.MGlobal.selectFromScreen(x, y, OpenMaya.MGlobal.kReplaceList)
        objects = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(objects)
            
        OpenMaya.MGlobal.setActiveSelectionList(sel, OpenMaya.MGlobal.kReplaceList)
            
        fromScreen = []
        objects.getSelectionStrings(fromScreen)
        return fromScreen

    def getSelectionModeIcons():
        # fix if anything other then object selection is used
        if cmds.selectMode(q=1, object=1):
            selectmode = "object"
        elif cmds.selectMode(q=1, component=1):
            selectmode = "component"
        elif cmds.selectMode(q=1, hierarchical=1):
            selectmode = "hierarchical"
        return selectmode
        
    active_view = OpenMayaUI.M3dView.active3dView()
    pos = QCursor.pos()
    widget = QApplication.widgetAt(pos)
        
    try:
        relpos = widget.mapFromGlobal(pos)
    except:
        return False
    
    if selectionType == "joint":
        maskOn = cmds.selectType( q=True, joint=True )
        sm = getSelectionModeIcons()    
        mel.eval("changeSelectMode -object;")
        cmds.selectType( joint=True )
    foundObjects = selectFromScreenApi( relpos.x()-margin, 
                                        active_view.portHeight() - relpos.y()-margin, 
                                        relpos.x()+margin, 
                                        active_view.portHeight() - relpos.y()+margin )
    if selectionType == "joint":
        cmds.selectType( joint=maskOn )
        mel.eval("changeSelectMode -%s;"%sm)

    foundBone = False
    boneName = ''
    for fobj in foundObjects:
        if cmds.objectType(fobj) == selectionType:
            foundBone = True
            boneName = fobj
            break
    return foundBone, boneName
        
class ToolTipFilter(QObject):
    def __init__(self, name = "MarkingMenu", isDebug = False, parent = None):
        super(ToolTipFilter, self).__init__(parent)
        self.__debug = isDebug
        self.MenuName = name  
        self.popup = None 
        self.getBoneUnderMouse = False
    
    def eventFilter(self, obj, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.getBoneUnderMouse = False
            return False
        
        if ( event.type() == QEvent.MouseButtonPress and event.button() == 4):
            print "mousePressed"
            foundObjects = objectUnderMouse()
            if self.__debug:
                foundObjects = (True, "testBone")
            print foundObjects

            if foundObjects == (False, '') or foundObjects is False:
                return False
            
            mainWin = wrapinstance( long( OpenMayaUI.MQtUtil.mainWindow() ) )

            self.popup = radialMenu(mainWin, foundObjects)
            self.popup.showAtMousePos()
            return True
        
        if self.popup is not None:
            self.popup.updateLine(QCursor.pos())

        if (event.type() == QEvent.MouseButtonRelease and event.button() == 4): 
            print "mouse released"
            if self.popup is None:
                return True
            _curItem = self.popup.getActiveItem()
            if _curItem is not None:
                # this is the function of the button that is under the mouse
                _curItem.runFunction()

            self.popup.hide()
            self.popup.deleteLater()
            self.popup = None
            return True


class radialMenu(QMainWindow):
    _red = QColor( 208, 52, 52, 255 ) 
    _green =  QColor(80, 230, 80, 255)
    
    pen = QPen()
    brush = QBrush()
    brush.setStyle(Qt.SolidPattern)
    brush.setColor(_green)

    __borders = { "default": "border: 1px solid black;",
                  "hilite" : "border: 2px solid #50E650;"}
    __geoSize = 800
    __radius = 70
    _availableSpaces = 8
    def __init__(self, parent=None, inputObjects = [], flags=Qt.FramelessWindowHint):
        super(radialMenu, self).__init__(parent, flags)
        #@note: clean this part up!!
        
        self.OrigPos = QPoint()
        self.mappingPos = QPoint(self.__geoSize*.5, self.__geoSize*.5)
        self.uiObjects = []
        self.__ActiveItem = None
        self.setFixedSize(self.__geoSize, self.__geoSize)
        self.checkState = cmds.softSelect(q=True, softSelectFalloff= True)
        self.inputObjects = inputObjects

        self.scene = QGraphicsScene()
        graphicsView = QGraphicsView()
        graphicsView.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)
        graphicsView.setScene( self.scene )
        graphicsView.setSceneRect(self.frameGeometry())
        graphicsView.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        graphicsView.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        graphicsView.setMouseTracking(True)

        self.setCentralWidget(graphicsView)
        self.setAttribute(  Qt.WA_TranslucentBackground , True)
        self.setStyleSheet("QWidget{background-color: rgba(100,0, 0, 50);background : transparent; border : none}")
        self.__drawUI()
        self._buildButtons()
    
    def _setPen(self, color, width, style):
        self.pen.setStyle( style )
        self.pen.setWidth( width )
        self.pen.setColor( color ) 

    def __drawUI(self):
        self._setPen(self._red, 2, Qt.DotLine )
        backgroundCircle = QGraphicsEllipseItem(-self.__radius + self.mappingPos.x(),-self.__radius + self.mappingPos.y(),self.__radius*2,self.__radius*2)
        backgroundCircle.setPen(self.pen)
        
        self._setPen(self._green, 5, Qt.SolidLine )
        self.itemToDraw = QGraphicsLineItem()
        circles = []
        for i in xrange(2):
            circle = QGraphicsEllipseItem(-2.5 + self.mappingPos.x(),-2.5 + self.mappingPos.y(), 5, 5)
            circle.setPen(self.pen)
            circle.setBrush(self.brush)
            circles.append(circle)
        
        self.itemToDraw.startCircle = circles[0]
        self.itemToDraw.endCircle = circles[1]

        self.itemToDraw.setPen(self.pen)
        self.itemToDraw.setPos(QPoint(0,0))
        
        for item in [backgroundCircle, circles[0], circles[1], self.itemToDraw]:
            self.scene.addItem(item)

    def updateLine(self, pos):
        self.itemToDraw.setLine(self.mappingPos.x(),self.mappingPos.y(), 
                                pos.x() - self.OrigPos.x()+ self.mappingPos.x(), 
                                pos.y() - self.OrigPos.y()+ self.mappingPos.y())
        self.itemToDraw.endCircle.setPos(QPoint(pos.x() - self.OrigPos.x(), 
                                                pos.y() - self.OrigPos.y()))
        _hit = False
        for item in self.uiObjects:
            item.setStyleSheet(self.__borders["default"]) 
        for coll in self.itemToDraw.collidingItems():
            if isinstance(coll, QGraphicsEllipseItem):
                continue
            if not coll.widget() in self.uiObjects:
                continue
            coll.widget().setStyleSheet(self.__borders["hilite"]) 
            self.__ActiveItem = coll.widget()
            _hit = True

        if not _hit:
            self.__ActiveItem = None

    def getActiveItem(self):
        return self.__ActiveItem

    def rotateVec(self, origin, point, angle):
        qx = origin.x + cos(angle) * (point.x - origin.x) - sin(angle) * (point.y - origin.y)
        qy = origin.y + sin(angle) * (point.x - origin.x) + cos(angle) * (point.y - origin.y)
        return  OpenMaya.MVector(qx, qy, 0.0)

    def __MMButton(self, inText, position, inValue = None, inFunction = None):
        item = QLabel(inText)
        item.setStyleSheet(self.__borders["default"]) 
        item.setAlignment(Qt.AlignCenter)
        w = QPainter().fontMetrics( ).width( item.text()) + 10
        item.setGeometry(position.x-(w*.5), position.y-10.5, w, 21)
        if inFunction is not None:
            item.runFunction = partial(inFunction, item, inValue)
        return item

    def __MMCheck(self, inText, position, inVal = True, inFunction = None):
        item = QCheckBox(inText)
        item.setChecked(inVal)
        item.setStyleSheet(self.__borders["default"]) 
        w = QPainter().fontMetrics( ).width( item.text()) + 20
        item.setGeometry(position.x-(w*.5)-2, position.y-11.5, w+4, 21)
        if inFunction is not None:
            item.runFunction = partial(inFunction, item)
        return item

    def _buildButtons(self):
        angle = (pi/(self._availableSpaces))*2
        origin = OpenMaya.MVector()
        basePos = OpenMaya.MVector(0,-self.__radius,0)
        offset = OpenMaya.MVector(self.mappingPos.x(), self.mappingPos.y(),0)
        
        positionList = []
        [positionList.append(self.rotateVec(origin, basePos, i*angle) + offset) for i in xrange(self._availableSpaces)]

        # ---- label -----
        item = self.__MMButton(self.inputObjects[1], positionList[0])
        self.scene.addWidget(item)

        # ---- surfaceAware -----
        item = self.__MMCheck("surface aware",positionList[5],  self.checkState, self._setCheckState)
        self.scene.addWidget(item)
        self.uiObjects.append(item)

        # ----- setVal -----
        _dict = {2:1, 3:.5, 6:0}
        for key, val in _dict.iteritems():
            item = self.__MMButton("set weight: %s"%val, positionList[key], val, self.__funcPressed)
            self.scene.addWidget(item)
            self.uiObjects.append(item)
        return True

    def __funcPressed(self, item, value, *args):
        print item.text()

    def _setCheckState(self, item, *args):
        self.checkState = not item.isChecked()
        cmds.softSelect(e=True, softSelectFalloff= self.checkState)

    def showAtMousePos(self):
        self.OrigPos = QCursor.pos()
        self.move(self.OrigPos.x()-(self.width() * .5), self.OrigPos.y()- (self.height()*0.5))
        self.show()
        return True


class testWidget(QMainWindow):
    #simple widget to install the eventfilter on to test the markingmenu 
    def __init__(self, parent=None):
        super(testWidget, self).__init__(parent)
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        self.setWindowFlags(Qt.Tool)

        filter = ToolTipFilter(isDebug=True, parent = self)
        self.installEventFilter(filter)

def showTest():
    def get_maya_window():
        for widget in QApplication.allWidgets():
            try:
                if widget.objectName() == "MayaWindow":
                    return widget
            except:
                pass
        return None

    window_name = 'testWidget'
    mainWindow = get_maya_window()

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


# @note: original Code:
"""
 
    def eventFilter(self, obj, event):
        '''middle mouse event to apply skin weight values through a custom marking menu'''
        def cleanupContext():
            if cmds.popupMenu("ContextModModule", exists=True):
                cmds.deleteUI("ContextModModule")

        
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.getBoneUnderMouse = False
            return False

        if self.getBoneUnderMouse == False:
            cleanupContext()

        if event.type() == QEvent.MouseButtonPress and event.button() == 4:
            selectionForMM = cmds.ls(sl=True,fl=True)
            if len(selectionForMM) == 0:
                return False
            inObject = selectionForMM[0]

            self.getBoneUnderMouse, boneName  =  self.boneUnderMouse()
            if self.getBoneUnderMouse == False:
                return False

            SkinningTools.doCorrectSelectionVisualization(inObject) 
            
            if len(selectionForMM) == 0:
                return False 
            
            if "." in inObject:
                inObject = selectionForMM[0].split('.')[0]
            else:
                return False 
            
            if SkinningTools.skinCluster(inObject, True) == None:
                return False 

            cmds.popupMenu("ContextModModule", alt=False, ctl=False, button=2,mm=True,p="viewPanes", pmc=functools.partial( self.getItem, boneName ))
            
        if event.type() == QEvent.MouseButtonRelease and event.button() == 4: 
            self.getBoneUnderMouse = False
            
        return False


    def applySkinValues( self,skinValue, expandedVertices, skinCluster, inObject, operation, mesh,*args ):
        '''skin weight functions used in marking menu, currently using skinPercent (slow maya command) '''
        from skinningTool import SkinningToolsUI
        oldSelection = expandedVertices
        cmds.ConvertSelectionToVertices()
        allBones = cmds.skinCluster( mesh, q=True, influence=True )
        
        if not inObject in allBones:
            cmds.skinCluster( skinCluster, e=True, lw=False, wt = 0.0, ai= inObject )

        expandedVertices1 = self.skinTool.convertToVertexList(expandedVertices)
        # option for non soft selected which speeds it up big time
        cmds.select(expandedVertices1)
        if operation == 1:
            cmds.skinPercent( skinCluster, tv =[ inObject, skinValue ], normalize=True)
        elif operation == 4:
            cmds.skinPercent( skinCluster, tv =[ inObject, 0.0 ], normalize=True)
        elif operation == 3:
            # for loop assigning verts: little bit more costly operation but safe for removal of weight information
            for index, obj in enumerate( expandedVertices ):
                val = cmds.skinPercent( skinCluster, obj, transform = inObject, q=True, value=True )
                newVal = val +  skinValue 
                if newVal < 0.0:
                    newVal = 0.0
                cmds.skinPercent( skinCluster, obj, tv =[ inObject, newVal ], normalize=True)
        else:
            cmds.skinPercent( skinCluster, relative=True, tv =[ inObject, skinValue ], normalize=True)
                
        if cmds.softSelect( q=True, softSelectEnabled=True) == 1:
            # costly but only necessary when sof selection is used
            progressDialogue = QProgressDialog()
            # progressDialogue.setWindowModality(1)
            progressDialogue.show()
            progressDialogue.setValue(0)
            
            expandedVertices, weights = SkinningToolsUI.softSelection()
            percentage = 99.0/ len(expandedVertices)
            for index, obj in enumerate( expandedVertices ):
                if weights[index] == 1.0:
                    continue
                val = cmds.skinPercent( skinCluster, obj, transform = inObject, q=True, value=True )
                if operation == 0:
                    newVal = weights[ index ]
                elif operation == 1:
                    newVal = ( skinValue * weights[ index ] )
                elif operation == 2:
                    newVal = val + ( skinValue * weights[ index ] )
                    if newVal > 1.0:
                        newVal = 1.0
                elif operation == 3:
                    newVal = val + ( skinValue * weights[ index ] )
                    if newVal < 0.0:
                        newVal = 0.0
                else:
                    newVal = 0.0
                cmds.skinPercent( skinCluster, obj, tv =[ inObject, newVal ])
                progressDialogue.setValue(percentage * index )
                QApplication.processEvents()
            progressDialogue.setValue(100)
            progressDialogue.close()

        if ".f[" in oldSelection[0]:
            mask = "facet"
        elif ".e[" in oldSelection[0]:
            mask = "edge"
        elif ".cv[" in oldSelection[0]:
            mask = "controlVertex"
        elif ".pt[" in oldSelection[0]:
            mask = "latticePoint"
        else:
            mask = "vertex"

        mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
        mel.eval('doMenuComponentSelection("%s", "%s");'%(mesh, mask))

        cmds.select( oldSelection )

        #cleanup marking menu as button is pressed
        self.getBoneUnderMouse = False
        if cmds.popupMenu("ContextModModule", exists=True):
            cmds.deleteUI("ContextModModule")
"""