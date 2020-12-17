# -*- coding: utf-8 -*-
"""
this file will handle everything to make sure that we have a correct package installed
these functions should only be called from the MEL file
and its only created because MEL is extremely limited

it probably needs to be moved next to the MEL file, and the only arguments necessary might be the paths, \
allthough we might be able to find that based on the current file(needs to be tested!)
what this should do:
 - check if there is already a folder named skinningtools
 - move the old folder into a backup or ask the user to delete?
 - copy contents of package over to new file
 - download extra information from google drive and unzip in correct locations

#------------------------------------------#
|         SkinningTools v5.0               |
|                                          |
|      |                           |       |
|      |           banner          |       |
|      |                           |       |
|                                          |
|               [  install   ]             | # < could also be : [overwrite] [backup previous]
|                                          |
|                                          |
|         extras:                          |
|                                          |
|  []keep old settings                     | # < copy the settings ini from previous setup to new (only use this(/make visible) when there is an older version)
|                                          |   # V  following functions are examples, need to be added based on necessity
|  []tooltip gifs                          | # <these functions should be added when necessary
|  []videos                                | # <these functions should be added when necessary
|  []help documentation                    | # <these functions should be added when necessary
|                                          |
|  [       create shelf button          ]  |
|                                          |
|                                          |
|                                          |
|                                          |
|  [##########% progress bar            ]  |
#------------------------------------------#
"""
import os, shutil, datetime

CURRENTFOLDER = os.path.dirname(__file__)

from SkinningTools.UI.qt_util import *
from SkinningTools.UI import utils
from SkinningTools.Maya import api
from maya import cmds

def checkSkinningToolsFolderExists(inScriptDir, copyOldSettings = True):
    '''check if the folder already exists, so we can ask the user what to do'''
    skinFile = os.path.join(inScriptDir, "SkinningTools")
    if not os.path.exists(skinFile):
        return
    
    myWindow = utils.QuickDialog("install conflict")
    myWindow.layout().instertWidget(0, QLabel("'Reject' if you want to delete"))
    myWindow.layout().instertWidget(0, QLabel("'Accept' if you want to backup the original"))
    myWindow.layout().instertWidget(0, QLabel("skinningtools folder already exists"))
    myWindow.exec_()

    if copyOldSettings:
        shutil.copy2(os.path.join(skinFile, "UI/settings.ini"), os.path.join(CURRENTFOLDER, "SkinningTools/UI/settings.ini"))

    if myWindow.result() == 0:
        shutil.rmtree(skinFile)
        print("removed original folder: %s"%skinFile)
    else:
        now = datetime.datetime.now( )
        versionDate = "%s%02d%02d" % (now.year, now.month, now.day)
        backup = os.path.join(inScriptDir, "Backup_%s"%versionDate)
        shutil.move(skinFile, backup)
        print("backed up folder to: %s"%backup)


def moveFolder( source = '', dest = ''):
    """move the current folder to the right location """
    shutil.move(source, dest)

def downloadExtraFiles(currentSkinningFolder):
    """ download the package, we need to make sure it also unpacks itself!
    this could be necessary and handy for multiple files
    currently we download a zip, maybe downloading individual gifs is slower but allows for more transparency on what is going on (progressbar?)

    we only need the download id and the place to put it
    """
    tooltip = os.path.join(currentSkinningFolder, "Maya/toolTips")
    if not os.path.exists(tooltip):
        os.makedirs(tooltip)
    toFolder = os.path.join(currentSkinningFolder, "Maya/toolTips/toolTips.7z")  #< lets make sure this is placed correctly when the time comes
    if not os.path.exists(toFolder):
        with open(toFolder, 'w'): pass
    print("gdrive install to folder: %s"%toFolder)
    # changed id based on what needs to be downlaoded, we can now acces elements based on what file they need to represent
    files = {
            "testFile.7z" : "https://drive.google.com/file/d/1owj0sLVrNjK3uvBQqBcoIK2Ty-XyUPBx/view?usp=sharing"
    }
    
    utils.gDriveDownload(files, toFolder)


def doFunction(testing = True):
    """use this function to gather all the data necessary that is to be moved"""
    currentMaya = cmds.about(v=1)
    if testing:
        scriptDir =  cmds.internalVar(userScriptDir=1) #< move to a local path in maya for testing purposes
    else:
        scriptDir =  cmds.internalVar(userScriptDir=1).replace("%s/"%currentMaya, "/")
    print("trying to place the file in: %s"%scriptDir)
    checkSkinningToolsFolderExists(scriptDir)
    """ removed the following as its not working yet and not necessary for the first few builds"""
    # downloadExtraFiles(os.path.join(CURRENTFOLDER, "SkinningTools"))
    moveFolder(os.path.join(CURRENTFOLDER, "SkinningTools"), os.path.join(scriptDir, "SkinningTools"))
