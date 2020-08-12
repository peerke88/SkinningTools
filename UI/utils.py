import re
from .qt_util import *

def buttonsToAttach(name, command,*args):
    button = QPushButton()
    
    button.setText (name)
    button.setObjectName (name)
    
    button.clicked.connect(command)
    button.setMinimumHeight(23)
    return button


def toolButton(pixmap = '', orientation = 0 ):
    btn = QToolButton()
    if isinstance(pixmap, str):
        pixmap = QPixmap(pixmap)
    if orientation != 0:
        transform = QTransform().rotate(orientation, Qt.ZAxis)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
    btn.setIcon( QIcon(pixmap) )
    btn.setFocusPolicy(Qt.NoFocus)
    btn.setStyleSheet('border: 0px;')
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
        names = [ n for n in names if n.startswith(text) ]
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