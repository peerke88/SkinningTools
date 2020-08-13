from shared import *
#@note: also import qt here for the connection with progressbar?



## adds label to joints, forces maya to recognise joints that are on the exact same position
#@param string inputLeft, string prefix to identify all joints that are on the left of the character 
#@param string inputRight, string prefix to identify all joints that are on the right of the character
@dec_undo
def autoLabelJoints(inputLeft, inputRight, progressBar = None):
    
    def setprogress(iteration, progressBar):
        if progressBar == None:
            return
        progressBar.setValue(iteration)
        qApp.processEvents()

    def SetAttrs(side, type, name):
        try:
            cmds.setAttr( bone + '.side', l=0)
            cmds.setAttr( bone + '.type', l=0)
            cmds.setAttr( bone + '.otherType', l=0)
            cmds.setAttr( bone + '.drawLabel', l=0)
        except:
            pass
        
        cmds.setAttr( bone + '.side', side )
        cmds.setAttr( bone + '.type', type)
        cmds.setAttr( bone + '.otherType', name, type="string" )
        cmds.setAttr( bone + '.drawLabel', 1)

    allJoints = cmds.ls(type="joint") or None
    allFoundjoints = cmds.ls(type="joint") or None
    if allJoints == None:
        return
    
    percentage = 99.0/len(allJoints)
    if not "*" in inputLeft:
        inputLeft = "*" + inputLeft + "*"
    if not "*" in inputRight:
        inputRight = "*" + inputRight + "*"
    
    leftJoints  = cmds.ls("%s"%inputLeft, type="joint")
    rightJoints = cmds.ls("%s"%inputRight, type="joint")
    iteration1 = 0
    iteration2 = 0
    iteration3 = 0

    for iteration1, bone in enumerate(leftJoints):
        SetAttrs(1, 18, str( bone ).replace( str(inputLeft).strip("*"), "" ) )
        allJoints.remove(bone)
        setprogress((iteration1+1)*percentage, progressBar)
                
    for iteration2, bone in enumerate(rightJoints):
        SetAttrs(2, 18, str( bone ).replace( str(inputRight).strip("*"), "" ) )
        allJoints.remove(bone)
        setprogress((iteration1+iteration2)*percentage, progressBar)
        
    for iteration3, bone in enumerate(allJoints):
        SetAttrs(0, 18, str( bone ) )
        setprogress((iteration1+iteration2+iteration3)*percentage, progressBar)
        
    for bone in allFoundjoints:
        cmds.setAttr(bone + '.drawLabel', 0)

    if progressBar != None:
        progressBar.setValue(100)
        qApp.processEvents()
    
    return True


@dec_undo
## reset the object back to bindpose without the need of the bindpose node!
# calculates the bindpose through the prebind matrix of the joints
#@param string object, mesh that should be reset to bindPost
def resetToBindPoseobject():

    #@todo: convert to openMaya api 2.0
    def getMayaMatrix(data):
        mMat = MMatrix()
        MScriptUtil.createMatrixFromList(data, mMat)
        return mMat

    def mayaMatrixToList(mMatrix):
        d = []
        for x in range(4):
            for y in range(4):
                d.append(mMatrix(x,y))
        return d

    skinCluster = skinCluster( object, silent=True )
    if skinCluster == None:
        return

    infjnts  = cmds.skinCluster(skinCluster, q=True, inf=True)
    bindPoseNode = cmds.dagPose( infjnts[ 0 ], q=True, bindPose=True )
    if bindPoseNode != None:
        cmds.select(object)
        mel.eval("gotoBindPose;")
    else:
        for i, joint in enumerate(infjnts):
            prebindMatrix= cmds.getAttr(skinCluster + ".bindPreMatrix[%s]"%i)
            
            matrix = mayaMatrixToList(getMayaMatrix(prebindMatrix).inverse())
            cmds.xform(joint, ws=True, m=matrix)

    return True

