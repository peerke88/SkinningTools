# -*- coding: utf-8 -*-
from functools import partial
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from SkinningTools.Maya.tools.shared import *
from SkinningTools.Maya import interface, api
from SkinningTools.Maya.tools.skinCluster import execCopySourceTarget
# @TODO: move this over to maya/tools or move the entire file over to maya
from maya import cmds


class TransferWeightsWidget(QWidget):
    toolName = "TransferWeightsWidget"

    @dec_loadPlugin(interface.getInterfaceDir() + "/plugin/skinToolWeightsCpp/comp/Maya%s/plug-ins/skinCommands%s" % (api.getMayaVersion(), api.getPluginSuffix()))
    def __init__(self, parent=None):
        super(TransferWeightsWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()

        self.__defaults()

        v1 = self.__vertexFunc()
        v2 = self.__skinClusterFunc()

        for v in [v2, v1]:
            self.layout().addLayout(v)

        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.__restoreSettings()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict={}):
        for key, value in localeDict.items():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName)
        _trs = translator.showUI(_dict, widgetName=self.toolName)

    # --------------------------------- ui setup ----------------------------------

    def __defaults(self):
        self.settings = QSettings('TransferWeightsWidget', 'storedSelection')
        self.textInfo = {}
        self.__loadBar = None
        self._toSelect = {"sources": [],
                          "targets": []}

    def addLoadingBar(self, loadingBar):
        self.__loadBar = loadingBar

    def __vertexFunc(self, ):
        v1 = nullVBoxLayout()
        h = nullHBoxLayout()

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.itemSelectionChanged.connect(self.__applySelectionCB)
        self.list.itemDoubleClicked.connect(self.__deleteItemCB)

        self.textInfo["btn"] = buttonsToAttach('StoreSelection', self.__storeSelectionCB)
        self.textInfo["btn1"] = buttonsToAttach('ClearList', self.__clearSelectionCB)
        for w in ["btn", "btn1"]:
            h.addWidget(self.textInfo[w])
            self.textInfo[w].setWhatsThis("transfer")

        v1.addWidget(self.list)
        v1.addLayout(h)
        return v1

    def __restoreSettings(self):
        for key in self.settings.allKeys():
            if not 'vtxSel/' in str(key):
                continue
            data = self.settings.value(key, None)
            if data is None:
                continue
            if QT_VERSION == "pyqt4":
                self.__addItem(key.split('/', 1)[1], data.toPyObject())
            else:
                self.__addItem(key.split('/', 1)[1], data)

    def selVert(self, toSel):
        cmds.select(self._toSelect[toSel], r=1)

    def __grabSkinCl(self, toSet, toEnable, selectSet):
        sc = skinCluster()
        if sc is None:
            toSet.setText('')
            toSet.setStyleSheet('color:#000; background-color: #ad4c4c;')
            toEnable.setEnabled(False)
            return
        toSet.setText(sc)
        toSet.setStyleSheet('background-color: #17D206;')
        selection = interface.getSelection()
        if "." in selection[0]:
            selection = convertToVertexList(selection)
        self._toSelect[selectSet] = selection
        toEnable.setEnabled(True)

    def __skinClusterFunc(self):
        v2 = nullVBoxLayout()
        grid = nullGridLayout()
        self.textInfo["source"] = QLineEdit()
        self.textInfo["source"].setPlaceholderText("No source given...")
        self.textInfo["source1"] = buttonsToAttach("select source vertices", partial(self.selVert, "sources"))
        self.textInfo["target"] = QLineEdit()
        self.textInfo["target"].setPlaceholderText("No target given...")
        self.textInfo["target1"] = buttonsToAttach("select target vertices", partial(self.selVert, "targets"))
        self.textInfo["btn2"] = buttonsToAttach("Grab Source", partial(self.__grabSkinCl, self.textInfo["source"], self.textInfo["source1"], "sources"))
        self.textInfo["btn3"] = buttonsToAttach("Grab Target", partial(self.__grabSkinCl, self.textInfo["target"], self.textInfo["target1"], "targets"))

        for l in [self.textInfo["source"], self.textInfo["target"],
                  self.textInfo["source1"], self.textInfo["target1"]]:
            if not isinstance(l, QPushButton):
                l.setText('')
                l.setStyleSheet('color:#000; background-color: #ad4c4c;')
            l.setEnabled(False)

        for i, w in enumerate([self.textInfo["source"], self.textInfo["target"],
                               self.textInfo["source1"], self.textInfo["target1"],
                               self.textInfo["btn2"], self.textInfo["btn3"]]):
            row = int(i / 2)
            grid.addWidget(w, i - (row * 2), row)

        hbox = nullHBoxLayout()
        self.textInfo["btn4"] = buttonsToAttach('Copy selected vertices', partial(self.__copySkinDataCB, True))
        self.textInfo["btn5"] = buttonsToAttach('Copy stored vertices', partial(self.__copySkinDataCB, False))
        self.textInfo["additive"] = QCheckBox('Additive')

        v2.addLayout(grid)
        hbox.addWidget(self.textInfo["btn4"])
        hbox.addWidget(self.textInfo["btn5"])
        v2.addLayout(hbox)
        v2.addWidget(self.textInfo["additive"])
        v2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        return v2

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

    def __copySkinDataCB(self, oneToOne=True):
        source = str(self.textInfo["source"].text())
        target = str(self.textInfo["target"].text())
        if not cmds.objExists(source) or not cmds.objExists(target):
            print('Must load an existing source and target skin cluster to copy between')
            return
        expandedVertices = convertToVertexList(cmds.ls(sl=1, fl=1))

        outInfluences = cmds.skinCluster(target, q=True, influence=True)
        inInfluences = cmds.skinCluster(source, q=True, influence=True)

        add = []
        for influence in inInfluences:
            if influence not in outInfluences:
                add.append(influence)
        if add:
            cmds.skinCluster(target, addInfluence=add, wt=0, e=True)

        sourceGeo = cmds.ls(cmds.skinCluster(source, q=True, g=True)[0], sl=0, fl=1, l=1)[0]
        targetGeo = cmds.ls(cmds.skinCluster(target, q=True, g=True)[0], sl=0, fl=1, l=1)[0]

        outInfluences = cmds.skinCluster(target, q=True, influence=True)

        numInInf = len(inInfluences)
        numOutInf = len(outInfluences)

        _isChecked = self.textInfo["additive"].isChecked()
        if _isChecked and oneToOne:
            if not expandedVertices:
                print('Must select vertices to copy weights for')
                return
            if len(convertToVertexList(sourceGeo)) != len(convertToVertexList(targetGeo)):
                print('meshes are not identical!')

            inWeights = cmds.SkinWeights(sourceGeo, source, q=True)
            outWeights = cmds.SkinWeights(targetGeo, target, q=True)
            percentage = 99.0 / len(expandedVertices)
            setProgress(0, self.__loadBar, "transfering weights from %s >> %s" % (source, target))
            # use the old way for additions
            for iteration, vertex in enumerate(expandedVertices):
                identifier = int(vertex.rsplit('[', 1)[-1].split(']', 1)[0])
                outWeights[identifier * numOutInf: (identifier + 1) * numOutInf] = [0] * numOutInf

                for i in range(numInInf):
                    offset = outInfluences.index(inInfluences[i])
                    outWeights[(identifier * numOutInf) + offset] += inWeights[(identifier * numInInf) + i]

                tw = sum(outWeights[(identifier * numOutInf):((identifier + 1) * numOutInf)])

                if tw == 0:
                    continue

                ratio = 1.0 / tw
                for i in range(numOutInf):
                    outWeights[identifier * numOutInf + i] *= ratio

                if iteration % 10 == 0:
                    setProgress(percentage * iteration, self.__loadBar, "transfering weights from %s >> %s" % (source, target))

            cmds.SkinWeights(targetGeo, target, nwt=outWeights)
            setProgress(100, self.__loadBar, "transfered weights from %s >> %s" % (source, target))
            return

        #  additive no longer possible
        if oneToOne and expandedVertices:
            if sourceGeo in expandedVertices[0]:
                _targetVerts = convertToVertexList(targetGeo)
            else:
                _targetVerts = convertToVertexList(sourceGeo)

            sourceVerts = closestPosCheck(expandedVertices, _targetVerts, self.__loadBar)
            targetVerts = expandedVertices

        elif not oneToOne:
            # use the stored values
            if [] in self._toSelect.values():
                print('no valid entrys found')
                return
            sourceVerts = self._toSelect["sources"]
            targetVerts = self._toSelect["targets"]
        else:
            print('Must select vertices to copy weights, or copy with the stored weights')

        cmds.copySkinWeights(sourceVerts, targetVerts, noMirror=True, surfaceAssociation='closestPoint', ia=['oneToOne', 'name'])
        setProgress(100, self.__loadBar, "transfered weights from %s >> %s" % (source, target))


