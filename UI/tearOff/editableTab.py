from SkinningTools.UI.utils import getNumericName
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.tearOff.tearOffTabBar import TearoffTabBar, EditableTabBar
from SkinningTools.py23 import *


class TabWidget(QTabWidget):
    tabAdded = pyqtSignal(unicode)
    undoOpen = pyqtSignal()
    undoClose = pyqtSignal()
    selectMapNode = pyqtSignal(int)
    tearOff = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(False)
        self.setMouseTracking(True)
        self.setObjectName('TabWidget')
        self.setCustomTabBar()

    def setCustomTabBar(self):
        tabBar = TearoffTabBar(self)
        self.setTabBar(tabBar)
        tabBar.tearOff.connect(self.tearOff.emit)

    def addGraphicsTab(self, text="NewTAB", changeCurrent=True):
        names = [self.tabText(i) for i in range(self.count())]
        text = getNumericName(text, names)
        tab = QWidget()
        tab.prefix = ''
        tab.usePrefix = False
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        if changeCurrent:
            index = self.currentIndex()
            index = self.insertTab(index + 1, tab, text)
            self.setCurrentIndex(index)
        else:
            index = self.count()
            index = self.insertTab(index, tab, text)
        view = QScrollArea()
        view.setWidgetResizable(1)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        view.frame = QFrame()
        view.frame.setFrameShape(QFrame.NoFrame)
        view.setWidget(view.frame)
        tab.view = view
        layout.addWidget(view)
        if changeCurrent:
            self.tabAdded.emit(text)
        return tab

    def addView(self, text, index, listView):
        tab = QWidget()
        index = self.insertTab(index, tab, text)
        self.setCurrentIndex(index)
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(listView)

    def viewAtIndex(self, index):
        if self.widget(index):
            return self.widget(index).findChild(QScrollArea)
        return None

    def clear(self):
        allTabs = [self.widget(i) for i in range(self.count())]
        self.blockSignals(True)
        for tab in allTabs:
            tab.deleteLater()

        QTabWidget.clear(self)
        self.blockSignals(False)


class EditableTabWidget(TabWidget):
    tabSizeChange = pyqtSignal(QSize)
    tabLabelRenamed = pyqtSignal(unicode, unicode)
    tabRemovedText = pyqtSignal(unicode)
    windowModified = pyqtSignal()
    addItemOn = pyqtSignal(QPointF, QColor, int)
    addItemWithSet = pyqtSignal(QPointF, QColor, unicode, dict)
    addPreviewedItem = pyqtSignal(QPointF, QColor, unicode, dict)
    copyItems = pyqtSignal(list)
    selectedItemsChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        TabWidget.__init__(self, parent)
        self.setAcceptDrops(False)
        self.setObjectName('EditableTabWidget')
        palette = self.palette()
        palette.setColor(QPalette.Midlight, QColor(0, 0, 0, 0))
        self.setPalette(palette)

    def setCustomTabBar(self):
        tabBar = EditableTabBar(self)
        self.setTabBar(tabBar)
        tabBar.tabMoved.connect(lambda: self.windowModified.emit())
        tabBar.tabLabelRenamed.connect(lambda: self.windowModified.emit())
        tabBar.tabLabelRenamed.connect(self.tabLabelRenamed.emit)
        tabBar.tearOff.connect(self.tearOff.emit)