## recomputes all prebind matrices in this pose, joints will stay in place while the mesh goes back to bindpose
# http://leftbulb.blogspot.nl/2012/09/resetting-skin-deformation-for-joint.html
#@param list joints, list of joints to recompute matrix
#@param string skincluster, skincluster object to reset
@dec_undo
def resetSkinnedJointsjoints( skinCluster = None):
    for joint in joints:
        skinClusterPlugs = cmds.listConnections(joint + ".worldMatrix[0]", type="skinCluster", p=1)
        if skinCluster is not None and skinClusterPlugs is not None:
            for sc in skinClusterPlugs:
                if skinCluster in sc:
                    skinClusterPlugs = [sc]

        if skinClusterPlugs:
            for skinClstPlug in skinClusterPlugs:
                index       = skinClstPlug[ skinClstPlug.index("[")+1 : -1 ]
                skinCluster = skinClstPlug[ : skinClstPlug.index(".") ]
                curInvMat   = cmds.getAttr(joint + ".worldInverseMatrix")
                cmds.setAttr( skinCluster + ".bindPreMatrix[%s]"%index, type="matrix", *curInvMat )
            try: 
                cmds.skinCluster(skinCluster, e = True, recacheBindMatrices = True)
            except StandardError:
                pass
        else:
            print("no skinCluster attached to %s!"%joint)
    return True

@dec_undo
def freezeSkinnedJointsjoints():
    '''cleanup joint orient of skinned/constrained bones'''
    for joint in joints:
        dup = cmds.duplicate(joint, rc=1)[0]
        ch = cmds.listRelatives(dup, children=1, f=1)
        if ch:
            cmds.delete(ch)
            
        cmds.makeIdentity(dup, apply=1, t=1, r=1, s=1)
        jo = cmds.getAttr(dup+'.jo')[0]

        cmds.setAttr(joint +'.jo', jo[0], jo[1], jo[2])
        cmds.delete(dup) 

        try: cmds.setAttr(joint +'.r', 0,0,0)
        except:pass            
              
        try:resetSkinnedJoints([joint])
        except:pass

    return joints

@dec_undo
def freezeSkinnedJointsFulljoints():
	#@todo have another look at this with skinned joints and joints part of ik-spline
    info = OrderedDict()
    parentInfo = OrderedDict()
    newTransforms = []
    forcedReparent = []
    for jnt in joints:
        children = cmds.listRelatives(jnt, c=1)
        info[jnt] = children
        parents = cmds.listRelatives(jnt, p=1,f = 1)
        if parents is None or parents == []:
            continue 
        parentlist = parents[0].split("|")[::-1]
        
        for index, obj in enumerate(parentlist):
            if obj != '' and cmds.objectType(obj) != "joint":
                forcedReparent.append(jnt)
            elif obj != '' and cmds.objectType(obj) == "joint":
                parentInfo[jnt] = obj
                break
    
    for jnt in joints:
        pos = cmds.xform(jnt, q=1, ws=1, t=1)
        dup = cmds.duplicate(jnt, rc=1)[0]
        ch = cmds.listRelatives(dup, children=1, f=1)
        if ch:
            cmds.delete(ch)
            
        cmds.makeIdentity(dup, apply=1, t=1, r=1, s=1)
        jo = cmds.getAttr(dup+'.jo')[0]

        cmds.setAttr(jnt +'.jo', jo[0], jo[1], jo[2])
        cmds.setAttr(jnt +'.r', 0,0,0)
        cmds.parent(jnt,world=True)
        parent = cmds.listRelatives(jnt, parent=1)
        if parent is not None and parent != []:
            cmds.setAttr(parent[0]+'.s', 1,1,1)
            newTransforms.append(parent[0])
            cmds.xform(jnt, ws=1, t=pos)
        cmds.setAttr(jnt +'.s', 1,1,1)
        cmds.delete(dup)
    
    for key, value in info.iteritems():
        if value is not None:
            cmds.parent(value, key)

    for jnt in  forcedReparent:
        if jnt in parentInfo.keys():
            cmds.parent(jnt, parentInfo[jnt])

    cmds.delete(newTransforms)
    resetSkinnedJoints(info.keys())
    return info.keys()

