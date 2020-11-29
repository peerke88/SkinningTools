from maya import cmds, OpenMayaUi as omui
from Qt import QtWidgets, QtCore, QtCompat


def Dock(Widget, width=300, show=True):
    """Dock `Widget` into Maya
    Arguments:
        Widget (QWidget): Class
        show (bool, optional): Whether to show the resulting dock once created
    """

    name = Widget.__name__
    label = getattr(Widget, "label", name)

    try:
        cmds.deleteUI(name)
    except RuntimeError:
        pass

    dockControl = cmds.workspaceControl(
        name,
        tabToControl=["AttributeEditor", -1],
        initialWidth=width,
        minimumWidth=True,
        widthProperty="preferred",
        label=label
    )

    dockPtr = omui.MQtUtil.findControl(dockControl)
    dockWidget = QtCompat.wrapInstance(long(dockPtr), QtWidgets.QWidget)
    dockWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    child = Widget(dockWidget)
    dockWidget.layout().addWidget(child)

    if show:
        cmds.evalDeferred(
            lambda *args: cmds.workspaceControl(
                dockControl,
                edit=True,
                restore=True
            )
        )

    return child