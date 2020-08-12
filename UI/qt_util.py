# -*- coding: utf-8 -*-
QT_VERSION = "none"
ERROR_LIST = {}
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtCore import Signal as pyqtSignal
    from PySide import QtGui
    from PySide.QtUiTools import *
    import sip
    QString = None
    QT_VERSION = "pyside"
except Exception as e:
    ERROR_LIST["Pyside import"] =  e
    try:
        from PySide2.QtGui import *
        from PySide2.QtCore import *
        from PySide2.QtWidgets import *
        from PySide2.QtCore import Signal as pyqtSignal
        from PySide2 import QtGui
        from PySide2.QtUiTools import *
        import pyside2uic as pysideuic
        import shiboken2 as shiboken
        QString = None
        QT_VERSION = "pyside2"
    except Exception as e:
        ERROR_LIST["Pyside2 import"] = e
        try:
            from PyQt4.QtCore import *
            from PyQt4.QtGui  import *
            from PyQt4 import  QtGui
            from PyQt4.QtUiTools import *
            import pysideuic, shiboken
            QT_VERSION = "pyqt4"
        except Exception as e:
            ERROR_LIST["PyQt4 import"] = e

if QT_VERSION == "none":
    for version in ERROR_LIST.keys():
      print(version, ERROR_LIST[version])

import os
QT_STYLESHEET =  os.path.normpath(os.path.join(__file__, "../qOrange.stylesheet"))

try:
    from PyQt4 import uic
    uic.uiparser.logger.setLevel( logging.CRITICAL )
    uic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass
try:
    import pysideuic
    pysideuic.uiparser.logger.setLevel( logging.CRITICAL )
    pysideuic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass
try:
    import pyside2uic as pysideuic
    pysideuic.uiparser.logger.setLevel( logging.CRITICAL )
    pysideuic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass

from maya import cmds
from functools import partial
import re, string, os, json
nameRegExp = QRegExp('\\w+')


JSONFILE =  os.path.normpath(os.path.join(__file__, "../namer.json"))