from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from maya import cmds, OpenMayaUI 
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget

class DockWidget(MayaQWidgetDockableMixin, QDialog):
    toolName = "mayaDockWidgetTool"
    def __init__(self, parent = None):
        self.deleteInstances()
        super(DockWidget, self).__init__(parent)

        self.setObjectName(self.__class__.toolName)

        self.closeEventTriggered.connect(self.closeEvent)
        self.closeEventTriggered.connect(self.cleanup)

    def dockCloseEventTriggered(self):
        self.closeEvent(None) 

    def deleteInstances(self):
        currentClass = "%sWorkspaceControl"%self.__class__.toolName
        if cmds.window(currentClass, exists=1):
            cmds.deleteUI(currentClass)

    def run(self):
        self.show(dockable = True)

    def cleanup(self, *_):
        self.deleteInstances()

    def closeEvent(self, *_):
        raise NotImplementedError( "%s.closeEvent"%self.__class__)

    