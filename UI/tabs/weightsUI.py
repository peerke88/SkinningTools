from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import weightsManager
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import os, json, random

# temp
from maya import cmds

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()


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
        btn1 = pushButton("import external") 
        btn2 = pushButton("load single")
        btn3 = pushButton("load all")
        # use this to load files that are not listed (ask user to add to list)
        
        for btn in [btn1, btn2, btn3]:
            h.addWidget(btn)

        self.layout().addLayout(h)

        self._loadFiles()

    def _loadFiles(self, *args):
        self.fileList.clear()
        for f in list(set(self.settings.value("weightFiles", []))):
            fName = os.path.basename(f).split(".skinWeights")[0]
            item = QListWidgetItem(QIcon(":/kinReroot.png"), fName)
            item.info = f
            self.fileList.addItem(item)

    def _getData(self, *args):
        _data = self.__wm.gatherData()
        print(_data)

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
        c = QComboBox()
        c.addItems(self.__cache[sender.info]["meshes"])
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
        currentText = currentC.currentText()
        def lockLine(inText):
            _line = QLineEdit(inText)
            _line.setEnabled(False)
            return _line

        self.__infoDetails = QWidget()
        self.__infoSpace.layout().addWidget(self.__infoDetails)
        self.__infoDetails.setLayout(nullGridLayout())
        
        # --- verts
        self.__infoDetails.layout().addWidget(QLabel("verts:"), 0,0)
        self.__infoDetails.layout().addWidget(lockLine(str(len(self.__cache[curFile]["vertIds"][currentText]))), 0,1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkVerts, self.__cache[curFile]["vertPos"][currentText], currentText, btn))
        self.__infoDetails.layout().addWidget(btn, 0,2)

        # --- bb
        self.__infoDetails.layout().addWidget(QLabel("bbox:"), 1,0)
        self.__infoDetails.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1,1)
        self.__infoDetails.layout().addWidget(buttonsToAttach("check", partial(self._makeBB, self.__cache[curFile]["bbox"][currentText])), 1,2)

        # --- joints
        self.__infoDetails.layout().addWidget(QLabel("joints:"), 2,0)
        self.__infoDetails.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 2,1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkJoints, self.__cache[curFile]["infl"][currentText], btn))
        self.__infoDetails.layout().addWidget(btn, 2,2)

        # --- uvs
        self.__infoDetails.layout().addWidget(QLabel("UVs:"), 3,0)
        chk = QCheckBox("instead of pos")
        chk.setEnabled(False)
        self.__incoDetails.layout().addWidget(chk, 3, 1)
        btn = pushButton("check")
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkUvs, self.__cache[curFile]["uvs"][currentText], btn, chk))
        self.__infoDetails.layout().addWidget(btn, 2,2)


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
            self.setToolTip("no uvs in saved weights file")
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
            self.setToolTip("no uvs on %s object in current scene"%["matching", "selected"][_selection])
            return 

        sender.setStyleSheet('background-color: #17D206;')
        checkBox.setEnabled(True)


    def _checkVerts(self, verts, currentMesh, sender):
        sel = interface.getSelection()
        if not sel:
            sel = [currentMesh]
        if '.' in sel[0]:
            sel = [sel[0].split('.')[0]]
        nVerts = api.meshVertexList(sel[0])
        sender.setStyleSheet('background-color: #17D206;')
        amount = len(nVerts)
        if len(verts) != amount:
            sender.setStyleSheet('background-color: #ad4c4c;')
            self.setToolTip("amount of verts do not match")
            return
            
        for i in xrange(5):
            _id =  random.randint(0, amount)
            pos = smart_roundVec(verts[_id], 3)
            nPos = smart_roundVec(cmds.xform("%s.vtx[%i]"%(sel[0], _id), q=1, ws=1,t=1), 3)
            if pos == nPos:
                continue
            self.setToolTip("position of verts do not match")
            sender.setStyleSheet('background-color: #ad4c4c;')

    def _checkJoints(self, joints, sender):
        for jnt in joints:
            if cmds.objExists(jnt):
                sender.setStyleSheet('background-color: #17D206;')
                continue
            self.setToolTip("joints in scene do not match")
            sender.setStyleSheet('background-color: #ad4c4c;')


    def _makeBB(self, bbox):
        if cmds.objExists(self.__bbCube):
            cmds.delete(self.__bbCube)
        self.__bbCube = cmds.polyCube(n = "bboxCube")[0]
        cmds.move(bbox[0][0], '%s.f[5]' % self.__bbCube, x=True)
        cmds.move(bbox[0][1], '%s.f[3]' % self.__bbCube, y=True)
        cmds.move(bbox[0][2], '%s.f[2]' % self.__bbCube, z=True)
        cmds.move(bbox[1][0], '%s.f[4]' % self.__bbCube, x=True)
        cmds.move(bbox[1][1], '%s.f[1]' % self.__bbCube, y=True)
        cmds.move(bbox[1][2], '%s.f[0]' % self.__bbCube, z=True)
        shape = cmds.listRelatives(self.__bbCube, s=1)[0]
        cmds.setAttr("%s.overrideEnabled"%shape, 1)
        cmds.setAttr("%s.overrideShading"%shape, 0)

    def hideEvent(self, event):
        if not self.__cache == {}:
            del self.__cache
        if self.__bbCube != '':
            cmds.delete(self.__bbCube)


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
"""
                                         
                                         






