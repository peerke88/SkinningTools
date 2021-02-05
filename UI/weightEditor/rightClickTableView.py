from SkinningTools.UI.qt_util import *

class RightClickTableView(QTableView):
    """ convenience setup on the table view to make sure right click connections are made
    emits signals once conditions are met
    """
    rightClicked = pyqtSignal()
    keyPressed = pyqtSignal(str)
    
    def __init__(self, parent = None):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        """
        super(RightClickTableView, self).__init__(parent)
        self.ignoreInput = False
    
    def mousePressEvent(self, event):
        """ get the position on of the mouse once the mouse is pressed
        """
        self.mousePos = QCursor.pos()
        super(RightClickTableView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ make sure that we only emit the signal if its the right mouse button
        """
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(RightClickTableView, self).mouseReleaseEvent(event)
            
    def keyPressEvent(self, event):
        """ use the keypress event to make sure that keyboard inputs are caught and emitted
        """
        self.keyPressed.emit(event.text())
        
        if self.ignoreInput:
            return
        super(RightClickTableView, self).keyPressEvent(event)