from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import weightsManager
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import os

# temp
from maya import cmds

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = True


class WeightsUI(QWidget):
    def __init__(self, settings = None, inProgressBar=None, parent=None):
        super(WeightsUI, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 30

        self.settings = settings
        self.progressBar = inProgressBar
        self.__wm = weightsManager.WeightsManager(inProgressBar)
        self.__addButtons()

    def __addButtons(self):
        h = nullHBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        lcl = pushButton("local")
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
        btn1 = pushButton("import")
        # use this to load files that are not listed (ask user to add to list)
        btn2 = pushButton("import external") 
        
        for btn in [btn1, btn2]:
            h.addWidget(btn)

        self.layout().addLayout(h)

        self._loadFiles()

    def _loadFiles(self, *args):
        files = self.settings.value("weightFiles", [])
        if files == [] and _DEBUG:
            files = ["testingFile.skinWeights", "testingFile2.skinWeights"]

        for f in files:
            fName = os.path.basename(f).split(".skinWeights")[0]
            item = QListWidgetItem(QIcon(":/kinReroot.png"), fName)
            item.info = f
            self.fileList.addItem(item)


    def _savePath(self, *args):
        _default = self.settings.value("weightPath", os.path.dirname(cmds.file(q=True, sn=True)))
        
        getFILEPATH = cmds.fileDialog2(fileFilter="*.skinWeights", fm=0, dir = _default ) or [None]
        if getFILEPATH[0] is None:
            return
        
        _data = self.__wm.gatherData()
        self.settings.setValue("weightPath", os.path.dirname(getFILEPATH[0]))
        with open(getFILEPATH[0], 'w') as f:
            json.dump(_jsonDict, f, encoding='utf-8', ensure_ascii = not binary, indent=4)
        return getFILEPATH[0]

    def clearInfo(self):
        while True:
            child = self.frm.layout().takeAt(0)
            if not child:
                break
            widget = child.widget()
            if not widget:
                continue
            widget.deleteLater()

    def _updateInfo(self, sender, *args):
        self.clearInfo()
        self.frm.layout().addWidget(pushButton(sender.info))
        # add buttons for display on possible information that this object might hold

        self.frm.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


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
                                         
                                         






