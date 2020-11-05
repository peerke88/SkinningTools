import sys
import os
from maya import cmds

from SkinningTools.Maya.interface import getInterfaceDir
from UI import SkinningToolsUI

DEFAULT_RELOAD_PACKAGES = ['SkinningTools']

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
    except Exception,err:
        print("failed to close window")
    
    if newScene:
        cmds.file(force=True, new=True)
    p1_name = os.path.join(getInterfaceDir(), os.path.join("plugin", "averageWeightPlugin.py"))
    p2_name = os.path.join(getInterfaceDir(), os.path.join("plugin", "SkinEditPlugin.py"))

    try:
        if cmds.pluginInfo(p1_name, q=True, loaded=True):
            p1_name = cmds.pluginInfo(p1_name, query=True, name=True)
            cmds.unloadPlugin(cmds.pluginInfo(p1_name, query=True, name=True))
    except Exception,err:
        print("failed to unload averageWeightPlugin.py")

    try:
        if cmds.pluginInfo(p2_name, q=True, loaded=True):
            p2_name = cmds.pluginInfo(p2_name, query=True, name=True)
            cmds.unloadPlugin(cmds.pluginInfo(p2_name, query=True, name=True))
    except Exception,err:
        print("failed to unload SkinEditPlugin.py")

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
        except Exception,err:
            print("failed to unload "+i)
            pass


