# -*- coding: utf-8 -*-
from functools import partial
from SkinningTools.Maya import api
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *

# @todo:
# currently searching by string name (easiest)
# add following options:
# search by closest in worldspace
# search by hierarchy? index?
# search by label?

class RemapDialog(QDialog):
    def __init__(self, leftside, rightSide, parent=None):
        super(RemapDialog, self).__init__(parent)
        self.setLayout(nullVBoxLayout())

        self.leftSideList = leftside
        self.rightSideList = rightSide

        self.connectionDict={}
        self.__icons = {}
        self.__iconInfo = { "correct" :QPixmap(":/rvGreenChannel.png"), 
                            "warning" :QPixmap(":/RS_WarningOldCollection.png"),
                            "warningFixed" :QPixmap(":/caution.png"),
                            "error"   :QPixmap(":/SP_MessageBoxCritical.png")}
        
        self.view = QScrollArea()
        self.view.setWidgetResizable(1)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.frame = QFrame()
        self.view.setWidget(self.view.frame)
        self.view.frame.setLayout(nullGridLayout())
        self.layout().addWidget(self.view)

        self.__buildUI()   


    def __buildUI(self):
        _layout = self.view.frame.layout()
        for i, left in enumerate(self.leftSideList):
            _layout.addWidget(QLabel("%i:"%i), i, 0)
            _layout.addWidget(QLabel(left), i, 1)

            menu = QComboBox()
            menu.addItems(self.rightSideList)
            getclosest = similarString(left, self.rightSideList)
            self.connectionDict[i] = getclosest
            icon = "warning"
            if getclosest is None:
                icon = "error"
            if getclosest == left:
                icon = "correct"

            _icon = QLabel()
            _icon.setPixmap(self.__iconInfo[icon])
            self.__icons[i] = icon
            index = self.rightSideList.index(getclosest)
            menu.setCurrentIndex(index)
            menu.currentIndexChanged.connect(partial(self.__changeConn, i, _icon))
            _layout.addWidget(menu, i, 3)
            _layout.addWidget(_icon, i, 2)

    def __changeConn(self, index, iconWidget, newIndex):
        newConn = self.rightSideList[newIndex]
        icon = "warningFixed"
        if self.leftSideList[index] in newConn :
            icon = "correct"

        iconWidget.setPixmap(self.__iconInfo[icon])
        self.__icons[index] = icon
        self.connectionDict[index] = newConn

    # returns a map from original joint to new joint!
    def getConnectionInfo(self):
        if "error" in self.__icons.values():
            cmds.warning("not all joints propperly remapped!")
        
        rMap = {}
        for key, value in self.connectionDict.iteritems():
            if self.__icons[key] == "error":
                rMap[self.leftSideList[key]] = None
                continue
            rMap[self.leftSideList[key]] = value

        return rMap


