from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import mathUtils
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.Maya.tools import initialWeight
from functools import  partial
import os, warnings

class InitWeightUI(QWidget):
    """ the widget that holds all custom single button / buttongroup functions for authoring in the dcc tools
    """
    toolName = "InitWeightUI"

    def __init__(self, inProgressBar=None, parent=None):
        super(InitWeightUI, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self._progressBar = inProgressBar
        self.__mesh = None
        self.__joints = []
        self.textInfo = {}
        self.deLinearMethods = mathUtils.getTweeningMethods()
        self.__toolsSetup()
        self.__connections()
        
    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.iteritems():
            self.textInfo[key].setText(value)
        
    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.iteritems():
            _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName) 
        _trs = translator.showUI(_dict, widgetName = self.toolName)

    # ------------------------------- visibility tools ------------------------------- 

    def __toolsSetup(self):

        hMesh =  nullHBoxLayout()
        self.textInfo["selectMesh"] = pushButton("select Mesh")
        self.textInfo["source"] = QLineEdit()
        self.textInfo["source"].setPlaceholderText("No mesh given...")
        self.textInfo["source"].setStyleSheet('color:#000; background-color: #ad4c4c;')
        for w in [self.textInfo["selectMesh"], self.textInfo["source"]]:
            hMesh.addWidget(w)

        hJoint =  nullHBoxLayout()
        self.textInfo["selectJoint"] = pushButton("select Joints")
        self.textInfo["target"] = QLineEdit()
        self.textInfo["target"].setPlaceholderText("No joints given...")
        self.textInfo["target"].setStyleSheet('color:#000; background-color: #ad4c4c;')
        for w in [self.textInfo["selectJoint"], self.textInfo["target"]]:
            hJoint.addWidget(w)

        h0 = nullHBoxLayout()
        self.textInfo["iter"] = QLabel("iterations")
        self.spinIter = QSpinBox()
        self.spinIter.setValue(3)
        for w in [self.textInfo["iter"], self.spinIter]:
            h0.addWidget(w)

        h1 = nullHBoxLayout()
        self.textInfo["proj"] = QLabel("projection")
        self.spinProj = QDoubleSpinBox()
        self.spinProj.setValue(.75)
        for w in [self.textInfo["proj"], self.spinProj]:
            h1.addWidget(w)

        h2 = nullHBoxLayout()
        self.textInfo["blend"] = QLabel("blend weights")
        self.check1 = QCheckBox()
        for w in [self.textInfo["blend"], self.check1]:
            h2.addWidget(w)

        h3 = nullHBoxLayout()
        self.textInfo["delinear"] = QLabel("De-linearize weights")
        self.textInfo["delinear"].setEnabled(False)
        self.check2 = QCheckBox()
        self.check2.setEnabled(False)
        for w in [self.textInfo["delinear"], self.check2]:
            h3.addWidget(w)

        h4 = nullHBoxLayout()
        self.textInfo["delineartype"] = QLabel("De-linearize Method")
        self.combo = QComboBox()
        self.combo.addItems(self.deLinearMethods.keys())
        self.combo.setEnabled(False)
        for w in [self.textInfo["delinear"], self.combo]:
            h4.addWidget(w)

        self.textInfo["applySkin"] = pushButton("apply skinning")

        for w in [hMesh, hJoint, h0, h1, h2, h3, h4]:
            self.layout().addLayout(w)
        self.layout().addWidget(self.textInfo["applySkin"])
        self.layout().addItem(QSpacerItem(2, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def __connections(self):
        self.textInfo["selectMesh"].clicked.connect(self._selectMesh)
        self.textInfo["selectJoint"].clicked.connect(self._selectJoint)
        self.textInfo["applySkin"].clicked.connect(self._applySkin)
        self.check1.toggled.connect(self._changeSetup)

    def _changeSetup(self):
        self.check2.setEnabled(self.check1.isChecked())
        self.combo.setEnabled(self.check1.isChecked())
        self.textInfo["delinear"].setEnabled(self.check1.isChecked())

    def _selectMesh(self):
        selection = interface.getSelection()
        if not selection:
            self.textInfo["source"].setText('')
            self.textInfo["source"].setStyleSheet('color:#000; background-color: #ad4c4c;')
            cmds.error("nothing selected")

        mesh = selection[0]
        if "." in mesh:
            mesh = mesh.split('.')[0]
        self.__mesh = mesh
        
        self.textInfo["source"].setText(mesh)
        self.textInfo["source"].setStyleSheet('background-color: #17D206;')

    def _selectJoint(self):
        joints = interface.getAllJoints(True)
        if joints in [[], None]:
            joints = interface.getAllJoints(False)
        if joints == []:
            self.textInfo["target"].setText('')
            self.textInfo["target"].setStyleSheet('color:#000; background-color: #ad4c4c;')
            cmds.error("no joints found")
        self.__joints = joints

        self.textInfo["target"].setText(str(joints))
        self.textInfo["target"].setStyleSheet('background-color: #17D206;')

    def _applySkin(self):
        if None in [self.__mesh, self.__joints]:
            warnings.warn("no mesh or joints found")
            return
        blendMethod = self.combo.currentText() if self.check2.isChecked() else None

        initialWeight.setInitialWeights(self.__mesh, self.__joints, 
                                        iterations = self.spinIter.value(), 
                                        projection = self.spinProj.value(), 
                                        blend = self.check1.isChecked(), 
                                        blendMethod = blendMethod,
                                        progressBar = self._progressBar)

def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("%sTest window"%InitWeightUI.toolName)
    wdw = InitWeightUI(parent = mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw