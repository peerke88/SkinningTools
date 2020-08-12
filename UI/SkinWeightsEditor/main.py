# -*- coding: utf-8 -*-

import re
from maya import cmds

from ..qtUtil import *

from skinningTool.SkinWeightsEditor import widget
from skinningTool.SkinWeightsEditor import model
from skinningTool.skinningTools     import SkinningTools

class SkinWeightsEditor(QWidget):
    def __init__(self, *args):
        super(SkinWeightsEditor, self).__init__(*args)
        self.__model = model.SkinWeightsProxyModel(model.SkinWeightsModel(None))
        self.__widget = widget.SkinWeightsWidget(self.__model)
        self.__scriptJob = None

        l = QGridLayout()
        self.setLayout(l)

        self.liveBtn = QPushButton('Make live')
        self.refreshBtn = QPushButton('Refresh')
        self.hideZero = QCheckBox('Hide zero columns')
        self.__hideLocked = QCheckBox('Hide locked columns')
        self.__meshLabel = QLabel('')

        l1 = QHBoxLayout()
        
        l1.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        l1.addWidget(self.hideZero)
        # l1.addWidget(self.__hideLocked)
        l.addWidget(self.__meshLabel, 0, 0)
        l.addLayout(l1, 0, 1)
        l.addWidget(self.__widget, 1, 0, 1, 2)
        l.addWidget(self.refreshBtn, 2, 0)
        l.addWidget(self.liveBtn, 2, 1)

        self.liveBtn.setCheckable(True)
        self.liveBtn.clicked.connect(self.setLive)
        self.refreshBtn.clicked.connect(self._refresh)
        self.hideZero.toggled.connect(self.setHideZeroColumns)
        self.__hideLocked.toggled.connect(self.setHideLockedColumns)

        self.hideZero.setChecked(True)
        self._refresh()

    def __del__(self):
        if self.__scriptJob is not None:
            cmds.scriptJob(kill=self.__scriptJob, force=True)

    def __setLive(self, state=True):
        # alter UI
        if state:
            self.liveBtn.setStyleSheet('background-color: rgb(255, 0, 0);')
        else:
            self.liveBtn.setStyleSheet('')

        # alter state
        if self.__scriptJob is not None:
            if state == False:
                cmds.scriptJob(kill=self.__scriptJob, force=True)
                self.__scriptJob = None
            return
        if state == True:
            self.__scriptJob = cmds.scriptJob(e=('SelectionChanged', self._refresh))

    def getScriptJob(self):
        return self.__scriptJob

    def __selectedVertexIds(self, mesh):
        vertices = SkinningTools().convertToVertexList(cmds.ls(sl=True, l=True))
        allVtx=  SkinningTools().convertToVertexList(mesh)
        self.__model.setVertList(allVtx) 
        if len(vertices) != len(allVtx):
            ids = []
            for vtx in vertices:
                vtxNumber = allVtx.index(vtx)
                ids.append(vtxNumber)
            return ids
        return None

    def __selectedMeshes(self):
        m = []
        try:
        	#added to try except statment as maya older then 2016 do not allow listrelatives on empty list
            m = cmds.listRelatives(cmds.ls(sl=True, l=True, o=True, type='transform') or [], c=True, f=True) or []
        except:
            pass
        m.extend(cmds.ls(sl=True, l=True, o=True) or [])
        skinnedMeshes = []
        for i in cmds.ls(type = "skinCluster"):
            skinnedMeshes.extend(cmds.ls(cmds.skinCluster(i, q=True, g=True) or [], l=True))

        return list(set(m) & set(skinnedMeshes))

    def setHideZeroColumns(self, state):
        self.__model.setHideZeroColumns(state)
        self.__widget._view.repaint()
        self.__widget._view.updateGeometry()

    def setHideLockedColumns(self, state):
        self.__model.setHideLockedColumns(state)
        self.__widget._view.repaint()
        self.__widget._view.updateGeometry()

    
    def setLive(self, state=True):
        # alter UI
        self.__setLive(self.liveBtn.isChecked())

    def _refresh(self):
        mesh = self.__selectedMeshes()
        if not mesh:
            self.__model.setGeometry(None)
            self.__widget._view.repaint()
            self.__widget._view.updateGeometry()
            return
       
        self.__model.setGeometry(mesh[0])
        self.__meshLabel.setText(str(mesh[0].split('|')[-1]))
        ids = self.__selectedVertexIds(mesh)
        self.__model.setVisibleRows(ids)

        self.__model.setHideZeroColumns(self.hideZero.isChecked())
        self.__widget._view.repaint()
        self.__widget._view.updateGeometry()
