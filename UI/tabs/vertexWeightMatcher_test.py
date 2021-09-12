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

    def __grabSkinCl(self, toSet, selectSet):
        sc = skinCluster()
        if sc is None:
            toSet.setText('')
            toSet.setStyleSheet('color:#000; background-color: #ad4c4c;')
            return
        toSet.setText(sc)
        toSet.setStyleSheet('background-color: #17D206;')
        selection = interface.getSelection()
        if "." in selection[0]:
            selection = convertToVertexList(selection)
        self._toSelect[selectSet] = selection

    def __skinClusterFunc(self):
        v2 = nullVBoxLayout()
        grid = nullGridLayout()
        self.textInfo["source"] = QLineEdit()
        self.textInfo["source"].setPlaceholderText("No source given...")
        self.textInfo["source1"] = buttonsToAttach("select source vertices", partial(self.selVert, "sources"))
        self.textInfo["target"] = QLineEdit()
        self.textInfo["target"].setPlaceholderText("No target given...")
        self.textInfo["target1"] = buttonsToAttach("select target vertices", partial(self.selVert, "targets"))
        self.textInfo["btn2"] = buttonsToAttach("Grab Source", partial(self.__grabSkinCl, self.textInfo["source"], "sources"))
        self.textInfo["btn3"] = buttonsToAttach("Grab Target", partial(self.__grabSkinCl, self.textInfo["target"], "targets"))

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

        self.textInfo["btn4"] = buttonsToAttach('Copy selected vertices', partial(self.__copySkinDataCB, True))
        self.textInfo["btn5"] = buttonsToAttach('Copy stored vertices', partial(self.__copySkinDataCB, False))
        self.textInfo["additive"] = QCheckBox('Additive')

        v2.addLayout(grid)
        v2.addWidget(self.textInfo["btn4"])
        v2.addWidget(self.textInfo["btn5"])
        v2.addWidget(self.textInfo["additive"])
        v2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        '''
        check if the current vertices are in the same position,
        otherwise select the closest vertices from the object that is not selected
        '''
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

        sourceGeo = cmds.skinCluster(source, q=True, g=True)[0]
        targetGeo = cmds.skinCluster(target, q=True, g=True)[0]

        outInfluences = cmds.skinCluster(target, q=True, influence=True)

        numInInf = len(inInfluences)
        numOutInf = len(outInfluences)

        _isChecked = self.textInfo["additive"].isChecked()
        if _isChecked and oneToOne:
            inWeights = cmds.SkinWeights(sourceGeo, source, q=True)
            outWeights = cmds.SkinWeights(targetGeo, target, q=True)
            if not expandedVertices:
                print('Must select vertices to copy weights for')
                return
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
            #  one to one based on current selection
            identifiers = [int(vertex.rsplit('[', 1)[-1].split(']', 1)[0]) for vertex in expandedVertices]
            sourceVerts = convertToCompList(identifiers, sourceGeo)
            targetVerts = convertToCompList(identifiers, targetGeo)
            #  maybe add version that works without current selection?
        else:
            # use the stored values
            if [] in self._toSelect.values():
                print('no valid entrys found')
                return
            sourceVerts = self._toSelect["sources"]
            targetVerts = self._toSelect["targets"]

        sourceVerts, targetVerts = closestPosCheck(sourceVerts, targetVerts)
        cmds.copySkinWeights(sourceVerts, targetVerts, noMirror=True, surfaceAssociation='closestPoint', ia=['oneToOne', 'name'])
        setProgress(100, self.__loadBar, "transfered weights from %s >> %s" % (source, target))


def testUI(widgetIndex=0):
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    widgets = {0: TransferWeightsWidget}

    mwd = QMainWindow(mainWindow)
    mwd.setWindowTitle("%s Test window" % widgets[widgetIndex].toolName)
    wdw = widgets[widgetIndex](parent=mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
