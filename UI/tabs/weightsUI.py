# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import weightsManager, shared
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import os, json, random

# temp:
from maya import cmds

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG = getDebugState()
_LOCALFOLDER = os.path.join( os.path.dirname(_DIR), "localWeights")
if not os.path.exists(_LOCALFOLDER):
    os.makedirs(_LOCALFOLDER)

# @todo: make it possible that we can upscale the information as well!
# rework combobox, multiple objects not necessary and making it more difficult to plan

class WeightsUI(QWidget):
    """ weights manager
    allows to save skinning information from given objects and to load it onto the same object or even others
    """
    toolName = "weightUI"
    def __init__(self, settings = None, inProgressBar=None, parent=None):
        """ the constructor
        
        :param settings: the default settings to be used
        :type settings: QSettings
        :param inProgressBar: the progress bar to use for display of progress
        :type inProgressBar: QProgressBar
        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(WeightsUI, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__IS = 30

        self.textInfo = {}
        self._infoTextOptions()
        self.__bbCube = ''
        self.__infoData = None
        self.__infoDetails = None
        self.__cache = {}
        self.settings = settings
        self.progressBar = inProgressBar
        self.__wm = weightsManager.WeightsManager(inProgressBar)
        self.__addButtons()
        self.ComboC = None


    def _infoTextOptions(self):
        """ seperate text labels to be used for translation
        """
        self.infoLabels = {"name" : "name: ",
                           "overwrite":"overwrite",
                           "exists": "skinWeights file already exists, overwrite?",
                           "verts": "verts:",
                           "check": "check",
                           "bbox": "bbox:",
                           "joints": "joints:",
                           "UVs": "UVs:",
                           "cPos": "instead of pos",
                           "noUvin": "no uvs in saved weights file",
                           "selected": "no uvs on selected object in current scene",
                           "matching": "no uvs on matching object in current scene",
                           "vPos": "vertex positions on all objects do not match",
                           "vCount": "vertex count on all objects does not match",
                           "jntMatch": "joints in scene do not match",
                           }

    def __addButtons(self):
        """ simple convenience function to add the buttons to the current ui
        """
        h = nullHBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.textInfo["lcl"] = buttonsToAttach("local", self._getData)
        self.textInfo["fld"] = buttonsToAttach("specify", self._savePath)
        self.textInfo["lbl1"] = QLabel("store meshes:")
        for w in [self.textInfo["lbl1"],  self.textInfo["lcl"], self.textInfo["fld"]]:
            if isinstance(w, QSpacerItem):
                h.addItem(w)
            h.addWidget(w)

        self.layout().addLayout(h)

        h = nullHBoxLayout()
        self.fileList = QListWidget()        
        self.fileList.setIconSize(QSize(self.__IS, self.__IS))
        self.fileList.currentItemChanged.connect(self._updateInfo)
        self.textInfo["frm"] = QGroupBox("info")
        self.textInfo["frm"].setLayout(nullVBoxLayout())
        self.textInfo["frm"].setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        for w in [self.fileList, self.textInfo["frm"]]:
            h.addWidget(w)

        self.layout().addLayout(h)

        h = nullHBoxLayout()
        # use this to load files that are not listed (ask user to add to list)
        self.textInfo["btn1"] = pushButton("import external") 
        self.textInfo["btn2"] = pushButton("load Info")
        
        self.textInfo["btn1"].clicked.connect(self._loadExternalFiles)
        self.textInfo["btn2"].clicked.connect(self._setSkinInfo)
        for btn in [self.textInfo["btn1"], self.textInfo["btn2"]]:
            h.addWidget(btn)

        self.layout().addLayout(h)

        self._loadFiles()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.items():
            if key in self.infoLabels.keys():
                self.infoLabels[key] = value
                continue
            if isinstance(self.textInfo[key], QGroupBox):
                self.textInfo[key].setTitle(value)
                continue
            self.textInfo[key].setText(value)

        self._loadFiles()

    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.items():
            if isinstance(self.textInfo[key], QGroupBox):
                _ret[key] = value.title()
            else:    
                _ret[key] = value.text()
        for key, value in self.infoLabels.items():
            _ret[key] = value
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName)
        _trs = translator.showUI(_dict, widgetName = self.toolName)

    # --------------------------------- ui setup ---------------------------------- 
    def _loadFiles(self, *args):
        """ convenience function to make sure to load files from known location
        """
        self.fileList.clear()
        onlyfiles = [os.path.join(_LOCALFOLDER, f) for f in os.listdir(_LOCALFOLDER) if os.path.isfile(os.path.join(_LOCALFOLDER, f))]
        for f in list(set(self.settings.value("weightFiles", []))) + onlyfiles:
            fName = os.path.basename(f).split(".skinWeights")[0]
            item = QListWidgetItem(QIcon(":/kinReroot.png"), fName)
            item.info = f
            self.fileList.addItem(item)

    def _getData(self, binary = False, *args):
        """ get the date from the current selection

        :param binary: if `True` stores the json information as binary to save space, if `False` stores the data as ascii
        :type binary: bool
        """
        _data = self.__wm.gatherData()
        name = _data["meshes"][0]
        if len(_data["meshes"]) > 1:
            pkgNameDlg = QuickDialog("create package name")
            h = nullHBoxLayout()
            lbl = QLabel(self.infoLabels["name"])
            lne = LineEdit()
            for w in [lbl, lne]:
                h.addWidget(w)
            pkgNameDlg.layout().insertLayout(0, h)
            pkgNameDlg.exec_()
            if pkgNameDlg.result() == 0 or lne.text() == '' or FalseFolderCharacters(lne.text()):
                return
            name = lne.text()

        onlyFiles = [os.path.join(_LOCALFOLDER, f) for f in os.listdir(_LOCALFOLDER) if os.path.isfile(os.path.join(_LOCALFOLDER, f))]
        toSave =os.path.join(_LOCALFOLDER, "%s.skinWeights"%(name.split("|")[-1]))
        if toSave in onlyFiles:
            _overWriteDlg = QuickDialog(self.infoLabels["overwrite"])
            _overWriteDlg.layout().instertWidget(0, QLabel(self.infoLabels["exists"]))
            _overWriteDlg.exec_()
            if _overWriteDlg.result() == 0:
                return
            os.remove(toSave)

        with open(toSave, 'w') as f:
            json.dump(_data, f, encoding='utf-8', ensure_ascii = not binary, indent=4)

    def _savePath(self, binary = False):
        """ save the current information to the default path

        :param binary: if `True` stores the json information as binary to save space, if `False` stores the data as ascii
        :type binary: bool
        :return: the path the information is saved to
        :rtype: string
        """
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
        """ clear the current information widget on the selected weights file
        """
        if self.__infoData is None:
            return
        self.__infoData.hide()
        self.__infoData.deleteLater()

    # ------- info box -------
    def _updateInfo(self, sender, *args):
        """ widget to hold extra information read fromt he current weight file

        :param sender: the item object that holds the information on the weight files
        :type sender: QWidget 
        """
        self.clearInfo()
        if not sender.info in self.__cache.keys():
            _data = self.__wm.readData(sender.info)
            self.__cache[sender.info] = _data
        
        self.__infoData = QWidget()
        self.__infoData.setLayout(nullVBoxLayout())
        self.textInfo["frm"].layout().addWidget(self.__infoData)
        
        h = nullHBoxLayout()
        h.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.ComboC = QComboBox()
        self.ComboC.addItems(self.__cache[sender.info]["meshes"])
        h.addWidget(self.ComboC)
        
        self.__infoData.layout().addLayout(h)
        self.__infoSpace = QWidget()
        self.__infoSpace.setLayout(nullVBoxLayout())
        self.__infoData.layout().addWidget(self.__infoSpace)
        self.__infoData.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.ComboC.currentIndexChanged.connect(partial(self._changeMeshInfo, sender.info))
        self._changeMeshInfo(sender.info, self.ComboC)

    def _changeMeshInfo(self, curFile,  *_):
        """ chagne the information based on the current weight file selection

        :param curFile: the weight file to gather data from
        :type curFile: string
        """
        if self.__infoDetails is not None:
            self.__infoDetails.deleteLater()
            for cube in self.__bbCube:
                if cmds.objExists(cube):
                    cmds.delete(cube)
        currentText = self.ComboC.currentText()
        
        def lockLine(inText, inMesh):
            info = len(inText[inMesh])
            _line = QLineEdit(str(info))
            _line.setEnabled(False)
            return _line

        self.__infoDetails = QWidget()

        self.__infoDetails.currentInfo = {}

        self.__infoSpace.layout().addWidget(self.__infoDetails)
        self.__infoDetails.setLayout(nullGridLayout())
        
        # --- verts
        self.__infoDetails.layout().addWidget(QLabel(self.infoLabels["verts"]), 0,0)
        self.__infoDetails.layout().addWidget(lockLine(self.__cache[curFile]["vertIds"], currentText), 0,1)
        btn = pushButton(self.infoLabels["check"])
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkVerts, self.__cache[curFile]["vertPos"], currentText, btn))
        chk = QSpinBox()
        chk.setMinimum(1)
        chk.setEnabled(False)
        self.__infoDetails.currentInfo['closest'] = chk
        self.__infoDetails.currentInfo['verts'] = btn
        self.__infoDetails.layout().addWidget(chk, 0,2)
        self.__infoDetails.layout().addWidget(btn, 0,3)

        # --- bb
        self.__infoDetails.layout().addWidget(QLabel(self.infoLabels["bbox"]), 1,0)
        spin = QDoubleSpinBox()
        spin.setValue(1.0)
        spin.setSingleStep(.05)
        spin.valueChanged.connect(self._scaleBBox)
        spin.setEnabled(False)
        self.__infoDetails.currentInfo['scale'] = spin
        self.__infoDetails.layout().addWidget(spin, 1,2)
        btn = buttonsToAttach(self.infoLabels["check"], partial(self._makeBB, self.__cache[curFile]["bbox"], currentText))
        self.__infoDetails.currentInfo['bbox'] = btn
        self.__infoDetails.layout().addWidget(btn, 1,3)

        # --- joints
        self.__infoDetails.layout().addWidget(QLabel(self.infoLabels["joints"]), 2,0)
        self.__infoDetails.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 2,2)
        btn = pushButton(self.infoLabels["check"])
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkJoints, self.__cache[curFile]["allJnts"], btn))
        self.__infoDetails.currentInfo['joints'] = btn
        self.__infoDetails.layout().addWidget(btn, 2,3)

        # --- uvs
        self.__infoDetails.layout().addWidget(QLabel(self.infoLabels["UVs"]), 3,0)
        chk = QCheckBox(self.infoLabels["cPos"])
        chk.setEnabled(False)
        self.__infoDetails.currentInfo['useUV'] = chk
        self.__infoDetails.layout().addWidget(chk, 3, 2)
        btn = pushButton(self.infoLabels["check"])
        btn.setMinimumHeight(23)
        btn.clicked.connect(partial(self._checkUvs, self.__cache[curFile]["uvs"], currentText, btn, chk))
        self.__infoDetails.currentInfo['uvs'] = btn
        self.__infoDetails.layout().addWidget(btn, 3,3)


    # @todo: move these functions to api/interface
    def _checkUvs(self, uvs, currentMesh, sender, checkBox):
        """ check if the object has uvs and if the uvs are similar

        :param uvs: input information on the uvs stored on file
        :type uvs: list
        :param currentMesh: the current objects to check for uvs
        :type currentMesh: list
        :param sender: the check button used to trigger this function
        :type sender: QPushButton
        :param checkBox: the checkbox to set if it can be used in stead of positions
        :type checkBox: QCheckBox
        """
        sel = interface.getSelection()
        _selection = True
        if not sel:
            sel = currentMesh
            _selection = False
        if '.' in sel:
            sel = [sel.split('.')[0]]

        checkBox.setEnabled(False)
        if None in uvs:
            sender.setStyleSheet('background-color: #ad4c4c;')
            sender.setToolTip(self.infoLabels["noUvin"])
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
            if _selection:
                sender.setToolTip(self.infoLabels["selected"])
            else:
                sender.setToolTip(self.infoLabels["matching"])
            return 

        sender.setStyleSheet('background-color: #17D206;')
        checkBox.setEnabled(True)
        self.__infoDetails.currentInfo['closest'].setEnabled(True)


    def _checkVerts(self, verts, currentMesh, sender):
        """ check if the objects vertices are similar

        :todo: make sure that the scale values are used

        :param verts: input information on the verts stored on file
        :type verts: list
        :param currentMesh: the current object to check for verts
        :type currentMesh: string
        :param sender: the check button used to trigger this function
        :type sender: QPushButton
        """
        sel = interface.getSelection()
        if not sel:
            sel = currentMesh
        if '.' in sel:
            sel = [sel.split('.')[0]]
        nVerts = api.meshVertexList(sel[0])
        sender.setStyleSheet('background-color: #17D206;')
        amount = len(nVerts)
        matches = True
        positions = True
        self.__infoDetails.currentInfo['verts'].type = 'Match'
        scl = self.__infoDetails.currentInfo['scale'].value()
        if len(verts[currentMesh]) != amount:
            sender.setStyleSheet('background-color: #ad4c4c;')
            sender.setToolTip(self.infoLabels["vPos"])
            self.__infoDetails.currentInfo['verts'].type = 'Pos'
            self.__infoDetails.currentInfo['closest'].setEnabled(True)
            
        for i in range(5):
            _id =  random.randint(0, amount)
            pos = smart_roundVec(verts[currentMesh][_id], 3)
            _fp = cmds.xform("%s.vtx[%i]"%(sel[0], _id), q=1, ws=1,t=1)
            nPos = smart_roundVec([_fp[0]*scl, _fp[1]*scl, _fp[2]*scl], 3)
            if pos == nPos:
                continue
            positions = False

        if not positions:
            sender.setStyleSheet('background-color: #e85617;')
            sender.setToolTip(self.infoLabels["vCount"])
            self.__infoDetails.currentInfo['verts'].type = 'noMatch'

    def _checkJoints(self, joints, sender):
        """ check if the objects joints inputs are similar

        :param joints: input information on the joints stored on file
        :type joints: list
        :param sender: the check button used to trigger this function
        :type sender: QPushButton
        """
        for jnt in joints:
            if cmds.objExists(jnt):
                sender.setStyleSheet('background-color: #17D206;')
                continue
            sender.setToolTip(self.infoLabels["jntMatch"])
            sender.setStyleSheet('background-color: #ad4c4c;')

    def _makeBB(self, bbox, mesh):
        """ create a cube that uses the infromation of the skinweights file bounding box, 
        to identify possible problems when loading the skincluster information
        """
        
        if cmds.objExists(self.__bbCube):
            cmds.delete(self.__bbCube)
        self.__bbCube = ''
        self.__infoDetails.currentInfo['scale'].setEnabled(True)
        self.__bbCube = cmds.polyCube(n = "bboxCube")[0]
        cmds.move(bbox[mesh][0][0], '%s.f[5]' % self.__bbCube , x=True)
        cmds.move(bbox[mesh][0][1], '%s.f[3]' % self.__bbCube , y=True)
        cmds.move(bbox[mesh][0][2], '%s.f[2]' % self.__bbCube , z=True)
        cmds.move(bbox[mesh][1][0], '%s.f[4]' % self.__bbCube , x=True)
        cmds.move(bbox[mesh][1][1], '%s.f[1]' % self.__bbCube , y=True)
        cmds.move(bbox[mesh][1][2], '%s.f[0]' % self.__bbCube , z=True)
        shape = cmds.listRelatives(self.__bbCube , s=1)[0]
        cmds.setAttr("%s.overrideEnabled"%shape, 1)
        cmds.setAttr("%s.overrideShading"%shape, 0)

    def _scaleBBox(self, inValue):
        if not cmds.objExists(self.__bbCube):
            return

        [cmds.setAttr("%s.scale%s"%(cube, ax), inValue) for ax in "XYZ"]

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

    def _setSkinInfo(self):
        """ set the skinning info from current object to selected or multiple
        :todo: need to make sure this only allows the user to check
        :todo: or if it actually has a meaningfull relationship to the weights manager 

        """
        if self.__infoDetails is None:
            print("no weight info selected")
            return
        print("setting the skinning info")

        currentMesh = self.ComboC.currentText()
        sel = interface.getSelection()
        if not sel:
            sel = currentMesh
        if '.' in sel:
            sel = sel.split('.')[0]

        curFile = self.fileList.selectedItems()[0]
        scale = self.__infoDetails.currentInfo["scale"].value()
        closest = self.__infoDetails.currentInfo["closest"].value()
        useUv = self.__infoDetails.currentInfo['useUV'].isChecked()
        self.__wm.importData(curFile.info, workMesh = sel, scale = scale, closestNPoints = closest, uvBased =  useUv)

    def hideEvent(self, event):
        """ make sure we don't have any lingering data
        """
        if not self.__cache == {}:
            del self.__cache
    
        if cmds.objExists(self.__bbCube):
            cmds.delete(self.__bbCube)
        super(WeightsUI, self).hideEvent(event)

                                 
def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("WeightsUI Test window")
    wdw = WeightsUI(settings = QSettings(os.path.join(_DIR, 'settings.ini'), QSettings.IniFormat), parent = mwd)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw                                   






