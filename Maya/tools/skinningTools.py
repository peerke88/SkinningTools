# -*- coding: utf-8 -*-


from maya import cmds, mel, OpenMaya
from maya.OpenMaya import *
from functools import wraps
from heapq import nsmallest
from collections import defaultdict, deque, OrderedDict
import re, decimal, types, traceback, sys
from . import polySelectionUtils
from .fallofCurveUI import BezierFunctions
try:
    #soft check for pymel
    from pymel.core.general import PyNode
    _pymel = True
except:
    _pymel = False

try:
    import cStringIO
except:
    import io as cStringIO

from .kdtree import KDTree
from math import pow, sqrt

from .qtUtil import *


#@note: split tools in here to mesh, skincluster, joint tools

class Graph(object):
    ''' dijkstra closest path technique (for nurbs and lattice)
    implemented from: https://gist.github.com/econchick/4666413  
    basic idea: http://www.redblobgames.com/pathfinding/a-star/introduction.html'''
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance

def dijkstra(graph, initial):
    ''' dijkstra closest path technique (for nurbs and lattice)'''
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node
        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            try:
                weight = current_weight + graph.distances[(min_node, edge)]
            except:
                continue
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path

def shortest_path(graph, origin, destination):
    ''' dijkstra closest path technique (for nurbs and lattice)'''
    visited, paths = dijkstra(graph, origin)
    full_path = deque()
    _destination = paths[destination]

    while _destination != origin:
        full_path.appendleft(_destination)
        _destination = paths[_destination]

    full_path.appendleft(origin)
    full_path.append(destination)

    return visited[destination], list(full_path)

