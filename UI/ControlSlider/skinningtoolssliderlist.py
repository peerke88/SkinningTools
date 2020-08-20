# -*- coding: utf-8 -*-
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.ControlSlider.vertexinfluenceeditor import VertexInfluenceEditor


class SkinningToolsSliderList(QWidget):
    def __init__(self):
        super(SkinningToolsSliderList, self).__init__()
        self.setLayout(QVBoxLayout())
        self.update()

    def update(self):
        # clear
        while True:
            child = self.layout().takeAt(0)
            if not child:
                break
            widget = child.widget()
            if not widget:
                continue
            widget.deleteLater()

        # get long selection
        vertices = api.selectedObjectVertexList(True)
        if not vertices:
            return

        skinClusterCache = {}
        for mesh, vertex in vertices[:20]:  # truncate the list so it will never cause a leak
            if mesh in skinClusterCache:
                skinCluster, skinBones = skinClusterCache[mesh]
            else:
                skinCluster = api.skinClusterForObject(mesh)
                if not skinCluster:
                    return
                skinBones = api.skinClusterInfluences(skinCluster)
                skinClusterCache[mesh] = skinCluster, skinBones

            weights = api.getSingleVertexWeights(skinCluster, vertex)

            self.layout().addWidget(VertexInfluenceEditor(skinCluster, vertex, skinBones, weights))

        self.layout().addStretch(1)

        api.selectVertices(vertices)

        if self.isVisible():
            self.finalize()

    def showEvent(self, event):
        super(SkinningToolsSliderList, self).showEvent(event)
        self.finalize()

    def finalize(self):
        """
        This function hides all unused influences
        Doing this before the widget is visible
        creates bugs in the minimumHeight of the
        widget when it is set to visible.
        """
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
