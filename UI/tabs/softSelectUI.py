from SkinningTools.Maya import api, interface
from SkinningTools.Maya.tools import softSelectWeight, mesh
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *

from maya import OpenMaya, cmds
from functools import partial

class AddInfluenceWidget(QWidget):
    """Widget used to add influences. Will emit the 'addInfluence' signal when
    the add button is released.

    :param parent:   
    :type parent: QWidget
    """
    addInfluence = Signal()

    def __init__(self, parent):
        super(AddInfluenceWidget, self).__init__( parent)
        
        self.setLayout(nullHBoxLayout())
        
        add = toolButton(":/setEdAddCmd.png", size = 24)
        label = QLabel("Add Influence")
        
        add.released.connect(self.addInfluence.emit)
        
        for w in [add, label]:
            self.layout().addWidget(w)
        

class FillerInfluenceWidget(QWidget):
    """Widget used to set the filler influence. 

    :param parent:   
    :type parent: QWidget
    """
    def __init__(self, parent):
        super(FillerInfluenceWidget, self).__init__(parent)
        
        self._influence = None

        self.setLayout(nullHBoxLayout())
        
        jointBtn = toolButton(":/kinJoint.png", size = 24)
        self.label = QLabel("< filler influence >")
        
        jointBtn.released.connect(self.setInfluenceFromSelection)
        
        for w in [jointBtn, self.label]:
            self.layout().addWidget(w)
        
    def _getInfluence(self):
        return self._influence
        
    def _setInfluence(self, influence):
        self._influence = influence
    
    influence = property( _getInfluence, _setInfluence)
          
    def setInfluenceFromSelection(self):
        """Get all of the joints in the current selection. If no joints are 
        selected a RuntimeError will be raised and the UI reset.
        
        :raises RuntimeError: if no joints are selected
        """
        joints = cmds.ls(sl=True, l=True, type="joint")
        
        if not joints:
            self.influence = None
            self.label.setText("< filler influence >")
            raise RuntimeError("No joint selection detected!")
            
        self.influence = joints[0]
        self.label.setText(joints[0].split("|")[-1])
  
    def contextMenuEvent(self, event): 
        menu = QMenu(self)
        influence = menu.addAction( "Select: Filler Influence",  partial( cmds.select,  self.influence ) )
        influence.setIcon(QIcon(":/customSoftSelectFalloffCurve.png"))
        influence.setEnabled(True if self.influence else False)

        menu.exec_(self.mapToGlobal(event.pos()))


class InfluenceWidget(QWidget):
    """Widget used to set the influence and soft selection. Once a new soft 
    selection is made the 'setSoftSelection' signal will be emitted.

    :param QWidget parent:   
    """
    setSoftSelection = Signal()

    def __init__(self, parent):
        super(InfluenceWidget, self).__init__(parent)
        
        self._influence = None
        self._ssActive = None
        self._ssData = {}
        self._ssSettings = {}
        
        self.setLayout(nullHBoxLayout())
        
        jointBtn = toolButton(":/kinJoint.png", size = 24)
        soft = toolButton(":/customSoftSelectFalloffCurve.png", size = 24)
        self.label = QLabel("< influence >")
        remove = toolButton(":/setEdRemoveCmd.png", size = 24)
                  
        jointBtn.released.connect(self.setInfluenceFromSelection)
        soft.released.connect(self.setSoftSelectionFromSelection)
        remove.released.connect(self.deleteLater)

        for w in [jointBtn, soft, self.label, remove]:
            self.layout().addWidget(w)


    def setInfluenceFromSelection(self):
        """Get all of the joints in the current selection. If no joints are 
        selected a RuntimeError will be raised and the UI reset.
        
        :raises RuntimeError: if no joints are selected
        """
        joints = cmds.ls(sl=True, l=True, type="joint")
        print joints
        if not joints:
            self.influence = None
            self.label.setText("< influence >")
            raise RuntimeError("No joint selection detected!")
            
        self.influence = joints[0]
        self.label.setText(joints[0].split("|")[-1])
    
    def _getInfluence(self):
        return self._influence
        
    def _setInfluence(self, influence):
        self._influence = influence
    
    def _getSsActive(self):
        return self._ssActive
        
    def _setSsActive(self, value):
        self._ssActive = value
    
    def _getSsSettings(self):
        return self._ssSettings
        
    def _setSsSettings(self, value):
        self._ssSettings = value

    def _getSsData(self):
        return self._ssData
        
    def _SetSsData(self, value):
        self._ssData = value
    
    influence = property(_getInfluence, _setInfluence)
    ssActive  =property(_getSsActive, _setSsActive)
    ssSettings  =property(_getSsSettings, _setSsSettings)
    ssData  =property(_getSsData, _SetSsData)
    

    def setSoftSelectionFromSelection(self):
        """ Get the current soft selection. If no soft selection is made a 
        RuntimeError will be raised.
        
        :raises RuntimeError: if no soft selection is made
        """
        self.ssActive, self.ssData = mesh.softSelection()
        self.setSoftSelection.emit()
        
        # reset values if no soft selection
        if not self.ssData:            
            self.ssActive = None
            self.ssData = {}
            self.ssSettings = {}
            raise RuntimeError("No soft selection detected!")
        
        self.ssSettings = { "ssc": cmds.softSelect(query=True, ssc=True),
                            "ssf": cmds.softSelect(query=True, ssf=True),
                            "ssd": cmds.softSelect(query=True, ssd=True)}
        
    def selectSoftSelection(self):
        """Set the stored soft selection.
        """
        cmds.softSelect(sse=1, **self.ssSettings) 
        OpenMaya.MGlobal.setActiveSelectionList(self.ssActive)
        
    def contextMenuEvent(self, event):    
        menu = QMenu(self)
        influence = menu.addAction("Select: Influence", partial( cmds.select,  self.influence ) )
        influence.setIcon(QIcon(":/redSelect.png"))
        influence.setEnabled(True if self.influence else False)

        soft = menu.addAction( "Select: Soft Selection", self.selectSoftSelection )
        soft.setIcon(QIcon(":/redSelect.png"))
        soft.setEnabled(True if self.ssData else False)
        
        menu.exec_(self.mapToGlobal(event.pos()))


