# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class DockWidget(MayaQWidgetDockableMixin, QDialog):
    """ convenience class to wrap the mixin of maya witha  QDialog
    fixes the closeevent and cleans up ui-scene on close and open
    """
    toolName = "mayaDockWidgetTool"

    def __init__(self, parent=None):
        """ construction method
        before calling the super we already check if we need to clean up the scene

        :param parent: possible QWidget parent, in this case its recommended to use the maya main window
        :type parent: QWidget
        """
        self.deleteInstances()
        super(DockWidget, self).__init__(parent)

        self.setObjectName(self.__class__.toolName)

        # new connection to the closeEvent so its always called even when we close the docked version
        self.closeEventTriggered.connect(self.closeEvent)

    def dockCloseEventTriggered(self):
        """this is the function that is called when you close the widget when its docked
        """
        self.closeEvent(QCloseEvent())

    def deleteInstances(self):
        """remove any lingering instances of the current tool,
        make sure that the toolName used in the class is clear and unique
        then this wont break any existing tools of maya
        """
        currentClass = "%sWorkspaceControl" % self.__class__.toolName
        if cmds.window(currentClass, exists=1):
            cmds.deleteUI(currentClass)
        if cmds.window(self.__class__.toolName, exists=1):
            cmds.deleteUI(self.__class__.toolName)

    def run(self):
        """show the current ui and attach to a dockwidget
        """
        self.show(dockable=True)

    def closeEvent(self, event):
        """ override for the closeEvent, we add one here as the Mixin in maya does not call the closeEvent
        currently using NotImplementedError as the tool we are using needs a closeEvent
        """
        self.deleteInstances()
        super(DockWidget, self).closeEvent(event)
