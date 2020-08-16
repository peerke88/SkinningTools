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
    def __init__(self, name = "MarkingMenu", parent = None):
        super(ToolTipFilter, self).__init__(parent)
        self.MenuName = name  
        self.popup = None 
        self.getBoneUnderMouse = False
        # self.setMouseTracking(True)
        print "test"
    
    def eventFilter(self, obj, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.getBoneUnderMouse = False
            return False

        
        if ( event.type() == QEvent.MouseButtonPress and event.button() == 4):
            print "mousePressed"
            foundObjects = objectUnderMouse()
            print foundObjects

            if foundObjects == (False, '') or foundObjects is False:
                return False
            
            
            mainWin = wrapinstance( long( OpenMayaUI.MQtUtil.mainWindow() ) )

            self.popup = radialMenu(mainWin, foundObjects, self)
            self.popup.showAtMousePos()
            return True
        
        if self.popup is not None:
            # print QCursor.pos()
            self.popup.updateLine(QCursor.pos())

        # do this on mouse press, show the menu and kill it when released, activate button under mouse!
        if (event.type() == QEvent.MouseButtonRelease and event.button() == 4): 
            print "mouse released"
            if self.popup is None:
                return True

            # gather information on object undre mouse? mayeb from global or scene position!
            # pos = QCursor.pos()
            # nPos = self.popup.graphicsView.mapFromGlobal(pos)
            # print nPos
            # self.popup.scene.itemAt(QPointF(nPos.x(), nPos.y()))

            self.popup.hide()
            self.popup.deleteLater()
            self.popup = None
            return True


class radialMenu(QMainWindow):
    brush = QBrush()
    brush.setStyle( Qt.SolidPattern )
    brush.setColor( QColor( 80, 230, 80, 255 ) ) 

    pen = QPen()
    pen.setStyle( Qt.SolidLine )
    pen.setWidth( 1 )
    pen.setColor( QColor( 104, 104, 104, 255 ) ) 

    __radius = 70
    def __init__(self, parent=None, inputObjects = [], parentObject = None, flags=Qt.FramelessWindowHint):
        super(radialMenu, self).__init__(parent, flags)
        self.__geoSize = 800
        self.OrigPos = QPoint()
        self.mappingPos = QPoint(self.__geoSize*.5, self.__geoSize*.5)
        self.setFixedSize(self.__geoSize, self.__geoSize)
        self.checkState = cmds.softSelect(q=True, softSelectFalloff= True)
        self.inputObjects = inputObjects
        self.scene = QGraphicsScene()
        self.parentObject = parentObject
        self.graphicsView = QGraphicsView()
        self.graphicsView.setScene( self.scene )
        self.graphicsView.setSceneRect(self.frameGeometry())
        self.graphicsView.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.graphicsView.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setCentralWidget(self.graphicsView)
        self.graphicsView.setMouseTracking(True)
        self.setAttribute(  Qt.WA_TranslucentBackground , True)
        self.setStyleSheet("QWidget{background-color: rgba(100,0, 0, 50);background : transparent; border : none}")

        nPen = QPen()
        nPen.setStyle( Qt.DotLine )
        nPen.setWidth( 2 )
        nPen.setColor( QColor( 208, 52, 52, 255 ) ) 
        item = QGraphicsEllipseItem(-self.__radius + self.mappingPos.x(),-self.__radius + self.mappingPos.y(),self.__radius*2,self.__radius*2)
        item.setPen(nPen)
        self.scene.addItem(item)
        
        self._buildButtons()

        baseColor = QColor(80, 230, 80, 255)
        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(5)
        pen.setColor(baseColor)
    
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(baseColor) 

        self.itemToDraw = QGraphicsLineItem()
        self.itemToDraw.setPen(pen)
        self.itemToDraw.setPos(QPoint(0,0))
        self.scene.addItem(self.itemToDraw)

    def updateLine(self, pos):
        self.itemToDraw.setLine(self.mappingPos.x(),self.mappingPos.y(), 
                                pos.x() - self.OrigPos.x()+ self.mappingPos.x(), 
                                pos.y() - self.OrigPos.y()+ self.mappingPos.y())

    def rotateVec(self, origin, point, angle):
        qx = origin.x + cos(angle) * (point.x - origin.x) - sin(angle) * (point.y - origin.y)
        qy = origin.y + sin(angle) * (point.x - origin.x) + cos(angle) * (point.y - origin.y)
        return  OpenMaya.MVector(qx, qy, 0.0)

    def _buildButtons(self):
        _availableSpaces = 8
        #@note change these buttons to bone setup marking menu
        angle = (pi/(_availableSpaces))*2
        origin = OpenMaya.MVector()
        basePos = OpenMaya.MVector(0,-self.__radius,0)
        offset = OpenMaya.MVector(self.mappingPos.x(), self.mappingPos.y(),0)
        denom = 0
        positionList = []
        [positionList.append(self.rotateVec(origin, basePos, (i - denom)*angle) + offset) for i in xrange(_availableSpaces)]


        # ---- label -----
        item = QLabel(self.inputObjects[1])
        item.setAlignment(Qt.AlignCenter)
        w = QPainter().fontMetrics( ).width( item.text()) + 10
        item.setGeometry(positionList[0].x-(w*.5),positionList[0].y-10.5, w, 21)
        self.scene.addWidget(item)


        # ---- surfaceAware -----
        item = QCheckBox("surface aware")
        item.setChecked(self.checkState)
        w = QPainter().fontMetrics( ).width( "surface aware") + 20
        item.setGeometry(positionList[5].x-(w*.5),positionList[5].y-11.5, w, 23)
        item.stateChanged.connect(self._setCheckState)

        self.scene.addWidget(item)

        # ----- setVal -----
        _dict = {2:1, 3:.5, 6:0}
        for key, val in _dict.iteritems():
            item = QLabel("set weight: %s"%val)
            item.setAlignment(Qt.AlignCenter)
            w = QPainter().fontMetrics( ).width( item.text()) + 10
            item.setGeometry(positionList[key].x-(w*.5),positionList[key].y-10.5, w, 21)
            self.scene.addWidget(item)

        # #move this over to the main menu?
        # # ---- incrementalVal ---
        # for i in xrange(9):
        #     item = QLabel("increment: %s"%(.1*(i+1)))
        #     item.setAlignment(Qt.AlignCenter)
        #     w = QPainter().fontMetrics( ).width( item.text()) + 10
        #     item.setGeometry(positionList[4].x-(w*.5),positionList[4].y-10.5, w, 21)
        #     self.scene.addWidget(item)
        #     positionList[4] += OpenMaya.MVector(0,23,0)
        return True

    def __funcPressed(self, *args):
        print self.sender().text()

    def _setCheckState(self):
        self.checkState = self.sender().isChecked()
        cmds.softSelect(e=True, softSelectFalloff= self.checkState)

    def showAtMousePos(self):
        self.OrigPos = QCursor.pos()
        self.move(self.OrigPos.x()-(self.width() * .5), self.OrigPos.y()- (self.height()*0.5))
        self.show()
        return True

# to test the functions
def forceInstallFilter():
    filter = ToolTipFilter()

    for x in xrange(OpenMayaUI.M3dView.numberOf3dViews()):    
        view =  OpenMayaUI.M3dView() 

        OpenMayaUI.M3dView.get3dView(x, view)
        viewWidget = wrapinstance(view.widget())
        try:
            viewWidget.removeEventFilter(view._customFilter)
        except:
            pass
        view._customFilter = ToolTipFilter(parent = viewWidget)
        viewWidget.installEventFilter(view._customFilter) 


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