class ClosestVertexWeightWidget(QWidget):
    toolName = "ClosestVertexWeightWidget"

    def __init__(self, parent=None):
        super(ClosestVertexWeightWidget, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.__defaults()
        self.__setButtons()
        self.clearUI()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict={}):
        for key, value in localeDict.items():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName=self.toolName)

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
            w.setWhatsThis("copyClosest")
        for w in [self.textInfo["line2"], self.textInfo["btn2"]]:
            h2.addWidget(w)
            w.setWhatsThis("copyClosest")

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
        if cmds.objectType(Mesh) != "transform":
            Mesh = cmds.listRelatives(Mesh, parent=1, f=1)[0]
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

        SourceSelection, SourceSkinCluster = self.textInfo["line1"].userData
        TargetSelection, TargetSkinCluster = self.textInfo["line2"].userData

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
    def translate(self, localeDict={}):
        for key, value in localeDict.items():
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
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        """
        from SkinningTools.UI import translator
        _dict = self.getButtonText()
        _trs = translator.showUI(_dict, widgetName=self.toolName)

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
        self.textInfo["sourceBtn"] = buttonsToAttach("Source", partial(self.__setValue, self.textInfo["line1"], self.combo1))
        self.textInfo["targetBtn"] = buttonsToAttach("Target", partial(self.__setValue, self.textInfo["line2"], self.combo2))

        h1 = nullHBoxLayout()
        h2 = nullHBoxLayout()
        h3 = nullHBoxLayout()

        self.layout().addWidget(label)
        for h in [h0, h1]:
            self.layout().addLayout(h)

        for w in [self.textInfo["sourceBtn"], self.textInfo["targetBtn"]]:
            h0.addWidget(w)
            w.setWhatsThis("uvTransfer")

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

        if type(sel) in (list, tuple) and sel != []:
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
                             sMap=self.combo1.currentText(), tMap=self.combo2.currentText(),
                             progressBar=self.__loadBar)

        self.clearUI()


def testUI(widgetIndex=0):
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    widgets = {0: TransferWeightsWidget,
               1: ClosestVertexWeightWidget,
               2: TransferUvsWidget}

    mwd = QMainWindow(mainWindow)
    mwd.setWindowTitle("%s Test window" % widgets[widgetIndex].toolName)
    wdw = widgets[widgetIndex](parent=mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
