"""
Makes python 2 behave more like python 3.
Ideally we import this globally so all our python 2 interpreters will assist in spotting errors early.
"""
# future imports are harmless if they implement behaviour that already exists in the current interpreter version
from __future__ import absolute_import, division, print_function
import sys
from collections import OrderedDict

if sys.version_info.major == 2:
    # Override dict and make items() behave like iteritems() to retain performance
    class dict(dict):
        def items(self):
            return super(dict, self).iteritems()

        def keys(self):
            return super(dict, self).iterkeys()

        def values(self):
            return super(dict, self).itervalues()

    class OrderedDict(OrderedDict):
        def items(self):
            return super(OrderedDict, self).iteritems()

        def keys(self):
            return super(OrderedDict, self).iterkeys()

        def values(self):
            return super(OrderedDict, self).itervalues()


    # Override range with xrange to mimic python3's range
    range = xrange
else:
	unicode = str
	long = int
	from importlib import reload

try:
    from typing import *
    T = TypeVar('T')
except:
    pass