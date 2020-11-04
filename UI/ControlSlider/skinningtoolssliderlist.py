# -*- coding: utf-8 -*-
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.ControlSlider.vertexinfluenceeditor import VertexInfluenceEditor


class SkinningToolsSliderList(QWidget):
    def __init__(self, parent=None):
        super(SkinningToolsSliderList, self).__init__(parent=None)
        self.setLayout(QVBoxLayout())
        self._infEditor = None
        self._showUnused = True
        self.__joints = []
        self.update()

    def clear(self):
        while True:
            child = self.layout().takeAt(0)
            if not child:
                break
            widget = child.widget()
            if not widget:
                continue
            widget.deleteLater()

    def update(self):
        self.clear()
        vertices = api.selectedObjectVertexList(True)
        if not vertices:
            return

        if len(vertices[0]) > 1:
            self.__doMultiAtOnce = True

        self.skinClusterCache = {}
        mesh = vertices[0][0]
        vertexList = vertices[0][1]
        if len(vertexList) > 1:
            vertexList = [vertex for mesh, vertex in vertices]
            #@todo: double check that all vertices are from the same mesh!
        
        self.__addSliders(mesh, vertexList)

        self.layout().addStretch(1)

        api.selectVertices(vertices)

    def __addSliders(self, mesh, vertex):    
        if mesh in self.skinClusterCache:
            skinCluster, self.__joints = self.skinClusterCache[mesh]
        else:
            skinCluster = api.skinClusterForObject(mesh)
            if not skinCluster:
                return
            self.__joints = api.skinClusterInfluences(skinCluster)
            self.skinClusterCache[mesh] = skinCluster, self.__joints

        if type(vertex) in [list, tuple]:
            weights = api.getSingleVertexWeights(skinCluster, vertex[0])
            amount = len(vertex)
            for vert in vertex[1:]:
                nWeights = api.getSingleVertexWeights(skinCluster, vert)

        else:
            weights = api.getSingleVertexWeights(skinCluster, vertex)
        self._infEditor =  VertexInfluenceEditor(skinCluster, vertex, self.__joints, weights, self)
        self._infEditor._toggleGroupBox(self._showUnused)
        self.layout().addWidget(self._infEditor)

    def showUnused(self, state):
        self._showUnused = state
        if self._infEditor is not None:
            self._infEditor._toggleGroupBox(state)

    def getJointData(self):
        return self.__joints

    def showOnlyJoints(self, inputList):
        if self._infEditor is not None:
            self._infEditor.showBones(inputList)  
        self.showUnused(self._showUnused)      

    def showEvent(self, event):
        super(SkinningToolsSliderList, self).showEvent(event)
