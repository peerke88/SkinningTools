from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.py23 import *
from functools import partial
import tempfile, os
from SkinningTools.UI.dialogs.remapDialog import RemapDialog


class MayaToolsHeader(QWidget):
    """ basic group object that holds all the maya Tools
    :note: this needs to change later based on the dcc tool
    """
    toolName = "MayaToolsHeader"

    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        """ the constructor

        :param inGraph: the graph function that allows change of the average weight function
        :type inGraph: BezierGraph
        :param inProgressBar: the progressbar to show progress on tools current state
        :type inProgressBar: QProgressBar
        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(MayaToolsHeader, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.BezierGraph = inGraph

        self.__graphSize = 60
        self.textInfo = {}

        self._skSaveLoad = interface.skinWeight()
        self._vtSaveLoad = interface.vertexWeight()

        self.__mayaToolsSetup()
        self.__connections()

    # --------------------------------- translation ----------------------------------
    def translate(self, localeDict={}):
        """ translate the ui based on given dictionary

        :param localeDict: the dictionary holding information on how to translate the ui
        :type localeDict: dict
        """
        for key, value in localeDict.items():
            self.textInfo[key].setText(value)

    def getButtonText(self):
        """ convenience function to get the current items that need new locale text
        """
        _ret = {}
        for key, value in self.textInfo.items():
            _ret[key] = value.text()
        return _ret

    def doTranslate(self):
        """ seperate function that calls upon the translate widget to help create a new language
        we use the english language to translate from to make sure that translation doesnt get lost
        """
        from SkinningTools.UI import translator
        _dict = loadLanguageFile("en", self.toolName)
        _trs = translator.showUI(_dict, widgetName=self.toolName)

    # --------------------------------- ui setup ----------------------------------

    def __mayaToolsSetup(self):
        """ convenience function to gather all buttons for the current UI
        """
        h = nullHBoxLayout()
        g = nullGridLayout()

        self.textInfo["skSave"] = pushButton("Save >>")
        self.textInfo["vtSave"] = pushButton("Save >>")
        self.skLine = QLineEdit()
        self.vtLine = QLineEdit()
        self.textInfo["skLoad"] = pushButton("<< Load")
        self.textInfo["vtLoad"] = pushButton("<< Load")

        self.textInfo["skSave"].setWhatsThis("saveSkin")
        self.textInfo["skLoad"].setWhatsThis("saveSkin")
        self.textInfo["vtSave"].setWhatsThis("saveVtx")
        self.textInfo["vtLoad"].setWhatsThis("saveVtx")

        self.textInfo["lbl0"] = QLabel("  skin:")
        self.textInfo["lbl1"] = QLabel("  Vtx :")
        g.addWidget(self.textInfo["lbl0"], 0, 0)
        g.addWidget(self.textInfo["lbl1"], 1, 0)
        g.addWidget(self.textInfo["skSave"], 0, 1)
        g.addWidget(self.textInfo["vtSave"], 1, 1)
        g.addWidget(self.skLine, 0, 2)
        g.addWidget(self.vtLine, 1, 2)
        g.addWidget(self.textInfo["skLoad"], 0, 3)
        g.addWidget(self.textInfo["vtLoad"], 1, 3)

        filePath = self._updateGraph()
        self.graph = toolButton(filePath, size=self.__graphSize)
        self.graph.setWhatsThis("Averagevtx")
        self.graph.clicked.connect(self.BezierGraph.show)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addLayout(g)
        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(self.graph)

        self.layout().addLayout(h)

    def __connections(self):
        """ signal connections
        """
        self.textInfo["skSave"].clicked.connect(self._storeSkin)
        self.textInfo["vtSave"].clicked.connect(self._storeVtx)
        self.textInfo["skLoad"].clicked.connect(self._loadSkin)
        self.textInfo["vtLoad"].clicked.connect(self._loadVtx)

    def _updateGraph(self):
        """ convert the graph to an image 

        :return: path to the image to use as button
        :rtype: string
        """
        filePath = os.path.join(tempfile.gettempdir(), 'screenshot.jpg')
        try:
            QPixmap.grabWidget(self.BezierGraph.view).save(filePath, 'jpg')
        except:
            imageVar2 = self.BezierGraph.view.grab(self.BezierGraph.view.rect())  # returns QPixMap
            imageVar2.save(filePath, 'jpg')

        return filePath

    def _updateGraphButton(self):
        """ update the button image with information of the current graph
        """
        filePath = self._updateGraph()
        self.graph.setIcon(QIcon(QPixmap(filePath)))
        self.graph.setIconSize(QSize(self.__graphSize, self.__graphSize))

    def _storeVtx(self):
        """ visual update on storing vertex weigth information
        """
        index = self._vtSaveLoad.getVtxWeight()
        self.vtLine.setText(str(index))

    def _loadVtx(self):
        """ load current stored vertex weigth information
        """
        if self.vtLine.text == '':
            return
        self._vtSaveLoad.setVtxWeight()

    def _storeSkin(self):
        """ visual update on storing object weigth information
        """
        index = self._skSaveLoad.getSkinWeight()
        self.skLine.setText(str(index))

    def _loadSkin(self):
        """ load current stored object weigth information
        """
        if self.skLine.text == '':
            return
        self._skSaveLoad.setSkinWeights()


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd = QMainWindow(mainWindow)
    from SkinningTools.UI.fallofCurveUI import BezierGraph
    mwd.setWindowTitle("MayaToolsHeader Test window")
    wdw = MayaToolsHeader(inGraph=BezierGraph(), parent=mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw
