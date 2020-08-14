# -*- coding: utf-8 -*-
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.SkinWeightsEditor import widget
from SkinningTools.UI.SkinWeightsEditor import model


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
            api.disconnectCallback(self.__scriptJob)
            self.__scriptJob = None

    def __setLive(self, state=True):
        # alter UI
        if state:
            self.liveBtn.setStyleSheet('background-color: rgb(255, 0, 0);')
        else:
            self.liveBtn.setStyleSheet('')

        # alter state
        if self.__scriptJob is not None:
            if not state:
                api.disconnectCallback(self.__scriptJob)
                self.__scriptJob = None
            return
        if state:
            self.__scriptJob = api.connectSelectionChangedCallback(self._refresh)

    def getScriptJob(self):
        return self.__scriptJob

    def __selectedVertexIds(self, mesh):
        vertices = api.selectedObjectVertexList()
        allVtx = api.meshVertexList(mesh)
        self.__model.setVertList(allVtx)
        if len(vertices) != len(allVtx):
            ids = []
            for vtx in vertices:
                vtxNumber = allVtx.index(vtx)
                ids.append(vtxNumber)
            return ids
        return None

    @staticmethod
    def __selectedMeshes():
        return api.selectedSkinnedShapes()

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
