import sys
import os
from maya import cmds

from SkinningTools.Maya.interface import getInterfaceDir
from UI import SkinningToolsUI

DEFAULT_RELOAD_PACKAGES = ['SkinningTools']

'''
from SkinningTools import reloader
reload(reloader)
reloader.unload()
'''
def unload(silent=True, packages=None):
    '''
    performs unloading.
        * silent flag specifies if utility should print the unloaded modules
        * packages: array of packages to unload. specify None to use
          defaults (DEFAULT_RELOAD_PACKAGES variable)

    '''

    if packages is None:
        packages = DEFAULT_RELOAD_PACKAGES

    reload(SkinningToolsUI)
    SkinningToolsUI.closeSkinningToolsMainWindow()

    cmds.file(force=True, new=True)
    p1_name = os.path.join(getInterfaceDir(), os.path.join("plugin", "averageWeightPlugin.py"))
    p2_name = os.path.join(getInterfaceDir(), os.path.join("plugin", "SkinEditPlugin.py"))

    if cmds.pluginInfo(p1_name, q=True, loaded=True):
        p1_name = cmds.pluginInfo(p1_name, query=True, name=True)
        cmds.unloadPlugin(cmds.pluginInfo(p1_name, query=True, name=True))

    if cmds.pluginInfo(p2_name, q=True, loaded=True):
        p2_name = cmds.pluginInfo(p2_name, query=True, name=True)
        cmds.unloadPlugin(cmds.pluginInfo(p2_name, query=True, name=True))

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


