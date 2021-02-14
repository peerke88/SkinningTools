# -*- coding: utf-8 -*-
from SkinningTools.py23 import *
from SkinningTools.UI.qt_util import *
from SkinningTools.ThirdParty.kdtree import KDTree
from SkinningTools.ThirdParty import requests

import re, difflib, math, tempfile, base64, os, json, warnings
from functools import partial

UIDIRECTORY = os.path.dirname(__file__)

def getDebugState():
    """ convenience function to work with debug mode 
    this gets turned to False when packaged using the package creator

    :return: the debug state
    :rtype: boolean
    """
    isDebug = True
    return isDebug

    
def nullVBoxLayout(parent=None, size=0):
    """ convenience function for the QVBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QVBoxLayout
    """
    v = QVBoxLayout()
    v.setContentsMargins(size, size, size, size)
    return v


def nullHBoxLayout(parent=None, size=0):
    """ convenience function for the QHBoxLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QHBoxLayout
    """
    h = QHBoxLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def nullGridLayout(parent=None, size=0):
    """ convenience function for the QGridLayout

    :param parent: the possible parent for the layout
    :type parent: QWidget
    :param size: the size of the margins
    :type size: int
    :return: the layout
    :rtype: QGridLayout
    """
    h = QGridLayout()
    h.setContentsMargins(size, size, size, size)
    return h


def pushButton(text=''):
    """ simple button command with correct stylesheet
    
    :param text: text to add to the button
    :type text: string
    :return: the button  
    :rtype: QPushButton
    """
    btn = QPushButton(text)
    btn.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #595959, stop:1 #444444);")
    return btn

def buttonsToAttach(name, command, *_):
    """ convenience function to attach signal command to qpushbutton on creation
    
    :param name: text to add to the button
    :type name: string
    :param command: python command to attach to the current button on clicked signal
    :type command: <function>
    :return: the button  
    :rtype: QPushButton
    """
    button = pushButton()

    button.setText(name)
    button.setObjectName(name)

    button.clicked.connect(command)
    button.setMinimumHeight(23)
    return button


def svgButton(name='', pixmap='', size=None, toolTipInfo = None):
    """ toolbutton function with image from svg file
    
    :param name: text to add to the button
    :type name: string
    :param pixmap: location of the svg file
    :type pixmap: string
    :param size: height and width of image in pixels
    :type size: int
    :return: the button  
    :rtype: QPushButton
    """
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
    if not toolTipInfo is None:
        btn.setWhatsThis(toolTipInfo)

    if size is not None:
        _size = QSize(size, size)
        btn.setIconSize(_size)
    return btn


def toolButton(pixmap='', orientation=0, size=None):
    """ toolbutton function with image
    
    :param pixmap: location of the image
    :type pixmap: string
    :param orientation: rotation in degrees clockwise
    :type orientation: int
    :param size: height and width of image in pixels
    :type size: int
    :return: the button  
    :rtype: QToolButton
    """
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
        if type(size) == int:
            btn.setFixedSize(QSize(size, size))
            btn.setIconSize(QSize(size, size))
        else:
            btn.setFixedSize(size)
            btn.setIconSize(size)
    return btn

def arrowButton(arrowType, sizePolicy ):
    """ toolbutton function with arrows
    
    :param arrowType: Arrow, arrow type to add to the button
    :type arrowType: Qt.Arrow
    :param sizePolicy: list of sizepolicy information for width and height
    :type sizePolicy: QSizePolicy
    :return: the button  
    :rtype: QToolButton
    """
    btn = QToolButton()
    btn.setArrowType(arrowType)
    if arrowType in [Qt.LeftArrow, Qt.RightArrow]:
        btn.setMaximumWidth(12)
    else:
        btn.setMaximumHeight(12) 
    btn.setSizePolicy(*sizePolicy)
    btn.setStyleSheet('border: 0px;')
    return btn

def findMissingItems(inList):
    """ find the numbers in the list that are not identified

    :param inList: list of names to check
    :type inList: list
    :return: list of missing numbers
    :rtype: list
    """
    origSet = set(inList)
    smallest = min(origSet)
    largest = max(origSet)
    fullSet = set(range(smallest, largest + 1))
    return sorted(list(fullSet - origSet))

