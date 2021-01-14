from SkinningTools.UI.qt_util import *

class SearchableComboBox(QComboBox):
    """ searchable combobox delegate
    creates a combobox with completer to make sure that the user can input any of the items present in the current setup
    """
    def __init__(self, parent=None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
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
        """ add an item to the setup

        :param text: the text used in the item
        :type text: string
        :param setChecked: if `True` will set the item as checked, if `False` will keep the item unchecked
        :type setChecked: bool
        """
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
        """ convenience function to add a list of items at the same time

        :param inList: list of items to fill the combobox
        :type inList: list
        :param setChecked: if `True` will set the item as checked, if `False` will keep the item unchecked
        :type setChecked: bool
        """
        for item in inList:
            self.addItem(item, setChecked)

    def setItemsChecked(self, inItems):
        """ convenience function to set multiple items checked

        :param inItems: list of items to set checked
        :type inItems: list
        """
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
        """ cleanup the combobox, clear the items and removed them from the current setup
        """
        self.holdsItems = []
        self.setMaxVisibleItems(1)
        super(SearchableComboBox, self).clear()

    def getCheckedItems( self ):
        """ get all the items that are checked

        :return: list of all checked items
        :rtype: list
        """
        checkedItems = []
        for index in xrange(self.count()):
            item = self.model().item(index)
            if item.checkState() != Qt.Checked:
                continue
            checkedItems.append(self.holdsItems[index])
        self.setMaxVisibleItems(len(self.holdsItems))
        return checkedItems

    def mousePressEvent(self, event):
        """ mouse press event, gets the current text of the clicked item in the combobox
        """
        if event.x() < self.width() - 20:
            self.setEditable(not self.isEditable())
            self.lineEdit().setText('')
        else:
            super(SearchableComboBox, self).mousePressEvent(event)
    
    def _toggle(self, index):
        """ toggle the checkstate of the current selected item

        :param index: the index of the item selected in the combobox
        :type index: int
        """
        item = self.model().item(index)
        item.setData(Qt.Unchecked if item.data(Qt.CheckStateRole) == Qt.Checked else Qt.Checked, Qt.CheckStateRole)
        self._sync()
    
    def setPlaceholderText(self, inText):
        """ set the placeholdertext for display in the combobox
        """
        self.placeholderText = inText

    def _sync(self):
        """ make sure that all checked items are listed on top of the combobox
        """
        self.setEditable(False)
        checked = self.getCheckedItems()
        self.setPlaceholderText(', '.join(checked))
        
    def paintEvent(self, event):
        """ the paint event, to make sure that the combobox is drawn properly
        """
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        geo = QRect(5, 0, self.width() - 25, self.height())
        painter.drawText(geo, Qt.AlignLeft | Qt.AlignVCenter, self.placeholderText)