# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
import re, difflib, functools, math
from SkinningTools.UI.qt_util import *

from SkinningTools.ThirdParty.kdtree import KDTree

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


def pushButton(text=''):
    btn = QPushButton(text)
    btn.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")
    return btn

def buttonsToAttach(name, command, *args):
    button = pushButton()

    button.setText(name)
    button.setObjectName(name)

    button.clicked.connect(command)
    button.setMinimumHeight(23)
    return button


def svgButton(name='', pixmap='', size=None):
    btn = QPushButton(name.lower())
    btn.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")
    if name != '':
        btn.setLayoutDirection(Qt.LeftToRight)
        btn.setStyleSheet("QPushButton { text-align: left; background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444); }")
    _empty = False
    if isinstance(pixmap, str):
        if "empty" in pixmap.lower():
            _empty = True
        pixmap = QPixmap(pixmap)
    btn.setIcon(QIcon(pixmap))
    btn.setFocusPolicy(Qt.NoFocus)
    if size is not None:
        _size = QSize(size, size)
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


def findMissingItems(inList):
    origSet = set(inList)
    smallest = min(origSet)
    largest = max(origSet)
    fullSet = set(range(smallest, largest + 1))
    return sorted(list(fullSet - origSet))

def getNumericName(text, names):
    if text in names:
        text = re.sub('\\d*$', '', text)
        names = [n for n in names if n.startswith(text)]
        ints = []
        for name in names:
            m = re.match('^%s(\\d+)' % text, name)
            if m:
                ints.append(int(m.group(1)))
            else:
                ints.append(0)

        ints.sort()
        missingIntegers = findMissingItems(ints)
        if missingIntegers:
            _id = str(missingIntegers[0])
        else:
            _id = str(ints[-1] + 1)
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


def setProgress(inValue, progressBar=None, inText=''):
    if progressBar is False:
        return
    if progressBar is None:
        from SkinningTools.Maya import api
        api.textProgressBar(inValue, inText)
        return
    progressBar.message = inText
    progressBar.setValue(inValue)
    QApplication.processEvents()


def smart_round(value, ndigits):
    return int(value * (10 ** ndigits)) / (10. ** ndigits)

def smart_roundVec(inVector, nDigits):
    return [smart_round(inVector[0], nDigits), smart_round(inVector[1], nDigits), smart_round(inVector[2], nDigits)]


def round_compare(vA, vB, debug=False):
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
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]) < epsilon

def clamp(val, minVal =0.0, maxVal = 1.0):
    return max(minVal, min(val, maxVal))
    
def lerp(a, b, t):
    return a * (1 - t) + b * t


def vLerp(start, end, percent):
    return start + percent * (end - start)


def invLerp(a, b, v):
    return (v - a) / (b - a)


def remap(iMin, iMax, oMin, oMax, v):
    t = invLerp(iMin, iMax, v)
    return lerp(oMin, oMax, t)

def veclength(inVec):
    return math.sqrt(sum(i**2 for i in x))
    
def widgetsAt(pos):
    widgets = []
    widget_at = QApplication.widgetAt(pos)
    return widget_at


def addChecks(cls, button, checks=None):
    v = nullVBoxLayout(size=3)
    h = nullHBoxLayout()
    v.addLayout(h)
    v.setAlignment(Qt.AlignRight)
    button.setLayout(v)
    button.setContextMenuPolicy(Qt.CustomContextMenu)
    button.checks = {}
    checks = checks or []
    for check in checks:
        chk = QCheckBox()
        chk.setEnabled(False)
        chk.setToolTip(check)
        v.addWidget(chk)
        button.checks[check] = chk

    functions, popup = addContextToMenu(cls, checks, button)
    button.customContextMenuRequested.connect(functools.partial(onContextMenu, button, popup, functions))


def addContextToMenu(cls, actionNames, btn):
    popMenu = QMenu(cls)
    allFunctions = {}
    for actionName in actionNames:
        check = QAction(actionName, cls)
        check.setCheckable(True)
        check.toggled.connect(btn.checks[actionName].setChecked)
        popMenu.addAction(check)
        allFunctions[actionName] = check

    return allFunctions, popMenu


def onContextMenu(buttonObj, popMenu, functions, point):
    for key, value in buttonObj.checks.iteritems():
        functions[key].setChecked(value.isChecked())
    popMenu.exec_(buttonObj.mapToGlobal(point))


def similarString(inString, inList):
    remove = .1
    for i in range(10):
        matches = difflib.get_close_matches(inString, inList, n=3, cutoff=1.0 - (i * remove))
        if matches:
            return matches[0]

# override the focus steal on the lineedit
class LineEdit(QLineEdit):
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Control or key == Qt.Key.Key_Shift:
            return
        else:
            super(self.__class__, self).keyPressEvent(event)

def getClosestVector(inList, currentPos, amountTosearch=1):
    sourceKDTree = KDTree.construct_from_data(inList)
    foundPoints = sourceKDTree.query(query_point=currentPos, t=amountTosearch)
    return foundPoints

def remapClosestPoints(sourceList, targetList, amount):
    sourceKDTree = KDTree.construct_from_data( sourceList )

    remap = OrderedDict()
    weights = OrderedDict()
    for target in targetList:
        closestPoints = sourceKDTree.query(query_point = target, t = amount)
        indices = []
        distances = []
        total = 0.0
        for pt in closestPoints:
            indices.append( sourceList.index(pt) )
            _curDist = veclength(pt) - veclength(target)
            distances.append(_curDist)
            total += _curDist

        wght = []
        for w in distances:
            # smallest value has heighest weight
            wght = 1.0 - (w/total)
        remap[target] = indices
        weights[target] = wght
    return remap, weights


