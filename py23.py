from __future__ import absolute_import
import sys
from collections import OrderedDict

if sys.version_info.major == 3:
    xrange = range
    OrderedDict.iteritems = OrderedDict.items
    dict.iteritems = dict.items
    unicode = str
    from io import StringIO as cStringIO
