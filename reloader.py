import sys
import os
from maya import cmds
from py23 import *

import SkinningTools.Maya.api as api
reload(api)
import SkinningTools.UI.tabs.skinBrushes as skinBrushes
reload( skinBrushes )
import  SkinningTools.Maya.interface as interface
reload( interface )

from UI import SkinningToolsUI

DEFAULT_RELOAD_PACKAGES = ['SkinningTools']

PLUGINS = [os.path.join(interface.getInterfaceDir(), os.path.join("plugin", "averageWeightPlugin.py")),
           api.getPlugin(),
           skinBrushes.pathToSmoothBrushPlugin(),
           os.path.join(interface.getInterfaceDir(), os.path.join("plugin", "SkinEditPlugin.py")) ]

'''
Instead of closing/opening maya to reflect changes in Python code one would 
usually do: reload("modifiedPythonModule") in Maya's python console.

But sometimes you need to reload several modules, unload/reload sub-plugins.
The code below will close the main window, reload every single python module 
create a new scene to ensure no plugin data is used and re-load sub-plugins:    
    from SkinningTools import reloader
    reload(reloader)
    reloader.unload()    
'''
def unload(silent=True, packages=None, newScene = True):
    '''
    performs unloading.
        * silent flag specifies if utility should print the unloaded modules
        * packages: array of packages to unload. specify None to use
          defaults (DEFAULT_RELOAD_PACKAGES variable)

    '''

    if packages is None:
        packages = DEFAULT_RELOAD_PACKAGES

    try:
        SkinningToolsUI.closeSkinningToolsMainWindow()
    except Exception as err:
        print("failed to close window")

    if newScene:
        cmds.file(force=True, new=True)

    for path in PLUGINS:
        try:
            if cmds.pluginInfo(path, q=True, loaded=True):
                name = cmds.pluginInfo(path, query=True, name=True)
                cmds.unloadPlugin(cmds.pluginInfo(name, query=True, name=True))
        except Exception as err:
            print("failed to unload "+path)

    # construct reload list
    reloadList =[]
    for i in sys.modules.keys():
        for package in packages:
            if i.startswith(package):
                reloadList.append(i)


    # unload everything
    for i in reloadList:
        try:
            #reload(i)
            if sys.modules[i] is not None:
                del(sys.modules[i])
                if not silent:
                    print("unloaded "+i)
        except Exception as err:
            print("failed to unload "+i)
            pass


