from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya import interface

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
        """ the constructor

        :param data: list of data to input into the current table model
        :type data: list
        :param parent: the parent widget for this object
        :type parent: QWidget
        :param window: the parent widget to get information from
        :type window: QWidget
        :param meshIndex: index positions on where to display a mesh name
        :type meshIndex: list
        :param jointNames: list of all joint names connected to the current mesh
        :type jointNames: list
        :param vtxSideBar: list of all vertices selected to display in the sidebar
        :type vtxSideBar: list
        :param jointColorList: list of all used joint colors
        :type jointColorList: list
        
        """
        super(WeightsTableModel, self).__init__(parent)
        
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
        """ amount of rows in current table model

        :return: amount of rows
        :rtype: int
        """
        return len(self._data)
    
    def columnCount(self, parent=None):
        """ amount of columns in current table model

        :return: amount of columns
        :rtype: int
        """
        return len(self._data[0])-1 if self.rowCount() else 0
        
    def headerData(self, index, orientation, role):
        """ set up the header data for all joint objects

        :param index: index of the header
        :type index: int
        :param orientation: the Qt orientation role on how to place the current header
        :type orientation: QT.orientation
        :param role: qt role on how to display the element
        :type role: Qt.DisplayRole
        :return: the color of the object
        :rtype: QColor
        """
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
        """ get specific data from the current given header

        :param index: index of the header
        :type index: int
        :param role: qt role on how to display the element
        :type role: Qt.DisplayRole
        :return: data gathered from the object
        :rtype: QColor/Qt.alignment
        """
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
                return QColor(*interface.skinnedJointColors()[color_id]) 
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
                
    def getCellData(self, index=None, row=0, col=0):
        """ get the value from the given cell

        :param index: index of the cell data if given
        :type index: cellindex
        :param row: index of the row
        :type row: int
        :param col: index of the column
        :type col: int
        :return: the value of the cell
        :rtype: float
        """
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
        """ set the data on the given cell

        :param index: index of the cell
        :type index: cellindex
        :param value: value to give to the cell
        :type value: float
        :param role: role of current edit
        :type role: Qt.role
        :return: if setting was succesfull
        :rtype: bool
        """
        if not isinstance(index, tuple):
            if not index.isValid() or not 0 <= index.row() < len(self._data):
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
        """ get the flags of given cell

        :param index: index of the cell
        :type index: cellindex
        :return: flags used on the current cell
        :rtype: Qt.flags
        """
        row = index.row()
        col = index.column()
        
        try:
            node = self.__parentWidget.vtxDataDict[row][6]
            influencesList = self.__parentWidget.jointIndexList[node]
            local_column = influencesList[col]
            value = self._data[row][local_column]
        except:
            value = None
            
        if row in self.meshIndexRows or value is None:
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
     