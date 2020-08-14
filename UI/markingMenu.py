from SkinningTools.UI.qt_util import *

from maya import cmds, mel, OpenMayaUI, OpenMaya
from functools import partial
from math import *

def objectUnderMouse():
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
    widget = qApp.widgetAt(pos)
        
    try:
        relpos = widget.mapFromGlobal(pos)
    except:
        return False

    margin = 4
    foundObjects = selectFromScreenApi( relpos.x()-margin, 
                                        active_view.portHeight() - relpos.y()-margin, 
                                        relpos.x()+margin, 
                                        active_view.portHeight() - relpos.y()+margin )
    
    toUse = None
    usedObject = None
    for fobj in foundObjects:
        connects = cmds.listConnections( fobj, s = 0, d = 1 )
        if connects is None:
            return 
        for conns in connects:
            if cmds.objectType( conns ) == "RigSystemDynamicParent":
                toUse = conns
                usedObject = fobj
    return usedObject, toUse 
        
class ToolTipFilter(QObject):
    def __init__(self):
        super(ToolTipFilter, self).__init__()
        self.MenuName = 'rigSystemSpaceSwitchMenu'  
        self.popup = None 
        self.isChecked = False
    
    def eventFilter(self, obj, event):
        if not ( QApplication.keyboardModifiers() == Qt.ControlModifier and event.type() == QEvent.MouseButtonPress and event.button() == 4):
            return False
        if event.type() == QEvent.MouseButtonRelease: 
            print(self.popup, "released")
            if self.popup is None:
                return True
            self.popup.hide()
            self.popup.deleteLater()
            return True
        test = objectUnderMouse()
        if test == (None, None) or test is None:
            return False
        
        mainWin = wrapinstance( long( OpenMayaUI.MQtUtil.mainWindow() ) )

        self.popup = radialMenu(mainWin, test, self)
        self.popup.showAtMousePos()
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
        self.setFixedSize(800, 800)
        self.checkState = False
        self.inputObjects = inputObjects
        self.scene = QGraphicsScene()
        self.parentObject = parentObject
        self.graphicsView = QGraphicsView(self.scene )
        self.setCentralWidget(self.graphicsView)
        self.graphicsView.setMouseTracking(True)
        self.setAttribute(  Qt.WA_TranslucentBackground , True)
        self.setStyleSheet("QWidget{background-color: rgba(100,0, 0, 50);background : transparent; border : none}")# 
        
        nPen = QPen()
        nPen.setStyle( Qt.DotLine )
        nPen.setWidth( 2 )
        nPen.setColor( QColor( 208, 52, 52, 255 ) ) 
        item = QGraphicsEllipseItem(-self.__radius,-self.__radius,self.__radius*2,self.__radius*2)
        item.setPen(nPen)
        self.scene.addItem(item)

    def rotateVec(self, origin, point, angle):
        qx = origin.x + cos(angle) * (point.x - origin.x) - sin(angle) * (point.y - origin.y)
        qy = origin.y + sin(angle) * (point.x - origin.x) + cos(angle) * (point.y - origin.y)
        return  OpenMaya.MVector(qx, qy, 0.0)

    def _buildButtons(self):
        #@note change these buttons to bone setup marking menu
        selectAttr = cmds.listConnections(self.inputObjects[1] +'.parentSelect', s=1, d=0, p=1)[0].split('.')[-1]
        if not cmds.attributeQuery(selectAttr, node=self.inputObjects[0], exists=True):
            return

        allSpaces = cmds.attributeQuery(selectAttr, node = self.inputObjects[0], listEnum  =1)[0].split(":")
        currentspace = cmds.getAttr("%s.%s"%(self.inputObjects[0], selectAttr), asString=True)
        
        angle = (pi/(len(allSpaces)-1))*2
        origin = OpenMaya.MVector()
        basePos = OpenMaya.MVector(0,-self.__radius,0)
        denom = 0
        for i, space in enumerate(allSpaces):
            if space == currentspace:
                denom = 1
                continue
            position = self.rotateVec(origin, basePos, (i - denom)*angle)
            w = QPainter().fontMetrics( ).width( space) + 10
            item = QPushButton(space)
            item.workData = space
            item.setGeometry(position.x-(w*.5),position.y-10.5, w, 21)
            self.scene.addWidget(item)
            item.clicked.connect(partial(self.spaceSwitchMatch, selectAttr, i))

        w = QPainter().fontMetrics( ).width("X") + 10
        item = QPushButton("X")
        item.setGeometry(-(w*.5),-11.5, w, 23)
        item.workData = "close"
        self.scene.addWidget(item)
        item.clicked.connect(self.close)

        nPos = basePos *-1.5
        text = "add keyFrames"
        item = QCheckBox(text)
        item.setChecked(self.parentObject.isChecked)
        w = QPainter().fontMetrics( ).width( text) + 20
        item.setGeometry(nPos.x-(w*.5),nPos.y-11.5, w, 23)
        item.stateChanged.connect(self._setCheckState)

        self.scene.addWidget(item)

    def _setCheckState(self, value):
        #@todo: find a way to keep the checkstate alive!
        # or check how to store or connect certain values
        if self.parentObject.isChecked:
            self.parentObject.isChecked = False
        else:
            self.parentObject.isChecked = True
        self.close()

    def spaceSwitchMatch(self, attrName, attrValue, *args):
        inputObject, dynparNode = self.inputObjects
        if self.parentObject.isChecked:
            currentTimeFrame = cmds.currentTime(query=True)
            frameBefore = currentTimeFrame - 1
            cmds.setKeyframe(inputObject, breakdown=0, hierarchy='none', controlPoints=0, shape=False, t=frameBefore)
        
        pos = cmds.xform(inputObject, q=1, ws=1, t=1)
        rot = cmds.xform(inputObject, q=1, ws=1, ro=1)
        cmds.setAttr("%s.%s"%(inputObject, attrName), attrValue)
        cmds.xform(inputObject, ws=1, t=pos)
        cmds.xform(inputObject, ws=1, ro=rot)

        if self.parentObject.isChecked:
            cmds.setKeyframe(inputObject, breakdown=0, hierarchy='none', controlPoints=0, shape=1)
        self.close()

    def mousePressEvent(self, event):
        # @todo: find a way to close the ui when transparent layer is pressed

        print("pressed!")

    def showAtMousePos(self):
        pos = QCursor.pos()
        self.move(pos.x()-(self.width() * .5), pos.y()- (self.height()*0.5))
        self.show()
        self._buildButtons()

