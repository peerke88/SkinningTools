from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from SkinningTools.UI.hoverIconButton import HoverIconButton

class SkinSliderSetup(QWidget):
    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        super(SkinSliderSetup, self).__init__(parent)
        self.setLayout(nullVBoxLayout())
        self.isInView = True
        self.inflEdit = SkinningToolsSliderList(self)

        self.jointSearch = []
        self._doSelectCB = None
        self.__setUI()

    def __setUI(self):
        searchLay = nullHBoxLayout()
        searchLay.setSpacing(0)
        searchLay.addWidget(QLabel('Search: '))
        self.jointSearchLE = LineEdit()
        self.jointSearchLE.editingFinished.connect(self.searchJointName)
        self.jointSearchLE.textChanged.connect(self.searchJointName)
        searchLay.addWidget(self.jointSearchLE)
        # self.showButton = QPushButton("")#"show infl.")
        # self.showButton = toolButton(":/RS_visible.png")
        self.showButton = HoverIconButton()
        self.showButton.setCustomIcon(":/RS_visible.png", ":/RS_visible.png", ":/hotkeyFieldClear.png")
        self.showButton.setCheckable(True)
        self.showButton.clicked.connect(self._showUnused)
        self.showButton.setChecked(True)
        
        searchLay.addWidget(self.showButton)
        _frm = QFrame()
        _frm.setMinimumWidth(10)
        _frm.setMaximumHeight(1)
        searchLay.addWidget(_frm)

        self.layout().addLayout(searchLay)
        self.layout().addWidget(self.inflEdit)

    def searchJointName(self):
        _allJoints = self.inflEdit.getJointData()
        self.jointSearch = _allJoints
        if str(self.jointSearchLE.text()) != '':
            _text = self.jointSearchLE.text().split(' ')
            _text = [name for name in _text if name != '']
            self.jointSearch = [inf for inf in _allJoints if any([True if s.upper() in inf.split('|')[-1].upper() else False for s in _text])]
        self.inflEdit.showOnlyJoints(self.jointSearch)
        
    def _showUnused(self, *args):
        self.inflEdit.showUnused(not self.showButton.isChecked())
        if self.jointSearch != []:
            self.inflEdit.showOnlyJoints(self.jointSearch)

    def _update(self):
        if not self.isInView:
            return
        self.inflEdit.update()
        self._showUnused()

    def createCallback(self):
        self.clearCallback()
        self._update()
        self._doSelectCB = api.connectSelectionChangedCallback(self._update) 
        
    def clearCallback(self):
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None