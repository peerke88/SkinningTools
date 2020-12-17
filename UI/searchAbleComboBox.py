from SkinningTools.UI.qt_util import *

class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)
        self.placeholderText = ''
        self.holdsItems =[]
        self.completer = QCompleter(self)
        self.completer.setModel(self.model())
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        self.lineEdit().editingFinished.connect(self._sync)
        self.currentIndexChanged.connect(self._toggle)
        self._sync()
    
    def addItem(self, text, setChecked = False, *args):
        if not text in self.holdsItems:
            self.holdsItems.append(text)
        amountItems = len(self.holdsItems)
        self.setMaxVisibleItems(amountItems)
        super(SearchableComboBox, self).addItem(text, *args)
        item = self.model().item(amountItems-1)
        if not setChecked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def addItems(self, inList, setChecked=False,  *args):
        for item in inList:
            self.addItem(item, setChecked)

    def setItemsChecked(self, inItems):
        if inItems == "all":
            inItems = self.holdsItems
        for item in inItems:
            if item not in self.holdsItems:
                continue
            index =self.holdsItems.index(item)
            modelItem = self.model().item(index)
            modelItem.setCheckState(Qt.Checked)
        self.repaint()

    def clear( self ):
        self.holdsItems = []
        self.setMaxVisibleItems(1)
        super(SearchableComboBox, self).clear()

    def getCheckedItems( self ):
        checkedItems = []
        for index in xrange(self.count()):
            item = self.model().item(index)
            if item.checkState() != Qt.Checked:
                continue
            checkedItems.append(self.holdsItems[index])
        self.setMaxVisibleItems(len(self.holdsItems))
        return checkedItems

    def mousePressEvent(self, event):
        if event.x() < self.width() - 20:
            self.setEditable(not self.isEditable())
            self.lineEdit().setText('')
        else:
            super(SearchableComboBox, self).mousePressEvent(event)
    
    def _toggle(self, index):
        item = self.model().item(index)
        item.setData(Qt.Unchecked if item.data(Qt.CheckStateRole) == Qt.Checked else Qt.Checked, Qt.CheckStateRole)
        self._sync()
    
    def setPlaceholderText(self, inText):
        self.placeholderText = inText

    def _sync(self):
        self.setEditable(False)
        checked = self.getCheckedItems()
        self.setPlaceholderText(', '.join(checked))
        
    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        geo = QRect(5, 0, self.width() - 25, self.height())
        painter.drawText(geo, Qt.AlignLeft | Qt.AlignVCenter, self.placeholderText)