def getNumericName(text, names):
    """ get unique identifiers for names that are created
    if the name already exists, add a number at the end to make it unique again

    :param text: the text to check for unique names
    :type text: string
    :param names: the names that already exist
    :type names: list
    :return: a unique name
    :rtype: string
    """
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
    """ checking a string for characters that are not allowed in folder structures

    :param inString: the string to check
    :type inString: string
    :return: if the string has bad characters
    :rtype: bool
    """
    return re.search(r'[\\/:\[\]<>"!@#$%^&-.]', inString) or re.search(r'[*?|]', inString) or re.match(r'[0-9]', inString) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def FalseFolderCharactersJapanese(self, inString):
    """ checking a string for characters that are not allowed in folder structures

    :param inString: the string to check
    :type inString: string
    :return: if the string has bad characters
    :rtype: bool
    """
    return re.search(r'[\\/:\[\]<>"!@#$%^&-]', inString) or re.search(r'[*?|]', inString) or "." in inString or (len(inString) > 0 and inString[0].isdigit()) or re.search(u'[\u4E00-\u9FFF]+', inString, re.U) or re.search(u'[\u3040-\u309Fー]+', inString, re.U) or re.search(u'[\u30A0-\u30FF]+', inString, re.U)


def checkStringForBadChars(self, inText, button, option=1, *args):
    """ checking a string for characters that are not allowed in folder structures

    :param inText: the text to check
    :type inText: string
    :param option: the type of structure to check for
    :type option: int

    :return: if the string has bad characters
    :rtype: bool
    """
    if (option == 1 and not FalseFolderCharacters(inText) in [None, True]) or (option == 2 and not FalseFolderCharactersJapanese(inText) in [None, False]):
        return False
    if inText == "":
        return False
    return True

def storeLanguageFile(inDict, language, widgetName):
    """ store the language file based on given inputs

    :param inDict: the translation dictionary
    :type inDict: dict
    :param language: the language used in the dictionary
    :type language: string
    :param widgetName: name of the widget used to link the language file with
    :type widgetName: string
    """
    languagesDir = os.path.join(UIDIRECTORY, "languages")
    curLangDir = os.path.join(languagesDir, language)
    if not os.path.exists(curLangDir):
        os.makedirs(curLangDir)
    
    widgetLanguageFile = os.path.join(curLangDir, "%s.LAN"%widgetName)
    with open(widgetLanguageFile, 'w+') as f:
        json.dump(inDict, f, indent=2)

def loadLanguageFile(language, widgetName):
    """ load the language file based on given inputs

    :param language: the language used in the dictionary
    :type language: string
    :param widgetName: name of the widget used to link the language file with
    :type widgetName: string
    :return: the translation dictionary
    :rtype: dict
    """
    languagesDir = os.path.join(UIDIRECTORY, "languages")
    curLangDir = os.path.join(languagesDir, language)
    if not os.path.exists(curLangDir):
        print("no language (%s) folder found for widget <%s>!"%(language, widgetName))
        return False

    widgetLanguageFile = os.path.join(curLangDir, "%s.LAN"%widgetName)
    if not os.path.exists(widgetLanguageFile):
        print("no language (%s) file found for widget <%s>!"%(language, widgetName))
        return False

    with open(widgetLanguageFile) as f:
        _data = json.load(f)
    return _data

def setProgress(inValue, progressBar=None, inText=''):
    """ convenience function to set the progress bar value even when a qProgressbar does not exist

    :param inValue: the current percentage of the progressbar
    :type inValue: int
    :param progressbar: the progressbar to update
    :type progressbar: QProgressBar
    :param inText: additional text to show with the progressbar
    :type inText: string
    """
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
    """ function to cap the decimals 

    :param value: the value to cap
    :type value: float/double
    :param ndigits: amount of decimals needed
    :type ndigits: int
    :return: rounded float
    :rtype: float
    """
    return int(value * (10 ** ndigits)) / (10. ** ndigits)

def smart_roundVec(inVector, nDigits):
    """ function to cap the decimals of a vector

    :param inVector: the value to cap
    :type inVector: list
    :param ndigits: amount of decimals needed
    :type ndigits: int
    :return: rounded vector
    :rtype: list
    """
    return [smart_round(inVector[0], nDigits), smart_round(inVector[1], nDigits), smart_round(inVector[2], nDigits)]


