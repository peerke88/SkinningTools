from SkinningTools.UI.qt_util import *

class RightClickTableView(QTableView):
    rightClicked = pyqtSignal()
    keyPressed = pyqtSignal(str)
    
    def __init__(self, parent = None):
        super(RightClickTableView, self).__init__(parent)
        self.ignoreInput = False
    
    def mouseReleaseEvent(self, event):
        self.mouse_pos = QCursor.pos()
        
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(RightClickTableView, self).mouseReleaseEvent(event)
            
    def keyPressEvent(self, event):
        self.keyPressed.emit(event.text())
        
        if self.ignoreInput:
            return
        super(RightClickTableView, self).keyPressEvent(event)