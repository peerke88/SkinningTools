from SkinningTools.UI.utils import getNumericName
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.tearOff.tearOffTabBar import TearoffTabBar 
from SkinningTools.py23 import *


class TabWidget(QTabWidget):
    """ the tab widget that allows the user to unparent tabs in seperate dialogs
    """
    tabAdded = pyqtSignal(unicode)
    tearOff = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        """ the constructor

        :param parent: the object to attach this ui to
        :type parent: QWidget
        """
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(False)
        self.setMouseTracking(True)
        self.setObjectName('TabWidget')
        self.setCustomTabBar()

    def setCustomTabBar(self):
        """ set the custom tab bar that has correct orientations and tear off signals
        """
        tabBar = TearoffTabBar(self)
        self.setTabBar(tabBar)
        tabBar.tearOff.connect(self.tearOff.emit)

    def addGraphicsTab(self, text="NewTAB", changeCurrent=True, useIcon = None):
        """ add a new tab with the correcet name and items attached

        :param text: the title used in the tab
        :type text: string
        :param changeCurrent: if `True` will override the current index, if `False` will append the tab
        :type changeCurrent: bool
        :param useIcon: if given will use an icon to display when the object is torn off
        :type useIcon: string
        :return: the widget that can be thrown around
        :rtype: QWidget
        """
        names = [self.tabText(i) for i in range(self.count())]
        text = getNumericName(text, names)
        tab = QWidget()
        tab.prefix = ''
        tab.tearOffTabName = text
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
        tab.cIndex = index
        view = QScrollArea()
        view.setWidgetResizable(1)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        view.frame = QWidget()
        view.windowDispIcon = useIcon
        view.setWidget(view.frame)
        tab.view = view
        layout.addWidget(view)
        if changeCurrent:
            self.tabAdded.emit(text)
        return tab

    def addView(self, text, index, inWidget):
        """ add the new widget to the tab

        :param text: the title used in the tab
        :type text: string
        :param index: the index onto which the view should be added
        :type index: int
        :param inWidget: the widget to attach
        :type inWidget: QWidget
        """
        tab = QWidget()
        index = self.insertTab(index, tab, text)
        self.setCurrentIndex(index)
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(inWidget)

    def viewAtIndex(self, index):
        """ get the widget attached at current index

        :return: the current tabs widget
        :rtype: QWidget
        """
        if self.widget(index):
            return self.widget(index).findChild(QScrollArea)
        return None

    def clear(self):
        """ make sure that the entire widget is cleared
        """
        allTabs = [self.widget(i) for i in range(self.count())]
        self.blockSignals(True)
        for tab in allTabs:
            tab.deleteLater()

        QTabWidget.clear(self)
        self.blockSignals(False)

