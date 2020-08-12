# -*- coding: utf-8 -*-
# Copyright (C) 2020 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
import re

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