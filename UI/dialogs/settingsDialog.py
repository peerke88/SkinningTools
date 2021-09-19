# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.UI.ControlSlider.sliderControl import SliderControl
from SkinningTools.UI import mmSearchDisplay
import os

_DIR = os.path.dirname(os.path.dirname(__file__))


class SettingsDialog(QDialog):
    toolName = "skintoolSettings"

    def __init__(self, parentWidget=None, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle(self.toolName)
        self.setLayout(nullVBoxLayout())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.parentWidget = parentWidget

        self.__defaults()
        self.__populate()
        self.__connections()

        self.setLanguage(self.parentWidget.language)

    def __defaults(self, *args):
        self.textInfo = OrderedDict()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict={}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.items():
            if key not in self.textInfo.keys():
                continue
            if isinstance(self.textInfo[key], SliderControl):
                self.textInfo[key].label.setText(value)
                continue
            self.textInfo[key].setText(value)

    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.items():
            if isinstance(self.textInfo[key], SliderControl):
                _ret[key] = value.label.text()
                continue
            _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName)
        _trs = translator.showUI(_dict, widgetName=self.toolName)

    # --------------------------------------------------------------------------

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
        self.mmDisplay.changeCircleSize(self.parentWidget.mmMargin)
        layout3.addWidget(self.mmDisplay)
        layout2.addWidget(self.textInfo["MMsearch"])
        layout2.addLayout(layout3)

        # --defaults
        self.textInfo["default"] = buttonsToAttach("reset settings", self.setDefault)

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
        self.parentWidget.saveUIState()

    def setIconInfo(self, value):
        self.parentWidget.vnbfWidget.iconSize = int(value)
        self.parentWidget.saveUIState()

    def setFontInfo(self, value):
        self.parentWidget.fontSize = int(value)
        self.parentWidget.saveUIState()

    def setLanguage(self, language="en"):
        if self.sender() is not None:
            self.parentWidget._changeLanguage(self.sender().currentText())
            _dict = loadLanguageFile(self.sender().currentText(), self.toolName)
        else:
            _dict = loadLanguageFile(language, self.toolName)
        self.translate(_dict)
        self.parentWidget.saveUIState()

    def setSearchRadius(self, value):
        self.mmDisplay.changeCircleSize(value)
        self.parentWidget.mmMargin = value
        self.parentWidget.saveUIState()

    def setDefault(self):
        self.textInfo["tooltip"].setChecked(False)
        self.textInfo["iconSize"].slider.setValue(40)
        self.textInfo["fontSize"].slider.setValue(12)
        self.comboBox.setCurrentIndex(0)
        self.textInfo["MMsearch"].slider.setValue(4)

    def __connections(self):
        self.textInfo["tooltip"].toggled.connect(self.setToolTipInfo)
        self.textInfo["iconSize"].slider.valueChanged.connect(self.setIconInfo)
        self.textInfo["fontSize"].slider.valueChanged.connect(self.setFontInfo)
        self.comboBox.currentIndexChanged.connect(self.setLanguage)
        self.textInfo["MMsearch"].slider.valueChanged.connect(self.setSearchRadius)


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    from SkinningTools.Maya import interface
    from SkinningTools.UI import SkinningToolsUI
    mainWindow = interface.get_maya_window()
    mwd = QMainWindow(mainWindow)
    mwd.setWindowTitle("settings Test window")
    wdw = SettingsDialog(parentWidget=SkinningToolsUI.SkinningToolsUI(), parent=mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
