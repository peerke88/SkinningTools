# -*- coding: utf-8 -*-

#@note:
#  this file will represent an interface between the ui and the actual commands
# this is where all the selection gets logged and the right arguments get piped through 
from maya import cmds
from SkinningTools.Maya.tools import shared, joints, mesh, skinCluster
from SkinningTools.Maya import api
from SkinningTools.UI.dialogs.jointLabel import JointLabel
from random import randint

#ensure we get ordered selection and all in long names
def getSelection():
	cmds.selectPref(tso=True)
	return cmds.ls(os=1, l=1, fl=1)

# --- maya menus ---

def mirrorSkinOptions():
    cmds.optionVar(stringValue=("mirrorSkinAxis", "YZ"))
    cmds.optionVar(intValue=("mirrorSkinWeightsSurfaceAssociationOption", 3))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption1", 3))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption2", 2))
    cmds.optionVar(intValue=("mirrorSkinWeightsInfluenceAssociationOption3", 1))
    cmds.optionVar(intValue=("mirrorSkinNormalize", 1))
    cmds.MirrorSkinWeightsOptions()


def copySkinWeightsOptions():
    cmds.optionVar(intValue=("copySkinWeightsSurfaceAssociationOption", 3))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption1", 4))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption2", 4))
    cmds.optionVar(intValue=("copySkinWeightsInfluenceAssociationOption3", 6))
    cmds.optionVar(intValue=("copySkinWeightsNormalize", 1))
    cmds.CopySkinWeightsOptions()


def uniteSkinned():
    selection = getSelection()
    cmds.polyUniteSkinned(selection, ch=0, mergeUVSets=1)


# --- dcc ---

def dccToolButtons():
    from SkinningTools.UI.utils import buttonsToAttach

    mb01 = buttonsToAttach('Smooth Bind', cmds.SmoothBindSkinOptions)
    mb02 = buttonsToAttach('Rigid Bind', cmds.RigidBindSkinOptions)
    mb03 = buttonsToAttach('Detach Skin', cmds.DetachSkinOptions)
    mb04 = buttonsToAttach('Paint Skin Weights', cmds.ArtPaintSkinWeightsToolOptions)
    mb05 = buttonsToAttach('Mirror Skin Weights', mirrorSkinOptions)
    mb06 = buttonsToAttach('Copy Skin Weights', copySkinWeightsOptions)
    mb07 = buttonsToAttach('Prune Weights', cmds.PruneSmallWeightsOptions)
    mb08 = buttonsToAttach('Combine skinned mesh', uniteSkinned)

    return [mb01, mb02, mb03, mb04, mb05, mb06, mb07, mb08]

# --- tools ---
@shared.dec_repeat
def avgVtx(useDistance=True, weightAverageWindow = None, progressBar = None):
	selection = getSelection()
	result = skinCluster.AvarageVertex(selection, useDistance, weightAverageWindow, progressBar)
	return result

@shared.dec_repeat
def copyVtx(progressBar = None):
	selection = getSelection()
	result = skinCluster.Copy2MultVertex(selection, selection[-1], progressBar)
	return result

@shared.dec_repeat
def switchVtx(progressBar = None):
	selection = getSelection()
	result = skinCluster.switchVertexWeight(selection[0], selection[1], progressBar)
	return result
	
@shared.dec_repeat
def labelJoints(progressBar = None):
	jnts = cmds.ls(type = "joint")
	jntAmount = len( jnts )
	_reLabel = False
	for i in xrange(5):
		if cmds.getAttr( jnts[ randint( 0, jntAmount -1) ] + '.type' ) == 0: 
			_reLabel = True
	if not _reLabel:
		return True

	dialog = JointLabel(parent = api.get_maya_window())
	dialog.exec_()
	result = joints.autoLabelJoints(dialog.L_txt.text(), dialog.R_txt.text(), progressBar)
	return result

@shared.dec_repeat
def unifyShells(progressBar = None):
	selection = getSelection()
	result = skinCluster.hardSkinSelectionShells(selection, progressBar)
	return result

@shared.dec_repeat
def copySkin(inplace, smooth, uvSpace, progressBar = None):
	labelJoints()
	selection = getSelection()
	result = skinCluster.transferSkinning(selection[0], selection[1:], inplace, smooth, uvSpace, progressBar)
	return result

@shared.dec_repeat
def neighbors(both, growing, full, progressBar = None):
	selection = getSelection()
	result = skinCluster.smoothAndSmoothNeighbours(selection, both, growing, full,progressBar)
	return result

@shared.dec_repeat
def smooth(progressBar = None):
	selection = getSelection()
	result = skinCluster.neighbourAverage(selection, progressBar= progressBar)
	return result
