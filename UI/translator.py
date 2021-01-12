# -*- coding: utf-8 -*-
"""
the translator class is there to provide ease of acces on changing ui language
(looking into qtranslator, but that has a lot of difficult extra mess to it so lets write our own)

the class will hold dictionary information of all possible languages the ui hass
the translator will load the information from seperate json files.
in these json files we will have keys that map the elements.
lets make sure that the returned value from the dictionary is decoded properly so it will always display the correct value

we can also let the translator call a qt widget that allows us to make a new language map
this for ease of access to create new languages if necessary, if these are saved in the same folder as the other languages, 
then this can be picked up automatically by te translator

we need to make sure that the keys for the dictionary are descriptive enough, preferably single word identifiers

so:
   - we need the current language identifier as a variable
   - we need to load different json modules to identify the amount of languages accessable
   - we only load the current json as a cached dictionary and return that, or we load in every language we want to switch between and cache that when requested
   - add a hook that we update the text of elements where possible, maybe make a mapping on qt on how to set text for specific elements

also check with the language of our current dcc tool to get that as a default

use google trans to get the first draft made? always have the original available when doing translations?
request possible languages from googletrans

- add a rightclick menu to the combobox that allows changing of the language to add a language (maybe use LANGUAGES to make sure there are no mistakes)

-------------------------------------------------
from SkinningTools.ThirdParty.googletrans import Translator , LANGUAGES

t = Translator()
txt = t.translate("to translate this piece of text", dest="ja")
print txt.text

print LANGUAGES.values()


# these are the current windows locales (check these on osx and linux as well)
import locale
print locale.windows_locale.values()

===============================================================

1. get a list of all current text in the ui
2. convert text to dictionary
3. use dictionary here to figure out what needs to be created

"""

from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.ThirdParty.google_trans_new import google_translator, LANGUAGES
from SkinningTools.Maya import interface

class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setEditable(True)

        self.completer = QCompleter(self)
        self.completer.setModel(self.model())
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        self.lineEdit().editingFinished.connect(self._sync)

    def _sync(self):
        text = self.currentText()
        opt = self.itemText(self.currentIndex())
        if opt != text:
            self.setCurrentText(opt)

class TranslatorDialog(QDialog):
    def __init__(self, inDict = None, defaultLanguage = "japanese", widgetName = None, parent = None):
        if widgetName is None:
            print "widgetName cannot be None"
            return
                
        super(TranslatorDialog, self).__init__(parent)
        self.setWindowTitle("translator")
        self.setLayout(nullVBoxLayout())

        self.widgetName = widgetName
        h = nullHBoxLayout()
        label = QLabel("translate to:")
        self.combo = SearchableComboBox()
        for language in LANGUAGES.values():
            self.combo.addItem(language)

        for w in [label, self.combo]:
            h.addWidget(w)

        self.layout().addLayout(h)

        self.progressBar = QProgressBar()
        self.layout().addWidget(self.progressBar)

        self._translator = google_translator()
        _id = 0
        if defaultLanguage in LANGUAGES.values():
            _id = LANGUAGES.values().index(defaultLanguage)

        self.combo.setCurrentIndex(_id)
        self.__inDict = inDict
        if inDict is None:
        	self.__inDict = loadLanguageFile("en", widgetName)
        self._layouts = []

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(1)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        _frame = QFrame()
        scrollArea.setWidget(_frame)
        self.frameLayout = nullVBoxLayout()
        _frame.setLayout(self.frameLayout)
        self.layout().addWidget(scrollArea)
        _outPath = os.path.join(os.path.dirname(__file__), "languages", self.getLangValue(), "%s.LAN"%self.widgetName )
        if os.path.exists(_outPath):
            self._recreateDialog()
        else:
            self._populateDialog()

        self.combo.currentIndexChanged.connect(self._doTranslate)

        btn = pushButton("save translation")
        btn.clicked.connect(self.storeTranslation)
        self.layout().addWidget(btn)

    def getLangValue(self):
        _txt = self.combo.currentText()
        _keyList = LANGUAGES.keys()
        _valList = LANGUAGES.values()
        _id = _valList.index(_txt)
        return _keyList[_id]

    def translateConnection(self, key, inText, doTranslate = True):
        h = nullHBoxLayout()
        if doTranslate:
            label = QLabel(inText)
        else:
        	label = QLabel(self.__inDict[key])
        txt = inText
        if doTranslate:
            txt = self._translator.translate(inText,lang_tgt=self.getLangValue())

        if type(txt) in [list, tuple]:
            txt = txt[0]
        line = QLineEdit(txt)
        for w in [label, line]:
            h.addWidget(w)
        h._info = [key, inText, line]    
        return h

    def _recreateDialog(self):
        _data = loadLanguageFile( self.getLangValue(), self.widgetName)
        perc = 99.0 / len(_data.values())
        for index, (key, value) in enumerate(_data.iteritems()):
            setProgress(index * perc, None, "getting translation info on : %s"%value)
            h = self.translateConnection(key, value, doTranslate=False)
            self._layouts.append(h)
            self.frameLayout.addLayout(h)

        setProgress(100, None, "grabbed all info")


    def _populateDialog(self):
        perc = 99.0 / len(self.__inDict.values())

        for index, (key, value) in enumerate(self.__inDict.iteritems()):
            setProgress(index * perc, None, "getting translation info on : %s"%value)
            h = self.translateConnection(key, value)
            self._layouts.append(h)
            self.frameLayout.addLayout(h)

        setProgress(100, None, "grabbed all info")
    
    def _doTranslate(self):
        perc = 99.0 / len(self.__inDict.values())

        for index, h in enumerate(self._layouts):
            key, base, lineEdit = h._info
            setProgress(index * perc, self.progressBar, "getting translation info on : %s"%base)
            txt = self._translator.translate(self.__inDict[key] ,lang_tgt=self.getLangValue())
            if type(txt) in [list, tuple]:
                txt = txt[0]
            lineEdit.setText(txt)
            self.update()
        
        setProgress(100, self.progressBar, "grabbed all info")

    def _createDict(self):
        outDict = {}
        for h in self._layouts:
            key, base, lineEdit = h._info
            outDict[key] = lineEdit.text()
        return outDict

    def storeTranslation(self):
        outDict = self._createDict()
        language = self.getLangValue()

        storeLanguageFile(outDict, language, self.widgetName)
        self.close()

def testUI(inDict, widgetName):
    mainWindow = interface.get_maya_window()
    wdw = TranslatorDialog(inDict, widgetName=widgetName, parent = mainWindow)
    wdw.show()
    return wdw

def showUI(inDict, widgetName):
    mainWindow = interface.get_maya_window()
    wdw = TranslatorDialog(inDict, widgetName=widgetName, parent = mainWindow)
    wdw.exec_()
    return wdw