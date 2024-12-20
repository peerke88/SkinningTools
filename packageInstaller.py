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
|  []tooltip gifs                          | # <these functions should be added when necessary
|                                          |
|  [       create shelf button          ]  |
|                                          |
|                                          |
|   install info                           |
|                                          |
|  [##########% progress bar            ]  |
#------------------------------------------#


:todo:
unzip the downloaded zip files (use zip instead of 7z as thats easier to use with python)

"""
import os, shutil, datetime, tempfile, zipfile, warnings, sys

CURRENTFOLDER = os.path.dirname(__file__)

from SkinningTools.UI.qt_util import *
from SkinningTools.py23 import * 
from SkinningTools.UI import utils
from SkinningTools.Maya import api 
from maya import cmds

import base64

__VERSION__ = "5.0.20240512"

class InstallWindow(QDialog):
    def __init__(self,scriptDir, parent = None):
        super(InstallWindow, self).__init__(parent)

        self.setWindowTitle("install SkinningTools %s"%__VERSION__)
        
        self.__scriptDir = scriptDir
        self.__skinFile = os.path.normpath(os.path.join(self.__scriptDir, "SkinningTools"))
        self.__exists = os.path.exists(self.__skinFile )
        self.__oldSettings =  os.path.normpath(os.path.join(self.__skinFile, "UI/settings.ini"))
        self.__oldEnhToolTip = os.path.normpath(os.path.join(self.__skinFile, "Maya/tooltips"))
        
        # ---- simple banner
        self.setLayout(utils.nullVBoxLayout(size = 1))

        inString = ['iVBORw0KGgoAAAANSUhEUgAAAkEAAACUCAIAAAAbCmpPAAAACXBIWXMAAAsTAAALEwEAmpwYAAAGtmlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgKFdpbmRvd3MpIiB4bXA6Q3JlYXRlRGF0ZT0iMjAyMC0xMi0yMVQxNjoxNTowMyswOTowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMC0xMi0yMVQxNjo0MTozMSswOTowMCIgeG1wOk1vZGlmeURhdGU9IjIwMjAtMTItMjFUMTY6NDE6MzErMDk6MDAiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6ZWMxZjM1N2UtMTZhYS1mMTQ5LTkwNzAtNmYyMGJmODZjNjRlIiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6ZjNmMzU4OWYtZDliYS0zZjRjLWJjNmEtMzk2OTQwOTFhYTE2IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6ZDIzZTRlNTEtNWYzOS1hZjQ4LTkwYTgtMDRhZDMyNDVkMWY5IiBkYzpmb3JtYXQ9ImltYWdlL3BuZyIgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIgcGhvdG9zaG9wOklDQ1Byb2ZpbGU9InNSR0IgSUVDNjE5NjYtMi4xIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpkMjNlNGU1MS01ZjM5LWFmNDgtOTBhOC0wNGFkMzI0NWQxZjkiIHN0RXZ0OndoZW49IjIwMjAtMTItMjFUMTY6MTU6MDMrMDk6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAoV2luZG93cykiLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjRmMzI5MDM0LWNmZjEtOGM0NS04MGE5LWU1M2MwYzMwOTdkYyIgc3RFdnQ6d2hlbj0iMjAyMC0xMi0yMVQxNjoxNTowMyswOTowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENDIChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZWMxZjM1N2UtMTZhYS1mMTQ5LTkwNzAtNmYyMGJmODZjNjRlIiBzdEV2dDp3aGVuPSIyMDIwLTEyLTIxVDE2OjQxOjMxKzA5OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Phts8a0AAFllSURBVHic7b15nJzH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', '.png']
        filePath = os.path.join(tempfile.gettempdir(), "img%s"%inString[-1])
        with open(filePath, "wb") as fh:
            fh.write(base64.b64decode(inString[0]))
            
        # img = utils.convertStringToImage(inString)
        lbl = utils.toolButton(filePath, size = QSize(577, 148))

        self.layout().addWidget(lbl)

        # ---- install location
        h = utils.nullHBoxLayout()
        self.layout().addLayout(h)
        self._installLine = QLineEdit(self.__scriptDir)
        self._installLine.setEnabled(False)
        folderBtn = utils.toolButton(":/SP_DirOpenIcon.png")
        folderBtn.clicked.connect(self._searchInstallLocation)

        for w in [QLabel("install location:"), self._installLine, folderBtn]:
            h.addWidget(w)

        # ---- bbasic functions when skinningtools already exist
        self.cbx = QComboBox()
        for item in ["backup", "replace"]:
            self.cbx.addItem(item)
        self.layout().addWidget(self.cbx)
        self.cbx.hide()

        self.oldSettings = QCheckBox("keep old settings?")
        if os.path.exists(self.__oldSettings):
            self.oldSettings.setChecked(True)
        self.layout().addWidget(self.oldSettings)
        self.oldSettings.hide()

        if self.__exists:
            self.cbx.show()
            self.oldSettings.show()

        # ---- this is the place where we can add extra infromation gathering options

        self.downloadChk = QCheckBox("download enhanced tooltips")
        self.downloadChk.setChecked(True)
        if os.path.exists(self.__oldEnhToolTip):
            self.downloadChk.setChecked(False)
        self.layout().addWidget(self.downloadChk)
        # ---- the installButtons

        self.layout().addItem(QSpacerItem(2,2,QSizePolicy.Minimum, QSizePolicy.Expanding))
        installBtn = utils.pushButton("install skinningtools")
        self.layout().addWidget(installBtn)
        self.progress = QProgressBar()
        self.layout().addWidget(self.progress)

        self.layout().addWidget(QLabel("use the following python code to start the tool"))
        self.layout().addWidget(QLabel("(note: maya needs to be restarted for it to work!)"))
        infoEdit = QPlainTextEdit()
        infoString = "import SkinningTools\nSkinningTools.tool()"
        infoEdit.setPlainText(infoString)
        infoEdit.setReadOnly(True)
        self.layout().addWidget(infoEdit)


        installBtn.clicked.connect(self.install)

    def _searchInstallLocation(self, *args):
        fd = QFileDialog.getExistingDirectory(self, "choose install location", self.__scriptDir )
        if fd is None or fd in ['',[]]:
            return
        self.__scriptDir = fd
        self._installLine.setText(fd)

        self.__skinFile = os.path.normpath(os.path.join(self.__scriptDir, "SkinningTools"))
        self.__exists = os.path.exists(self.__skinFile )
        if self.__exists:
            self.cbx.show()
            self.oldSettings.show()
        else:
            self.cbx.hide()
            self.oldSettings.hide()
        self.__oldSettings =  os.path.normpath(os.path.join(self.__skinFile, "UI/settings.ini"))
        self.__oldEnhToolTip = os.path.normpath(os.path.join(self.__skinFile, "Maya/tooltips"))

    def install(self):
        utils.setProgress(0, self.progress, "start installing the skinningtools")
        if self.__exists:
            # ---- copy old settings file 
            if os.path.exists(self.__oldSettings) and self.oldSettings.isChecked():
                newIni = os.path.normpath(os.path.join(CURRENTFOLDER, "SkinningTools/UI/settings.ini"))
                with open(newIni, "w") as fh: pass
                shutil.copy2(self.__oldSettings, newIni)
                utils.setProgress(10, self.progress, "copied old settings")
            
            # ---- copy or download enhanced tooltips
            if not self.downloadChk.isChecked():
                newETT = os.path.normpath(os.path.join(CURRENTFOLDER, "SkinningTools/Maya/tooltips"))
                if os.path.exists(self.__oldEnhToolTip):
                    shutil.move(self.__oldEnhToolTip, newETT)

            # ---- check what to do with previous version
            if self.cbx.currentIndex() == 1:
                shutil.rmtree(self.__skinFile)
                utils.setProgress(30, self.progress, "removed original folder")
            else:
                now = datetime.datetime.now( )
                versionDate = "%s%02d%02d" % (now.year, now.month, now.day)
                backup = os.path.normpath(os.path.join(self.__scriptDir, "Backup_%s"%versionDate))
                if os.path.exists(backup):
                    print("backup already created: %s"%backup)
                else:
                    shutil.move(self.__skinFile, backup)
                    utils.setProgress(30, self.progress, "backed up folder as: Backup_%s"%versionDate)

        if self.downloadChk.isChecked():
            self.downloadExtraFiles(os.path.join(CURRENTFOLDER, "SkinningTools"))

        utils.setProgress(40, self.progress, "move skinningtools")
        shutil.move(os.path.normpath(os.path.join(CURRENTFOLDER, "SkinningTools")), os.path.normpath(os.path.join(self.__scriptDir, "SkinningTools")))
        utils.setProgress(100, self.progress, "skinningtools installed")

        self.close()


    def downloadExtraFiles(self, currentSkinningFolder):
        """ download the package, we need to make sure it also unpacks itself!
        this could be necessary and handy for multiple files
        currently we download a zip, maybe downloading individual gifs is slower but allows for more transparency on what is going on (progressbar?)

        we only need the download id and the place to put it
        """
        tooltip = os.path.join(currentSkinningFolder, "Maya/toolTips")
        if not os.path.exists(tooltip):
            os.makedirs(tooltip)
        print("gdrive install to folder: %s"%tooltip)
        # changed id based on what needs to be downlaoded, we can now acces elements based on what file they need to represent
        files = {
                "toolTips.zip" : "https://firebasestorage.googleapis.com/v0/b/skinningtoolstooltips.appspot.com/o/tooltips.zip?alt=media&token=07f5c1b1-f8c2-4f18-83ce-2ea65eee4187"
        }
        utils.setProgress(60, self.progress, "downloaded extra files")
        try:
            utils.gDriveDownload(files, tooltip, None )
            
            with zipfile.ZipFile(os.path.join(tooltip, "toolTips.zip")) as zip_ref:
                zip_ref.extractall(tooltip)
            utils.setProgress(80, self.progress, "unzipped tooltips")
        except:
            utils.setProgress(80, self.progress, "possible failure downloading tooltips")
            warnings.warn("could not download tooltips, tool will continue installing and request download later")


def doFunction(useLocalMayaFolder = True):
    """use this function to gather all the data necessary that is to be moved"""
    currentMaya = cmds.about(v=1)
    if useLocalMayaFolder:
        scriptDir =  cmds.internalVar(userScriptDir=1) #< move to a local path in maya for testing purposes
    else:
        scriptDir =  cmds.internalVar(userScriptDir=1).replace("%s/"%currentMaya, "")
    
    myWindow = InstallWindow(scriptDir,  parent = api.get_maya_window())
    myWindow.exec_()

    