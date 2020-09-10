from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
from SkinningTools.UI.ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList


class SkinSliderSetup(QWidget):
    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        super(SkinSliderSetup, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.__liveIMG = QPixmap(":/UVPivotLeft.png")
        self.__notLiveIMG = QPixmap(":/enabled.png")
        self.__isConnected = QPixmap(":/hsDownStreamCon.png")
        self.__notConnected = QPixmap(":/hsNothing.png")

        self.inflEdit = SkinningToolsSliderList(self)

        self.__skinSliderSetup()

    def __skinSliderSetup(self):
        h = nullHBoxLayout()
        cnct = toolButton(self.__notConnected)
        rfr = toolButton(":/playbackLoopingContinuous_100.png")
        live = toolButton(self.__liveIMG)

        cnct.setCheckable(True)
        live.setCheckable(True)

        live.clicked.connect(self._updateLive)
        cnct.clicked.connect(self._updateConnect)

        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for btn in [cnct, rfr, live]:
            h.addWidget(btn)

        self.layout().addLayout(h)
        self.layout().addWidget(self.inflEdit)

    def _updateLive(self):
        liveBtn = self.sender()
        if liveBtn.isChecked():
            liveBtn.setIcon(QIcon(self.__notLiveIMG))
        else:
            liveBtn.setIcon(QIcon(self.__liveIMG))

    def _updateConnect(self):
        liveBtn = self.sender()
        if liveBtn.isChecked():
            liveBtn.setIcon(QIcon(self.__isConnected))
        else:
            liveBtn.setIcon(QIcon(self.__notConnected))