#too Install
# filter = ToolTipFilter()

# for x in xrange(OpenMayaUI.M3dView.numberOf3dViews()):    
#     view =  OpenMayaUI.M3dView() 
#     OpenMayaUI.M3dView.get3dView(x, view)
#     view._customFilter = filter 
#     viewWidget = wrapinstance(view.widget())
#     viewWidget.removeEventFilter(view._customFilter)
#     viewWidget.installEventFilter(view._customFilter) 


# @note: original Code:
"""
    def boneUnderMouse(self):
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
        widget = qApp.widgetAt(pos)
        
        try:
            relpos = widget.mapFromGlobal(pos)
        except:
            return False

        margin = 4
        maskOn = cmds.selectType( q=True, joint=True )
        sm = getSelectionModeIcons()    
        mel.eval("changeSelectMode -object;")
        cmds.selectType( joint=True )
        foundObjects = selectFromScreenApi( relpos.x()-margin, 
                                            active_view.portHeight() - relpos.y()-margin, 
                                            relpos.x()+margin, 
                                            active_view.portHeight() - relpos.y()+margin )
        cmds.selectType( joint=maskOn )
        mel.eval("changeSelectMode -%s;"%sm)

        foundBone = False
        boneName = ''
        for fobj in foundObjects:
            if cmds.objectType(fobj) == "joint":
                foundBone = True
                boneName = fobj
                break
        return foundBone, boneName

    def eventFilter(self, obj, event):
        '''middle mouse event to apply skin weight values through a custom marking menu'''
        def cleanupContext():
            if cmds.popupMenu("ContextModModule", exists=True):
                cmds.deleteUI("ContextModModule")

        if event.type() == QEvent.KeyPress:
            keyType = event.key()
            if keyType == Qt.Key_Up:
                pickwalk = weightPaintUtils.pickWalkSkinClusterInfluenceList("up")
                if pickwalk == True:
                    return True

            elif keyType == Qt.Key_Down:
                pickwalk = weightPaintUtils.pickWalkSkinClusterInfluenceList("down")
                if pickwalk == True:
                    return True

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
        
    def valueMenu(self, inputVal = None, *args):
        ''' seperate def for the ability to change the value increment of the marking menu'''
        SkinningToolsUI.skinPercentValue = inputVal

    def valueAddition(self, inputVal = None, *args):
        SkinningToolsUI.skinPercentValue += inputVal  
    def getItem(self, jntName, *args):
        ''' find the bone wo work with if all conditions are met and create the marking menu'''

        hitFound      = cmds.dagObjectHit(mn= "ContextModModule")
        popUpChildren = cmds.popupMenu("ContextModModule", q=True, itemArray=True)
        if popUpChildren != None and len(popUpChildren) > 0:
            cmds.popupMenu("ContextModModule",e =True, deleteAllItems=True)
            self.__skinMarkingMenu( jntName, inItems = popUpChildren )
            return

    def __skinMarkingMenu(self, inObject, inItems=None, *args):
        selectedObjects = cmds.ls(sl=True,fl=True)
        if not selectedObjects:
            return
        mesh        = selectedObjects[0].split('.')[0]
        skincluster = SkinningTools.skinCluster(mesh, True)
        
        try:
            cmds.deleteUI(inItems)
        except:
            pass
        cmds.menuItem( l = inObject, p = "ContextModModule",  rp = "N", en = False )
        cmds.menuItem( l="set weight: 0",  p = "ContextModModule", rp="W",   c = functools.partial( self.applySkinValues, 0.0, selectedObjects, skincluster, inObject, 4 , mesh ) )
        cmds.menuItem( l="set weight: 1",  p = "ContextModModule", rp="E",   c = functools.partial( self.applySkinValues, 1.0, selectedObjects, skincluster, inObject, 0 , mesh ) )
        cmds.menuItem( l="set weight: %s"%SkinningToolsUI.skinPercentValue,  p = "ContextModModule", rp="SE", c = functools.partial( self.applySkinValues, SkinningToolsUI.skinPercentValue, selectedObjects, skincluster, inObject, 1 , mesh ) )
        cmds.menuItem( l="Add Value %s"%SkinningToolsUI.skinPercentValue,    p = "ContextModModule", rp="NE", c = functools.partial( self.applySkinValues, SkinningToolsUI.skinPercentValue, selectedObjects, skincluster, inObject, 2 , mesh ) )
        cmds.menuItem( l="Remove Value %s"%SkinningToolsUI.skinPercentValue, p = "ContextModModule", rp="NW", c = functools.partial( self.applySkinValues, -(SkinningToolsUI.skinPercentValue), selectedObjects, skincluster, inObject, 3 , mesh ) )
        if cmds.softSelect( q=True, softSelectEnabled=True) == 1:
            softSelectionMode = cmds.softSelect(q=True, softSelectFalloff= True)
            checkboxValue = 0
            if softSelectionMode == 1:
                checkboxValue = 1
            cmds.menuItem( l="surface Aware", p = "ContextModModule", rp="SW", cb=checkboxValue, c= self.setContentAware )
        incrementMenu = cmds.menuItem( l= "increment Value Menu", sm=True,   p = "ContextModModule", rp="S" )
        for i in range(1, 10, 1):
            value = i / 10.0
            cmds.menuItem( label='%s'%value, p = incrementMenu, c = functools.partial( self.valueMenu, value ) )
        
        subMenuEMenu = cmds.menuItem( l= "add 2f values", sm=True, p = incrementMenu, rp="NE" )
        for i in range(-5, 5, 1):
            value = i / 100.0
            cmds.menuItem( label='%s'%value, p = subMenuEMenu, c = functools.partial( self.valueAddition, value ) )
        
        subMenuWMenu = cmds.menuItem( l= "add 3f values", sm=True, p = incrementMenu, rp="NW" )
        for i in range(-5, 5, 1):
            value = i / 1000.0
            cmds.menuItem( label='%s'%value, p = subMenuWMenu, c = functools.partial( self.valueAddition, value ) )

        SkinningTools.doCorrectSelectionVisualization(mesh)
        return

    def setContentAware( self, *args ):
        ''' extra functionality that works with the smooth selection modifier in maya'''
        softSelectionMode = cmds.softSelect(q=True, softSelectFalloff= True)
        if softSelectionMode > 0:
            cmds.softSelect(e=True, softSelectFalloff= 0)
        else:
            cmds.softSelect(e=True, softSelectFalloff= 1)

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