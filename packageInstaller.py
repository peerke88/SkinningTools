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
|                                          |   # V  following functions are examples, need to be added based on necessity
|  []tooltip gifs                          | # <these functions should be added when necessary
|  []videos                                | # <these functions should be added when necessary
|  []help documentation                    | # <these functions should be added when necessary
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

def checkSkinningToolsFolderExists(inScriptDir):
    '''check if the folder already exists, so we can ask the user what to do'''
    skinFile = os.path.join(inScriptDir, "SkinningTools")
    if not os.path.exists(skinFile):
        return

    myWindow = QDialog(api.get_maya_window())
    myWindow.setWindowTitle("install conflict")
    myWindow.setLayout(QVBoxLayout())
    myWindow.layout().addWidget(QLabel("skinningtools folder already exists"))
    myWindow.layout().addWidget(QLabel("'Accept' if you want to backup the original"))
    myWindow.layout().addWidget(QLabel("'Reject' if you want to delete"))
    h = QHBoxLayout()
    myWindow.layout().addLayout(h)
    btn = QPushButton("Accept")
    btn.clicked.connect(myWindow.accept)
    h.addWidget(btn)
    btn = QPushButton("Reject")
    btn.clicked.connect(myWindow.reject)
    h.addWidget(btn)
    myWindow.exec_()

    if myWindow.result() == 0:
        shutil.rmtree(skinFile)
        print "removed original folder: %s"%skinFile
    else:
        now = datetime.datetime.now( )
        versionDate = "%s%02d%02d" % (now.year, now.month, now.day)
        backup = os.path.join(inScriptDir, "Backup_%s"%versionDate)
        shutil.move(skinFile, backup)
        print "backed up folder to: %s"%backup


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
    print "gdrive install to folder: %s"%toFolder
    # change id based on what needs to be downlaoded
    id  = "1owj0sLVrNjK3uvBQqBcoIK2Ty-XyUPBx" #< pointer to the old gif zip
    utils.gDownload(id, toFolder)

def doFunction(testing = True):
    """use this function to gather all the data necessary that is to be moved"""
    currentMaya = cmds.about(v=1)
    if testing:
        scriptDir =  cmds.internalVar(userScriptDir=1) #< move to a local path in maya for testing purposes
    else:
        scriptDir =  cmds.internalVar(userScriptDir=1).replace("%s/"%currentMaya, "/")
    print "trying to place the file in: %s"%scriptDir
    checkSkinningToolsFolderExists(scriptDir)
    moveFolder(os.path.join(CURRENTFOLDER, "SkinningTools"), os.path.join(scriptDir, "SkinningTools"))
    # downloadExtraFiles(os.path.join(scriptDir, "SkinningTools"))