@dec_undo
def removeBindPoses():
    '''deletes all bindpose nodes from current scene'''
    dagPoses = cmds.ls( type="dagPose" )
    for dagPose in dagPoses:
        if not cmds.getAttr( "%s.bindPose"%dagPose ):
            continue
        cmds.delete( dagPose )
    return True

@dec_undo
def addUnlockedZeroInfljoints(mesh):
    '''adds joints to the current mesh without altering the weights, and makes sure that the joints are unlocked
    @param joints: joints to be added to the mesh
    @param mesh: mesh onto which the joints will be added as an influence'''
    skinClusterName = SkinningTools.skinCluster( mesh, silent=True )
    if skinClusterName != None:
        jointInfls = cmds.skinCluster( skinClusterName, q=True, inf=True )
        for joint in joints:
            if joint in jointInfls:
                continue
            cmds.skinCluster( skinClusterName, e=True, lw=False, wt=0.0, ai=joint )
    return True

@dec_undo
def BoneMove(bone1, bone2, skin):
    '''transfer weights between 2 joints using the selected mesh'''
    skinClusterName    = SkinningTools.skinCluster(skin, True)
    infjnts  = cmds.skinCluster(skinClusterName, q=True, inf=True)

    if not bone1  in infjnts:
        cmds.skinCluster( skinClusterName, e=True, lw=False, wt=0.0, ai=bone1 )
    if not bone2  in infjnts:
        cmds.skinCluster( skinClusterName, e=True, lw=False, wt=0.0, ai=bone2 )

    
    meshShapeName      = cmds.listRelatives(skin, s=True)[0]
    outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName],  q=True)
    
    # get bone1 position and bone2 position in list
    infLengt = len(infjnts)
    bone1Pos = 0
    bone2Pos = 0
    for i in range(infLengt):
        if infjnts[i] == bone1:
            bone1Pos  = i
        if infjnts[i] == bone2:
            bone2Pos  = i

    lenOutInfArray = len(outInfluencesArray)
    amountToLoop   = (lenOutInfArray/infLengt)

    for j in range(amountToLoop):
        newValue = outInfluencesArray[ ( j*infLengt )+bone2Pos ] + outInfluencesArray[ ( j*infLengt )+bone1Pos ]
        outInfluencesArray[ ( j*infLengt )+bone2Pos ] = newValue
        outInfluencesArray[ ( j*infLengt )+bone1Pos ] = 0.0
    
    cmds.SkinWeights([meshShapeName, skinClusterName] , nwt=outInfluencesArray)
    return True