class SkinningTools(object):
    def dec_undo(func):
        '''undo decorator'''
        @wraps(func)
        def _undo_func(*args, **kwargs):
            try:
                cmds.undoInfo(ock=True)
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                print(e.__class__)
                print(sys.exc_info())
                cmds.warning(traceback.format_exc( )) 
            finally:
                cmds.undoInfo(cck=True)
        
        return _undo_func

    @staticmethod
    def skinCluster(object, silent=False):
        '''static function to get the skincluster from any mesh
        @param object: mesh to get the skinCluster
        @param silent: flag to display warning dialog or to silently continue the current function'''
        
        object = SkinningTools.getParentShape(object)
        skinCluster = mel.eval('findRelatedSkinCluster("%s");'%object) 
        if not skinCluster:
            if silent == False:
                cmds.confirmDialog( title='Error', message='no SkinCluster found on: %s!'%object, button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
            else:
                skinCluster = None
        return skinCluster

    @staticmethod
    def getParentShape(object):
        '''static function to get the correct dagnode of a mesh which is used in other functions'''
        if isinstance(object, list):
            object = object[0]
        objType = cmds.objectType(object)
        if objType == 'mesh' or objType == "nurbsCurve" or objType == "lattice":
            object = cmds.listRelatives(object, p=True, f=True)[0]
        if cmds.objectType(object) != "transform":
            object = cmds.listRelatives(object, p=True, f=True)[0]
        return object

    @staticmethod
    def doCorrectSelectionVisualization(skinMesh):
        '''static function to cleanup selection details in maya so selection is correctly visualized'''
        objType = cmds.objectType(skinMesh)
        if objType == "transform":
            shape = cmds.listRelatives(skinMesh, c=1, s=1)[0]
            objType = cmds.objectType(shape)

        mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
        if objType == "nurbsSurface" or objType == "nurbsCurve":
            mel.eval('doMenuNURBComponentSelection("%s", "controlVertex");'%skinMesh )
        elif objType == "lattice":
            mel.eval('doMenuLatticeComponentSelection("%s", "latticePoint");'%skinMesh )
        elif objType == "mesh":
            mel.eval('doMenuComponentSelection("%s", "vertex");'%skinMesh )

    def convertToVertexList(self, object):
        '''conveniently converts every polygonal selection to vertices as vertices are the components on which skin is applied
        @param object: can be either the mesh, the shape or a component based selection
        selection will be flattened so each vertix is listed without nesting (i.e. ['.vtx[0:20]'] becomes ['.vtx[0]', '.vtx[1]', .....])'''
        checkObject = object
        if isinstance(object, list):
            checkObject = object[0]
        objType = cmds.objectType(checkObject)
        checkType = checkObject
        if objType == "transform":
            shapes = cmds.listRelatives(object, ad=1, s=1)
            if not shapes == []:
                checkType = object
            checkType = shapes[0]

        objType = cmds.objectType(checkType)
        if objType == 'mesh': # or objType == "nurbsCurve" or objType == "lattice":
            convertedVertices = cmds.polyListComponentConversion(object, tv=True)
            return cmds.filterExpand(convertedVertices, sm=31)
        
        if objType == "nurbsCurve" or objType == "nurbsSurface":
            if isinstance(object, list) and ".cv" in object[0]:
                return cmds.filterExpand(object, sm=28)
            elif isinstance(object, list):
                return cmds.filterExpand('%s.cv[*]'%object[0], sm=28)
            elif ".cv" in object:
                return cmds.filterExpand(object, sm=28)
            else:
                return cmds.filterExpand('%s.cv[*]'%object, sm=28)
        
        if objType == "lattice":
            if isinstance(object, list) and ".pt" in object[0]:
                return cmds.filterExpand(object, sm =46 )
            elif isinstance(object, list):
                return cmds.filterExpand('%s.pt[*]'%object[0], sm =46 )
            elif ".pt" in object:
                return cmds.filterExpand(object, sm =46 )
            else:
                return cmds.filterExpand('%s.pt[*]'%object, sm =46 )

    def getVertOverMaxInfluence(self,singleObject = None, MaxInfluenceValue = 8, notSelect = False, progressBar = None):
        '''select all vertices that have more influences then the set Maximum'''
        if not notSelect:
            cmds.undoInfo(ock=True)
        allVerticesOverMaxInfluence = []
        
        cmds.select(singleObject, r=True)
        try:
            mel.eval('doPruneSkinClusterWeightsArgList 1 { "0.001" };')
        except:
            pass
        
        expandedVertices = self.convertToVertexList(singleObject)
        skinClusterName  = SkinningTools.skinCluster(singleObject)
        bones = cmds.skinCluster(skinClusterName, q=True, inf = None)

        if progressBar:
            totalVertices = len(expandedVertices)
            percentage    = 99.0/totalVertices
            iteration     = 1

        for vert in expandedVertices:
            # faster way then iteration over values
            numOfVertInfluences = len(cmds.skinPercent( skinClusterName , vert , q=True , value=True , ignoreBelow=0.001 ))
            if numOfVertInfluences > MaxInfluenceValue:
                allVerticesOverMaxInfluence.append(vert)

            if progressBar:
                progressBar.setValue(percentage * iteration)
                qApp.processEvents()
                iteration += 1
        
        if progressBar:
            progressBar.setValue(100)

        if not notSelect:
            cmds.undoInfo(cck=True)
        
        return allVerticesOverMaxInfluence

    @dec_undo
    def setMaxJointInfluences(self,objects = None, MaxInfluenceValue = 8, progressBar = None):
        '''function that forces each vertex to have a maximum number of influences, pruning lowest values untill maximum is reached'''
        objectAmount = len(objects)
        fullPercentage = 99.0/objectAmount
        for percentIteration, singleObject in enumerate(objects):
            toMuchinfls       = self.getVertOverMaxInfluence(singleObject = singleObject, MaxInfluenceValue= MaxInfluenceValue, notSelect=True) #returns the vertices that have too much influences
            if toMuchinfls == None or len(toMuchinfls) == 0:
                cmds.warning( "no vertices over limit on: ", singleObject)
                continue

            if progressBar:
                totalVertices = len(toMuchinfls)
                percentage    = fullPercentage/totalVertices
                iteration     = 1;

            skin               = toMuchinfls[0].split('.')[0]
            skinClusterName    = SkinningTools.skinCluster(skin)
            meshShapeName      = cmds.listRelatives(skin, s=True)[0]
            outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName],  q=True)

            generatedArray = outInfluencesArray[:]
            infjnts  = cmds.skinCluster(skinClusterName,q=True, inf=True)
            infLengt = len(infjnts)
            if outInfluencesArray == None:
                print("please check '%s' again!"%singleObject)
                continue

            lenOutInfArray = len(outInfluencesArray)
            amountToLoop   = (lenOutInfArray/infLengt)

            for vertex in toMuchinfls:
                values = cmds.skinPercent(skinClusterName, vertex, q=1, v=1, ib=float(decimal.Decimal('1.0e-17')))
                curAmountValues = len(values)
                toPrune = curAmountValues - MaxInfluenceValue

                pruneFix =  max(nsmallest(toPrune, values))+0.001
                cmds.skinPercent(skinClusterName, vertex, pruneWeights= pruneFix ) 

                if progressBar:
                    progressBar.setValue((percentIteration*fullPercentage) + percentage*iteration)
                    qApp.processEvents()
                    iteration+=1;

            cmds.skinCluster(skinClusterName,e=True,fnw=1)
            
            cmds.setAttr( "%s.maxInfluences"%skinClusterName, MaxInfluenceValue )
            cmds.setAttr( "%s.maintainMaxInfluences"%skinClusterName, 1 )

        if progressBar:
            progressBar.setValue(100)

        return True

    @dec_undo
    def autoLabelJoints(self, inputLeft, inputRight, progressBar = None):
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
    def execCopySourceTarget(self,TargetSkinCluster, SourceSkinCluster,  TargetSelection, SourceSelection, smoothValue= 1, progressBar = None, amount =1):
        '''copy skincluster information from 1 object to another using closest amount of vertices based on selection'''
        self.sourcePoints    = []
        self.sourcePointPos  = []
        succeeded = True
        try:
            # make sure that both objects have the same joints
            mesh1 = TargetSelection[ 0 ].split( '.' )[ 0 ]
            mesh2 = SourceSelection[ 0 ].split( '.' )[ 0 ]
            joint   = cmds.skinCluster(SourceSkinCluster, q=True, inf=True)     
            joint1  = cmds.skinCluster(TargetSkinCluster, q=True, inf=True)    
            jointAmount = len(joint)
            skinClusterName = SkinningTools.skinCluster( mesh1, True )
            bindPoseNode = cmds.dagPose( joint[ 0 ], q=True, bindPose=True )
            if bindPoseNode:
                outOfPose    = cmds.dagPose( bindPoseNode, q=True, atPose=True )
            
            sourceInflArray = cmds.SkinWeights([mesh2, SourceSkinCluster],  q=True)
            targetInflArray = cmds.SkinWeights([mesh1, TargetSkinCluster],  q=True)
    
            sameMesh = True
            if mesh1 != mesh2:
                sameMesh = False
                compared = self.comparejointInfluences( [mesh1, mesh2], True )
                if compared != None:
                    if outOfPose != None:
                        result = cmds.confirmDialog( title='Confirm', 
                                                     message='object is not in BindPose,\ndo you want to continue out of bindpose?\npressing "No" will exit the operation! ', 
                                                     button=['Yes','No'], 
                                                     defaultButton='Yes', 
                                                     cancelButton='No', 
                                                     dismissString='No' )
                        if result == "Yes":
                            self.comparejointInfluences( [mesh1, mesh2] )
                        else:
                            return
                    else:
                        self.comparejointInfluences( [mesh1, mesh2] )

            allVerticesSource = self.convertToVertexList(mesh2)
            allVerticesTarget = self.convertToVertexList(mesh1)

            for sourceVert in SourceSelection:
                pos      = cmds.xform( sourceVert, q=True, ws=True,t=True )
                self.sourcePoints.append( pos )
                self.sourcePointPos.append( [ sourceVert, pos ] )
            sourceKDTree = KDTree.construct_from_data( self.sourcePoints )
    
            if progressBar:
                oldValue = progressBar.value()
                if oldValue == 100:
                    oldValue = 0
                totalVertices = len( TargetSelection )
                percentage    = ( 99.0/totalVertices )/amount
                iteration     = 1;
    
            weightlist = []
            for targetVertex in TargetSelection:
                pos = cmds.xform(targetVertex, q=True, ws=True, t=True)
                pts = sourceKDTree.query(query_point = pos, t=smoothValue)
    
                weights = []
                distanceWeightsArray = []
                totalDistanceWeights = 0
                for positionList in self.sourcePointPos:
                    for index in range( smoothValue ):
                        if pts[ index ] != positionList[ 1 ]:
                            continue
                        length = sqrt( pow( ( pos[ 0 ] - pts[ index ][ 0 ] ), 2 ) + 
                                       pow( ( pos[ 1 ] - pts[ index ][ 1 ] ), 2 ) + 
                                       pow( ( pos[ 2 ] - pts[ index ][ 2 ] ), 2 ) )
    
                        distanceWeight = ( 1.0/ ( 1.0 + length ) )
                        distanceWeightsArray.append( distanceWeight )
                        totalDistanceWeights += distanceWeight 
                        
                        weight =[]
                        indexing = allVerticesSource.index(positionList[ 0 ])
                        for i in range(jointAmount):
                            weight.append(sourceInflArray[(indexing*jointAmount)+i])
                        weights.append( weight )
    
                newWeights = []
                for index in range( smoothValue ):
                    for i,  wght in enumerate( weights[ index ] ):
                        # distance/totalDistance is weight of the distance caluclated
                        weights[ index ][ i ] = ( distanceWeightsArray[ index ] / totalDistanceWeights ) * wght
    
                    if len( newWeights ) == 0:
                        newWeights = list( range( len( weights[ index ] ) ) )
                        for j in range( len( newWeights ) ):
                            newWeights[ j ] = 0.0    
                    
                    for j in range( len( weights[ index ] ) ):
                        newWeights[ j ] = newWeights[ j ] + weights[ index ][ j ]
                
                divider = 0.0
                for wght in newWeights:
                    divider = divider + wght
                weightsCreation = []
                for jnt in joint1:
                   for count, skinJoint in enumerate( joint ):
                        if jnt != skinJoint:
                            continue
                        weightsCreation.append((newWeights[count]/divider))
                weightlist.extend(weightsCreation)
    
                if progressBar:
                    progressBar.setValue(oldValue + (percentage*iteration) )
                    qApp.processEvents()
                    iteration+=1;
            
            index = 0
            for vertex in TargetSelection:
                number = allVerticesTarget.index(vertex)
                for jointIndex in range(jointAmount):
                    weightindex = (number*jointAmount) + jointIndex
                    targetInflArray[weightindex] = weightlist[index]
                    index +=1
    
            cmds.SkinWeights([mesh1, TargetSkinCluster] , nwt=targetInflArray)
        except Exception as e :
            succeeded = False
            cmds.warning(e)
        finally:
            if progressBar:
                if amount == 1:
                    progressBar.setValue(100)
            
        return succeeded

    @dec_undo
    def resetToBindPose(self, object):
        """ reset the object back to bindpose without the need of the bindpose node!
        calculates the bindpose through the prebind matrix of the joints"""
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

    def getInfluencingjoints(self, object):
        '''returns all the joints that influence the mesh'''
        skinClusterName = SkinningTools.skinCluster( object, silent=True )
        if skinClusterName != None:
            jointInfls = cmds.skinCluster( skinClusterName, q=True, inf=True )
            return jointInfls

    @dec_undo
    def resetSkinnedJoints(self, joints, skinCluster = None):
        '''recomputes all prebind matrices in this pose, joints will stay in place while the mesh goes back to bindpose'''
        # http://leftbulb.blogspot.nl/2012/09/resetting-skin-deformation-for-joint.html
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
                try: # make sure it works visibly in maya 2016+ as well
                    cmds.skinCluster(skinCluster, e = True, recacheBindMatrices = True)
                except StandardError:
                    pass
            else:
                print("no skinCluster attached to %s!"%joint)
        return True

    @dec_undo
    def freezeSkinnedJoints(self, joints):
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
                  
            try:SkinningTools().resetSkinnedJoints([joint])
            except:pass

        return joints

    @dec_undo
    def freezeSkinnedJointsFull(self, joints):
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
        SkinningTools().resetSkinnedJoints(info.keys())
        return info.keys()

    @dec_undo
    def transferClosestSkinning(self, objects, smoothValue, progressBar):
        '''copy skincluster information from 1 object to another using closest amount of vertices'''
        object1     = objects[0]
        skinCluster = SkinningTools.skinCluster(object1)
        baseJoints  = cmds.skinCluster( skinCluster, q=True, inf=True )  
        amount      = len(objects)-1

        percentage = 100.0/amount
        for iteration, object in enumerate(objects):
            if object == object1:
                continue

            skinCluster1 = SkinningTools.skinCluster(object, silent=True)
            if skinCluster1 == None:
                skinCluster1 = cmds.skinCluster(object, baseJoints)[0]
            else:
                self.comparejointInfluences( [ object1, object ] )
            
            self.execCopySourceTarget(skinCluster1, skinCluster,  self.convertToVertexList(object), self.convertToVertexList(object1), smoothValue, progressBar, amount)
            if progressBar:
                progressBar.setValue(percentage*iteration)
                qApp.processEvents()

        if progressBar:
            progressBar.setValue(100)

        return True

    @dec_undo
    def removeBindPoses(self):
        '''deletes all bindpose nodes from current scene'''
        dagPoses = cmds.ls( type="dagPose" )
        for dagPose in dagPoses:
            if not cmds.getAttr( "%s.bindPose"%dagPose ):
                continue
            cmds.delete( dagPose )
        return True

    @dec_undo
    def addUnlockedZeroInfl(self, joints, mesh):
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
    def transferSkinning(self, baseSkin, otherSkins, inPlace=True, sAs = True, uvSpace = False):
        '''using native maya copyskinweight to generate similar weight values
        @param baseSkin: mesh to copy skinning information from
        @param otherSkins: all other meshes that will gather weight information from the baseSkin
        @param inPlace: if True will make sure to cleanup the mesh and apply the skinning (also to be used for freezin the mesh in pose),
                        when false it assumes skinning is already applied to otherSkins and just copies the weights'''
        skinclusterBase = SkinningTools.skinCluster( baseSkin, silent=False )
        if skinclusterBase == None:
            return 

        if sAs:
            surfaceAssociation = "closestComponent"
        else:
            surfaceAssociation = "closestPoint"

        for skin in otherSkins:
            if inPlace:
                cmds.delete( skin, ch=True )
            else:
                skincluster = SkinningTools.skinCluster( skin, silent=False )
                if skincluster == None:
                    continue
                cmds.skinCluster( skincluster, e=True, ub=True )
            
            jointInfls = cmds.skinCluster( skinclusterBase, q=True, inf=True )
            maxInfls   = cmds.skinCluster( skinclusterBase, q=True, mi=True )
            self.removeBindPoses()
            newSkinCl  = cmds.skinCluster( jointInfls, skin, mi=maxInfls )
            if uvSpace:
                cmds.copySkinWeights( ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation = surfaceAssociation, uv=["map1", "map1"], influenceAssociation =["label", "oneToOne", "name"], normalize=True  )
            else:
                cmds.copySkinWeights( ss=skinclusterBase, ds=newSkinCl[0], nm=True, surfaceAssociation = surfaceAssociation, influenceAssociation =["label", "oneToOne", "name"], normalize=True  )
        return True

    def _shortestPolySurfaceCurvePathAverage(self, selection, skinClusterName, useDistance, diagonal = False, weightWindow = None):      
        ''' method to find a path between 2 given points (vertex and cv)
        polygons uses edges to find shortes path (loops and shortest edgepath functions)
        nurbs surface uses dijkstra algorythim (both diagonally and u/v based)
        nurbs curve uses simple indexing'''
        def measureLength(object1, object2):
            pos1 = OpenMaya.MVector(*cmds.xform(object1, q=True, ws=True, t=True))
            pos2 = OpenMaya.MVector(*cmds.xform(object2, q=True, ws=True, t=True))
            return (pos1-pos2).length()

        start = selection[0]
        end = selection[-1]
        surface = start.split('.')[0]
        
        objType = cmds.objectType(start)
        poly = False
        if objType == 'mesh': 
            poly = True
            added = 0.0
            firstExtendedEdges = cmds.polyListComponentConversion( start, te=True )
            firstExtended  = cmds.filterExpand(firstExtendedEdges, sm=32 )
            secondExtendedEdges = cmds.polyListComponentConversion( end, te=True )
            secondExtended  = cmds.filterExpand(secondExtendedEdges, sm=32 )

            found = []
            for e1 in firstExtended:
                for e2 in secondExtended:
                    e1n = int(e1.split(".e[")[-1].split("]")[0])
                    e2n = int(e2.split(".e[")[-1].split("]")[0])
                    edgeSel = cmds.polySelect(surface, elp=[e1n, e2n], ns = True)
                    if edgeSel == None:
                        continue
                    found.append(edgeSel)
            amountFound = len(found)
            if amountFound != 0:
                # first choice:
                if amountFound == 1:
                    edgeSelection = found[0]
                else:
                    edgeSelection = found[0]
                    for sepList in found:
                        if not len(sepList) < len(edgeSelection):
                            continue
                        edgeSelection = sepList
            else:
                #second choice:
                vertexNumber1 = int(start.split('vtx[')[-1].split("]")[0])
                vertexNumber2 = int(end.split('vtx[')[-1].split("]")[0])
                edgeSelection = cmds.polySelect(surface, shortestEdgePath=[vertexNumber1, vertexNumber2] )
                if edgeSelection == None:
                    cmds.error("selected vertices are not part of the same polyShell!")
            
            allEdges = []
            newVertexSelection = []
            for edge in edgeSelection:
                allEdges.append("%s.e[%s]"%(surface, edge))
                midexpand = self.convertToVertexList("%s.e[%s]"%(surface, edge))                
                newVertexSelection.append(midexpand)
                
            start = selection[0]
            end = selection[-1]
            
            if start in newVertexSelection[0]:
                reverse = False
            else:
                reverse = True

            inOrder = []
            lastVertex = None
            for listVerts in newVertexSelection:
                if start in listVerts:
                    listVerts.remove(start)
                if lastVertex != None:
                    listVerts.remove(lastVertex)
                if end in listVerts:
                    listVerts.remove(end)
                if len(listVerts) != 0:
                    lastVertex = listVerts[0]
                    inOrder.append(lastVertex)

            amount =  len(inOrder)+1
            if reverse:
                inOrder.reverse()

            totalDistance = measureLength(inOrder[-1], end)

        elif objType == "nurbsSurface":
            allCvs = cmds.filterExpand("%s.cv[*][*]"%surface, sm=28)
            graph = Graph() # implemented from above (dijkstra algorithm)
            added  = -2.0
            recomputeDict = {}
            for node in allCvs:
                base = (node)
                graph.add_node(base)
                recomputeDict[base] = node

            for node in allCvs:
                cmds.select(cl=1)
                cmds.nurbsSelect(node, gs=1)
                gro = cmds.ls(sl=1)[0]
                
                if diagonal == False:    
                    # rough implementation to not cross U and V at the same time (2 implementation only)
                    workString = node.split("][")
                    groString = gro.split("][")
                    gro = ["%s][%s"%(workString[0],groString[-1]), "%s][%s"%(groString[0],workString[-1])]

                gro = cmds.filterExpand(gro, sm=28)    

                gro.remove(node)
                basePos = OpenMaya.MVector(*cmds.xform(node, q=1, ws=1, t=1))
                for f in gro:
                    fPos = OpenMaya.MVector(*cmds.xform(f, q=1, ws=1, t=1))
                    fLen = (fPos-basePos).length()
                    graph.add_edge((node), (f), fLen)

            shortest = shortest_path(graph, (start), (end))
        
            inOrder = []
            for sh in shortest[-1]:
                inOrder.append(recomputeDict[sh])
            amount =  len(inOrder)+1
            totalDistance = shortest[0]
        
        elif objType == "lattice":
            allCvs = cmds.filterExpand("%s.pt[*]"%surface, sm=46)
            graph = Graph() # implemented from above (dijkstra algorithm)
            added  = -2.0
            recomputeDict = {}
            for node in allCvs:
                base = (node)
                graph.add_node(base)
                recomputeDict[base] = node

            for node in allCvs:
                gro =  polySelectionUtils.growLatticePoints([node])
                gro.remove(node)
                basePos = OpenMaya.MVector(*cmds.xform(node, q=1, ws=1, t=1))
                for f in gro:
                    fPos = OpenMaya.MVector(*cmds.xform(f, q=1, ws=1, t=1))
                    fLen = (fPos-basePos).length()
                    graph.add_edge((node), (f), fLen)

            shortest = shortest_path(graph, (start), (end))
        
            inOrder = []
            for sh in shortest[-1]:
                inOrder.append(recomputeDict[sh])
            amount =  len(inOrder)+1
            totalDistance = shortest[0]
        
        else:
            numbers = [int(start.split("[")[-1].split("]")[0]), int(end.split("[")[-1].split("]")[0])]
            added = -1.0
            rangeList = range(min(numbers), max(numbers)+1)
            amount = len(rangeList)
            inOrder = []
            totalDistance = 0.0
            for i, num in enumerate(rangeList):
                cv = "%s.cv[%s]"%(surface, num)
                inOrder.append(cv)
                if i == 0:
                    continue
                totalDistance += measureLength(inOrder[i-1], cv)

        listBoneInfluences = cmds.skinCluster(surface, q=True, inf=True)
        weights1 = cmds.skinPercent( skinClusterName, start, q=True, v=True )        
        weights2 = cmds.skinPercent( skinClusterName, end, q=True, v=True )  

        lengths = []
        if useDistance:
            for index, vertex in enumerate(inOrder):
                if index == 0:
                    length = measureLength(start, vertex)
                else:
                    length = measureLength(inOrder[index-1], vertex)
                if poly:
                    totalDistance+=length
                lengths.append(length)
     
        percentage = float(1.0)/(amount +added)
        currentLength = 0.0
        for index, vertex in enumerate(inOrder):
            if not useDistance:
                currentPercentage = (index)*percentage
                if poly:
                    currentPercentage = (index+1)*percentage
                
                if weightWindow == None:
                    continue
                if type(weightWindow) == types.ListType or type(weightWindow) ==  types.TupleType:
                    currentPercentage = BezierFunctions().getDataOnPercentage(currentPercentage, weightWindow)
                else:
                    currentPercentage = weightWindow.getDataOnPerc(currentPercentage)
                    
            else:
                currentLength += lengths[index] 
                currentPercentage = ( currentLength/ totalDistance)
                if weightWindow == None:
                    continue
                if type(weightWindow) == types.ListType or type(weightWindow) ==  types.TupleType:
                    currentPercentage = BezierFunctions().getDataOnPercentage(currentPercentage, weightWindow)
                else:
                    currentPercentage = weightWindow.getDataOnPerc( currentPercentage )
                    
            newWeightsList = []
            for idx, weight in enumerate(weights1):
                value1 = weights2[idx] * currentPercentage
                value2 = weights1[idx] * (1-currentPercentage)
                newWeightsList.append( (listBoneInfluences[ idx ], value1 + value2) )

            cmds.skinPercent(skinClusterName, vertex, transformValue= newWeightsList)

        cmds.select([start, end], r=1)

    def AvarageVertex(self, selection, useDistance, weightAverageWindow = None, progressBar = None):
        '''generate an average weigth from all selected vertices to apply to the last selected vertice'''
        cmds.undoInfo(ock=True)
        vertexAmount = len(selection)
        if vertexAmount < 2:
            cmds.undoInfo(cck=True)
            cmds.error("not enough vertices selected! select a minimum of 2")

        objectSel = selection[0]
        if "." in selection[0]:
            objectSel = selection[0].split('.')[0]

        isEdgeSelection = False
        if ".e[" in selection[0]:
            isEdgeSelection = True

        skinClusterName = SkinningTools.skinCluster(objectSel, True)
        succeeded = True
        cmds.setAttr( "%s.envelope"%skinClusterName, 0)        
        try:
            cmds.skinCluster(objectSel, e=True, nw=1)
            if vertexAmount == 2 or isEdgeSelection:
                baseList = [selection]
                if isEdgeSelection:
                    baseList = self.edgesToSmooth(selection)
                
                percentage = 99.0 / len(baseList)
                for iteration, vertlist in enumerate(baseList):
                    self._shortestPolySurfaceCurvePathAverage(vertlist, skinClusterName, useDistance, weightWindow = weightAverageWindow)
                    
                    if progressBar != None:
                        cmds.setAttr( "%s.envelope"%skinClusterName, 1)
                        cmds.select(vertlist, r=1)
                        cmds.refresh()
                        progressBar.setValue(percentage*iteration)
                        QApplication.processEvents()
                        cmds.setAttr( "%s.envelope"%skinClusterName, 0)
                        
                if progressBar != None:
                    cmds.setAttr( "%s.envelope"%skinClusterName, 1)
                    progressBar.setValue(100)
                    QApplication.processEvents()
            
            else:
                lastSelected  = selection[-1]
                pointList     = [x for x in selection if x!= lastSelected ]
                meshName        = lastSelected.split('.')[0]
                
                listBoneInfluences = cmds.skinCluster(meshName, q=True, weightedInfluence=True)
                influenceSize = len(listBoneInfluences)
                
                TemporaryVertexJoints  = []
                TemporaryVertexWeights = []
                for point in pointList:
                    for bone in xrange(influenceSize):
                        pointWeights   = cmds.skinPercent(skinClusterName, point, transform = listBoneInfluences[bone], q=True, value=True)
                        if pointWeights < 0.000001:
                            continue
                        TemporaryVertexJoints.append(listBoneInfluences[bone])
                        TemporaryVertexWeights.append(pointWeights)

                totalValues   = 0.0
                AvarageValues = []
                CleanList     = []
                for i in TemporaryVertexJoints:
                    if i not in CleanList:
                        CleanList.append(i)

                for i in xrange(len(CleanList)):
                    WorkingValue = 0.0
                    for j in xrange(len(TemporaryVertexJoints)):
                        if not TemporaryVertexJoints[j] == CleanList[i]:
                            continue
                        WorkingValue += TemporaryVertexWeights[j]
                    numberOfPoints  = len(pointList)
                    AvarageValues.append((WorkingValue/numberOfPoints))
                    totalValues += AvarageValues[i];
                
                summary = 0
                for Value in xrange(len(AvarageValues)):
                    temporaryValue       = AvarageValues[Value]/totalValues
                    AvarageValues[Value] = temporaryValue
                    summary              += AvarageValues[Value]

                command = cStringIO.StringIO()
                command.write('cmds.skinPercent("%s","%s", transformValue=['%(skinClusterName, lastSelected))

                for count, skinJoint in enumerate( CleanList ):
                    command.write('("%s", %s)'%(skinJoint, AvarageValues[count]))
                    if not count == len(CleanList)-1:
                         command.write(', ')
                command.write('])')
                eval(command.getvalue())

        except Exception as e:
            cmds.warning(e)
            succeeded = False
        finally:
            cmds.setAttr( "%s.envelope"%skinClusterName, 1)
            cmds.undoInfo(cck=True)

        return succeeded

    def edgesToSmooth(self, inEdges):

        def convertToIndexList(vertList):
            indices = []
            for i in vertList:
                index = int(i.split("[")[-1].split("]")[0])
                indices.append(index)
            return indices

        def convertToVertList(indices, mesh):
            vertices = []
            for i in list(indices):
                vrt = "%s.vtx[%s]"%(mesh, i)
                
                vertices.append(vrt)
            return vertices 

        def toToEdgeNumber(vtx):
            toEdges = cmds.polyListComponentConversion( vtx, te=True )
            edges  = cmds.filterExpand(toEdges, sm=32 )
            en = []
            for e in edges:
                en.append(int(e.split(".e[")[-1].split("]")[0]))
            return en

        def checkEdgeLoop(mesh, vtx1, vtx2, first = True):
            e1n = toToEdgeNumber(vtx1)
            e2n = toToEdgeNumber(vtx2)
            found = []
            for e1 in e1n:
                for e2 in e2n:
                    edgeSel = cmds.polySelect(mesh, elp=[e1, e2], ns = True)
                    if edgeSel == None:
                        continue
                    if len(edgeSel) > 40 and first:
                        continue
                    return True

        mesh = inEdges[0].split('.')[0]
        convertToVerts = convertToIndexList(SkinningTools().convertToVertexList(inEdges))

        selectionLists = polySelectionUtils.getConnectedVerts(mesh, convertToVerts)
        list1 = convertToVertList( selectionLists[0], mesh)
        list2 = convertToVertList( selectionLists[1], mesh)

        baseList = []
        fixed = []
        for vert in list1:
            for vtx in list2:
                if not checkEdgeLoop(mesh, vert, vtx):
                    continue
                baseList.append([vert, vtx])
                fixed.extend([vert, vtx])
        
        # quick fix so it will not take the longest loop first
        for vert in list1:
            for vtx in list2:
                if vert in fixed or vtx in fixed:
                    continue

                if not checkEdgeLoop(mesh, vert, vtx, False):
                    continue
                baseList.append([vert, vtx])

        return baseList

    @dec_undo
    def Copy2MultVertex(self,selection,  secondSelection = False):
        ''' copy vertex informaton from 1 vetex to the rest of the selection, making sure all weights are the same'''
        if not len(selection) >= 2:
            cmds.error("please select more then 2 components!")
        lastSelected  = selection[-1]
        if secondSelection:
            lastSelected = selection[1]
        pointList     = [x for x in selection if x!= lastSelected ]
        baseMesh = lastSelected.split('.')[0]
        meshShapeName = cmds.listRelatives(baseMesh, s=True)[0]
        skinClusterName = SkinningTools.skinCluster(baseMesh, True)

        SkinWeightCopyInfluences = cmds.skinCluster(skinClusterName,q=True, inf=True)
        SkinWeightCopyWeights = cmds.skinPercent(skinClusterName, lastSelected , query=True, value=True )
        
        # using selection is faster then going through for loop ... thank you maya!
        cmds.select(pointList)
        command = cStringIO.StringIO()
        command.write('cmds.skinPercent("%s", transformValue=['%(skinClusterName))

        for count, skinJoint in enumerate( SkinWeightCopyInfluences ):
            command.write('("%s", %s)'%(skinJoint, SkinWeightCopyWeights[count]))
            if not count == len(SkinWeightCopyInfluences)-1:
                 command.write(', ')
        command.write('], normalize=False, zeroRemainingInfluences=True)')
        eval(command.getvalue())
        
        return True
    
    @dec_undo
    def neighbourAverage(self, components, warningPopup=True):
        '''similar to hammer skinweights, more brute force, smooths current weights according to nearest neighbour'''
        expandedVertices = self.convertToVertexList(components)
        if warningPopup and len(expandedVertices) > 1000:
            result = cmds.confirmDialog( title='warning', message='current selection can take a long time to process, continue?', button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No' )
            if result == "No":
                cmds.undoInfo(cck=True)
                return

        meshes = {}
        for expandedVert in expandedVertices:
            mesh = expandedVert.split('.')[0]
            if not mesh in meshes:
                meshes[mesh] = [expandedVert]
            else:
                meshes[mesh].append(expandedVert)

        for mesh in meshes:
            skinClusterName = SkinningTools.skinCluster(mesh)

            for vertex in meshes[mesh]:
                cmds.AverageVtxWeight(vertex, sc=skinClusterName, wt=1)

        return True

    @dec_undo
    def BoneMove(self,bone1, bone2, skin):
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
    def BoneSwitch(self,joint1, joint2, skin):
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
            
            SkinningTools().resetSkinnedJoints([joint1, joint2], skinClusterName)
        except Exception as e:
            cmds.warning(e)
            return False
        return True

    @dec_undo
    def ShowInfluencedVerts(self,skin, bones, progressBar = None):
        ''' management to show and select all vertices that are influenced by the given bones. 
        even a small influence (for example: "1.0e-17") will be shown '''
        selection = []
        percentage = 100.0/len(bones)
        
        skinClusterName =  SkinningTools.skinCluster(skin, True)
        for iteration, bone in enumerate(bones):
            # pymel version is cleaner as it doesnt do unecesary selections in between
            if _pymel:
                jointsAttached = cmds.skinCluster( skinClusterName, q=True, inf=True ) 
                if not bone in jointsAttached:
                    continue
                skinNode = PyNode(skinClusterName)
                vert_list, values = skinNode.getPointsAffectedByInfluence(bone)
                foundVerts = vert_list.getSelectionStrings()
                if len(foundVerts) == 0:
                    continue
                expandedVertices = self.convertToVertexList(foundVerts)
            else:
                cmds.select(cl=True)
                cmds.skinCluster(skin, e=True, nw=1)
                cmds.select(bone, d =True)
                SkinningTools.doCorrectSelectionVisualization(skin)
                cmds.select(cl=True)
                cmds.skinCluster( skinClusterName , e=True , siv=bone )
                expandedVertices = cmds.ls(sl=True, fl=True)
            if expandedVertices == None or len(expandedVertices) == 0:
                continue
            for select in expandedVertices:
                if not "." in select:
                    continue
                selection.append(select)

            if progressBar != None:
                progressBar.setValue(percentage*iteration)
                QApplication.processEvents()
        if progressBar != None:
            progressBar.setValue(100)
            QApplication.processEvents()
        
        SkinningTools.doCorrectSelectionVisualization(skin)
        return selection

    @dec_undo
    def switchVertexWeight(self, vertex1, vertex2):
        '''switches weight infromation between 2 vertices'''
        mesh        = vertex1.split('.')[0]
        skinClusterName = SkinningTools.skinCluster( mesh )
        cmds.skinCluster( mesh, e=True, nw=1 )
        listBoneInfluence = cmds.skinCluster( mesh, q=True, influence=True )

        boneAmount = len(listBoneInfluence)

        pointWeights1  = cmds.skinPercent(skinClusterName, vertex1, q=True, value=True)
        pointWeights2  = cmds.skinPercent(skinClusterName, vertex2, q=True, value=True)

        pointsWeightsList1 = [None] *boneAmount
        pointsWeightsList2 = [None] *boneAmount
        for j, bone in enumerate(listBoneInfluence):
            pointsWeightsList1[j] = (bone, pointWeights1[j])
            pointsWeightsList2[j] = (bone, pointWeights2[j])

        cmds.skinPercent(skinClusterName, vertex1, transformValue= pointsWeightsList2)
        cmds.skinPercent(skinClusterName, vertex2, transformValue= pointsWeightsList1)
        return True

    @dec_undo
    def removeJoints(self, skinObjects, jointsToRemove, useParent = True, delete =True, fast = False , progressBar = None):
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

    def comparejointInfluences( self, skinObjects , query = False):
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

    @dec_undo
    def hammerVerts(self, input, needsReturn = True):
        ''' simple call for the weight hammer mel command + added functionality to return vertices'''
        cmds.select(input, r=1)
        mel.eval("weightHammerVerts")
        if needsReturn:
            return self.convertToVertexList( input )
        return True

    @dec_undo
    def smoothAndSmoothNeighbours(self, input, both= False, growing = False ):
        '''will hammer the weights of the selected region and then also hammer the edge of the selected region'''
        expandedVertices  = self.convertToVertexList( input )
        meshes = {}
        for expandedVert in expandedVertices:
            mesh = expandedVert.split('.')[0]
            if not mesh in meshes:
                meshes[mesh] = [expandedVert]
            else:
                meshes[mesh].append(expandedVert)

        for mesh in meshes:
            skinClusterName   = self.skinCluster( mesh )
            if both:
                cmds.select(meshes[mesh], r=1)
                cmds.skinCluster( skinClusterName, geometry = meshes[mesh], e = True, sw = 0.000001, swi = 5, omi = 0, forceNormalizeWeights=1)
            convertedFaces    = cmds.polyListComponentConversion( meshes[mesh], tf = True )
            expandedVertices1 = self.convertToVertexList( convertedFaces )
            fixedList         =  list( set( expandedVertices1 ) ^ set( meshes[mesh] ) )
            cmds.select(fixedList, r=1)
            cmds.skinCluster(skinClusterName, geometry = fixedList,  e = True, sw = 0.000001, swi = 5, omi = 0, forceNormalizeWeights=1)

        if not growing or both == False:
            return expandedVertices
        return fixedList
    
    @dec_undo
    def removeUnusedInfluences(self, objects, progressBar = None):
        percentage = 100.0/len(objects)
        for index, obj in enumerate(objects):
            skinClusterName = SkinningTools.skinCluster( obj, True )
            if not skinClusterName:
                shape = cmds.listRelatives(obj, s=1) or None
                if progressBar:
                    progressBar.setValue(percentage * (index+1) )
                    qApp.processEvents()
                if shape != None:
                    cmds.warning("mesh object: %s has no skincluster attached!"%obj)
                continue
            attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)
            weightedJoints = cmds.skinCluster(skinClusterName, q=True, wi=True)

            nonInfluenced = []
            for attached in attachedJoints:
                if attached in weightedJoints:
                    continue
                nonInfluenced.append(attached)

            for joint in nonInfluenced:
                cmds.skinCluster(skinClusterName, e=True, ri= joint)

            cmds.flushUndo()
            if progressBar:
                progressBar.setValue(percentage * (index+1) )
                qApp.processEvents()
        
        if progressBar:
            progressBar.setValue(100.0)
            qApp.processEvents()
        return True

    @dec_undo
    def transferUvToSkinnedObject(self, mesh_source, mesh_target):
        '''transfer uv's to intermediate shape instead of final shape. clean and no deformation with bind movement'''
        shapes = cmds.listRelatives(mesh_target, ad=True, type = "mesh")
        mesh_orig = None
        for shape in shapes:
            if cmds.getAttr("%s.intermediateObject"%shape) == 0:
                continue
            mesh_orig = shape

        if mesh_orig == None:
            cmds.error("no intermediate shape found!")

        cmds.setAttr("%s.intermediateObject"%shape, 0)
        cmds.transferAttributes(mesh_source, mesh_orig,
                transferPositions=False,
                transferNormals=False,
                transferUVs=2,
                transferColors=2,
                sampleSpace=4,
                sourceUvSpace="map1",
                targetUvSpace="map1",
                searchMethod=3,
                flipUVs=False,
                colorBorders=True
            )
        cmds.setAttr("%s.intermediateObject"%shape, 1)
        cmds.delete(mesh_orig, ch=1)

        return mesh_target
       
    def freezeSkinnedMesh(self, meshes, progressBar = None):
        '''freeze transformations and delete history on skinned mesh 
        @param meshes: all meshes that need to be cleaned'''
        if len(meshes) == 0:
            cmds.error("nothing selected please select a mesh")
        
        cmds.undoInfo(stateWithoutFlush=0)
        try:
            percentage = 100.0/len(meshes)
            for index, mesh in enumerate(meshes):
                skinClusterName = SkinningTools.skinCluster( mesh, True )
                attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)

                meshShapeName = cmds.listRelatives(mesh, s=True)[0]
                outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName],  q=True)

                cmds.skinCluster(meshShapeName ,e=True, ub=True)
                cmds.delete(mesh, ch=1)
                cmds.makeIdentity(mesh, apply=True)

                newSkinClusterName = cmds.skinCluster( attachedJoints, mesh, tsb=True, bm=0, nw=1)
                cmds.SkinWeights([meshShapeName, newSkinClusterName] , nwt=outInfluencesArray)

                if progressBar:
                    progressBar.setValue(percentage * (index+1) )
                    qApp.processEvents()
        except Exception as e:
            cmds.warning(e)
            meshes = None
        finally:
            if progressBar:
                progressBar.setValue(100.0)
                qApp.processEvents()

        cmds.undoInfo(stateWithoutFlush=1)
        return meshes

    @dec_undo
    def seperateSkinnedObject(self, meshes, progressBar = None):
        '''seperates mesh by polyshells and keeps skinning information intact
        @param meshes: all meshses that need to be seperated'''
        def getShellFaces(poly):
            shells = []
            shells1 = []
            faces = set()
            total = cmds.polyEvaluate(s=True)

            for f in xrange(cmds.polyEvaluate(poly, f=True)):

                if len(shells) >= total:
                    break
                if f in faces:
                    continue

                shell = cmds.polySelect(poly, q=1, extendToShell=f)
                faces.update(shell)

                val = ".f[%d:%d]" % ( min(shell), max(shell))
                shells.append(val)
                
            return shells

        objectAmount = len(meshes)
        fullPercentage = 99.0/objectAmount

        for percentIteration, mesh in enumerate(meshes):
            shape = cmds.listRelatives(mesh, ad =True, s=True)
            shells1 = getShellFaces(mesh)
            
            if progressBar:
                total = len(shells1)
                percentage    = fullPercentage/total
                iteration     = 1;
            
            newMeshes = []
            for i, shell in enumerate(shells1):

                dup = cmds.duplicate(mesh)[0]
                newShells=[]
                for obj in shells1:
                    newShells.append(dup+obj)  
                newShells.pop(i)
                cmds.delete( newShells )
                cmds.flushUndo()
                newMeshes.append(dup)

                if progressBar:
                    progressBar.setValue((percentIteration*fullPercentage) + percentage*iteration)
                    qApp.processEvents()
                    iteration+=1;

            self.transferSkinning(mesh, newMeshes, inPlace=True)
            cmds.delete(shape)
            cmds.parent(newMeshes, mesh)

        
        if progressBar:
            progressBar.setValue(100)
            qApp.processEvents()
        return True

    @dec_undo
    def extractSkinnedShells(self, components):
        '''extracts selected components as a new mesh but keeps skininfo
        @param components: components needed to extract to include skinning, if no skincluster found only extracts mesh'''
        def convertToFaces(components):
            convertedFaces = cmds.polyListComponentConversion(components, tf=True)
            expandedFaces  = cmds.filterExpand(convertedFaces, sm=34)
            return expandedFaces        

        if len(components) > 0:
            mesh = components[0]
        else:
            mesh = components
        
        if "." in mesh:
            mesh = mesh.split(".")[0]
        
        faces = convertToFaces(components)
        dup = cmds.duplicate(mesh)[0]
        allFaces = convertToFaces(dup)

        newSel = []
        for face in faces:
            newSel.append("%s.%s"%(dup, face.split(".")[-1]))

        cmds.delete( list( set( allFaces ) ^ set( newSel ) ) )
        cmds.delete(dup, ch=1)
        if SkinningTools.skinCluster(mesh, True) == None:
            return
        self.transferSkinning(mesh, [dup], inPlace=True)
        return dup

    @dec_undo
    def combineSkinnedMeshes(self, meshes):
        '''combines meshes and keeps skin info in tact
        uses maya command for maya 2016+
        @param meshes: all the meshes that need to be combined, if a mesh has no skincluster it will not be included'''
        self.comparejointInfluences( meshes )
        
        attachedSortedJoints = None
        sourcePos = []
        sourcePosWeight = []
        for mesh in meshes:
            meshShapeName = cmds.listRelatives(mesh, s=True)[0]
            skinClusterName = SkinningTools.skinCluster(mesh, True)
            if skinClusterName == None:
                continue
            attachedJoints = cmds.skinCluster(skinClusterName, q=True, inf=True)
            
            outInfluencesArray = cmds.SkinWeights([meshShapeName, skinClusterName],  q=True)
            jointLen = len(attachedJoints)
            if attachedSortedJoints == None:
                attachedSortedJoints = attachedJoints 

            vertices = self.convertToVertexList(mesh)
            for index, vert in enumerate(vertices):
                position = cmds.xform(vert, q=True, ws=True, t=True)
                sourcePos.append(position)
                
                newList = []
                if attachedSortedJoints != attachedJoints:
                    d = {}
                    wList = outInfluencesArray[:jointLen]
                    for ids, joint in enumerate(attachedJoints) :
                        d[joint] = wList[ids]
                    for jnt in attachedSortedJoints:
                        newList.append(d[jnt])

                else:
                    newList = outInfluencesArray[:jointLen]

                sourcePosWeight.append([position, newList ])
                del outInfluencesArray[:jointLen]

        newMesh = cmds.polyUnite(meshes, ch=1, mergeUVSets= 1 )[0]
        cmds.delete(newMesh, ch=1)
        
        sourceKDTree= KDTree.construct_from_data( sourcePos )

        skinCluster = cmds.skinCluster(newMesh, attachedJoints, tsb=True)
        attachedJoints = cmds.skinCluster(skinCluster, q=True, inf=True)

        newInfluenceArray = []
        newMeshVertices = self.convertToVertexList( newMesh )
        for index, vertex in enumerate(newMeshVertices):
            pos = cmds.xform(vertex, q=True, ws=True, t=True)
            pts = sourceKDTree.query(query_point = pos, t=1)

            for positionList in sourcePosWeight:
                if pts[0] != positionList[ 0 ]:
                    continue
                newList = []
                d = {}
                for ids, joint in enumerate(attachedSortedJoints) :
                    d[joint] = positionList[1][ids]
                for jnt in attachedJoints:
                    newList.append(d[jnt])
                newInfluenceArray.extend(newList)
        
        meshShapeName = cmds.listRelatives(newMesh, s=True)[0]
        cmds.SkinWeights([meshShapeName, skinCluster[0]] , nwt=newInfluenceArray )
        return newMesh

    @dec_undo
    def keepOnlySelectedInfluences(self, fullSelection, jointOnlySelection):
        '''removes influences on selected component that are not selected in the jointsselection given
        @param fullSelection: component or mesh selection that needs te be cleaned
        @param jointOnlySelection: these are the joints that are allowed to influence the selected components/meshes'''
        
        onlyMesh = list(set(fullSelection)^set(jointOnlySelection))
        mesh = onlyMesh[0].split(".")[0]
        skinCluster =  SkinningTools.skinCluster(mesh, True)
        
        allJoints=  cmds.ls(type = "joint")
        jointsToRemove = list(set(allJoints)^set(jointOnlySelection))
        attachedJoints = cmds.skinCluster(skinCluster, q=True, inf=True)

        expandedVertices  = self.convertToVertexList(onlyMesh)

        cmds.select(expandedVertices, r=1)        
        jointsToRemoveValues = []
        for jnt in jointsToRemove:
            if not jnt in attachedJoints:
                continue
            jointsToRemoveValues.append((jnt , 0))
            
        cmds.skinPercent( skinCluster, tv =jointsToRemoveValues, normalize=True)
        return True

    @dec_undo
    def hardSkinSelectionShells(self, selection, progressBar = False):
        '''converts selection to shells, gathers weights from each shell and averages it out and give each vertex of the shell the new weights
        @param selection: input selection, any component selection will do'''

        expanded = self.convertToVertexList(selection)
        
        meshName = cmds.ls(sl=1)[0].split('.')[0]
        skinClusterName = self.skinCluster( meshName, True)
        attachedJoints  = cmds.skinCluster(skinClusterName, q=True, inf=True)
        jointAmount     = len(attachedJoints)

        objType = cmds.objectType(expanded[0])
        foundFriendDict = {}
        if not objType == "mesh":
            cmds.error("selectionShells only work on polygon components")
        vtxList = set( [int(x.split("[")[-1][:-1]) for x in expanded])
        foundFriendDict = polySelectionUtils.getConnectedVerts(meshName, vtxList) 
    
        
        if progressBar:
            percentage = 100.0/ len(foundFriendDict)
            iteration = 0
        
        for group, entries in foundFriendDict.iteritems():
            list1 = foundFriendDict[group]
            vertices= []
            vertexWeights = dict.fromkeys(attachedJoints, 0.0)
            for vertex in list1:
                
                vertexName = "%s.vtx[%s]"%(meshName, vertex)
                
                vertices.append(vertexName )
                for jnt in attachedJoints:
                    value = cmds.skinPercent( skinClusterName, vertexName ,  transform=jnt, query=True )
                    vertexWeights[jnt] += value 
            
            jointValueList = []
            for jnt in attachedJoints:
                newValue = vertexWeights[jnt] / float(len(vertices))
                jointValueList.append([jnt, newValue])
            
            cmds.select(vertices, r=1)
            cmds.skinPercent(skinClusterName,  transformValue = jointValueList, normalize=1)
            cmds.refresh()
            if progressBar:
                progressBar.setValue(percentage*iteration)
                qApp.processEvents()
                iteration+=1;
        if progressBar:
            progressBar.setValue(100.0)
        return selection

    def getMeshesInfluencedByJoint(self, currentJoints):
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