# -*- coding: utf-8 -*-
from .qt_util import *
from .utils import *
from functools import partial
from ..Maya.tools.shared import *
from ..Maya.tools.skinCluster import comparejointInfluences, execCopySourceTarget

class TransferWeightsWidget(QWidget):
    def __init__(self, parent=None):
        super(TransferWeightsWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()

        v1 = self.__vertexFunc()
        v2 = self.__skinClusterFunc()
        
        for v in [v2, v1]:
            self.layout().addLayout(v)

        self.__restoreSettings()    

    def __defaults(self):
        self.settings = QSettings('TransferWeightsWidget', 'storedSelection')

    def __vertexFunc(self, ):
        v1 = nullVBoxLayout()
        h = nullHBoxLayout()

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.itemSelectionChanged.connect(self.__applySelectionCB)
        self.list.itemDoubleClicked.connect(self.__deleteItemCB)

        btn = buttonsToAttach('StoreSelection', self.__storeSelectionCB)
        btn1 = buttonsToAttach('ClearList', self.__clearSelectionCB)
        h.addWidget(btn)
        h.addWidget(btn1)

        v1.addWidget(self.list)
        v1.addLayout(h)
        return v1

    def __skinClusterFunc(self):
        v2 = nullVBoxLayout()
        grid  = nullGridLayout()
        self.source = QLabel('No source')
        self.target = QLabel('No target')
        btn = buttonsToAttach("Grab Source", partial(self.__grabSkinCl, self.source))
        btn1 = buttonsToAttach("Grab Target", partial(self.__grabSkinCl, self.target))

        for i, w in enumerate([self.source, self.target, btn, btn1]):
            row = i/2
            grid.addWidget(w, i -(row*2), row)

        
        btn2 = buttonsToAttach('Copy selected vertices', self.__copySkinDataCB)
        self.additive = QCheckBox('Additive')
        v2.addLayout(grid)
        v2.addWidget(btn2)
        v2.addWidget(self.additive)
        v2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.__loadBar= None
        return v2

    def __restoreSettings(self):    
        for key in self.settings.allKeys():
            forceString = str(key)
            if not 'vtxSel/' in str(key):
                continue
            data = self.settings.value(key, None)
            if data is None:
                continue
            if QT_VERSION == "pyqt4":
                self.__addItem(key.split('/',1)[1], data.toPyObject())
            else:
                self.__addItem(key.split('/',1)[1], data)

    def __grabSkinCl(self, toSet = None):
        skinCluster = skinCluster()
        if skinCluster is None:
            return
        toSet.setText(skinCluster)
    
    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar
    
    def __copySkinDataCB(self):
        source = str(self.source.text())
        target = str(self.target.text())
        if not cmds.objExists(source) or not cmds.objExists(target):
            cmds.error('Must load an existing source and target skin cluster to copy between')
            return
        expandedVertices = convertToVertexList(cmds.ls(sl=1, fl=1))
        if not expandedVertices:
            cmds.error('Must select vertices to copy weights for')
        
        outInfluences = cmds.skinCluster(target, q=True, influence=True)
        inInfluences = cmds.skinCluster(source, q=True, influence=True)
        
        add = []
        for influence in inInfluences:
            if influence not in outInfluences:
                add.append(influence)
        if add:
            cmds.skinCluster(target, addInfluence=add, wt=0, e=True)
        
        inWeights = cmds.SkinWeights(cmds.skinCluster(source, q=True, g=True)[0], source, q=True)
        outWeights = cmds.SkinWeights(cmds.skinCluster(target, q=True, g=True)[0], target, q=True)
        outInfluences = cmds.skinCluster(target, q=True, influence=True)
        
        numInInf = len(inInfluences)
        numOutInf = len(outInfluences)

        if self.__loadBar != None:
            percentage = 99.0/len(expandedVertices) 
            self.__loadBar.message = "transfering weights from %s >> %s"%(source, target)
        
        for iteration, vertex in enumerate(expandedVertices):
            id = int(vertex.rsplit('[',1)[-1].split(']',1)[0])
            if not self.additive.isChecked():
                outWeights[id * numOutInf : (id + 1) * numOutInf] = [0]*numOutInf
            for i in range(numInInf):
                offset = outInfluences.index(inInfluences[i])
                outWeights[id * numOutInf + offset] += inWeights[id * numInInf + i]
            tw = 0
            for i in range(numOutInf):
                tw += outWeights[id * numOutInf + i]
            if tw == 0:
                continue
            ratio = 1.0 / tw
            for i in range(numOutInf):
                outWeights[id * numOutInf + i] *= ratio

            if self.__loadBar != None:
                self.__loadBar.setValue( percentage*(iteration + 1) )
                qApp.processEvents()
                
        cmds.SkinWeights(cmds.skinCluster(target, q=True, g=True)[0], target, nwt=outWeights)
        if self.__loadBar != None:
            self.__loadBar.setValue( 100 )
            qApp.processEvents()

    def __addItem(self, name, pyData):
        match = self.list.findItems(name, Qt.MatchExactly)
        if len(match):
            match[0].setData(Qt.UserRole, pyData)
            return match[0]
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, pyData)
        self.list.addItem(item)
        return item

    def __deleteItemCB(self, item):
        self.settings.remove(item.text())
        self.list.takeItem(self.list.row(item))

    def __clearSelectionCB(self):
        self.list.clear()
        self.settings.clear()

    def __storeSelectionCB(self):
        expandedVertices = convertToVertexList(cmds.ls(sl=1, fl=1))
        
        name = QInputDialog.getText(self, 'Name selection', 'Please enter a name for this selection', text=expandedVertices[0].split('.',1)[0])
        if not name[1]:
            return

        item = self.__addItem(name[0], expandedVertices)
        self.settings.setValue('vtxSel/%s'%name[0], item.data(Qt.UserRole))
        cmds.select(expandedVertices)

    def __applySelectionCB(self):
        cmds.select(clear=True)
        for item in self.list.selectedItems():
            if QT_VERSION == "pyqt4":
                selectionItem = item.data(Qt.UserRole).toPyObject()
            else:
                selectionItem = item.data(Qt.UserRole)

            if cmds.objExists(str(selectionItem[0].split('.')[0])): 
                doCorrectSelectionVisualization(str(selectionItem[0].split('.')[0]))
                cmds.select(selectionItem, add=True)
            else:
                cmds.warning('%s does not exist in currentScene'%(selectionItem[0].split('.')[0]))