@dec_undo
def BoneSwitch(joint1, joint2, skin):
    '''switch bone influences by reconnecting matrices in the skincluster plugs
    really fast, downside: only applicable in bindpose'''

    skinClusterName = SkinningTools.skinCluster(skin, True)
    connection1 = cmds.listConnections(joint1+'.worldMatrix', s=0,d=1,c=1,p=1, type = "skinCluster" )
    connection2 = cmds.listConnections(joint2+'.worldMatrix', s=0,d=1,c=1,p=1, type = "skinCluster" )

    sameCluster1 = False
    sameCluster2 = False
    currentConnection1 = ''
    currentConnection2 = ''
    for conn1 in connection1:
        if conn1.split('.')[0] == skinClusterName:
            sameCluster1 = True
            currentConnection1 = conn1
    for conn2 in connection2:
        if conn2.split('.')[0] == skinClusterName:
            sameCluster2 = True
            currentConnection2 = conn2

    if sameCluster1 == False or sameCluster2 == False:
        cmds.warning("bones not part of the same skincluster!")
    try:
        origConnection1 = currentConnection1.split('matrix')[-1]
        origConnection2 = currentConnection2.split('matrix')[-1]
        
        cmds.disconnectAttr(joint1+'.worldMatrix', currentConnection1)
        cmds.disconnectAttr(joint2+'.worldMatrix', currentConnection2)
        cmds.disconnectAttr("%s.lockInfluenceWeights"%joint1, "%s.lockWeights%s"%(skinClusterName, origConnection1))
        cmds.disconnectAttr("%s.lockInfluenceWeights"%joint2, "%s.lockWeights%s"%(skinClusterName, origConnection2))
        
        cmds.connectAttr(joint1+'.worldMatrix', currentConnection2, f=1)
        cmds.connectAttr(joint2+'.worldMatrix', currentConnection1, f=1)
        cmds.connectAttr("%s.lockInfluenceWeights"%joint1, "%s.lockWeights%s"%(skinClusterName, origConnection2), f=1)
        cmds.connectAttr("%s.lockInfluenceWeights"%joint2, "%s.lockWeights%s"%(skinClusterName, origConnection1), f=1)
        
        resetSkinnedJoints([joint1, joint2], skinClusterName)
    except Exception as e:
        cmds.warning(e)
        return False
    return True

@dec_undo
def removeJointsskinObjects( jointsToRemove, useParent = True, delete =True, fast = False , progressBar = None):
    '''stores joint weight information on another joint before it gets removed
    @param skinObjects: all objects from which joints need to be removed
    @param jointsToRemove: all joints that need to be removed:
    @param useParent: if true it will store current weight information of joint to be removed on the parent
                    if False it will look for the closest joint using a pointcloud system to make sure all joint information is stored propperly
    just deleting joints will give problems in the skincluster this method makes it safer to remove joints that are not necessary'''
    if len(skinObjects) == 0:
        cmds.error('mesh needs to be selected for this operation to work!')
    skinClusters = []
    skinPercentage = 100.0/len(skinObjects)

    for skinIter, skinObject in enumerate( skinObjects ):
        skinClusterName = SkinningTools.skinCluster(skinObject, True)
        if skinClusterName == None:
            continue

        jointsAttached = cmds.skinCluster( skinClusterName, q=True, inf=True ) 
        if fast:
            verts = self.ShowInfluencedVerts(skinObject, jointsToRemove, progressBar = None)
            if verts == None or len(verts) == 0:
                continue
            
            jnts = []
            for jnt in jointsToRemove:
                if not jnt in jointsAttached:
                    continue
                jnts.append((jnt, 0.0))
            
            cmds.select(verts, r=1)
            cmds.skinPercent( skinClusterName, tv =jnts, normalize=True)

            if progressBar != None:
                progressBar.setValue( (skinIter*skinPercentage) )
                QApplication.processEvents()
            skinClusters.append(skinClusterName)
            
        else:
            if not useParent:
                for rjnt in jointsToRemove:
                    if rjnt in jointsAttached:
                        jointsAttached.remove(rjnt)

                sourcePositions = []
                sourceJoints = []
                for joint in jointsAttached:
                    pos = cmds.xform(joint, q=True, ws=True, t=True)
                    sourcePositions.append(pos)
                    sourceJoints.append([joint, pos])

                sourceKDTree = KDTree.construct_from_data( sourcePositions ) 

            jntPercentage = skinPercentage/ len( jointsToRemove )
            for jntIter, jnt in enumerate(jointsToRemove):
                bone1 = jnt
                if useParent:
                    bone2 = cmds.listRelatives(jnt, parent=True)[0] or None
                    if bone2 == None:
                        removePos = cmds.xform(jnt, q=True, ws=True, t=True)
                        pts = sourceKDTree.query(query_point = removePos, t=1)
                        for index, position in enumerate(sourceJoints):
                            if position[1] != pts[0]:
                                continue
                            bone2 = position[0]
                else:
                    removePos = cmds.xform(jnt, q=True, ws=True, t=True)
                    pts = sourceKDTree.query(query_point = removePos, t=1)\

                    for index, position in enumerate(sourceJoints):
                        if position[1] != pts[0]:
                            continue
                        bone2 = position[0]

                self.BoneMove(bone1, bone2, skinObject)

                if progressBar != None:
                    progressBar.setValue(((jntIter+1)*jntPercentage) + (skinIter*skinPercentage) )
                    QApplication.processEvents()
            skinClusters.append(skinClusterName)
    
    for skinClusterName in skinClusters:
        jointsAttached = cmds.skinCluster( skinClusterName, q=True, inf=True ) 
        for jnt in jointsToRemove:
            if not jnt in jointsAttached:
                continue
            cmds.skinCluster(skinClusterName, e=True, ri= jnt)
    
    print("removed these joints from influence: ", jointsToRemove)
    if delete:
        for jnt in jointsToRemove:
            childJoints = cmds.listRelatives(jnt, c=1)
            parent = cmds.listRelatives(jnt, p=1)
            if childJoints == None or len(childJoints) == 0:
                continue
            if parent == None or len(parent) == 0:
                cmds.parent(childJoints, w=1)
                continue
            cmds.parent(childJoints, parent)
        cmds.delete(jointsToRemove)
            
    if progressBar != None:
        progressBar.setValue(100)
        qApp.processEvents()
    
    return True

