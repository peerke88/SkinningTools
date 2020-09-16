from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *

class PopupSpinBox(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, parent = None, value=0.0, direct=False):
        super(PopupSpinBox, self).__init__(parent)
        self.setWindowFlags( Qt.Window|Qt.FramelessWindowHint )
        pos = QCursor.pos()
        self.resize(50, 23)
        
        if direct:
            self.input = LineEdit(self)
            self.setCentralWidget(self.input)
            self.input.setText(value)
            
        else:
            self.input = QDoubleSpinBox(self)
            self.input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            
            self.setCentralWidget(self.input)
            
            self.input.setDecimals(3)
            self.input.setRange(0, 10)
            self.input.setValue(value)
            
            self.input.selectAll()
        
        self.move(pos.x()-20, pos.y()-12)
        self.input.editingFinished.connect(self.close)
            
        self.show()
        self.activateWindow()
        self.raise_()
        self.input.setFocus()
        
    def closeEvent(self, e):
        self.closed.emit()