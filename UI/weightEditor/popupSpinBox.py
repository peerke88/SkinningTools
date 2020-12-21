from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *

class PopupSpinBox(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent = None, value=0.0, textValue=False):
        super(PopupSpinBox, self).__init__(parent)
        self.setWindowFlags( Qt.Window|Qt.FramelessWindowHint )

        pos = QCursor.pos()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(parent.rect().width(), parent.rect().height())
        if textValue:
            self.input = LineEdit(self)
            self.input.setText(value)
            
        else:
            self.input = QDoubleSpinBox(self)
            self.input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.input.setDecimals(3)
            self.input.setRange(0, 10)
            self.input.setValue(value)
            
            self.input.selectAll()

        self.input.resize(50, 23)
        #@todo: need to set up in a way that the popup is placed ontop of the table cells
        self.input.move(parent.view.mapFromGlobal(pos).x(), parent.view.mapFromGlobal(pos).y())
        self.input.editingFinished.connect(self.close)
            
        self.show()
        self.activateWindow()
        self.raise_()
        self.input.setFocus()
    
    def closeEvent(self, e):
        self.closed.emit()