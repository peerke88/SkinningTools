# -*- coding: utf-8 -*-
from functools import partial
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools.shared import *
from SkinningTools.Maya import interface
from SkinningTools.Maya.tools.skinCluster import execCopySourceTarget, SoftSkinBuilder



# @TODO: move this over to maya/tools or move the entire file over to maya
from maya import cmds


class TransferWeightsWidget(QWidget):
    toolName = "TransferWeightsWidget"

    def __init__(self, parent=None):
        super(TransferWeightsWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()

        self.textInfo = {}

        v1 = self.__vertexFunc()
        v2 = self.__skinClusterFunc()

        for v in [v2, v1]:
            self.layout().addLayout(v)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.__restoreSettings()
    
    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName) 
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui setup ---------------------------------- 
    def __defaults(self):
        self.settings = QSettings('TransferWeightsWidget', 'storedSelection')

    def __vertexFunc(self, ):
        v1 = nullVBoxLayout()
        h = nullHBoxLayout()

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.itemSelectionChanged.connect(self.__applySelectionCB)
        self.list.itemDoubleClicked.connect(self.__deleteItemCB)

        self.textInfo["btn"] = buttonsToAttach('StoreSelection', self.__storeSelectionCB)
        self.textInfo["btn1"] = buttonsToAttach('ClearList', self.__clearSelectionCB)
        h.addWidget(self.textInfo["btn"])
        h.addWidget(self.textInfo["btn1"])

        v1.addWidget(self.list)
        v1.addLayout(h)
        return v1

    def __skinClusterFunc(self):
        v2 = nullVBoxLayout()
        grid = nullGridLayout()
        self.textInfo["source"] = QLineEdit()
        self.textInfo["source"].setPlaceholderText("No source given...")
        self.textInfo["target"] = QLineEdit()
        self.textInfo["target"].setPlaceholderText("No target given...")
        self.textInfo["btn2"] = buttonsToAttach("Grab Source", partial(self.__grabSkinCl, self.textInfo["source"]))
        self.textInfo["btn3"] = buttonsToAttach("Grab Target", partial(self.__grabSkinCl, self.textInfo["target"]))

        for l in [self.textInfo["source"], self.textInfo["target"]]:
            l.setText('')
            l.setStyleSheet('color:#000; background-color: #ad4c4c;')
            l.setEnabled(False)

        for i, w in enumerate([self.textInfo["source"], self.textInfo["target"], self.textInfo["btn2"], self.textInfo["btn3"]]):
            row = i / 2
            grid.addWidget(w, i - (row * 2), row)

        self.textInfo["btn4"] = buttonsToAttach('Copy selected vertices', self.__copySkinDataCB)
        self.textInfo["additive"] = QCheckBox('Additive')
        v2.addLayout(grid)
        v2.addWidget(self.textInfo["btn4"])
        v2.addWidget(self.textInfo["additive"])
        v2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.__loadBar = None
        return v2

    def __restoreSettings(self):
        for key in self.settings.allKeys():
            try:
                forceString = str(key)
            except:
                continue
            if not 'vtxSel/' in str(key):
                continue
            data = self.settings.value(key, None)
            if data is None:
                continue
            if QT_VERSION == "pyqt4":
                self.__addItem(key.split('/', 1)[1], data.toPyObject())
            else:
                self.__addItem(key.split('/', 1)[1], data)

    def __grabSkinCl(self, toSet=None):
        sc = skinCluster()
        if sc is None:
            toSet.setText('')
            toSet.setStyleSheet('color:#000; background-color: #ad4c4c;')
            return
        toSet.setText(sc)
        toSet.setStyleSheet('background-color: #17D206;')

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar

    def __copySkinDataCB(self):
        source = str(self.textInfo["source"].text())
        target = str(self.textInfo["target"].text())
        if not cmds.objExists(source) or not cmds.objExists(target):
            print('Must load an existing source and target skin cluster to copy between')
            return
        expandedVertices = convertToVertexList(cmds.ls(sl=1, fl=1))
        if not expandedVertices:
            print('Must select vertices to copy weights for')
            return
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

        percentage = 1.0
        if self.__loadBar is not None:
            percentage = 99.0 / len(expandedVertices)
            self.__loadBar.message = "transfering weights from %s >> %s" % (source, target)

        for iteration, vertex in enumerate(expandedVertices):
            identifier = int(vertex.rsplit('[', 1)[-1].split(']', 1)[0])
            if not self.additive.isChecked():
                outWeights[identifier * numOutInf: (identifier + 1) * numOutInf] = [0] * numOutInf
            for i in range(numInInf):
                offset = outInfluences.index(inInfluences[i])
                outWeights[identifier * numOutInf + offset] += inWeights[identifier * numInInf + i]
            tw = 0
            for i in range(numOutInf):
                tw += outWeights[identifier * numOutInf + i]
            if tw == 0:
                continue
            ratio = 1.0 / tw
            for i in range(numOutInf):
                outWeights[identifier * numOutInf + i] *= ratio

            if self.__loadBar is not None:
                self.__loadBar.setValue(percentage * (iteration + 1))
                qApp.processEvents()

        cmds.SkinWeights(cmds.skinCluster(target, q=True, g=True)[0], target, nwt=outWeights)
        if self.__loadBar is not None:
            self.__loadBar.setValue(100)
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

        name = QInputDialog.getText(self, 'Name selection', 'Please enter a name for this selection', text=expandedVertices[0].split('.', 1)[0])
        if not name[1]:
            return

        item = self.__addItem(name[0], expandedVertices)
        self.settings.setValue('vtxSel/%s' % name[0], item.data(Qt.UserRole))
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
                cmds.warning('%s does not exist in currentScene' % (selectionItem[0].split('.')[0]))

