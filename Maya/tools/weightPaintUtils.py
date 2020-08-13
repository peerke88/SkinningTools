# pickwalk through joints while painting 
# created by ryan porter: https://yantor3d.wordpress.com/
from maya import cmds, mel

SKIN_CLUSTER_INFLUENCE_LIST = 'theSkinClusterInflList'

def pickWalkSkinClusterInfluenceList(direction):
    if not _paintingWeights():
        return False
    
    ctx = cmds.currentCtx() 
    selected = cmds.artAttrSkinPaintCtx(ctx, query=True, attrSelected=True)
    
    nodeType, scls, attr = selected.split('.')

    joints = cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, query=True, children=True)
    visibleJoints = cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, query=True, itemVisible=True)

    selectedJoint = None
    
    for i, jnt in enumerate(joints):
        if cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, query=True, itemSelected=jnt):
            selectedJoint = jnt
            break
            
    if not selectedJoint:
        return False

    idx = joints.index(selectedJoint)       

    d = 1 if direction == 'down' else -1

    for i, __ in enumerate(joints):
        idx += d 

        if idx == len(joints):
            idx = 0

        if joints[idx] in visibleJoints:
            jnt = joints[idx]
            break
    else:
        return False
    
    mel.eval('artSkinInflListChanging "{}" 0'.format(selectedJoint))
    cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, edit=True, clearSelection=True)
    cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, edit=True, selectItem=(jnt, True))
    mel.eval('artSkinInflListChanging "{}" 1'.format(jnt))

    mel.eval('artSkinInflListChanged artAttrSkinPaintCtx')

    mel.eval('refreshAE')
    return True

def _paintingWeights():            
    ctx = cmds.currentCtx()
    
    if not ctx == 'artAttrSkinContext':
        return False
        
    if not cmds.treeView(SKIN_CLUSTER_INFLUENCE_LIST, q=True, exists=True):
        return False
    
    return True
