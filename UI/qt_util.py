# -*- coding: utf-8 -*-
QT_VERSION = "none"
ERROR_LIST = {}

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtCore import Signal as pyqtSignal
    from PySide.QtSvg import *
    from PySide import QtGui
    from PySide.QtUiTools import *
    import sip

    QString = None
    QT_VERSION = "pyside"
except Exception as e:
    ERROR_LIST["Pyside import"] = e
    try:
        from PySide2.QtGui import *
        from PySide2.QtCore import *
        from PySide2.QtWidgets import *
        from PySide2.QtCore import Signal as pyqtSignal
        from PySide2.QtSvg import *
        from PySide2 import QtGui
        from PySide2.QtUiTools import *
        import shiboken2 as shiboken

        QString = None
        QT_VERSION = "pyside2"
    except Exception as e:
        ERROR_LIST["Pyside2 import"] = e
        try:
            from PyQt4.QtCore import *
            from PyQt4.QtGui import *
            from PyQt4.QtSvg import *
            from PyQt4 import QtGui
            from PyQt4.QtUiTools import *
            import  shiboken

            QT_VERSION = "pyqt4"
        except Exception as e:
            ERROR_LIST["PyQt4 import"] = e

if QT_VERSION == "none":
    for version in ERROR_LIST.keys():
        print(version, ERROR_LIST[version])


nameRegExp = QRegExp('\\w+')

def wrapinstance(ptr, base=None):
    '''workaround to be able to wrap objects with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=485'''
    if ptr is None:
        return None
    ptr = int(ptr)
    if 'shiboken' in globals().keys():
        if base is None:
            qObj = shiboken.wrapInstance(int(ptr), QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QWidget
        return shiboken.wrapInstance(int(ptr), base)
    elif "sip" in globals().keys():
        base = QObject
        return sip.wrapinstance(int(ptr), base)
    else:
        return None