class ClosestVertexWeightWidget(QWidget):
    toolName = "ClosestVertexWeightWidget"

    def __init__(self, parent=None):
        super(ClosestVertexWeightWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()
        self.__setButtons()
        self.clearUI()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui setup ---------------------------------- 
    def __setButtons(self):
        self.textInfo["label"] = QLabel("look closest Vtx amount:")
        self.spinBox = QSpinBox()
        self.spinBox.setSingleStep(1)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(6)

        h0 = nullHBoxLayout()
        h1 = nullHBoxLayout()
        h2 = nullHBoxLayout()

        for h in [h0, h1, h2]:
            self.layout().addLayout(h)

        for w in [self.textInfo["label"], self.spinBox]:
            h0.addWidget(w)

        self.textInfo["line1"] = QLineEdit()
        self.textInfo["line1"].setPlaceholderText("No Source given...")
        self.textInfo["line2"] = QLineEdit()
        self.textInfo["line2"].setPlaceholderText("No Target given...")
        for l in [self.textInfo["line1"], self.textInfo["line2"]]:
            l.userData = []
            l.setEnabled(0)

        self.textInfo["btn1"] = buttonsToAttach("<< Source", partial(self.__setValue, self.textInfo["line1"]))
        self.textInfo["btn2"] = buttonsToAttach("<< Target", partial(self.__setValue, self.textInfo["line2"]))

        for w in [self.textInfo["line1"], self.textInfo["btn1"]]:
            h1.addWidget(w)
        for w in [self.textInfo["line2"], self.textInfo["btn2"]]:
            h2.addWidget(w)

        self.textInfo["trnsComp"] = buttonsToAttach("Transfer Components", self._transferComp)

        self.textInfo["rst"] = buttonsToAttach("reset", self.clearUI)
        for btn in [self.textInfo["trnsComp"], self.textInfo["rst"]]:
            self.layout().addWidget(btn)
        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __defaults(self):
        self.textInfo = {}
        self.compSetting = [0, 0]
        self.__loadBar = None

    def clearUI(self):
        for l in [self.textInfo["line1"], self.textInfo["line2"]]:
            l.setText('')
            l.setStyleSheet('color:#000; background-color: #ad4c4c;')
        self.compSetting = [0, 0]
        self.__checkEnabled()

    def __setValue(self, inLineEdit):
        verts = convertToVertexList(cmds.ls(sl=True, fl=True))
        mesh, selection, skinCluster = self.__storeVerts(verts)
        inLineEdit.userData = [selection, skinCluster]
        inLineEdit.setText(mesh)
        inLineEdit.setStyleSheet('background-color: #17D206;')
        self.compSetting[[self.textInfo["line1"], self.textInfo["line2"]].index(inLineEdit)] = 1
        self.__checkEnabled()

    def __checkEnabled(self):
        self.textInfo["trnsComp"].setEnabled(self.compSetting == [1, 1])
        self.textInfo["rst"].setEnabled(self.compSetting != [0, 0])

    def __storeVerts(self, inputVerts):
        Mesh = inputVerts[0].split('.')[0]
        SkinCluster = skinCluster(Mesh)

        Selection = []
        for i in inputVerts:
            expandedVertices = convertToVertexList(i)
            for vert in expandedVertices:
                if vert in Selection:
                    continue
                Selection.append(vert)
        return Mesh, Selection, SkinCluster

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar

    def _transferComp(self):
        if '' in [self.textInfo["line1"].text(), self.textInfo["line2"].text()]:
            cmds.warning('source or target selection is not defined!')
            return

        TargetSelection, TargetSkinCluster = self.textInfo["line1"].userData
        SourceSelection, SourceSkinCluster = self.textInfo["line2"].userData

        execCopySourceTarget(
            TargetSkinCluster=TargetSkinCluster,
            SourceSkinCluster=SourceSkinCluster,
            TargetSelection=TargetSelection,
            SourceSelection=SourceSelection,
            smoothValue=self.spinBox.value(),
            progressBar=self.__loadBar)

        self.clearUI()

class TransferUvsWidget(QWidget):
    toolName = "TransferUvsWidget"

    def __init__(self, parent=None):
        super(TransferUvsWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()
        self.__setButtons()
        self.clearUI()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui setup ---------------------------------- 
    def __setButtons(self):
        label = QLabel("transfer Uv from static to skinned:")
        h0 = nullHBoxLayout()

        self.textInfo["line1"] = QLineEdit()
        self.textInfo["line1"].setPlaceholderText("No Source given...")
        self.textInfo["line2"] = QLineEdit()
        self.textInfo["line2"].setPlaceholderText("No Target given...")
        for l in [self.textInfo["line1"], self.textInfo["line2"]]:
            l.setEnabled(0)
        
        self.combo1 = QComboBox()
        self.combo2 = QComboBox()
        self.textInfo["sourceBtn"] = buttonsToAttach( "Source", partial(self.__setValue, self.textInfo["line1"], self.combo1))
        self.textInfo["targetBtn"] = buttonsToAttach( "Target", partial(self.__setValue, self.textInfo["line2"], self.combo2))

        h1 = nullHBoxLayout()
        h2 = nullHBoxLayout()
        h3 = nullHBoxLayout()

        self.layout().addWidget(label)
        for h in [h0, h1]:
            self.layout().addLayout(h)
        
        for w in [self.textInfo["sourceBtn"], self.textInfo["targetBtn"]]:
            h0.addWidget(w)

        for h in [h2, h3]:
            h1.addLayout(h)

        for w in [self.textInfo["line1"], self.combo1]:
            h2.addWidget(w)

        for w in [self.textInfo["line2"], self.combo2]:
            h3.addWidget(w)

        self.textInfo["trnsComp"] = buttonsToAttach("Transfer uvs", self._transferUV)

        self.textInfo["rst"] = buttonsToAttach("reset", self.clearUI)
        for btn in [self.textInfo["trnsComp"], self.textInfo["rst"]]:
            self.layout().addWidget(btn)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def __defaults(self):
        self.textInfo = {}
        self.compSetting = [0, 0]
        self.__loadBar = None

    
    def clearUI(self):
        for l in [self.textInfo["line1"], self.textInfo["line2"]]:
            l.setText('')
            l.setStyleSheet('color:#000; background-color: #ad4c4c;')
        self.compSetting = [0, 0]
        self.__checkEnabled()

    def __setValue(self, inLineEdit, inCombo):
        sel = interface.getSelection()
        if len(sel) > 1:
            sel = sel[0]
        if "." in sel:
            sel = sel.split('.')[0]
        
        inLineEdit.setText(sel)
        inLineEdit.setStyleSheet('background-color: #17D206;')

        uvSets = interface.getUVInfo(sel)
        inCombo.clear()
        inCombo.addItems(uvSets)

        self.compSetting[[self.textInfo["line1"], self.textInfo["line2"]].index(inLineEdit)] = 1

        self.__checkEnabled()

    def __checkEnabled(self):
        self.textInfo["trnsComp"].setEnabled(self.compSetting == [1, 1])
        self.textInfo["rst"].setEnabled(self.compSetting != [0, 0])

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar

    def _transferUV(self):
        if '' in [self.textInfo["line1"].text(), self.textInfo["line2"].text()]:
            cmds.warning('source or target selection is not defined!')
            return

        interface.transferUV(self.textInfo["line1"].text(), self.textInfo["line2"].text(), 
                             sMap = self.combo1.currentText(), tMap = self.combo2.currentText(), 
                             progressBar = self.__loadBar)

        self.clearUI()

class AssignWeightsWidget(QWidget):
    toolName = "AssignWeightsWidget"

    '''
    #@note: untested!
    
    idea:

    add all joints in a list + a select button next to it
    all buttons are gray from the start

    once the button next to the joint is selected it will store vertex selection into the button and make it green (selection can be soft selection)
    maybe add a second button to analize the current vertices already inluenced by that given joint (turn buttons red?)

    make sure all weights are normalized in the end
    if the joints are not pre-analized we do an add influence command
    otherwise we do a full override(maybe with apiweights functions)
    '''
    def __init__(self, parent=None, progressBar = None):
        super(AssignWeightsWidget, self).__init__(parent)
        self.mainLayout = nullVBoxLayout()
        self.setLayout(self.mainLayout)

        self.__softSkinData = SoftSkinBuilder(progressBar)

        self.__mesh = ''
        self.__widgets = {}

        self.__defaults()
        self.__setButtons()
        self.clearUI()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        for key, value in localeDict.iteritems():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui setup ----------------------------------
    def __defaults(self):
        self.textInfo = {}
        
    def _JointSoftGroup(self, joint):
        # todo: do we need more info in this setup?
        if joint in self.__widgets.keys():
            return
        h = nullHBoxLayout()
        lbl = QLabel(joint)

        self.textInfo["view"] = toolButton(":/hotkeyFieldSearch.png")
        self.textInfo["assign"] = toolButton(":/aselect.png")
        self.textInfo["clear"] = toolButton(":/noAccess.png")
        self.textInfo["view"].clicked.connect( partial(self._viewData, joint)) 
        self.textInfo["assign"].clicked.connect(partial(self._addData, joint))
        self.textInfo["clear"].clicked.connect(partial(self._cleardData, joint))
        for w in [lbl, self.textInfo["view"], self.textInfo["assign"], self.textInfo["clear"]]:
            w.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")
            h.addWidget(w)

        self.frameLayout.addLayout(h)
        self.__widgets[joint] = h
        
    def _addData(self, joint):
        self.__softSkinData.addSoftSkinInfo(joint)

    def _cleardData(self, joint):
        self.__softSkinData.removeData(joint)

    def _viewData(self, joint):
        cmds.select(self.__softSkinData.getVerts(joint), r=1)

    def searchJointName(self):
        _allJoints = self.__widgets.keys()
        jointSearch = _allJoints
        if str(searchLine.text()) != '':
            _text = searchLine.text().split(' ')
            _text = [name for name in _text if name != '']
            jointSearch = [inf for inf in _allJoints if any([True if s.upper() in inf.split('|')[-1].upper() else False for s in _text])]
        self.inflEdit.showOnlyJoints(jointSearch)

        for bone, w in self.__widgets.iteritems():
            w.setVisible(bone in jointSearch)


    def __setButtons(self):
        h = nullHBoxLayout()
        self.textInfo["searchLine"] = QLineEdit()
        self.textInfo["searchLine"].setPlaceholderText("Type part of joint name to search...")
        self.textInfo["searchLine"].editingFinished.connect(self.searchJointName)
        self.textInfo["searchLine"].textChanged.connect(self.searchJointName)
        

        self.textInfo["lbl"] = QLabel("Search:")
        self.textInfo["analyzeBtn"] = buttonsToAttach("analyze", self.addBones)
        self.textInfo["addBtn"] = buttonsToAttach("add", self.addBone)
        for w in [self.textInfo["lbl"], self.textInfo["searchLine"], self.textInfo["analyzeBtn"], self.textInfo["addBtn"]]:
            h.addWidget(w)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(1)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        _frame = QFrame()
        scrollArea.setWidget(_frame)
        self.frameLayout = nullVBoxLayout()
        _frame.setLayout(self.frameLayout)
        self.mainLayout.addLayout(h)
        self.mainLayout.addWidget(scrollArea)
        self.textInfo["build"] = buttonsToAttach("build info", self.build)
        self.mainLayout.addWidget(self.textInfo["build"])

    def addBone(self):
        # get the joint to add to the current setup
        selected = interface.getSelection()
        allJoints = interface.getAllJoints()
        for jnt in selected:
            if not jnt in allJoints:
                continue
            if "|" in jnt:
                jnt = jnt.rsplit("|")[-1]
            self._JointSoftGroup(jnt)

    def addBones(self):
        self.clearUI()

        selection = interface.getSelection()
        print(selection)
        if len(selection) > 0:
            selection = selection[0]
        if "." in selection:
            selection = selection.split('.')[0]    
        _data = self.__softSkinData.analyzeSkin(selection)
        for jnt in _data:
            if "|" in jnt:
                jnt = jnt.rsplit("|")[-1]
            self._JointSoftGroup(jnt)

    def build(self):
        # note: add only when not all joints are configured
        add = True
        if self.__mesh == '':
            self.__mesh = interface.getSelection()[0]
            add = False
        self.__softSkinData.setSoftSkinInfo(self.__mesh, add)

    def clearUI(self):
        for jnt, h in self.__widgets.iteritems():
            h.deleteLater()


def testUI(widgetIndex = 0):
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    widgets = {0: TransferWeightsWidget,
               1: ClosestVertexWeightWidget,
               2: TransferUvsWidget,
               3: AssignWeightsWidget}

    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("%s Test window"%widgets[widgetIndex].toolName)
    wdw = widgets[widgetIndex](parent = mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw