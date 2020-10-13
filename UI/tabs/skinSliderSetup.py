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

        self._doSelectCB = None

        self.layout().addWidget(self.inflEdit)

    def _update(self):
        if not self.isInView:
            return
        self.inflEdit.update()

    def createCallback(self):
        self.clearCallback()
        self._update()
        self._doSelectCB = api.connectSelectionChangedCallback(self._update) 
        
    def clearCallback(self):
        if self._doSelectCB is not None:
            api.disconnectCallback(self._doSelectCB)
            self._doSelectCB = None