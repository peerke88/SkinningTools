from SkinningTools.Maya import api, interface
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from functools import partial
import tempfile, os

class MayaToolsHeader(QWidget):
    def __init__(self, inGraph = None, inProgressBar = None, parent = None):
        super(MayaToolsHeader, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.BezierGraph = inGraph
        self.__graphSize = 60

        self.__mayaToolsSetup()

    def __mayaToolsSetup(self):
        h = nullHBoxLayout()
        g = nullGridLayout()

        g.addWidget(QLabel("  skin:"), 0, 0)
        g.addWidget(QLabel("  Vtx :"), 1, 0)

        g.addWidget(QPushButton("Save >>"), 0, 1)
        g.addWidget(QPushButton("Save >>"), 1, 1)

        g.addWidget(QLineEdit(), 0, 2)
        g.addWidget(QLineEdit(), 1, 2)

        g.addWidget(QPushButton("<< Load"), 0, 3)
        g.addWidget(QPushButton("<< Load"), 1, 3)

        filePath = self._updateGraph()

        self.graph = toolButton(filePath, size=self.__graphSize)
        self.graph.clicked.connect(self._showGraph)
        self.BezierGraph.closed.connect(self._updateGraphButton)
        h.addLayout(g)
        h.addItem(QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(self.graph)

        self.layout().addLayout(h)
    
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