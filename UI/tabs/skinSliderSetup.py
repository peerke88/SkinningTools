# -*- coding: utf-8 -*-
from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from functools import partial
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.hoverIconButton import HoverIconButton

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



class SkinSliderSetup(QWidget):
    """ skinslider setup, 
    allows the weights to be changed with a slider widget while keeping everything normalized
    """
    toolName = "SkinSliderSetup"

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(SkinSliderSetup, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.isInView = True
        self.inflEdit = SkinningToolsSliderList(self)

        self.jointSearch = []
        self._doSelectCB = None
        self.textInfo = {}
        self.__setUI()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict = {}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
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
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName) 
        _trs = translator.showUI(_dict, widgetName = self.toolName)
          
    # --------------------------------- ui setup ----------------------------------    
    def __setUI(self):
        """ convenience function to gather all buttons for the current UI
        """
        searchLay = nullHBoxLayout()
        searchLay.setSpacing(0)
        self.textInfo["label"]=QLabel('Search: ')
        searchLay.addWidget(self.textInfo["label"])
        self.textInfo["jointSearchLE"] = LineEdit()
        self.textInfo["jointSearchLE"].setPlaceholderText("Type part of joint name to search...")
        self.textInfo["jointSearchLE"].editingFinished.connect(self.searchJointName)
        self.textInfo["jointSearchLE"].textChanged.connect(self.searchJointName)
        searchLay.addWidget(self.textInfo["jointSearchLE"])
        self.showButton = HoverIconButton()
        self.showButton.setCustomIcon(":/RS_visible.png", ":/RS_visible.png", ":/hotkeyFieldClear.png")
        self.showButton.setCheckable(True)
        self.showButton.clicked.connect(self._showUnused)
        self.showButton.setChecked(True)
        self.inflEdit.showUnused(False)
        
        def _svgPath(svg):
            return os.path.join(_DIR, "Icons/%s.svg" % svg)

        searchLay.addWidget(self.showButton)
        hammerButton = svgButton("", _svgPath("hammer"), size=20, toolTipInfo="weightHammer")
        hammerButton.clicked.connect(self.hammerupdate)
        searchLay.addWidget(hammerButton)
        _frm = QWidget()
        _frm.setMinimumWidth(10)
        _frm.setMaximumHeight(1)
        searchLay.addWidget(_frm)

        solverLay = nullHBoxLayout()
        self.radio_group = QButtonGroup(self)

        rb_low = QRadioButton("Low priority", self)
        rb_high = QRadioButton("High priority", self)
        rb_avg = QRadioButton("Uniform", self)
        rb_avg.setChecked(True)
        
        for idx, radio in enumerate([rb_avg, rb_low, rb_high]):
            self.radio_group.addButton(radio)
            solverLay.addWidget(radio)
            radio.toggled.connect(partial(self._setWeightSolver, idx))

        self.layout().addLayout(solverLay)
        self.layout().addLayout(searchLay)
        self.layout().addWidget(self.inflEdit)

    def _setWeightSolver(self, idx, *args):
        self.inflEdit.solver = idx

    def searchJointName(self):
        """ based on the given text we only display jointsliders that are represted by a partial identification of the given string in the search lineedit
        """
        _allJoints = self.inflEdit.getJointData()
        self.jointSearch = _allJoints
        if str(self.textInfo["jointSearchLE"].text()) != '':
            _text = self.textInfo["jointSearchLE"].text().split(' ')
            _text = [name for name in _text if name != '']
            self.jointSearch = [inf for inf in _allJoints if any([True if s.upper() in inf.split('|')[-1].upper() else False for s in _text])]
        self.inflEdit.showOnlyJoints(self.jointSearch)
        
    def _showUnused(self, *args):
        """ setup to display the joints if they have or do not have a weight value assigned
        """
        self.inflEdit.showUnused(self.showButton.isChecked())
        if self.jointSearch != []:
            self.inflEdit.showOnlyJoints(self.jointSearch)  

    def hammerupdate(self, *args):
        interface.hammerVerts()
        self._update()

    def _update(self):
        """ convenience function to refresh and update the current widget
        """
        if not self.isInView:
            return
        self.inflEdit.update()
        self._showUnused()

    def createCallback(self):
        """ create callback to refresh the current widget based on selection in dcc tool
        """
        self.clearCallback()
        self._update()
        self._doSelectCB = api.connectSelectionChangedCallback(self._update) 
        
    def clearCallback(self):
        """ remove selection based callback
        """
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("SkinSliderSetup Test window")
    wdw = SkinSliderSetup(parent = mainWindow)
    wdw.isInView = True
    wdw.createCallback()
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw