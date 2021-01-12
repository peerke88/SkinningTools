# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya import interface, api

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
from SkinningTools.Maya.tools.apiWeights import ApiWeights

class WeightEditorWindow(QWidget):
    toolName = "WeightEditorWindow"

    def __init__(self, parent = None):
        super(WeightEditorWindow, self).__init__(parent)
        self.isInView = True
        self.limit = 4
        self.apiWeights = ApiWeights()
        
        self.setLayout(nullVBoxLayout())

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

        self.textInfo["label"] = QLabel('Search: ')
        searchLay.addWidget(self.textInfo["label"])
        self.textInfo["jointSearchLE"] = LineEdit()
        self.textInfo["jointSearchLE"].setPlaceholderText("Type part of joint name to search...")
        self.textInfo["jointSearchLE"].editingFinished.connect(self.searchJointName)
        self.textInfo["jointSearchLE"].textChanged.connect(self.searchJointName)
        searchLay.addWidget(self.textInfo["jointSearchLE"])
        
        headerView = VertHeaderView(self)
        headerView.sectionDoubleClicked.connect(self.lockJointWeight)
        headerView.rightClicked.connect(self.selectFromHeader)
        
        self.view = RightClickTableView(self)
        self.view.setHorizontalHeader(headerView)
        self.view.rightClicked.connect(self.getClickedItemVal)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.view.keyPressed.connect(self.directInput)
        self.mainLay.addWidget(self.view)
    
        self.createCallback()
        self.getSkinWeights()
        self.setStyleSheet("border 0px;")
    
    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
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
        for key, value in self.textInfo.iteritems():
            if isinstance(self.textInfo[key], QLineEdit):
                _ret[key] = value.placeholderText()
            else:
                _ret[key] = value.text()
        for key, value in self.actionLabels.iteritems():
            _ret[key] = value
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName) 
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui math ----------------------------------  
    def getIgnoreList(self, row, column, rowLen, colLen):
        toIgnore = []
        for _row, _col in itertools.product(range(rowLen), range(colLen)):
            toIgnore.append([row + _row, column + _col])
        return toIgnore

    def getRows(self):
        return list(set([item.row() for item in self.selectedCells]))

    def clearCopyPaste(self):
        self.copyRows = []
        self.copyWeightList = []
        self.copyJointInfl = []
        self.weightTable.copyVertWeight = []
        self.cellToCopy = []
        self.weightTable.cellToCopy = []

        self.weightSelectModel.clearSelection()
        self.refreshTable()

    def vxtCopy(self):
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
        
            if subset:
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
                if pinf in copyInf:
                    influenceID = copyInf.index(pinf)
                    newWeigths[i] = wghtToPaste[ influenceID ]
            
            self.rowsToUpdate.add(row)
            
        self.tryNormalizeWeights()
                   
    def copyCells(self):
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
        if not self.weightSelectModel.selectedIndexes() or string == '':
            return
        if string in '0123456789-.':
            self.view.ignoreInput = True
            self.popupBox = PopupSpinBox(parent = self, value=string, textValue=True)
            self.popupBox.closed.connect(partial( self.setPopupValue, True))
        
    def searchJointName(self):
        self.jointSearch = []
        if str(self.textInfo["jointSearchLE"].text()) != '':
            self.jointSearch = self.textInfo["jointSearchLE"].text().split(' ')
            self.jointSearch  = [name for name in self.jointSearch if name != '']
        self.getSkinWeights()

    def evalHeaderWidth(self, index=None, add=3):
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
        for l in self.weightLockData:
            if l[1] == jointID:
                self.lockWeigths(jointID=[jointID], lock = False )
                break
        else:
            self.lockWeigths(jointID=[jointID], lock = True )
        self.weightSelectModel.clearSelection()
        self.refreshTable()
    
    def lockWeigths(self, jointID=None, lock = True):
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
        for index in ids:
            interface.setJointLocked(self.allInfJoints[index], inValue)

    def copyMenu(self):
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
        
        for nodeId, node in enumerate(self.nodesToHilite):
            if cmds.objectType(node) != "transform":
                continue
            shape = cmds.listRelatives(node, s=1, type="mesh") or None
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
                
            filter_vtx = self.meshVerts[node]
            targets = sorted(list(set(_current) & set(filter_vtx)))
            
            if targets:
                meshWeightList = self.meshWeights[node]
                
                items = []
                for v in targets:
                    vertex = "{0:}.vtx[{1:}]".format(node, v)
                    locks = lockedData.get(v, None)
                    if locks:
                        self.lockedData[_allRows] = [vertex, locks]
                        
                    self.vertexSideBar.append(v)
                    
                    weightList = meshWeightList[v][:]
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
        
    def cellChanged(self, selected, deselected):

        if self._beforeCtx:
            self._beforeCtx = None
            self._headerSelection = None
        
        self.selectedCells =  self.weightSelectModel.selectedIndexes()
        
    @api.dec_undo
    def selectFromHeader(self):
        self._beforeCtx = cmds.currentCtx()
        self._headerSelection = self.baseSelection[:]
        self._beforeMode = cmds.selectMode(q=True, co=True)
        pos = self.view.mapFromGlobal(QCursor.pos())
        col = self.view.columnAt(pos.x() - self.view.verticalHeader().sizeHint().width() - 2)
        self.selectMode = True
        interface.doSelect(self.allInfJoints[col], False)
                    
    def getCellValue(self):
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
        
        for mesh, vertIds in self.meshIDdict.iteritems():
            sc = self.meshSkinClusters[mesh]
            newWeight = self.meshWeigthDict[mesh]
            jnts = self.meshInfDict[mesh]
            orig = self.origMeshWeights[mesh]
            cmds.SkinEditor(mesh, sc, vid=vertIds, nw = newWeight, jid = jnts, ow = orig )
        
        self.refreshTable()
        
    def refreshTable(self):
        self.view.setFocus()
        header = self.view.verticalHeader()
        for i in xrange(header.count()):
            header.updateSection(i)
                
    def createCallback(self):
        self.clearCallback()
        self._doSelectCB = api.connectSelectionChangedCallback(self.getSkinWeights) 
        
    def clearCallback(self):
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None

    def cleanupTable(self):
        if self.weightTable is not None:
            self.weightTable._data = {}
            self.weightTable.deleteLater()
            self.weightTable = None
        if self.weightSelectModel is not None:
            self.weightSelectModel.deleteLater()
    
    def setClose(self):
        self.isClosed=True
        self.cleanupTable()
        self.clearCallback()
        self.deleteLater()

    def closeEvent(self, e):
        self.setClose()

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