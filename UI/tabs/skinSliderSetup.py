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

        self.__skinSliderSetup()

    def __skinSliderSetup(self):
        h = nullHBoxLayout()
        cnct = HoverIconButton(icon = ":/hsNothing.png", checked = ":/hsDownStreamCon.png", parent = self)
        rfr = HoverIconButton(icon = ":/playbackLoopingContinuous_100.png")
        live = HoverIconButton(icon = ":/UVPivotLeft.png", checked = ":/enabled.png")

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [cnct, rfr, live]:
            h.addWidget(btn)

        self.layout().addLayout(h)
        self.layout().addWidget(self.inflEdit)
