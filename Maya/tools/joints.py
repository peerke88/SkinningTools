from shared import dec_undo
#@note: also import qt here for the connection with progressbar?

@dec_undo
def autoLabelJoints(inputLeft, inputRight, progressBar = None):
    '''adds label to joints, forces maya to recognise joints that are on the exact same position
    @param inputLeft: string prefix to identify all joints that are on the left of the character 
    @param inputRight: string prefix to identify all joints that are on the right of the character'''
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
def resetToBindPose(self, object):
    """ reset the object back to bindpose without the need of the bindpose node!
    calculates the bindpose through the prebind matrix of the joints"""

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

    skinCluster = SkinningTools.skinCluster( object, silent=True )
    if skinCluster == None:
        return

    infjnts  = cmds.skinCluster(skinCluster, q=True, inf=True)
    bindPoseNode = cmds.dagPose( infjnts[ 0 ], q=True, bindPose=True )
    if bindPoseNode != None:
        cmds.select(object)
        mel.eval("gotoBindPose;")
    else:
        """ reset the object back to bindpose without the need of the bindpose node!"""
        for i, joint in enumerate(infjnts):
            prebindMatrix= cmds.getAttr(skinCluster + ".bindPreMatrix[%s]"%i)
            
            matrix = mayaMatrixToList(getMayaMatrix(prebindMatrix).inverse())
            cmds.xform(joint, ws=True, m=matrix)

    return True