def round_compare(vA, vB, debug=False):
    """ compare 2 objects if they are close enough to eahother, rounding the values as we dont want precision to interfere

    :param vA: the value to compare
    :type vA: float/ double
    :param vB: the value to compare
    :type vB: float/ double
    :param debug: if `True` prints the info, if `False` just returns the value
    :type debug: bool
    :return: if the objects are the same or not
    :rtype: bool
    """
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
    """ compare 2 vectors if they are close enough to eahother, rounding the values as we dont want precision to interfere

    :param a: the value to compare
    :type a: list
    :param b: the value to compare
    :type b: list
    :param epsilon: the precision allowance that the vectors can have between them
    :type epsilon: double
    :return: if the objects are the same or not
    :rtype: bool
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]) < epsilon

def clamp(val, minVal =0.0, maxVal = 1.0):
    """ clamp value between min and max

    :param val: value to clamp
    :type val: float 
    :param minVal: minimum value 
    :type minVal: float
    :param maxVal: maximum value
    :type maxVal: float
    :return: the clamped value
    :rtype: float
    """
    return max(minVal, min(val, maxVal))
    
def lerp(a, b, t):
    """ blend the value from start to end based on the weight

    :param a: start value
    :type a: float 
    :param b: end value 
    :type b: float
    :param t: the weight
    :type t: float
    :return: the value in between
    :rtype: float
    """
    return a * (1 - t) + b * t


def vLerp(start, end, percent):
    """ blend the vector from start to end based on the weight

    :param start: start vector
    :type start: vector 
    :param end: end vector 
    :type end: vector
    :param percent: the weight
    :type percent: float
    :return: the vector in between
    :rtype: vector
    """
    return start + percent * (end - start)


def invLerp(a, b, v):
    """ lerp the other way around, use the end product to get the weigth

    :param a: start value
    :type a: float 
    :param b: end value 
    :type b: float
    :param v: middle value
    :type v: float
    :return: the weight
    :rtype: float
    """
    return (v - a) / (b - a)


def remap(iMin, iMax, oMin, oMax, v):
    """ remap the value from 1 range to another range

    :param iMin: new min value
    :type iMin: float 
    :param iMax: new max value
    :type iMax: float
    :param oMin: old min value
    :type oMin: float
    :param oMax: old max value
    :type oMax: float
    :param v: value to remap
    :type v: float
    :return: remapped value
    :rtype: float
    """    
    t = invLerp(iMin, iMax, v)
    return lerp(oMin, oMax, t)

def veclength(inVec):
    """ get the length of a vector

    :param inVec: the vector to get the length of
    :type inVec: list 
    :return: length of a vector
    :rtype: float
    """    
    return math.sqrt(sum(i**2 for i in x))
    
def widgetsAt(pos):
    """ Qt convenience function to get the widget at given screen position

    :param pos: the position on screen
    :type pos: QPos 
    :return: widget on the position given
    :rtype: QWidget
    """
    widgets = []
    widget_at = QApplication.widgetAt(pos)
    return widget_at


def addChecks(cls, button, checks=None):
    """ add checkboxes to a button for extra functionality

    :param cls: parent class
    :type cls: <class>
    :param button: the button to add the checkboxes to
    :type button: QPushButton
    :param checks: names of all the checkboxes to add
    :type checks: list
    """
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
        # chk.setEnabled(False)
        chk.setToolTip(check)
        chk.displayText = check
        v.addWidget(chk)
        button.checks[check] = chk

    functions, popup = addContextToMenu(cls, checks, button)
    button.customContextMenuRequested.connect(partial(onContextMenu, button, popup, functions))
    
    button.getNameInfo = {}
    for check in checks:
        button.getNameInfo[check] = functions[check]

def addContextToMenu(cls, actionNames, btn):
    """ add context menu to button based on the checkboxes

    :param cls: parent class
    :type cls: <class>
    :param actionNames: names of all the checkboxes
    :type actionNames: list
    :param button: the button to add context menu to
    :type button: QPushButton
    :return: functions dictionary, Qmenu
    :rtype: list
    """
    popMenu = QMenu(cls)
    allFunctions = {}
    for actionName in actionNames:
        _name = btn.checks[actionName].displayText
        check = QAction(_name, cls)
        check.setCheckable(True)
        check.toggled.connect(btn.checks[actionName].setChecked)
        popMenu.addAction(check)
        allFunctions[actionName] = check

    return allFunctions, popMenu


def onContextMenu(buttonObj, popMenu, functions, point):
    """ popup the context menu when requested

    :param buttonObj: the button to add context menu to
    :type buttonObj: QPushButton
    :param popMenu: the menu to popup
    :type popMenu: QMenu
    :param functions: names of all the checkboxes
    :type functions: list
    :param point: position to spawn the menu on screen
    :type point: Qpos
    """
    for key, value in buttonObj.checks.iteritems():
        functions[key].setChecked(value.isChecked())
    popMenu.exec_(buttonObj.mapToGlobal(point))


def similarString(inString, inList):
    """ check if there is an object that resembles the given string in the list

    :param inString: string to check for
    :type inString: string
    :param inList: list of strings to choose from
    :type inList: list
    :return: the string that resembles the input the most
    :rtype: string
    """
    remove = .1
    for i in range(10):
        matches = difflib.get_close_matches(inString, inList, n=3, cutoff=1.0 - (i * remove))
        if matches:
            return matches[0]

class LineEdit(QLineEdit):
    """override the focus steal on the lineedit"""
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Control or key == Qt.Key.Key_Shift:
            return
        else:
            super(self.__class__, self).keyPressEvent(event)

def getClosestVector(inList, currentPos, amountTosearch=1):
    """ get the closest position in the given list from current position

    :param inList: list of positions to choose from
    :type inList: list
    :param currentPos: the position to search from
    :type currentPos: vector
    :param amountToSearch: the amoutn of closest positions to return
    :type amountToSearch: int
    :return: list of closest positions
    :rtype: list
    """
    sourceKDTree = KDTree.construct_from_data(inList)
    foundPoints = sourceKDTree.query(query_point=currentPos, t=amountTosearch)
    return foundPoints

def remapClosestPoints(sourceList, targetList, amount):
    """ map given positions to the closest positions

    :param sourceList: list of positions to search from
    :type sourceList: 
    :param targetList: list of positions to choose from
    :type targetList: list
    :param amount: the amoutn of closest positions to return
    :type amount: int
    :return: closest positions, weight values
    :rtype: list
    """
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

def incrementName(name):
    """ simple version of adding new trailing number

    :param name: object to add trailing number to
    :type name: string
    :return: objects name with new trailing number
    :rtype: string
    """
    trailingNumber = re.compile(r'\d+$')
    m = trailingNumber.search(name)
    if m:
        i = m.group(0)
        return "%s%s"%( name[:-len(i)], int(i) + 1)
    return name + '1'

def convertImageToString(inPath):
    """ convenience function to save an image as a string format so the image does not have to be placed with the file

    :param inPath: the path the the image
    :type inPath: string
    :return: encoded string and extension type
    :rtype: list
    """
    with open(inPath, "rb") as imageFile:
        _str = base64.b64encode(imageFile.read())
    return [_str, os.path.splitext(inPath)[-1]]

def convertStringToImage(inString):
    """ convenience function to restore an image from an encoded string

    :param inString: encoded string and extension type
    :type inString: list
    :return: the path the the image
    :rtype: string
    """
    filePath = os.path.join(tempfile.gettempdir(), "img%s"%inString[-1])
    with open(filePath, "wb") as fh:
        fh.write(inString[0].decode('base64'))
    return filePath

# ----------- google drive functionality --------

def gDriveDownload(urlinfo, destination, progressBar = None):
    """ google download functionality
    
    :param urlinfo: dict of  filenames and corresponding files to download 
    :type urlinfo: dict
    :param destination: the folder to place downloaded files
    :type destination: string
    :param progressBar: the progressbar to show how much is downloaded
    :type progressBar: QProgressbar
    """
    setProgress(0, progressBar, inText="start download information")
    
    setProgress(10, progressBar, inText="send request")
    percentage = 80.0/len(urlinfo.keys())
    for index, (fileName, url) in enumerate(urlinfo.iteritems()):

        response = requests.get(url, stream=True)
        saveResponseContent(response, os.path.join( destination, fileName ) )
        setProgress(10 + (index * percentage), progressBar, inText="checking response")
    
    setProgress(100, progressBar, inText="downloaded information")

def saveResponseContent(response, destination):
    """ save the chunks of data into a file
    
    :param response: the information gathered from the website
    :type response: <response>
    :param destination: the folder to place downloaded files
    :type destination: string
    """
    if response.status_code == 200:
        with open(destination, "wb") as f:
            for chunk in response:
                if chunk: 
                    f.write(chunk)
    else:
        print(response.status_code) 

# ------------------ google drive end -------------------------------

def QuickDialog(title):
    """ convenience Quick dialog for simple accept and reject functions
    
    :param title: title for the dialog
    :type title: string
    :return: the window to be created
    :rtype: QDialog
    """
    from SkinningTools.Maya import api
    myWindow = QDialog(api.get_maya_window())
    myWindow.setWindowTitle(title)
    myWindow.setLayout(nullVBoxLayout())
    h = nullHBoxLayout()
    myWindow.layout().addLayout(h)
    btn = pushButton("Accept")
    btn.clicked.connect(myWindow.accept)
    h.addWidget(btn)
    btn = pushButton("Reject")
    btn.clicked.connect(myWindow.reject)
    h.addWidget(btn)
    return myWindow

class SimplePopupSpinBox(QDialog):
    """ spinbox delegate that is able to display as its own window
    """
    closed = pyqtSignal()

    def __init__(self, parent = None, value=0.5):
        """ the constructor

        :param parent: the parent widget for this object
        :type parent: QWidget
        :param value: the default value to display on the widget
        :type value: float
        """
        super(SimplePopupSpinBox, self).__init__(parent)
        self.setWindowFlags( Qt.Window|Qt.FramelessWindowHint )

        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.input = QDoubleSpinBox(self)
        self.input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.input.setDecimals(3)
        self.input.setRange(0, 1)
        self.input.setSingleStep(.1)
        self.input.setValue(value)
        self.input.selectAll()
        
        pos = QCursor.pos()
        self.setGeometry(pos.x()-25, pos.y()-23, 50, 23)
        self.input.editingFinished.connect(self.close)
            
        self.input.setFocus()
        self.activateWindow()
        self.exec_()
        
    def closeEvent(self, e):
        self.closed.emit()