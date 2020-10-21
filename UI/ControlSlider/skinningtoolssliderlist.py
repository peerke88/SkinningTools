# -*- coding: utf-8 -*-
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.ControlSlider.vertexinfluenceeditor import VertexInfluenceEditor


class SkinningToolsSliderList(QWidget):
    def __init__(self, parent=None):
        super(SkinningToolsSliderList, self).__init__(parent=None)
        self.setLayout(QVBoxLayout())
        # self.__doMultiAtOnce = True
        
        self.update()

    # def setMultiAtOnce(self, inValue):
    #     self.__doMultiAtOnce = inValue
    #     self.update()

    # def getMultiAtOnce(self):
    #     return self.__doMultiAtOnce

    # multi = property(getMultiAtOnce, setMultiAtOnce)

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

        #@todo: always live?? check with component editor!
        # use 1 view for many vertices if requested, 
        # show multiple vertices if this setting is off
        # truncate based on spinbox?

        self.skinClusterCache = {}
        mesh = vertices[0][0]
        vertexList = vertices[0][1]
        if len(vertexList) > 1:
            vertexList = [vertex for mesh, vertex in vertices]
            #@todo: double check that all vertices are from the same mesh!
        
        self.__addSliders(mesh, vertexList)

        self.layout().addStretch(1)

        api.selectVertices(vertices)

        if self.isVisible():
            self.finalize()

    def __addSliders(self, mesh, vertex):    
        if mesh in self.skinClusterCache:
            skinCluster, skinBones = self.skinClusterCache[mesh]
        else:
            skinCluster = api.skinClusterForObject(mesh)
            if not skinCluster:
                return
            skinBones = api.skinClusterInfluences(skinCluster)
            self.skinClusterCache[mesh] = skinCluster, skinBones

        if type(vertex) in [list, tuple]:
            weights = api.getSingleVertexWeights(skinCluster, vertex[0])
            amount = len(vertex)
            for vert in vertex[1:]:
                nWeights = api.getSingleVertexWeights(skinCluster, vert)

        else:
            weights = api.getSingleVertexWeights(skinCluster, vertex)

        self.layout().addWidget(VertexInfluenceEditor(skinCluster, vertex, skinBones, weights, self))

    def showEvent(self, event):
        super(SkinningToolsSliderList, self).showEvent(event)
        self.finalize()

    def finalize(self):
        counter = 0
        while True:
            item = self.layout().itemAt(counter)
            counter += 1
            if not item:
                return
            widget = item.widget()
            if not widget:
                continue
            widget.finalize()
