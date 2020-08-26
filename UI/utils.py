# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
import re, functools
from SkinningTools.UI.qt_util import *
from SkinningTools.Maya import api

def nullVBoxLayout(parent=None, size=0):
    v = QVBoxLayout()
    v.setContentsMargins(size, size, size, size)
    return v


def nullHBoxLayout(parent=None, size=0):
    h = QHBoxLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def nullGridLayout(parent=None, size=0):
    h = QGridLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def buttonsToAttach(name, command, *args):
    button = QPushButton()

    button.setText(name)
    button.setObjectName(name)

    button.clicked.connect(command)
    button.setMinimumHeight(23)
    return button

def svgButton(name = '', pixmap = '', size = None):
    btn = QPushButton(name.lower())
    if name != '':
        btn.setLayoutDirection(Qt.LeftToRight)
        btn.setStyleSheet("QPushButton { text-align: left; }")
    _empty = False
    if isinstance(pixmap, str):
        if "empty" in pixmap.lower():
            _empty = True        
        pixmap = QPixmap(pixmap)
    btn.setIcon( QIcon(pixmap) )
    btn.setFocusPolicy(Qt.NoFocus)
    if size is not None:
        _size = QSize(size, size)
        # if _empty:
        #     print name, "is empty"
        #     _size = QSize(size, 1)
        # btn.setFixedSize(_size)
        btn.setIconSize(_size)
    return btn


def toolButton(pixmap='', orientation=0, size=None):
    btn = QToolButton()
    if isinstance(pixmap, str):
        pixmap = QPixmap(pixmap)
    if orientation != 0 and not _isSVG:
        transform = QTransform().rotate(orientation, Qt.ZAxis)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
    btn.setIcon(QIcon(pixmap))
    btn.setFocusPolicy(Qt.NoFocus)
    btn.setStyleSheet('border: 0px;')
    if size is not None:
        btn.setFixedSize(QSize(size, size))
        btn.setIconSize(QSize(size, size))
    return btn


def find_missing_items(int_list):
    original_set = set(int_list)
    smallest_item = min(original_set)
    largest_item = max(original_set)
    full_set = set(xrange(smallest_item, largest_item + 1))
    return sorted(list(full_set - original_set))


def getNumericName(text, names):
    if text in names:
        text = re.sub('\\d*$', '', text)
        names = [n for n in names if n.startswith(text)]
        int_list = []
        for name in names:
            m = re.match('^%s(\\d+)' % text, name)
            if m:
                int_list.append(int(m.group(1)))
            else:
                int_list.append(0)

        int_list.sort()
        missing_int = find_missing_items(int_list)
        if missing_int:
            _id = str(missing_int[0])
        else:
            _id = str(int_list[-1] + 1)
    else:
        _id = ''
    text += _id
    return text


def FalseFolderCharacters(inString):
    return re.search(r'[\\/:\[\]<>"!@#$%^&-.]', inString) or re.search(r'[*?|]', inString) or re.match(r'[0-9]', inString) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def FalseFolderCharactersJapanese(self, inString):
    return re.search(r'[\\/:\[\]<>"!@#$%^&-]', inString) or re.search(r'[*?|]', inString) or "." in inString or (len(inString) > 0 and inString[0].isdigit()) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def checkStringForBadChars(self, inText, button, option=1, *args):
    if (option == 1 and not FalseFolderCharacters(inText) in [None, True]) or (option == 2 and not FalseFolderCharactersJapanese(inText) in [None, False]):
        return False
    if inText == "":
        return False
    return True

def setProgress(inValue, progressBar=None, inText = ''):
    if progressBar == None:
        api.textProgressBar(inValue, inText)
        return
    progressBar.message = inText
    progressBar.setValue(inValue)
    QApplication.processEvents()

def smart_round(value, ndigits):
    return int(value * (10 * ndigits)) / (10. * ndigits)

def round_compare(vA, vB, debug = False):
    for a, b in zip(vA, vB):
        x = smart_round(a, 5)
        y = smart_round(b, 5)
        if not x == y:
            if debug:
                print(x)
                print(y)
            return False
    return True

def compare_vec3(a, b, epsilon=1e-5):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) +abs(a[2] - b[2]) < epsilon


def lerp(a, b, t):
    return a * (1 - t) + b * t

def vLerp(start, end, percent):
    return start + percent * (end - start)

def invLerp(a, b, v):
    return (v - a) / (b - a)

def remap(iMin, iMax, oMin, oMax, v):
    t = invLerp(iMin, iMax, v)
    return lerp(oMin, oMax, t)



def addChecks(cls, button, checks = []):
    v=nullVBoxLayout(size = 3)
    h=nullHBoxLayout()
    v.addLayout(h)
    v.setAlignment(Qt.AlignRight)
    button.setLayout(v)
    button.setContextMenuPolicy(Qt.CustomContextMenu)
    button.checks = {}
    for check in checks:
        chk = QCheckBox()
        chk.setEnabled(False)
        chk.setToolTip(check)
        v.addWidget(chk)
        button.checks[check] = chk

    functions, popup = add_contextToMenu(cls, checks, button )
    button.customContextMenuRequested.connect(functools.partial(on_context_menu, button, popup))

def add_contextToMenu(cls, actionNames, btn ):
    popMenu = QMenu(cls)
    allFunctions = []
    for actionName in actionNames:
        check = QAction(actionName, cls)
        check.setCheckable(True)
        check.toggled.connect(btn.checks[actionName].setChecked)
        popMenu.addAction(check)
        allFunctions.append(check)
    
    return allFunctions, popMenu  

def on_context_menu(buttonObj, popMenu, point):
    popMenu.exec_(buttonObj.mapToGlobal(point)) 