def comparejointInfluences(skinObjects , query = False):
    '''makes sure that given skinobjects have the same joints influencing, its a safety measure when copying weights between different objects'''
    compareLists = []
    for skinObject in skinObjects:
        skinClusterName = SkinningTools.skinCluster( skinObject, True )
        if skinClusterName == None:
            continue

        joints = cmds.skinCluster( skinClusterName, q=True, inf=True )     
        compareLists.append( [ skinObject, joints ] )
    
    if len(compareLists) < 2:
        cmds.error("please select at least 2 objects with skinclusters")
    totalCompares = len( compareLists )
    missingJointsList = []
    for i in range( totalCompares ):
        for list in compareLists:
            if list == compareLists[ i ]:
                continue
            missedjoints = []
            for match in list[ 1 ]:
                if not any( match in value for value in compareLists[ i ][ 1 ] ):
                    missedjoints.append( match )

            missingJointsList.append( [ compareLists[ i ][ 0 ], missedjoints ] )
    if query == True:
        joints = []
        for missingList in missingJointsList:
            for joint in missingList[1]:
                joints.append(joint)
        if len(joints) == 0:
            return None
        else:
            return True
    else:
        for missingJoints in missingJointsList:
            skinClusterName = SkinningTools.skinCluster( missingJoints[ 0 ], True )
            for joint in missingJoints[ 1 ]:
                try:
                    cmds.skinCluster( skinClusterName, e=True, lw=False, wt=0.0, ai=joint )
                except:
                    pass
    return True

def getMeshesInfluencedByJointcurrentJoints():
    '''returns all meshes that have any skincluster attachemt with given joints'''
    allSkinClusters = cmds.ls(type = "skinCluster")

    attachedSkinCluster = []
    for scl in allSkinClusters:
        joints = cmds.skinCluster(scl, q=True, inf=True)
        for jnt in currentJoints:
            if jnt in joints and not scl in attachedSkinCluster:
                attachedSkinCluster.append(scl)
    meshes = []
    for scl in attachedSkinCluster:
        geo = cmds.skinCluster(scl, q=1, g=1)[0]
        meshes.append(geo)

    return meshes


def getInfluencingjoints(object):
    '''returns all the joints that influence the mesh'''
    skinClusterName = SkinningTools.skinCluster( object, silent=True )
    if skinClusterName != None:
        jointInfls = cmds.skinCluster( skinClusterName, q=True, inf=True )
        return jointInfls