from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import tempfile, os
from SkinningTools.UI.dialogs.remapDialog import RemapDialog


class MayaToolsHeader(QWidget):
    def __init__(self, inGraph=None, inProgressBar=None, parent=None):
        super(MayaToolsHeader, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.BezierGraph = inGraph

        self.__graphSize = 60

        self._skSaveLoad = interface.skinWeight()
        self._vtSaveLoad = interface.vertexWeight()

        self.__mayaToolsSetup()
        self.__connections()

    def __mayaToolsSetup(self):
        h = nullHBoxLayout()
        g = nullGridLayout()

        self.skSave = pushButton("Save >>")
        self.vtSave = pushButton("Save >>")
        self.skLine = QLineEdit()
        self.vtLine = QLineEdit()
        self.skLoad = pushButton("<< Load")
        self.vtLoad = pushButton("<< Load")

        g.addWidget(QLabel("  skin:"), 0, 0)
        g.addWidget(QLabel("  Vtx :"), 1, 0)
        g.addWidget(self.skSave, 0, 1)
        g.addWidget(self.vtSave, 1, 1)
        g.addWidget(self.skLine, 0, 2)
        g.addWidget(self.vtLine, 1, 2)
        g.addWidget(self.skLoad, 0, 3)
        g.addWidget(self.vtLoad, 1, 3)

        filePath = self._updateGraph()
        self.graph = toolButton(filePath, size=self.__graphSize)
        self.graph.clicked.connect(self._showGraph)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addLayout(g)
        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(self.graph)

        self.layout().addLayout(h)

    def __connections(self):
        self.skSave.clicked.connect(self._storeSkin)
        self.vtSave.clicked.connect(self._storeVtx)
        self.skLoad.clicked.connect(self._loadSkin)
        self.vtLoad.clicked.connect(self._loadVtx)

    def _showGraph(self):
        self.BezierGraph.show()

    def _updateGraph(self):
        filePath = os.path.join(tempfile.gettempdir(), 'screenshot.jpg')
        QPixmap.grabWidget(self.BezierGraph.view).save(filePath, 'jpg')
        return filePath

    def _updateGraphButton(self):
        filePath = self._updateGraph()
        self.graph.setIcon(QIcon(QPixmap(filePath)))
        self.graph.setIconSize(QSize(self.__graphSize, self.__graphSize))

    def _storeVtx(self):
        index = self._vtSaveLoad.getVtxWeigth()
        self.vtLine.setText(index)

    def _loadVtx(self):
        if self.vtLine.text == '':
            return
        self._vtSaveLoad.setVtxWeigth()

    def _storeSkin(self):
        index = self._skSaveLoad.getSkinWeigth()
        self.skLine.setText(index)

    def _loadSkin(self):
        if self.skLine.text == '':
            return
        if self._skSaveLoad.needsRemap():
            rmpDialog = RemapDialog(self._skSaveLoad, interface.getAllJoints(), shelf)
            rmpDialog.exec_()
            # @todo: make sure that the order here is correct?
            # maybe this doesnt work as intended and we need to remap by index
            self._skSaveLoad.boneInfo = rmpDialog.getConnectionInfo().values()
        self._skSaveLoad.setSkinWeigth()
