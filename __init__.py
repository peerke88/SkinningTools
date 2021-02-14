# -*- coding: utf-8 -*-
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
import os
from SkinningTools.UI import SkinningToolsUI

def tool():
    _settings = os.path.join(os.path.dirname(__file__), "UI/settings.ini")
    global skinToolWindow
    skinToolWindow = SkinningToolsUI.showUI(not os.path.exists(_settings))
    