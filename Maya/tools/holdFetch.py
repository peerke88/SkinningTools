# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
import os
from maya import cmds

def hold(Force=False):
	try:
		selection = saveSelectionToAttrs()
		tempDir = cmds.internalVar(utd=True);
		holdfetchFile = tempDir + "holdfetch.mb";
		if Force:
			cmds.file(holdfetchFile, typ="mayaBinary", es=True, pr=True,pmt=0, f=True)
		else:
			cmds.file(holdfetchFile, typ="mayaBinary", es=True, pr=True, pmt = 0)
		print (os.path.exists(holdfetchFile))
		removeSelectionFromAttrs(selection)
	except:
		cmds.warning('Could not Hold');
	
def fetch():
	try:
		topLevelDagObjects = cmds.ls(assemblies=True, l=True);
		allDagObjects = cmds.ls(l=True);
		tempDir = cmds.internalVar(utd=True);
		holdfetchFile = tempDir + "holdfetch.mb";
		nonUsedString = "temporary_NonUsed_String"
		cmds.file(holdfetchFile, i=True, pr=True, pmt=False, rpr=nonUsedString);
		
		afterObjects = cmds.ls(l=True);
		newObjects = [];
		for obj in afterObjects:
			if not obj in allDagObjects:
				newObjects.append(obj);
		for obj in newObjects:
			try:
				if nonUsedString in obj:
					newName = obj.replace((nonUsedString + "_"), "");
					if cmds.objExists(obj):
						cmds.rename(obj, newName)
			except:
				print("Could not rename " + obj)
		remainingTopDagNodes = cmds.ls(assemblies=True, l=True);
		try:
			finalAssemblies = cleanupFetch(topLevelDagObjects, remainingTopDagNodes);
			selection = selectFromAttrs(finalAssemblies);
			return selection;
		except:
			return remainingTopDagNodes;
	except:
		cmds.warning('Could not Fetch.')
		return [];
	
def cleanupFetch(topLevelDagObjects, remainingTopDagNodes):
	if topLevelDagObjects == None or len(topLevelDagObjects) == 0:
		return []
	if remainingTopDagNodes == None or len(remainingTopDagNodes) == 0:
		return [];
	newAssemblies = [];
	for afterAssembly in remainingTopDagNodes:
		if not afterAssembly in topLevelDagObjects:
			newAssemblies.append(afterAssembly);
	return newAssemblies;

def saveSelectionToAttrs():
	selection = cmds.ls(sl=True, fl=True, l=True);
	for obj in selection:
		try:
			cmds.addAttr(obj, shortName="holdFetchAttr", at="bool")
		except:
			pass;
	return selection;

def removeSelectionFromAttrs(nodes):
	for node in nodes:
		if cmds.objExists(node + ".holdFetchAttr"):
			try:
				cmds.deleteAttr( node, at='holdFetchAttr' );
			except:
				pass;
			
def selectFromAttrs(topNodes):
	selection = [];
	for topNode in topNodes:
		decendants = cmds.listRelatives(topNode, ad=True, f=True);
		decendants.append(topNode);
		for node in decendants:
			if cmds.objExists(node + ".holdFetchAttr"):
				selection.append(node);
	if len(selection) == 0:
		return;
	removeSelectionFromAttrs(selection);

	renamed = []
	for obj in selection:
		if not obj in topNodes:
			newObj = cmds.parent(obj, w=True);
			renamed.append([obj, newObj[0]]);
	for r in renamed:
		selection.remove(r[0]);
		selection.append(r[1]);

	for node in topNodes:
		if not node in selection:
			cmds.delete(node);

	cmds.select(selection, r=True)
	return selection;