class ClosestVertexWeightWidget(QWidget):
    def __init__(self, parent=None):
        super(ClosestVertexWeightWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()
        self.__setButtons()
        self.clearUI()

    def __setButtons(self):
        label = QLabel("look closest Vtx amount:")
        self.spinBox = QSpinBox()
        self.spinBox.setSingleStep(1)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(6)

        h0 = nullHBoxLayout()
        h1 = nullHBoxLayout()
        h2 = nullHBoxLayout()

        for h in [h0, h1, h2]:
            self.layout().addLayout(h)

        for w in [label, self.spinBox]:
            h0.addWidget(w)

        self.line1 = QLineEdit()
        self.line2 = QLineEdit()
        for l in [self.line1, self.line2]:
            l.userData = []
            l.setEnabled(0)

        btn1=  buttonsToAttach("<< Source", partial(self.__setValue, self.line1))
        btn2=  buttonsToAttach("<< Target", partial(self.__setValue, self.line2))
        
        for w in [self.line1, btn1]:
            h1.addWidget(w)
        for w in [self.line2, btn2]:
            h2.addWidget(w)

        self.trnsComp = buttonsToAttach("Transfer Components", self._transferComp)

        self.rst = buttonsToAttach("reset", self.clearUI)
        for btn in [ self.trnsComp, self.rst]:
            self.layout().addWidget(btn)

    def __defaults(self):
        self.compSetting = [0,0]
        self.__loadBar = None

    def clearUI(self):
        for l in [self.line1, self.line2]:
            l.setText('')
            l.setStyleSheet('background-color: #C23A3A;')
        self.compSetting = [0,0]
        self.__checkEnabled()

    def __setValue(self, inLineEdit):
        verts = convertToVertexList(cmds.ls(sl=True,fl=True))
        mesh, selection, skinCluster = self.__storeVerts(verts)
        inLineEdit.userData  = [selection, skinCluster]
        inLineEdit.setText(mesh)
        inLineEdit.setStyleSheet('background-color: #17D206;')
        self.compSetting[[self.line1,self.line2].index(inLineEdit)] = 1
        self.__checkEnabled()

    def __checkEnabled(self):
        self.trnsComp.setEnabled(self.compSetting == [1,1])
        self.rst.setEnabled(self.compSetting != [0,0])

    def __storeVerts(self, inputVerts):
        Mesh        = inputVerts[0].split('.')[0]
        SkinCluster = skinCluster(Mesh)

        Selection     = []
        for i in inputVerts:
            expandedVertices = convertToVertexList(i)
            for vert in expandedVertices:
                if vert in Selection:
                    continue
                Selection.append(vert)
        return  Mesh, Selection, SkinCluster

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar
    
    def _transferComp(self):
        if '' in [self.line1.text(), self.line2.text()]:
            cmds.warning('source or target selection is not defined!')
            return

        TargetSelection, TargetSkinCluster = self.line1.userData
        SourceSelection, SourceSkinCluster = self.line2.userData
        
        execCopySourceTarget(
            TargetSkinCluster = TargetSkinCluster, 
            SourceSkinCluster = SourceSkinCluster, 
            TargetSelection = TargetSelection, 
            SourceSelection = SourceSelection, 
            smoothValue = self.spinBox.value(),
            progressBar = self.__loadBar)

        self.clearUI()
