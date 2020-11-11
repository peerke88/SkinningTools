# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.ThirdParty.kdtree import KDTree

class MeshSelector(QDialog):
    def __init__(self, inMesh='', inBB=[], meshes = {}, parent=None):
        super(JointName, self).__init__(parent)
        _current = inMesh.keys()[0]
        self.setWindowTitle("select mesh to represent %s"%_current)
        self.setLayout(nullVBoxLayout())

        nameLabel = QLabel("select mesh to be used instead of: %s"%_current, self)
        txtLabel = QLabel("mesh: ", self)
        self.combo = QComboBox(self)
        
        _curList = meshes.keys()
        self.combo.addItems( _curList )

        _closestMesh = self.getBestBasedOnBB( inMesh, meshes )
        index = _curList.index(_closestMesh)
        if index is not None:
            self.combo.setCurrentIndex(index)

        leftLayout = nullHBoxLayout()
        for w in [txtLabel, self.combo]:
            leftLayout.addWidget(w)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        for wl in [nameLabel, leftLayout, buttonBox]:
            if isinstance(wl, QLayout):
                self.layout().addLayout(wl)
                continue
            self.layout().addWidget(wl)

    def getBestBasedOnBB(currentMesh, otherMeshes):
        _current = currentMesh.keys()[0]
        _bbox = currentMesh[_current]

        minList = []
        maxList = []
        meshList = []
        for (mesh, bbox) in otherMeshes.iteritems():
            minList.append(bbox[0])
            maxList.append(bbox[1])
            meshList.append(mesh)
        closestMinimum = getClosestVector(minList, _bbox[0], 3)
        closestMaximum = getClosestVector(maxList, _bbox[1], 3)
        
        for _min in closestMinimum:
            minIndex = minList.index(_min)
            for _max in closestMaximum:
                maxIndex = maxList.index(_max)
                if minIndex == maxIndex:
                    return meshList[minIndex]
        return None

