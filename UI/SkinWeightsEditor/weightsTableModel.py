from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools import interface

class WeightsTableModel(QAbstractTableModel):
    
    default = [61]*3
    notNormalizedColor = [235, 52, 52]
    overMaxInfColor = [235, 110, 52]
    lockedBG = [30]*3
    lockedTXT = [60]*3
    copyCellColor = [90, 120, 90]
    vertex_copy_color = [90, 90, 120]
    cell_vertex_copy_color = [70, 120, 120]
    _baseColor  = [200]*3

    def __init__(self, data, parent=None, window = None, meshIndex=[], jointNames=[], vtxSideBar=[], jointColorList=[]):
        super(TableModel, self).__init__(parent)
        
        self.__parentWidget = window
        
        self._data = data
        
        self.meshIndexRows = meshIndex
        self.jointNames = jointNames
        self.vtxSideBar = vtxSideBar
        self.jointColorList = jointColorList

        self.totalNotNormalized = set()
        self.overMaxInfDict = {}
        self.lockedWeigths = set()
        self.cellToCopy = []
        self.copyVertWeight = []
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._data[0])-1 if self.rowCount() else 0
        
    def headerData(self, index, orientation, role):
        if orientation == Qt.Horizontal:
            if index >= len(self.jointNames):
                return None

            if role == Qt.DisplayRole:
                return self.jointNames[index].split('|')[-1]

            elif role == Qt.BackgroundRole:
                color_id = self.jointColorList[index]
                return QColor(*interface.skinnedJointColors()[color_id])
                
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return self.vtxSideBar[index]

            elif role == Qt.BackgroundRole:
                if index in self.meshIndexRows:
                    vertStart = self.meshIndexRows[self.meshIndexRows.index(index)+1] 
                    meshIndexRows = set(range(index+1,vertStart))
                    if meshIndexRows & self.totalNotNormalized:
                        return QColor(*self.notNormalizedColor)
                    for idx in meshIndexRows:
                        if self.overMaxInfDict[idx] > self.__parentWidget.limit > 0:
                            return QColor(*self.overMaxInfColor)
                            
                if index in self.totalNotNormalized:
                    return QColor(*self.notNormalizedColor)
                if index in self.overMaxInfDict.keys():
                    if self.overMaxInfDict[index] > self.__parentWidget.limit > 0:
                        return QColor(*self.overMaxInfColor)
                    
                return QColor(*self.default)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignRight
        return None
    
        
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            if row in self.__parentWidget.vtxDataDict.keys():
                node = self.__parentWidget.vtxDataDict[row][6]
                influencesList = self.__parentWidget.jointIndexList[node]
                if influencesList[col] is None:
                    return
                weight = self._data[row][influencesList[col]]
                return '%.3f'%weight
            
        elif role == Qt.BackgroundRole:
            if row in self.meshIndexRows:
                color_id = self.jointColorList[col]
                return QColor(*self.joint_color_list[color_id]) 
            if row in self.copyVertWeight and index in self.cellToCopy:
                return QColor(*self.cell_vertex_copy_color)
            if row in self.copyVertWeight:
                return QColor(*self.vertex_copy_color)
            if index in self.cellToCopy:
                return QColor(*self.copyCellColor)
            if (row, col) in self.lockedWeigths:
                return QColor(*self.lockedBG)
        
        elif role == Qt.ForegroundRole:
            isZero = False
            color = self._baseColor
            if row in self.__parentWidget.vtxDataDict.keys():  
                node = self.__parentWidget.vtxDataDict[row][6]
                influencesList = self.__parentWidget.jointIndexList[node]
                if influencesList[col] is None:
                    return
                weight = self._data[row][influencesList[col]]
                if weight == 0.0:
                    isZero=True
                
            if (row, col) in self.lockedWeigths:
                color = self.lockedTXT
            else:
                if row in self.totalNotNormalized:
                    color = self.notNormalizedColor
                elif row in self.overMaxInfDict.keys():
                    if self.overMaxInfDict[row] > self.__parentWidget.limit > 0:
                        color = self.overMaxInfColor
                if isZero:
                    color = [min([c - 60, 255]) if c - 60 > 43 else 43 for c in color]
                    
            return QColor(*color)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
                
    def get_data(self, index=None, row=0, col=0):
        if index:
            row = index.row()
            col = index.column()
        if row in self.__parentWidget.vtxDataDict.keys():
            node = self.__parentWidget.vtxDataDict[row][6]
            influencesList = self.__parentWidget.jointIndexList[node]
            value  = self._data[row][influencesList[col]]
        else:
            value = None
        return value
        
    def setData(self, index, value, role=Qt.EditRole):
        if not isinstance(index, tuple):
            if not index.isValid() or not 0 <= index.row() < len(self._data):
                print 'can not set data : retrun'
                return
            row = index.row()
            col = index.column()
        else:
            row = index[0]
            col = index[1]
        if role == Qt.EditRole and value != "":
            node = self.__parentWidget.vtxDataDict[row][6]
            influencesList = self.__parentWidget.jointIndexList[node]
            local_column = influencesList[col]
            
            self._data[row][local_column] = value
            self.dataChanged.emit((row, col), (row, col))
            return True
        else:
            return False
            
    def flags(self, index):
        row = index.row()
        col = index.column()
        
        if row in self.__parentWidget.vtxDataDict.keys():
            node = self.__parentWidget.vtxDataDict[row][6]
            influencesList = self.__parentWidget.jointIndexList[node]
            local_column = influencesList[col]
            value = self._data[row][local_column]
        else:
            value = None
        if row in self.meshIndexRows or value is None:
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
     