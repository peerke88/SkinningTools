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

        self.inflEdit = SkinningToolsSliderList(self)

        self._doSelectCB = None

        self.__skinSliderSetup()

    def __skinSliderSetup(self):
        h = nullHBoxLayout()
        cnct = HoverIconButton(icon = ":/hsNothing.png", checked = ":/hsDownStreamCon.png", parent = self)
        rfr = HoverIconButton(icon = ":/playbackLoopingContinuous_100.png")
        live = HoverIconButton(icon = ":/UVPivotLeft.png", checked = ":/enabled.png")

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [cnct, rfr, live]:
            h.addWidget(btn)

        cnct.clicked.connect(self._mutliSelection)
        rfr.clicked.connect(self._update)
        live.clicked.connect(self._live)
        
        self.layout().addLayout(h)
        self.layout().addWidget(self.inflEdit)

    def _mutliSelection(self):
        doMulti = self.sender().isChecked()
        self.inflEdit.setMultiAtOnce(doMulti)

    def _update(self):
        self.inflEdit.update()

    def _live(self):
        doLive = self.sender().isChecked()
        if doLive:
            self.createCallback()
            return
        self.clearCallback()            

    def createCallback(self):
        self.clearCallback()
        self._update()
        self._doSelectCB = api.connectSelectionChangedCallback(self._update) 
        
    def clearCallback(self):
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None