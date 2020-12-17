# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import weightsManager
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.searchAbleComboBox import SearchableComboBox
from functools import partial
import os, json, random

"""
----------------------------------------
|store meshes:      [local] [to folder]|
----------------------------------------
|local files       | info widget       |
|global files      |  show info of     |
|all listed here   |  selected file    |
|   rightclickmenu |                   |
|   delete file    | add options       |
|                  |  for override     |
|                  |  [single/multi]   |
|                  |  [pos or uv]      |
|                  |                   |
| _____________________________________|
|[              import                ]|
----------------------------------------


use checkakle combobox for selection of elements to be loaded into the scene
"""
        
# temp
from maya import cmds

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()
_LOCALFOLDER = os.path.join( os.path.dirname(_DIR), "localWeights")
if not os.path.exists(_LOCALFOLDER):
    os.makedirs(_LOCALFOLDER)

class WeightsUI(QWidget):
    def __init__(self, settings = None, inProgressBar=None, parent=None):
        super(WeightsUI, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 30

        self.__bbCube = ''
        self.__infoData = None
        self.__infoDetails = None
        self.__cache = {}
        self.settings = settings
        self.progressBar = inProgressBar
        self.__wm = weightsManager.WeightsManager(inProgressBar)
        self.__addButtons()

    def __addButtons(self):
        h = nullHBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        lcl = buttonsToAttach("local", self._getData)
        fld = buttonsToAttach("specify", self._savePath)

        for w in [QLabel("store meshes:"),  lcl, fld]:
            if isinstance(w, QSpacerItem):
                h.addItem(w)
            h.addWidget(w)

        self.layout().addLayout(h)

        h = nullHBoxLayout()
        self.fileList = QListWidget()        
        self.fileList.setIconSize(QSize(self.__IS, self.__IS))
        self.fileList.currentItemChanged.connect(self._updateInfo)
        self.frm = QGroupBox("info")
        self.frm.setLayout(nullVBoxLayout())
        self.frm.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        for w in [self.fileList, self.frm]:
            h.addWidget(w)

        self.layout().addLayout(h)

        h = nullHBoxLayout()
        # use this to load files that are not listed (ask user to add to list)
        btn1 = pushButton("import external") 
        btn2 = pushButton("load Info")
        
        btn1.clicked.connect(self._loadExternalFiles)
        for btn in [btn1, btn2]:
            h.addWidget(btn)

        self.layout().addLayout(h)

        self._loadFiles()


    def _loadFiles(self, *args):
        self.fileList.clear()
        onlyfiles = [os.path.join(_LOCALFOLDER, f) for f in os.listdir(_LOCALFOLDER) if os.path.isfile(os.path.join(_LOCALFOLDER, f))]
        for f in list(set(self.settings.value("weightFiles", []))) + onlyfiles:
            fName = os.path.basename(f).split(".skinWeights")[0]
            item = QListWidgetItem(QIcon(":/kinReroot.png"), fName)
            item.info = f
            self.fileList.addItem(item)

    def _getData(self, *args):
        _data = self.__wm.gatherData()
        name = _data["meshes"][0]
        if len(_data["meshes"]) > 1:
            pkgNameDlg = QuickDialog("create package name")
            h = nullHBoxLayout()
            lbl = QLabel("name: ")
            lne = LineEdit()
            for w in [lbl, lne]:
                h.addWidget(w)
            pkgNameDlg.layout().instertLayout(0, h)
            pkgNameDlg.exec_()
            if pkgNameDlg.result() == 0 or lne.text() == '' or FalseFolderCharacters(lne.text()):
                return
            name = lne.text()

        onlyfiles = [os.path.join(_LOCALFOLDER, f) for f in os.listdir(_LOCALFOLDER) if os.path.isfile(os.path.join(_LOCALFOLDER, f))]
        toSave =os.path.join(_LOCALFOLDER, "%s.skinWeights"%(name))
        if toSave in onlyFiles:
            _overWriteDlg = QuickDialog("overwrite")
            _overWriteDlg.layout().instertWidget(0, QLabel("skinWeights file already exists, overwrite?"))
            _overWriteDlg.exec_()
            if _overWriteDlg.result() == 0:
                return
            os.remove(toSave)

        with open(toSave, 'w') as f:
            json.dump(_data, f, encoding='utf-8', ensure_ascii = not binary, indent=4)

    def _savePath(self, binary = False):
        _default = self.settings.value("weightPath", os.path.dirname(cmds.file(q=True, sn=True)))
        
        getFILEPATH = cmds.fileDialog2(fileFilter="*.skinWeights", fm=0, dir = _default ) or [None]
        if getFILEPATH[0] is None:
            return
        
        _data = self.__wm.gatherData()
        self.settings.setValue("weightPath", os.path.dirname(getFILEPATH[0]))
        with open(getFILEPATH[0], 'w') as f:
            json.dump(_data, f, encoding='utf-8', ensure_ascii = not binary, indent=4)
        _current = self.settings.value("weightFiles", [])
        _current.append(getFILEPATH[0])
        self.settings.setValue("weightFiles", list(set(_current)))
        self._loadFiles()
        return getFILEPATH[0]

    def clearInfo(self):
        if self.__infoData is None:
            return
        self.__infoData.hide()
        self.__infoData.deleteLater()

    # ------- info box -------
    def _updateInfo(self, sender, *args):
        self.clearInfo()
        if not sender.info in self.__cache.keys():
            _data = self.__wm.readData(sender.info)
            self.__cache[sender.info] = _data
        
        self.__infoData = QWidget()
        self.__infoData.setLayout(nullVBoxLayout())
        self.frm.layout().addWidget(self.__infoData)
        
        h = nullHBoxLayout()
        h.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        c = SearchableComboBox()
        c.addItems(self.__cache[sender.info]["meshes"], True)
        h.addWidget(c)
        
        self.__infoData.layout().addLayout(h)
        self.__infoSpace = QWidget()
        self.__infoSpace.setLayout(nullVBoxLayout())
        self.__infoData.layout().addWidget(self.__infoSpace)
        self.__infoData.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        c.currentIndexChanged.connect(partial(self._changeMeshInfo, sender.info, c))
        self._changeMeshInfo(sender.info, c)

    def _changeMeshInfo(self, curFile, currentC, *_):
        if self.__infoDetails is not None:
            self.__infoDetails.deleteLater()
        currentText = currentC.getCheckedItems()
        def lockLine(inText, inList):
            info = 0
            for l in inList:
                info += inText[l]
            _line = QLineEdit(str(inText))
            _line.setEnabled(False)
            return _line

        self.__infoDetails = QWidget()
        self.__infoSpace.layout().addWidget(self.__infoDetails)
        self.__infoDetails.setLayout(nullGridLayout())
        
        # --- verts
        self.__infoDetails.layout().addWidget(QLabel("verts:"), 0,0)
        self.__infoDetails.layout().addWidget(lockLine(self.__cache[curFile]["vertIds"], currentText), 0,1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkVerts, self.__cache[curFile]["vertPos"], currentText, btn))
        self.__infoDetails.layout().addWidget(btn, 0,2)

        # --- bb
        self.__infoDetails.layout().addWidget(QLabel("bbox:"), 1,0)
        self.__infoDetails.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1,1)
        self.__infoDetails.layout().addWidget(buttonsToAttach("check", partial(self._makeBB, self.__cache[curFile]["bbox"], currentText)), 1,2)

        # --- joints
        self.__infoDetails.layout().addWidget(QLabel("joints:"), 2,0)
        self.__infoDetails.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 2,1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkJoints, self.__cache[curFile]["allJnts"], btn))
        self.__infoDetails.layout().addWidget(btn, 2,2)

        # --- uvs
        self.__infoDetails.layout().addWidget(QLabel("UVs:"), 3,0)
        chk = QCheckBox("instead of pos")
        chk.setEnabled(False)
        self.__incoDetails.layout().addWidget(chk, 3, 1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkUvs, self.__cache[curFile]["uvs"][currentText], btn, chk))
        self.__infoDetails.layout().addWidget(btn, 2,3)


    # @todo: move these functions to api/interface
    def _checkUvs(self, uvs, currentMesh, sender, checkBox):
        sel = interface.getSelection()
        _selection = True
        if not sel:
            sel = [currentMesh]
            _selection = False
        if '.' in sel[0]:
            sel = [sel[0].split('.')[0]]


        checkBox.setEnabled(False)
        if None in uvs:
            sender.setStyleSheet('background-color: #ad4c4c;')
            sender.setToolTip("no uvs in saved weights file")
            return 

        uvCoords = []
        meshPath = shared.getDagpath(sel[0])
        vertIter = OpenMaya.MItMeshVertex(meshPath)
        while not vertIter.isDone():
            try:
                u, v, __ = vertIter.getUVs()
                uvCoords.append([u[0], v[0]])
            except:
                uvCoords.append(None)
            vertIter.next()
        
        if None in uvCoords:
            sender.setStyleSheet('background-color: #ad4c4c;')
            sender.setToolTip("no uvs on %s object in current scene"%["matching", "selected"][_selection])
            return 

        sender.setStyleSheet('background-color: #17D206;')
        checkBox.setEnabled(True)


    def _checkVerts(self, verts, currentMeshes, sender):
        sel = interface.getSelection()
        if not sel:
            sel = [currentMesh]
        if '.' in sel[0]:
            sel = [sel[0].split('.')[0]]
        nVerts = api.meshVertexList(sel[0])
        sender.setStyleSheet('background-color: #17D206;')
        amount = len(nVerts)
        matches = True
        positions = True
        for currentMesh in currentMeshes:
            if len(verts[currentMesh]) != amount:
                matches = False
                continue
                
            for i in xrange(5):
                _id =  random.randint(0, amount)
                pos = smart_roundVec(verts[currentMesh][_id], 3)
                nPos = smart_roundVec(cmds.xform("%s.vtx[%i]"%(sel[0], _id), q=1, ws=1,t=1), 3)
                if pos == nPos:
                    continue
                positions = False

        if not matches:
            sender.setStyleSheet('background-color: #ad4c4c;')
            sender.setToolTip("vertex positions on all objects do not match")

        if not positions:
            sender.setStyleSheet('background-color: #e85617;')
            sender.setToolTip("vertex count on all objects does not match")

    def _checkJoints(self, joints, sender):
        for jnt in joints:
            if cmds.objExists(jnt):
                sender.setStyleSheet('background-color: #17D206;')
                continue
            sender.setToolTip("joints in scene do not match")
            sender.setStyleSheet('background-color: #ad4c4c;')


    def _makeBB(self, bbox, meshList):
        if cmds.objExists(self.__bbCube):
            cmds.delete(self.__bbCube)
        self.__bbCube = []
        for mesh in meshList:
            _bb = cmds.polyCube(n = "bboxCube")[0]
            self.__bbCube.append(_bb)
            cmds.move(bbox[mesh][0][0], '%s.f[5]' % _bb , x=True)
            cmds.move(bbox[mesh][0][1], '%s.f[3]' % _bb , y=True)
            cmds.move(bbox[mesh][0][2], '%s.f[2]' % _bb , z=True)
            cmds.move(bbox[mesh][1][0], '%s.f[4]' % _bb , x=True)
            cmds.move(bbox[mesh][1][1], '%s.f[1]' % _bb , y=True)
            cmds.move(bbox[mesh][1][2], '%s.f[0]' % _bb , z=True)
            shape = cmds.listRelatives(_bb , s=1)[0]
            cmds.setAttr("%s.overrideEnabled"%shape, 1)
            cmds.setAttr("%s.overrideShading"%shape, 0)

    def _loadExternalFiles(self):
        """ load external weight files, 
        this can be used to load skinweights files that are not listed from settings.
        this will add the folder to the settignsfile so it can be found from now, but will not set skinning info
        """
        _default = self.settings.value("weightPath", os.path.dirname(cmds.file(q=True, sn=True)))
        getFILEPATH = cmds.fileDialog2(fileFilter="*.skinWeights", fm=2, dir = _default ) or [None]
        _current = self.settings.value("weightFiles", [])
        _current.append(getFILEPATH[0])
        self.settings.setValue("weightFiles", list(set(_current)))
        self._loadFiles()


    def hideEvent(self, event):
        if not self.__cache == {}:
            del self.__cache
        if self.__bbCube != '':
            cmds.delete(self.__bbCube)

                                 
                                         






