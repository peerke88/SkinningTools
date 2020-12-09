# -*- coding: utf-8 -*-
import os
from maya import cmds


def hold(Force=False):
    """ hold the current selected objects
    this is an override function for the copy (ctrl+c) function
    it forces only clean connections to be copied and stored somewhere else so when pasted the scene isn't a mess

    :param Force: if `True` forces the export of selected object to take place ,if `False` it will not force the action (might break in some cases)
    :type Force: bool
    """
    try:
        selection = saveSelectionToAttrs()
        tempDir = cmds.internalVar(utd=True)
        holdfetchFile = tempDir + "holdfetch.mb"
        if Force:
            cmds.file(holdfetchFile, typ="mayaBinary", es=True, pr=True, pmt=0, f=True)
        else:
            cmds.file(holdfetchFile, typ="mayaBinary", es=True, pr=True, pmt=0)
        print(os.path.exists(holdfetchFile))
        removeSelectionFromAttrs(selection)
    except:
        cmds.warning('Could not Hold')


def fetch():
    """ fetch the holded objects
    this is an override function for the paste (ctrl+v) function
    it forces only clean connections to be pasted in the current scene without making a mess out of it

    :return: created nodes
    :rtype: list
    """
    try:
        topLevelDagObjects = cmds.ls(assemblies=True, l=True)
        allDagObjects = cmds.ls(l=True)
        tempDir = cmds.internalVar(utd=True)
        holdfetchFile = tempDir + "holdfetch.mb"
        nonUsedString = "temporary_NonUsed_String"
        cmds.file(holdfetchFile, i=True, pr=True, pmt=False, rpr=nonUsedString)

        afterObjects = cmds.ls(l=True)
        newObjects = []
        for obj in afterObjects:
            if not obj in allDagObjects:
                newObjects.append(obj)
        for obj in newObjects:
            try:
                if nonUsedString in obj:
                    newName = obj.replace((nonUsedString + "_"), "")
                    if cmds.objExists(obj):
                        cmds.rename(obj, newName)
            except:
                print("Could not rename " + obj)
        remainingTopDagNodes = cmds.ls(assemblies=True, l=True)
        try:
            finalAssemblies = cleanupFetch(topLevelDagObjects, remainingTopDagNodes)
            selection = selectFromAttrs(finalAssemblies)
            return selection
        except:
            return remainingTopDagNodes
    except:
        cmds.warning('Could not Fetch.')
        return []


def cleanupFetch(topLevelDagObjects, remainingTopDagNodes):
    """ clean the connections and objects fetched
    
    :param topLevelDagObjects: all objects that are part of the root of the scene before fetch
    :type topLevelDagObjects: list
    :param remainingTopDagNodes: all objects that are part of the root of the scene after fetch
    :type remainingTopDagNodes: list
    :return: newly added top level nodes
    :rtype: list
    """
    if topLevelDagObjects == None or len(topLevelDagObjects) == 0:
        return []
    if remainingTopDagNodes == None or len(remainingTopDagNodes) == 0:
        return []
    newAssemblies = []
    for afterAssembly in remainingTopDagNodes:
        if not afterAssembly in topLevelDagObjects:
            newAssemblies.append(afterAssembly)
    return newAssemblies


def saveSelectionToAttrs():
    """ add identifying attributes to the objects about to be stored
    
    :return: the current selection we want to hold
    :rtype: list
    """
    selection = cmds.ls(sl=True, fl=True, l=True)
    for obj in selection:
        try:
            cmds.addAttr(obj, shortName="holdFetchAttr", at="bool")
        except:
            pass
    return selection


def removeSelectionFromAttrs(nodes):
    """ cleanup identifying attributes to the objects about to be stored
    
    :param nodes: the nodes that are imported into the new scene will have their attribute removed
    :type nodes: list
    """
    for node in nodes:
        if cmds.objExists(node + ".holdFetchAttr"):
            try:
                cmds.deleteAttr(node, at='holdFetchAttr')
            except:
                pass


def selectFromAttrs(topNodes):
    """ based on top nodes imported we are going to check what is added to the scene
    
    :param topNodes: the topnodes that are imported into the new scene
    :type topNodes: list
    :return: all new added nodes
    :rtype: list
    """
    selection = []
    for topNode in topNodes:
        decendants = cmds.listRelatives(topNode, ad=True, f=True)
        decendants.append(topNode)
        for node in decendants:
            if cmds.objExists(node + ".holdFetchAttr"):
                selection.append(node)
    if len(selection) == 0:
        return
    removeSelectionFromAttrs(selection)

    renamed = []
    for obj in selection:
        if not obj in topNodes:
            newObj = cmds.parent(obj, w=True)
            renamed.append([obj, newObj[0]])
    for r in renamed:
        selection.remove(r[0])
        selection.append(r[1])

    for node in topNodes:
        if not node in selection:
            cmds.delete(node)

    cmds.select(selection, r=True)
    return selection
