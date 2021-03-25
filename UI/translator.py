# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from SkinningTools.ThirdParty.google_trans_new import google_translator, LANGUAGES
from SkinningTools.Maya import interface

class SearchableComboBox(QComboBox):
    """ combobox that adds functionality to search for the object necessary out of the list of items
    """
    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
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
        """ sync the current text with the text of give item at the index
        """
        text = self.currentText()
        opt = self.itemText(self.currentIndex())
        if opt != text:
            self.setCurrentText(opt)

class TranslatorDialog(QDialog):
    """ simple dialog with google translate connections
    making sure that we can translate any given text to any language
    the items displayed will always have the english text to the left to compare
    """
    def __init__(self, inDict = None, defaultLanguage = "japanese", widgetName = None, parent = None):
        """ the constructor

        :param inDict: the base dictionary to translate from
        :type inDict: dict
        :param defaultLanguage: default language used to translate to
        :type defaultLanguage: string
        :param widgetName: the name of the widget we are translating
        :type widgetName: string
        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        if widgetName is None:
            print("widgetName cannot be None")
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
        """ convenience function to get the name of the language we are translating to

        :return: the language to translate to
        :rtype: string
        """
        _txt = self.combo.currentText()
        _keyList = LANGUAGES.keys()
        _valList = LANGUAGES.values()
        _id = _valList.index(_txt)
        return _keyList[_id]

    def translateConnection(self, key, inText, doTranslate = True):
        """ create layout with the setup using a label and a lineedit to make sure we can change the translation if necessary
 
        :param key: key value of the original dictionary to use for later
        :type key: string
        :param inText: the text to translate or use as the input to change
        :type inText: string
        :param doTranslate: if `True` the text given will be translated, if `False` we use the text for asjustments
        :type doTranslate: bool
        :return: the layout holding the widgets
        :rtype: QLayout
        """
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
        line = QPlainTextEdit(txt)
        for w in [label, line]:
            h.addWidget(w)
        h._info = [key, inText, line]    
        return h

    def _recreateDialog(self):
        """ create the dialog with all the information of the given dictionary
        """
        _data = loadLanguageFile( self.getLangValue(), self.widgetName)
        perc = 99.0 / len(_data.values())
        for index, (key, value) in enumerate(_data.items()):
            setProgress(index * perc, None, "getting translation info on : %s"%value)
            h = self.translateConnection(key, value, doTranslate=False)
            self._layouts.append(h)
            self.frameLayout.addLayout(h)

        setProgress(100, None, "grabbed all info")


    def _populateDialog(self):
        """ populate the dialog using the given dictionary and auto translate the necessary pieces of information
        """
        perc = 99.0 / len(self.__inDict.values())

        for index, (key, value) in enumerate(self.__inDict.items()):
            setProgress(index * perc, None, "getting translation info on : %s"%value)
            h = self.translateConnection(key, value)
            self._layouts.append(h)
            self.frameLayout.addLayout(h)

        setProgress(100, None, "translated info")
    
    def _doTranslate(self):
        """ seperate function to translate elements when the dialog is already build
        """
        perc = 99.0 / len(self.__inDict.values())

        for index, h in enumerate(self._layouts):
            key, base, lineEdit = h._info
            setProgress(index * perc, self.progressBar, "getting translation info on : %s"%base)
            txt = self._translator.translate(self.__inDict[key] ,lang_tgt=self.getLangValue())
            if type(txt) in [list, tuple]:
                txt = txt[0]
            lineEdit.setPlainText(txt)
            self.update()
        
        setProgress(100, self.progressBar, "translated info")

    def _createDict(self):
        """ create the dictionary using the information of the widget

        :return: the translated dictionary
        :rtype: dict
        """
        outDict = {}
        for h in self._layouts:
            key, base, lineEdit = h._info
            outDict[key] = lineEdit.toPlainText()
        return outDict

    def storeTranslation(self):
        """ build the translation json file 
        """
        outDict = self._createDict()
        language = self.getLangValue()

        storeLanguageFile(outDict, language, self.widgetName)
        self.close()

def testUI(inDict, widgetName):
    """ convenience function to show the current widget without it being part of the system

    :param inDict: the dictionary to translate
    :type inDict: dict
    :param widgetName: the name of the widget to use to store the file
    :type widgetName: string
    :return: the current widget
    :rtype: QWidget
    """
    mainWindow = interface.get_maya_window()
    wdw = TranslatorDialog(inDict, widgetName=widgetName, parent = mainWindow)
    wdw.show()
    return wdw

def showUI(inDict, widgetName):
    """ function to show the widget blocking other functionality
    
    :param inDict: the dictionary to translate
    :type inDict: dict
    :param widgetName: the name of the widget to use to store the file
    :type widgetName: string
    :return: the current widget
    :rtype: QWidget
    """
    mainWindow = interface.get_maya_window()
    wdw = TranslatorDialog(inDict, widgetName=widgetName, parent = mainWindow)
    wdw.exec_()
    return wdw