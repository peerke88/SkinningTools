# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya import interface, api
from SkinningTools.py23 import *

#@todo: make sure all cmds modules are moved over to interface/api
from maya import cmds
from maya.api import OpenMaya

from collections import defaultdict, OrderedDict
import copy, itertools
from functools import partial

from SkinningTools.UI.weightEditor.rightClickTableView import RightClickTableView
from SkinningTools.UI.weightEditor.weightsTableModel import WeightsTableModel
from SkinningTools.UI.weightEditor.vertHeaderView import VertHeaderView
from SkinningTools.UI.weightEditor.popupSpinBox import PopupSpinBox
from SkinningTools.UI.hoverIconButton import HoverIconButton
from SkinningTools.Maya.tools.apiWeights import ApiWeights
from SkinningTools.Maya.tools import weightPaintUtils as paintUtil

class WeightEditorWindow(QWidget):
    """ weight editor widget, 
    allows for skincluster visualisation based on the vertex selection and the joints in the skincluster
    """
    toolName = "WeightEditorWindow"

    def __init__(self, parent = None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(WeightEditorWindow, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        
        self.__defaults()
        self.apiWeights = ApiWeights()
        
        self._uiSetup()
        self.createCallback()
        self.getSkinWeights()
        self.setStyleSheet("border 0px;")
    
    def __defaults(self):
        """ conveninece function to gather all the default values to be used
        """
        self.isInView = True
        self.limit = 4
        self._data = []
        self.jointSearch = []
        self.selectedCells = []
        self.copyWeightList = []
        self.copyJointInfl = []
        self.nodesToHilite = []
        self.cellToCopy = []
        self.copyValues = []
        self.copyCellPos = []
        self.allInfJoints = []

        self.textInfo = {}
        self.cellDict = {}

        self.actionLabels = {"cpVtx" : 'Copy Vtx Weigh"self"s',
                             "ptVtx" : 'Paste Vtx Weight',
                             "cpCll" : 'Copy Cell Value',
                             "ptCll" : 'Paste Cell Value',
                             "clear" : 'clear value'}

        self.weightTable = None
        self.weightSelectModel = None
        self._beforeCtx = None
        self._headerSelection = None
        self._beforeMode = None
        self._doSelectCB = None
        self.isClosed = False
        self.selectMode = False

    def _uiSetup(self):
        """ convenience function to gather all buttons for the current UI
        """
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)
        scroll.setMinimumHeight(1)
        self.layout().addWidget(scroll)
        self.mainLay = nullVBoxLayout()
        scroll.setLayout(self.mainLay)
        
        searchLay = nullHBoxLayout()
        searchLay.setSpacing(0)
        self.mainLay.addLayout(searchLay)
        
        self.textInfo["label"] = QLabel('Search: ')
        self.textInfo["jointSearchLE"] = LineEdit()
        self.textInfo["jointSearchLE"].setPlaceholderText("Type part of joint name to search...")
        self.textInfo["jointSearchLE"].editingFinished.connect(self.searchJointName)
        self.textInfo["jointSearchLE"].textChanged.connect(self.searchJointName)
        
        searchLay.addWidget(self.textInfo["label"])
        searchLay.addWidget(self.textInfo["jointSearchLE"])
        
        self.LockAllButton = HoverIconButton()
        self.LockAllButton.setCustomIcon(':/nodeGrapherUnlocked.png',':/lockGeneric.png')
        self.LockAllButton.setCheckable(True)
        self.LockAllButton.clicked.connect(self.lockAllWeights)
        searchLay.addWidget(self.LockAllButton)

        self.showButton = HoverIconButton()
        self.showButton.setCustomIcon(":/RS_visible.png", ":/RS_visible.png", ":/hotkeyFieldClear.png")
        self.showButton.setCheckable(True)
        self.showButton.clicked.connect(self.getSkinWeights)
        searchLay.addWidget(self.showButton)

        headerView = VertHeaderView(self)
        headerView.sectionDoubleClicked.connect(self.lockJointWeight)
        headerView.rightClicked.connect(self.selectFromHeader)
        
        self.view = RightClickTableView(self)
        self.view.setHorizontalHeader(headerView)
        self.view.rightClicked.connect(self.getClickedItemVal)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.view.keyPressed.connect(self.directInput)
        self.mainLay.addWidget(self.view)

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.items():
            if key in self.actionLabels.keys():
                self.actionLabels[key] = value
                continue
            if isinstance(self.textInfo[key], QLineEdit):
                self.textInfo[key].setPlaceholderText(value)
            else:
                self.textInfo[key].setText(value)
        
    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.items():
            if isinstance(self.textInfo[key], QLineEdit):
                _ret[key] = value.placeholderText()
            else:
                _ret[key] = value.text()
        for key, value in self.actionLabels.items():
            _ret[key] = value
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName) 
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui math ----------------------------------  
    def getIgnoreList(self, row, column, rowLen, colLen):
        """ get the list of items to be ignored

        :param row: the index of the row
        :type row: int
        :param column: the index of the column
        :type column: int
        :param rowLen: amoutn of rows
        :type rowLen: int
        :param colLen: amount of columns
        :type colLen: int
        :return: list of itmems to ignore
        :rtype: list
        """
        toIgnore = []
        for _row, _col in itertools.product(range(rowLen), range(colLen)):
            toIgnore.append([row + _row, column + _col])
        return toIgnore

    def getRows(self):
        """ get the rows of selected cells

        :return: list of selected rows
        :rtype: list
        """
        return list(set([item.row() for item in self.selectedCells]))

    def clearCopyPaste(self):
        """ clear the copy paste data
        """
        self.copyRows = []
        self.copyWeightList = []
        self.copyJointInfl = []
        self.weightTable.copyVertWeight = []
        self.cellToCopy = []
        self.weightTable.cellToCopy = []

        self.weightSelectModel.clearSelection()
        self.refreshTable()

    def vxtCopy(self):
        """ copy the date of selected vertices
        """
        self.copyRows = self.getRows()
        self.copyWeightList = []
        self.copyJointInfl = []
        for row in self.copyRows:
            self.copyWeightList.append(self._data[row])
            self.copyJointInfl.append(self.vtxDataDict[row][2])
        self.weightTable.copyVertWeight = self.copyRows
        self.weightSelectModel.clearSelection()
        self.refreshTable()
        
    def vtxPaste(self):
        """ paste the gathered date onto newly selected vertices
        """
        self.rowsToUpdate = set()
        self.lockedCells = self.weightTable.lockedWeigths
        rows = self.getRows()
        
        meshes = []
        joints = []
        
        for row in rows:
            node = self.vtxDataDict[row][6]
            if node in meshes:
                continue
            meshes.append(node)
            joints.append(self.vtxDataDict[row][2])
        
        copyInf  = []
        for influences in self.copyJointInfl:
            if not influences in copyInf:
                copyInf.append(influences)
        
        allCopyInf = []
        for influences in copyInf:
            allCopyInf += influences
        allCopyInf = list(set(allCopyInf))
        
        influenceAdded = False
        for meshInfl, mesh in zip(joints, meshes):
            subset = list(set(allCopyInf) - set(meshInfl))
            if not subset:
                continue
        
            influenceAdded = True
            api.addCleanJoint(subset, mesh, False)
        
        if influenceAdded:
            self.getSkinWeights()
        
            self.weightTable.copyVertWeight = self.copyRows
            self.weightTable.cellToCopy = self.cellToCopy
            
        amountRows = len(self.copyRows)
        if not amountRows:
            return
        
        for index, row in enumerate(rows):
        
            newWeigths = self._data[row]
            curInf  = self.vtxDataDict[row][2]
            
            currentID = (index % amountRows) -1
            copyInf = self.copyJointInfl[ currentID ]
            wghtToPaste = self.copyWeightList[ currentID ]
            
            for i, pinf in enumerate(curInf):
                newWeigths[i] = 0.0
                if not pinf in copyInf:
                    continue
                
                influenceID = copyInf.index(pinf)
                newWeigths[i] = wghtToPaste[ influenceID ]
            
            self.rowsToUpdate.add(row)
            
        self.tryNormalizeWeights()
                   
    def copyCells(self):
        """ copy cell information 
        """
        self.cellToCopy = self.selectedCells
        self.weightTable.cellToCopy = self.cellToCopy
        self.weightSelectModel.clearSelection()
        self.refreshTable()
        
        self.copyValues = []
        self.copyCellPos = []
        
        if not self.cellToCopy:
            return
            
        startRow = self.cellToCopy[0].row()
        startCol = self.cellToCopy[0].column()
        for cell in self.cellToCopy:
            row = cell.row()
            col = cell.column() 
            self.copyCellPos.append([row - startRow, col - startCol])
            value = self.weightTable.getCellData(row=row, col=col)
            self.copyValues.append(value)

        smallestRow = min( self.copyCellPos, key = lambda x: x[ 0 ] )[ 0 ]
        biggestRot = max( self.copyCellPos, key = lambda x: x[ 0 ] )[ 0 ]
        smallestCol = min( self.copyCellPos, key = lambda x: x[ 1 ] )[ 1 ]
        biggestCol = max( self.copyCellPos, key = lambda x: x[ 1 ] )[ 1 ]

        self.rowLen = biggestRot - smallestRow + 1
        self.colLen = biggestCol - smallestCol + 1
        
    def pasteCells(self):
        """ paste cell information
        """
        pastedCells = self.selectedCells
       
        startCell = pastedCells[0]
        startRow = startCell.row()
        startCol = startCell.column()
        cellPos = [[startRow, startCol]]
        toIgnore = self.getIgnoreList(startRow, startCol, self.rowLen, self.colLen )
        for cell in pastedCells[1:]:
            row = cell.row()
            col = cell.column() 
            index = [row, col]
            if index in toIgnore:
                continue
            cellPos.append(index)
            toIgnore += self.getIgnoreList(row, col, self.rowLen, self.colLen )
        
        self.rowsToUpdate = set()
        self.cellDict = {}
        self.lockedCells = self.weightTable.lockedWeigths
        for [startRow, startCol] in cellPos:
            for value, pos in zip(self.copyValues,  self.copyCellPos):
                row = startRow + pos[0]
                col = startCol + pos[1]
                if (row, col) in self.lockedCells:
                    continue
                wghtList = self._data[row]
                node = self.vtxDataDict[row][6]
                jointIdx = self.jointIndexList[node]
                wghtList[jointIdx[col]] = value
                
                if row in self.cellDict.keys():
                    self.rowsToUpdate.add(row)
                    self.cellDict[row].append(col)
        
        self.tryNormalizeWeights()
            
    def directInput(self, string):
        """ set up popup box based on given string

        :param string: string object representing the number
        :type string: string
        """
        if not self.weightSelectModel.selectedIndexes() or string == '':
            return
        if string in '0123456789-.':
            self.view.ignoreInput = True
            self.popupBox = PopupSpinBox(parent = self, value=string, textValue=True)
            self.popupBox.closed.connect(partial( self.setPopupValue, True))
        
    def searchJointName(self):
        """ based on the given text we only display columns that are represted by a partial identification of the given string in the search lineedit
        """
        self.jointSearch = []
        if str(self.textInfo["jointSearchLE"].text()) != '':
            self.jointSearch = self.textInfo["jointSearchLE"].text().split(' ')
            self.jointSearch  = [name for name in self.jointSearch if name != '']
        self.getSkinWeights()

    def evalHeaderWidth(self, add=3):
        """ in here we change the size of the header based on the format of the font and amount of bones

        :param add: buffer pixels to extend the size with
        :type add: int
        """
        if self.weightTable is None:
            return
        _space = 45
        _max = _space + add
        if hasattr(self.view.horizontalHeader(), 'setResizeMode'):
            resize_mode = self.view.horizontalHeader().setResizeMode  
        else:
            resize_mode = self.view.horizontalHeader().setSectionResizeMode 

        count = self.weightTable.columnCount()
        for index in range(count):
            width = _space + add
            width -= 7
            if width > _max:
                width = _max
            self.view.setColumnWidth(index, width)
            
    @Slot(int)
    def lockJointWeight(self, jointID):
        """ based on joint id given we lock the joint weights so they cannot change,
        this will be represented in the table widget as well by darkening the cells

        :param jointID: the index of the joint to be locked
        :type jointID: int
        """
        for l in self.weightLockData:
            if l[1] == jointID:
                self.lockWeigths(jointID=[jointID], lock = False )
                break
        else:
            self.lockWeigths(jointID=[jointID], lock = True )
        self.weightSelectModel.clearSelection()
        self.refreshTable()
        paintUtil.forceRefreshPaintTool()

    def lockAllWeights(self):
        for jnt in self.allInfJoints:
            interface.setJointLocked(jnt, self.sender().isChecked())
        paintUtil.forceRefreshPaintTool()
        self.refreshTable()

    def lockWeigths(self, jointID=None, lock = True):
        """ function to lock or unlock weights, this will be represented in the widget as well as in the dcc tool

        :param jointID: the index of the joint to be locked
        :type jointID: int
        :param lock: if `True` will lock the weight so it cannot be changed, if `False` will unlock the weight
        :type lock: bool
        """
        for cell in self.selectedCells:
            row = cell.row()
            col = cell.column()
            index = (row, col)
        
            _data = self.vtxDataDict[row]
            influences =  _data[2]
            vtxName = _data[5]
            mesh = _data[6]
            meshInfl = self.jointIndexList[mesh]
            lockedID = meshInfl[col]

            lock_influence = influences[lockedID]
            if lock:
                self.weightLockData.add(index)
                self.weightTable.lockedWeigths.add(index)
                self.vtxlockedData[vtxName].add(lockedID)
            else:
                if index in self.weightLockData:
                    self.weightLockData.remove(index)
                if index in self.weightTable.lockedWeigths:
                    self.weightTable.lockedWeigths.remove(index)
                if lockedID in self.vtxlockedData[vtxName]:
                    self.vtxlockedData[vtxName].remove(lockedID)
                lock_influence = influences[lockedID]
            
        self.setLockedData(jointID, lock)

    def setLockedData(self, ids, inValue):
        """ make sure that the weights are also locked in the dcc tool
        

        :param ids: the list of indeces of the joints to be locked
        :type ids: list
        :param inValue: if `True` will lock the weight so it cannot be changed, if `False` will unlock the weight
        :type inValue: bool
        """
        for index in ids:
            interface.setJointLocked(self.allInfJoints[index], inValue)

    def copyMenu(self):
        """ simple popup menu with copy functions
        """
        popMenu = QMenu()

        cpVtx = popMenu.addAction( self.actionLabels["cpVtx"] )
        ptVtx = popMenu.addAction( self.actionLabels["ptVtx"] )
        cpCll = popMenu.addAction( self.actionLabels["cpCll"] )
        ptCll = popMenu.addAction( self.actionLabels["ptCll"] )
        clear = popMenu.addAction( self.actionLabels["clear"] )
        
        cpVtx.triggered.connect(self.vxtCopy)
        ptVtx.triggered.connect(self.vtxPaste)
        cpCll.triggered.connect(self.copyCells)
        ptCll.triggered.connect(self.pasteCells)
        clear.triggered.connect(self.clearCopyPaste)
        
        cursor = QCursor.pos()
        popMenu.exec_(cursor)
            
    def getClickedItemVal(self):
        """ get the current value of the selected cells
        """
        shiftPressed = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)
        ctrlPressed = bool(QApplication.keyboardModifiers() & Qt.ControlModifier)
        width = self.view.verticalHeader().sizeHint().width()
        height = self.view.horizontalHeader().sizeHint().height()
        
        pos = self.view.mapFromGlobal(self.view.mousePos)
        row = self.view.rowAt(pos.y() - height - 2)
        col = self.view.columnAt(pos.x() - width - 2)
        if col == -1:
            col = len(self.allInfJoints)
        text = self.weightTable.getCellData(row=row, col=col)
        
        if text is None or shiftPressed or ctrlPressed:
            self.copyMenu()
            return

        self.popupBox = PopupSpinBox(parent = self,value=float(text))
        self.popupBox.closed.connect(self.setPopupValue)
    
    def setPopupValue(self, textValue=True):
        """ set the value for the popup menu based on the current cells
        
        :note: maybe make this smarter so it just checks what the input is and base it on that instead of using an arg
        :param textValue: if `True` will convert the information from string to float, if `False` expects the information to be float already 
        :type textValue: bool
        """
        if textValue:
            try:
                self.inputValue = float(self.popupBox.input.text())
            except:
                return
        else:
            self.inputValue = self.popupBox.input.value()
        self.getCellValue()
        
        self.activateWindow()
        self.raise_()
        self.view.setFocus()
        self.view.ignoreInput = False
        
    def getSkinWeights(self):
        """ get skinweights function,
        this is where we grab all the information from the dcc tool to populate the table
        based on either object or component selection we make sure to grab all joints and weights associated
        the selections will be listed as vertex components and will be split according to the object where they came from
        """
        if not self.isInView:
            return
        
        if self.selectMode:
            self.selectMode = False
            return

        self.baseSelection =  interface.getSelection()
        if len(self.baseSelection) == 0:
            return
        
        self.apiWeights.getData()
        self.nodesToHilite = list(set(self.apiWeights.meshNodes))
        self.allInfJoints = copy.copy(self.apiWeights.allInfJoints)
        self.meshInfluences = self.apiWeights.meshInfluences
        self.meshVerts = self.apiWeights.meshVerts
        self.meshWeights = self.apiWeights.meshWeights
        self.meshSkinClusters = self.apiWeights.meshSkinClusters

        if len(self.meshSkinClusters) == 0:
            print( "No skin cluster found" )
            return
        
        if self._beforeCtx:
            self._beforeCtx = None
        
        _allRows = 0
        self._headerSelection = []
        self.vertexSideBar = []
        self._data = []
        self.meshIndexRows = []
        self.vtxDataDict = {}
        self.totalNotNormalized = set()
        
        self.overMaxInfDict = {}
        self.weightLockData = set()
        self.vtxlockedData = defaultdict(lambda : set())
        self.meshIDdict = {}
        self.meshItems = {} 
        self.nodeVtxIndexList = {}
        self.lockedData = {}
        self.nodeInfIds = {}
        weightedJoints = []

        for nodeId, node in enumerate(self.nodesToHilite):
            if cmds.objectType(node) != "transform":
                continue
            shape = cmds.listRelatives(node, s=1, type="mesh", fullPath=1) or None
            if shape is None:
                continue

            self.meshIDdict[node] = nodeId

            skinCluster = self.meshSkinClusters[node]
            influences = self.meshInfluences[node]
            nodeInfIDs =  {inf:influences.index(inf)  for inf in influences}
            
            self.nodeInfIds[node] = nodeInfIDs
            
            amountInfluences = len(influences)
            jointIdx = range(len( influences))
            
            lockedData = dict.fromkeys(self.meshVerts[node], interface.getLockData(skinCluster))

            self.vertexSideBar.append(node.split('|')[-1].split(':')[-1])
            self.meshIndexRows.append(_allRows)
            _allRows += 1
            
            items = defaultdict(lambda: None)
            self.meshItems[node] = items
            items[0] = node.split('|')[-1]
            self._data.append(items)
            
            _current = self.apiWeights.selectedVertIds(node)
            if not _current:
                continue
                
            filterVtx = self.meshVerts[node]
            targets = sorted(list(set(_current) & set(filterVtx)))
            
            if not targets:
                continue

            items = []
            for v in targets:
                vertex = "{0:}.vtx[{1:}]".format(node, v)
                locks = lockedData.get(v, None)
                if locks:
                    self.lockedData[_allRows] = [vertex, locks]
                    
                self.vertexSideBar.append(v)
                weightList = self.meshWeights[node][v][:]
                
                nonzero = [i for i, e in enumerate(weightList) if e != 0]
                for i in nonzero:
                    _cur = influences[i].split("|")[-1]
                    
                    if _cur in weightedJoints:
                        continue
                    weightedJoints.append(_cur)

                self.nodeVtxIndexList[vertex] = weightList
                self._data.append(weightList)
                
                sumWeights = round(sum(weightList), 12)
                totalInfluences = amountInfluences - weightList.count(0.0)
                self.overMaxInfDict[_allRows] = totalInfluences

                if not round(sumWeights-1.0, 10) < 1e-6:
                    self.totalNotNormalized.add(_allRows)
                    
                self.vtxDataDict[_allRows] = [v, skinCluster, influences, [], jointIdx, vertex, node, nodeId]
                _allRows += 1
             
        self.meshIndexRows.append(_allRows)
        
        if self.jointSearch:
            self.allInfJoints = [inf for inf in self.allInfJoints if any([True if s.upper() in inf.split('|')[-1].upper() else False for s in self.jointSearch])]
        if self.showButton.isChecked():
            self.allInfJoints = [inf for inf in self.allInfJoints if any([True if s.upper() in inf.split('|')[-1].upper() else False for s in weightedJoints])]
        
        self.jointIndexList = {}
        for node in self.nodesToHilite:          
            influences = self.meshInfluences[node]
            infIdList = [influences.index(inf) if inf in influences else None for inf in self.allInfJoints]       
            self.jointIndexList[node] = infIdList
            
            items = self.meshItems[node]
            for inf in self.allInfJoints:
                items[inf] = None
                
        self.jointColors = [cmds.getAttr('%s.objectColor'%j) for j in self.allInfJoints]
        self.jointIndexDict = {inf:i for i, inf in enumerate(self.allInfJoints)}
        
        for row, locks in self.lockedData.items():
            node = self.vtxDataDict[row][6]
            nodeInfIDs = self.nodeInfIds[node]
            
            vertex = locks[0]
            lock_influences = locks[1]
            for influence in lock_influences:
                if influence in self.jointIndexDict.keys():
                    col = self.jointIndexDict[influence]
                    self.weightLockData.add((row, col))
                self.vtxlockedData[vertex].add(nodeInfIDs[influence])
        
        try:      
            self.cleanupTable()
        except:
            self.weightTable = None
            
        self.weightTable = WeightsTableModel(self._data, self.view, self, self.meshIndexRows, self.allInfJoints, self.vertexSideBar, self.jointColors)
        self.weightTable.overMaxInfDict = self.overMaxInfDict
        self.weightTable.totalNotNormalized = self.totalNotNormalized
        self.weightTable.norm = True
        self.weightTable.lockedWeigths = self.weightLockData
            
        self.weightSelectModel = QItemSelectionModel(self.weightTable)
        self.weightSelectModel.selectionChanged.connect(self.cellChanged)
        self.view.setModel(self.weightTable)
        self.view.setSelectionModel(self.weightSelectModel)
        self.selectedCells = []

        self.evalHeaderWidth()
        
    def cellChanged(self, *args):
        """ cell changed signal, makes sure that the selected indices are returned and the contexts are cleared
        """
        if self._beforeCtx:
            self._beforeCtx = None
            self._headerSelection = None
        
        self.selectedCells =  self.weightSelectModel.selectedIndexes()
        
    @api.dec_undo
    def selectFromHeader(self):
        """ select the current joint we work with from the current header (based on right-click)

        :todo: needs to change when other dcc then maya will be used
        """
        self._beforeCtx = cmds.currentCtx()
        self._headerSelection = self.baseSelection[:]
        self._beforeMode = cmds.selectMode(q=True, co=True)
        pos = self.view.mapFromGlobal(QCursor.pos())
        col = self.view.columnAt(pos.x() - self.view.verticalHeader().sizeHint().width() - 2)
        self.selectMode = True
        interface.doSelect(self.allInfJoints[col], False)
                    
    def getCellValue(self):
        """ get and set the new cell value based on the self.inputValue from the popupbox
        """
        if self.isClosed:
            return
            
        if not self.selectedCells:
            return
           
        if not self.isActiveWindow():
            QApplication.setActiveWindow(self)
        
        self.lockedCells = self.weightTable.lockedWeigths

        self.rowsToUpdate = set()
        self.cellDict = defaultdict(lambda : [])

        newVal = clamp(self.inputValue) 

        for cell in self.selectedCells:
            row = cell.row()
            col = cell.column() 

            if (row, col) in self.lockedCells:
                continue

            weightList = self._data[row]
            node = self.vtxDataDict[row][6]
            jointIdx = self.jointIndexList[node]
            weightList[jointIdx[col]] = newVal

            self.rowsToUpdate.add(row)
            self.cellDict[row].append(col)
        
        self.tryNormalizeWeights()

    def tryNormalizeWeights(self):
        """ force normalize the weights of the current vertex row
        making sure that all elements are adding up to a maximum of 1
        trys to make sure that the maximum influences are kept unless more cells are altered at the same time
        htis is used as the set weights function as we dont want weights that are not normalized
        """
        _workData = self.weightTable._data
        
        self.meshIDdict = defaultdict( lambda : OpenMaya.MIntArray() )
        self.meshInfDict = defaultdict( lambda : OpenMaya.MIntArray() )
        self.meshWeigthDict = defaultdict( lambda : OpenMaya.MDoubleArray() )
        self.origMeshWeights = defaultdict( lambda : OpenMaya.MDoubleArray() )
        
        meshWeightList = []
        origMeshWeightList = []
        prevMesh = None
        prevJointIDs = None
        self.rowsToUpdate = sorted(list(self.rowsToUpdate))
        if not self.rowsToUpdate:
            return

        _lastRow = list(self.rowsToUpdate)[-1]
        for row in self.rowsToUpdate:
            _recalc = True

            vtx = self.vtxDataDict[row][0]
            influences =  self.vtxDataDict[row][2]
            amountJoints = len(influences)
            currentJointIDs = self.vtxDataDict[row][4]
            vertex = self.vtxDataDict[row][5]
            mesh = self.vtxDataDict[row][6]
            
            jointIndexlist = self.jointIndexList[mesh]
            lockedJoints = self.vtxlockedData[vertex]
            
            origWeights = self.meshWeights[mesh][vtx]
            nWeight = _workData[row]
            
            calcNWeigth = []
            lockedSum = sum([nWeight[i] for i in lockedJoints])
            
            if lockedSum >= 1.0:
                for index, wght in enumerate(nWeight):
                    if index in lockedJoints:
                        calcNWeigth.append(wght)
                        continue
                    calcNWeigth.append(0.0)
            else:
                selectedCols = []
                if row in self.cellDict.keys():
                    selectedCols = self.cellDict[row]
                selJointID = [jointIndexlist[i] for i in selectedCols]
                    
                sumSelection = sum([nWeight[i] for i in selJointID if i is not None])
                restJntID = list(set(currentJointIDs) - set(selJointID))
                restSum = sum([nWeight[i] for i in restJntID]) - lockedSum
                
                if restSum + sumSelection == 0.0:
                    nWeight = origWeights
                    sumSelection = sum([nWeight[i] for i in selJointID if i is not None])
                if sumSelection + lockedSum >= 1.0:
                    for index, wght in enumerate(nWeight):
                        if index in lockedJoints:
                            calcNWeigth.append(wght)
                        elif index in selJointID:
                            calcNWeigth.append(wght/sumSelection*(1.0-lockedSum))
                        else:
                            calcNWeigth.append(0.0)
                            
                elif sumSelection < 1.0:
                    sumTotal = sumSelection + lockedSum
                    if sumTotal >= 1.0 or restSum == 0.0:
                        if restSum == sumSelection == 0.0:
                            _recalc = False
                        other = 0.0
                        ratio = 0.0
                        if sumSelection != 0.0:
                            ratio = (1 - lockedSum) / sumSelection
                    else:
                        newRestSum = 1.0 - sumTotal
                        other = newRestSum / restSum
                        ratio = 1.0

                    for index, wght in enumerate(nWeight):
                        if index in lockedJoints:
                            calcNWeigth.append(wght)
                        elif index in selJointID:
                            calcNWeigth.append(nWeight[index]  * ratio)
                        else:
                            calcNWeigth.append(nWeight[index]  * other)

            nWeight = calcNWeigth[:]
                
            if _recalc:
                if mesh != prevMesh and prevMesh is not None:
                    self.meshWeigthDict[prevMesh] += meshWeightList
                    self.origMeshWeights[prevMesh] += origMeshWeightList
                    meshWeightList = []
                    origMeshWeightList = []
                    self.meshInfDict[prevMesh] = OpenMaya.MIntArray() + prevJointIDs

                if row == _lastRow:
                    meshWeightList += nWeight
                    origMeshWeightList += origWeights
                    self.meshWeigthDict[mesh] += meshWeightList
                    self.origMeshWeights[mesh] += origMeshWeightList
                    self.meshInfDict[mesh] = OpenMaya.MIntArray() + currentJointIDs

                meshWeightList += nWeight
                origMeshWeightList += origWeights
                self.meshIDdict[mesh] += [vtx] 

            prevMesh = mesh
            prevJointIDs = currentJointIDs
            
            wghtList = self.nodeVtxIndexList[vertex] 
            for i, w in enumerate(nWeight):
                wghtList[i] = w
                    
            if not round(sum(nWeight) - 1.0, 10) < 1e-6 :
                self.weightTable.totalNotNormalized.add(row)
            else:
                if row in self.weightTable.totalNotNormalized:
                    self.weightTable.totalNotNormalized.remove(row)
            
            self.weightTable.overMaxInfDict[row] = amountJoints - nWeight.count(0.0)
        
        for mesh, vertIds in self.meshIDdict.items():
            sc = self.meshSkinClusters[mesh]
            newWeight = self.meshWeigthDict[mesh]
            jnts = self.meshInfDict[mesh]
            orig = self.origMeshWeights[mesh]
            cmds.SkinEditor(mesh, sc, vid=vertIds, nw = newWeight, jid = jnts, ow = orig )
        
        self.refreshTable()
        
    def refreshTable(self):
        """ force redraw the current table view
        """
        self.view.setFocus()
        header = self.view.verticalHeader()
        for i in range(header.count()):
            header.updateSection(i)
                
    def createCallback(self):
        """ create callback to refresh the current table based on selection in dcc tool
        """
        self.clearCallback()
        self._doSelectCB = api.connectSelectionChangedCallback(self.getSkinWeights) 
        
    def clearCallback(self):
        """ remove selection based callback
        """
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None

    def cleanupTable(self):
        """ cleanup table data, forced garbage collection as this tool deals with a lot of data
        """
        if self.weightTable is not None:
            self.weightTable._data = {}
            self.weightTable.deleteLater()
            self.weightTable = None
        if self.weightSelectModel is not None:
            self.weightSelectModel.deleteLater()
    
    def setClose(self):
        """ close and cleanup the weights table
        """
        self.isClosed=True
        self.cleanupTable()
        self.clearCallback()
        self.deleteLater()

    def closeEvent(self, event):
        """ close event override
        """
        self.setClose()
        super(WeightEditorWindow, self).closeEvent(event)

def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("WeightEditor Test window")
    wdw = WeightEditorWindow(parent = mainWindow)
    wdw.isInView = True
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw