# -*- coding: utf-8 -*-
# Copyright (c)
#
# Mio Zwickl
# Website: https://www.artstation.com/ikitamonday
#
# Rodolphe Vaillant
# Website: http://rodolphe-vaillant.fr/
#
# Trevor van Hoof
# Website: http://www.trevorius.com
#
# Jan Pijpers
# Website: http://www.janpijpers.com/
#
# Perry Leijten
# Website: http://www.perryleijten.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# --------------------------------------------------------------------------------------
import os
from SkinningTools.UI import SkinningToolsUI


def tool():
    _settings = os.path.join(os.path.dirname(__file__), "UI/settings.ini")
    global skinToolWindow
    skinToolWindow = SkinningToolsUI.showUI(not os.path.exists(_settings))
