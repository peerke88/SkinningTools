# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl
from SkinningTools.UI import mmSearchDisplay
import os

_DIR = os.path.dirname(os.path.dirname(__file__))


class SettingsDialog(QDialog):
    def __init__(self, title="Settings", parentWidget=None, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(nullVBoxLayout())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.parentWidget = parentWidget

        self.__defaults()
        self.__populate()
        self.__connections()

    def __defaults(self, *args):
        self.textInfo = OrderedDict()

    def __populate(self, *args):
        # -- tooltip
        self.textInfo["tooltip"] = QCheckBox("show enhanced tooltips")
        self.textInfo["tooltip"].setChecked(self.parentWidget.showToolTips)

        # -- iconSize
        self.textInfo["iconSize"] = SliderControl("iconSize", label="set icon size", mn=0, mx=120, rigidRange=True)
        self.textInfo["iconSize"].slider.setValue(self.parentWidget.vnbfWidget.iconSize)
        self.textInfo["iconSize"].slider.decimals = 0

        # -- fontSize
        self.textInfo["fontSize"] = SliderControl("fontSize", label="set font size", mn=-1, mx=48, rigidRange=True)
        self.textInfo["fontSize"].slider.setValue(self.parentWidget.fontSize)
        self.textInfo["fontSize"].slider.decimals = 0

        # -- language
        layout1 = nullHBoxLayout()
        self.textInfo["language"] = QLabel("language")
        self.comboBox = QComboBox()
        languages = os.listdir(os.path.join(_DIR, "languages"))
        self.comboBox.addItems(languages)
        self.comboBox.setCurrentIndex(languages.index(self.parentWidget.language))
        for w in [self.comboBox, self.textInfo["language"]]:
            layout1.addWidget(w)

        # -- joint search distance
        layout2 = nullVBoxLayout()
        self.textInfo["MMsearch"] = SliderControl("searchDistance", label="set MM search distance", mn=4, mx=30, rigidRange=True)
        self.textInfo["MMsearch"].slider.decimals = 0
        self.textInfo["MMsearch"].slider.setValue(self.parentWidget.mmMargin)
        layout3 = nullHBoxLayout()
        layout3.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.mmDisplay = mmSearchDisplay.MmSearchDisplay()
        layout3.addWidget(self.mmDisplay)  # this needs to become the visualiser!
        layout2.addWidget(self.textInfo["MMsearch"])
        layout2.addLayout(layout3)

        for key in self.textInfo.keys():
            if key == "language":
                self.layout().addLayout(layout1)
                continue
            if key == "MMsearch":
                self.layout().addLayout(layout2)
                continue
            self.layout().addWidget(self.textInfo[key])

    def setToolTipInfo(self, value):
        self.parentWidget.showToolTips = value

    def setIconInfo(self, value):
        self.parentWidget.vnbfWidget.iconSize = int(value)

    def setFontInfo(self, value):
        self.parentWidget.fontSize = int(value)

    def setLanguage(self):
        self.parentWidget._changeLanguage(self.sender().currentText())

    def setSearchRadius(self, value):
        self.mmDisplay.changeCircleSize(value)
        self.parentWidget.mmMargin = value

    def __connections(self):
        self.textInfo["tooltip"].toggled.connect(self.setToolTipInfo)
        self.textInfo["iconSize"].slider.valueChanged.connect(self.setIconInfo)
        self.textInfo["fontSize"].slider.valueChanged.connect(self.setFontInfo)
        self.comboBox.currentIndexChanged.connect(self.setLanguage)
        self.textInfo["MMsearch"].slider.valueChanged.connect(self.setSearchRadius)