def showTest():
    window_name = 'RemapDialog'
    mainWindow = api.get_maya_window()

    if mainWindow:
        for child in mainWindow.children():
            if child.objectName() == window_name:
                child.close()
                child.deleteLater()
    _left = ['root', 'C_Spine_0', 'C_Spine_1', 'C_Spine_2', 'C_Spine_3', 'C_Spine_4', 'C_Spine_5', 'C_Spine_6', 'C_Neck_1', 'C_Neck_2', 'C_Neck_3', 'C_Neck_4', 'C_Head', 'C_HeadEnd', 'C_HairTail', 'C_HairTail_0', 'C_HairTail_1', 'C_HairTail_2', 'C_HairTail_3', 'C_HairTail_4', 'C_HairTail_5', 'C_HairTail_6', 'C_HairTail_7', 'C_HairTail_8', 'C_HairTail_9', 'C_HairTail_10', 'C_HairTail_11', 'R_Eye_0', 'R_Eye_1', 'R_Eye_2', 'R_DnLid_0', 'R_DnLid_1', 'R_DnLid_2', 'R_DnLid_3', 'R_DnLid_4', 'R_UpLid_0', 'R_UpLid_1', 'R_UpLid_2', 'R_UpLid_3', 'R_UpLid_4', 'L_Eye_0', 'L_Eye_1', 'L_Eye_2', 'L_DnLid_0', 'L_DnLid_1', 'L_DnLid_2', 'L_DnLid_3', 'L_DnLid_4', 'L_UpLid_0', 'L_UpLid_1', 'L_UpLid_2', 'L_UpLid_3', 'L_UpLid_4', 'R_EyeBrow_0', 'R_EyeBrow_1', 'R_EyeBrow_2', 'R_EyeBrow_3', 'L_EyeBrow_0', 'L_EyeBrow_1', 'L_EyeBrow_2', 'L_EyeBrow_3', 'C_Jaw_0', 'C_Jaw_1', 'C_Jaw_2', 'R_DnLip', 'C_DnLip', 'L_DnLip', 'C_Tongue_0', 'C_Tongue_1', 'C_Tongue_2', 'C_Tongue_3', 'C_Tongue_4', 'C_DnTeeth', 'L_Ear_0', 'L_Ear_1', 'L_Ear_2', 'R_Ear_0', 'R_Ear_1', 'R_Ear_2', 'C_Nose_0', 'C_Nose_1', 'L_Nose', 'R_Nose', 'C_UpLip', 'L_UpLip', 'L_Lip', 'R_UpLip', 'R_Lip', 'L_Cheek', 'R_Cheek', 'C_Hair_0', 'C_Hair_1', 'C_Hair_2', 'C_Hair_3', 'C_Hair_4', 'L_HairA_0', 'L_HairA_1', 'L_HairA_2', 'L_HairA_3', 'L_HairA_4', 'L_HairA_5', 'L_HairA_6', 'L_HairA_00', 'HairA_01', 'HairA_02', 'HairA_03', 'HairA_04', 'C_Hair_00', 'Hair_01', 'Hair_02', 'Hair_03', 'Hair_04', 'Hair_05', 'L_HairB_0', 'L_HairB_1', 'L_HairB_2', 'L_HairB_3', 'L_HairB_4', 'L_HairB_5', 'L_HairB_00', 'HairB_01', 'HairB_02', 'HairB_03', 'L_HairC_0', 'L_HairC_1', 'L_HairC_2', 'L_HairC_3', 'L_HairC_4', 'L_HairC_5', 'L_HairC_6', 'L_HairC_00', 'HairC_01', 'HairC_02', 'HairC_03', 'HairC_04', 'R_HairA_0', 'R_HairA_1', 'R_HairA_2', 'R_HairA_3', 'R_HairA_4', 'R_HairA_5', 'R_HairA_00', 'R_HairA_01', 'R_HairA_02', 'R_HairA_03', 'R_HairA_04', 'R_HairB_0', 'R_HairB_1', 'R_HairB_2', 'R_HairB_3', 'R_HairB_4', 'R_HairB_5', 'R_HairB_6', 'R_HairC_0', 'R_HairC_1', 'R_HairC_2', 'R_HairC_3', 'R_HairC_4', 'R_HairC_5', 'R_HairC_00', 'R_HairC_01', 'R_HairC_02', 'L_Lip1', 'R_Lip1', 'C_UpTeeth', 'L_Clavicle', 'L_Shoulder', 'L_Elbow', 'L_Wrist', 'L_Pinky_0', 'L_Pinky_1', 'L_Pinky_2', 'L_Pinky_3', 'L_PinkyEnd', 'L_Middle_0', 'L_Middle_1', 'L_Middle_2', 'L_Middle_3', 'L_MiddleEnd', 'L_Index_0', 'L_Index_1', 'L_Index_2', 'L_Index_3', 'L_IndexEnd', 'L_Thumb_0', 'L_Thumb_1', 'L_Thumb_2', 'L_ThumbEnd', 'L_Ring_0', 'L_Ring_1', 'L_Ring_2', 'L_Ring_3', 'L_RingEnd', 'L_WristRoll_1', 'L_WristRoll_2', 'L_WristRollEnd', 'L_ElbowPush', 'L_ShoulderRoll_1', 'L_ShoulderRoll_2', 'L_ShoulderRollEnd', 'R_Clavicle', 'R_Shoulder', 'R_Elbow', 'R_Wrist', 'R_Pinky_0', 'R_Pinky_1', 'R_Pinky_2', 'R_Pinky_3', 'R_PinkyEnd', 'R_Middle_0', 'R_Middle_1', 'R_Middle_2', 'R_Middle_3', 'R_MiddleEnd', 'R_Index_0', 'R_Index_1', 'R_Index_2', 'R_Index_3', 'R_IndexEnd', 'R_Thumb_0', 'R_Thumb_1', 'R_Thumb_2', 'R_ThumbEnd', 'R_Ring_0', 'R_Ring_1', 'R_Ring_2', 'R_Ring_3', 'R_RingEnd', 'R_WristRoll_1', 'R_WristRoll_2', 'R_WristRollEnd', 'R_ElbowPush', 'R_ShoulderRoll_1', 'R_ShoulderRoll_2', 'R_ShoulderRollEnd', 'C_Hood', 'L_Hood_1', 'L_Hood_2', 'L_Hood_3', 'L_Hood_4', 'R_Hood_1', 'R_Hood_2', 'R_Hood_3', 'R_Hood_4', 'C_Zipper_0', 'C_Zipper_1', 'L_Hip', 'L_Knee', 'L_Ankle', 'L_Ball', 'L_ToeEnd', 'L_ShoeTongue_0', 'L_ShoeTongue_1', 'L_KneePush', 'L_KneeRoll_1', 'L_KneeRoll_2', 'L_KneeRoll_3', 'L_KneeRollEnd', 'L_HipRoll_1', 'L_HipRoll_2', 'L_HipRoll_3', 'L_HipRollEnd', 'R_Hip', 'R_Knee', 'R_Ankle', 'R_Ball', 'R_ToeEnd', 'R_ShoeTongue_0', 'R_ShoeTongue_1', 'R_KneePush', 'R_KneeRoll_1', 'R_KneeRoll_2', 'R_KneeRoll_3', 'R_KneeRollEnd', 'R_HipRoll_1', 'R_HipRoll_2', 'R_HipRoll_3', 'R_HipRollEnd']
    _right = ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck', 'Head', 'HeadTop_End', 'LeftEye', 'RightEye', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'LeftHandThumb4', 'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandIndex4', 'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandMiddle4', 'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4', 'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand', 'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4', 'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandRing4', 'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandMiddle4', 'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4', 'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumb4', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'LeftToe_End', 'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase', 'RightToe_End']

    window = RemapDialog(_left, _right, mainWindow)
    window.setObjectName(window_name)
    window.setWindowTitle(window_name)
    window.show()

    return window