class SoftSelectionToWeightsWidget(QWidget):
    """Widget used to manage all of the added influences and their soft selection.
    
    :param parent:   
    :type parent: QWidget
    """
    def __init__(self, parent= None):
        super(SoftSelectionToWeightsWidget, self).__init__(parent)
        self.setWindowTitle("SoftSelWidget")           
        # self.setWindowIcon(QIcon(":/render_rampShader.png"))
    
        self.setLayout(nullVBoxLayout())
        
        title = AddInfluenceWidget(self)
        title.addInfluence.connect(self.addInfluence)
        self.layout().addWidget(title)

        scrollArea = QScrollArea(self)
        scrollArea.setWidgetResizable(True)

        self.widget = QWidget(self)
        self.lay = nullVBoxLayout(self.widget)
        self.widget.setLayout(self.lay)
        
        scrollArea.setWidget(self.widget)
        self.layout().addWidget(scrollArea)
        
        self.filler = FillerInfluenceWidget(self)
        self.lay.addWidget(self.filler)
        
        self.lay.addItem(QSpacerItem(1, 1,QSizePolicy.Minimum,QSizePolicy.Expanding))
        
        button = pushButton("skin")
        button.clicked.connect(self.skin)
        self.layout().addWidget(button)
        
    def addInfluence(self):
        """Add an new influence widget to the layout, :class:`InfluenceWidget`.
        """
        widget = InfluenceWidget(self)
        widget.setSoftSelection.connect(self.setEnableInfluence)
        
        num = self.lay.count() - 2
        self.lay.insertWidget(num, widget)
        
    def getInfluences(self):
        """Loop over all of the content of the scroll layout and yield if the
        item is an instance of :class:`InfluenceWidget`.
        
        :return: All influence widgets in the scroll layout
        :rtype: iterator
        """
        _inf = []
        for i in range(self.lay.count()-1):
            item = self.lay.itemAt(i)
            widget = item.widget()
            if isinstance(widget, InfluenceWidget):
                _inf.append(widget)
        return _inf
                
    # ------------------------------------------------------------------------
    
    def setEnableInfluence(self):
        """This function is called when a soft selection is made. All influences 
        will be checked to see if there is a mesh with no skin cluster 
        attached. If this is the case the filler joint widget 
        :class:`FillerInfluenceWidget` will be enabled.
        """
        self.filler.setEnabled(False)
        influences = self.getInfluences()
        for influence in influences:
            for inMesh in influence.ssData.keys():
                if shared.skinCluster(inMesh, True):
                    self.filler.setEnabled(True)
                    return
                
    def skin(self):
        """This function is called when the skin button is released. All of the
        influences sorted and the mesh skin weights updated. As this can be 
        a time consuming process a progress bar will be updated with every 
        mesh that gets updated.
        """
        data = {}
        infs = []
        
        influences = self.getInfluences()
        for influence in influences:
            inf = influence.influence
            soft = influence.ssData
            
            if not inf or not soft:
                continue
                
            infs.append(inf)
            
            for curMesh, weights in soft.iteritems():
                if curMesh not in data.keys():
                    data[curMesh] = {}
                    
                for index, w in weights.iteritems():
                    if index not in data[curMesh].keys():
                        data[curMesh][index] = {}
                        
                    if inf not in data[curMesh][index].keys():
                        data[curMesh][index][inf] = 0
                        
                    data[curMesh][index][inf] += w

        for curMesh, meshData in data.iteritems():
            filler = self.filler.influence
            if not shared.skinCluster(inMesh, True) and not filler:
                print "No Filler Influence found for mesh: {0}".format( curMesh )
                continue

            softSelectWeight.setSkinWeights( curMesh, meshData, infs, filler )


def testUI():
    """ test the current UI without the need of all the extra functionality
    """
    mainWindow = interface.get_maya_window()
    mwd  = QMainWindow(mainWindow)
    mwd.setWindowTitle("VertAndBoneFunction Test window")
    wdw = SoftSelectionToWeightsWidget(parent = mainWindow)
    mwd.setCentralWidget(wdw)
    mwd.show()
    return wdw