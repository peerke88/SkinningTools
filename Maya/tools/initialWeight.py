# -*- coding: utf-8 -*-
from SkinningTools.Maya.tools import mathUtils, shared, joints
from maya import cmds
from SkinningTools.UI import utils
from maya.api.OpenMaya import MVector
'''
based on robert joosten's tool:
https://github.com/robertjoosten/maya-skinning-tools/tree/master/scripts/skinningTools/initializeWeights
'''


def closestLineToPoint(lines, point):
    """Loop over all lines and find the closest point on the line from the
    provided point. After this is done the list of lines is sorted based on
    closest distance to the line.

    :param lines:
    :type lines: dict
    :param point:
    :type point: MVector
    :return: Closest lines and points ordered on distance
    :rtype: tuple
    """
    names, closestPoints = zip(*[(name, mathUtils.closestPointOnLine(line[0], line[1], point)) for name, line in lines.items()])
    return mathUtils.sortByDistance(names, point, closestPoints)


def jointsToLines(inJoints):
    """Filter the provided joints list and loop its children to generate lines
    between the parent and its children. It is possible that multiple children
    lie on the same line thinking twister joints for example. This function
    filters those out and creates lines between the twisters rather than lines
    overlapping each other.

    :param joints:
    :type joints: list
    :return: Line data
    :rtype: dict
    """
    lines = {}

    inJoints = cmds.ls(inJoints, l=True)

    positions = {j: MVector(*cmds.xform(j, query=True, ws=True, t=True)) for j in inJoints}

    for j in inJoints:
        point = positions.get(j)
        children = cmds.listRelatives(j, c=True, type="joint", f=True) or []

        childrenData = [(child, positions.get(child)) for child in children if child in inJoints and (point - positions.get(child)).length() > 0.001]

        if not childrenData:
            continue

        children, childrenPositions = zip(*childrenData)
        children, childrenPositions = mathUtils.sortByDistance(children, point, childrenPositions)

        children.reverse()
        childrenPositions.reverse()

        children.append(j)
        childrenPositions.append(point)

        iter = zip(children[1:], childrenPositions[1:], children[:-1], childrenPositions[:-1])

        for p, pPoint, t, tPoint in iter:
            if (pPoint - tPoint).length() < 0.001:
                continue

            # jName = mesh.getRootPath(j)
            # pName = mesh.getRootPath(p)
            # tName = mesh.getRootPath(t)

            cPoint = mathUtils.closestPointOnLine(point, tPoint, pPoint)
            cLength = (cPoint - pPoint).length()

            if cLength < 0.001:
                name = "{}@{}".format(p, t)
                lines[name] = [pPoint, tPoint]
            else:
                name = "{}@{}".format(j, t)
                lines[name] = [point, tPoint]

    return lines


def buildSkinCluster(inMesh, inJoints):
    """
    This function will check if the provided mesh has a skin cluster attached
    to it. If it doesn't a new skin cluster will be created with the provided
    joints as influences. No additional arguments are used to setup the skin
    cluster. This is something that needs to be done afterwards by the user.
    If a skin cluster already exists all provided joints will be added to the
    skin cluster as an influence.

    :param str mesh:
    :param list inJoints:
    :return: Skin cluster
    :rtype: str
    """
    # full path joints
    inJoints = cmds.ls(inJoints, l=True)

    # get skin cluster
    sk = shared.skinCluster(inMesh, True)
    if not sk:
        # create skin cluster
        sk = cmds.skinCluster(inJoints, inMesh, dropoffRate=0.1)[0]

    else:
        # make sure all provided joints are an influence of the skin cluster
        # that is already attached to the mesh
        joints.addCleanJoint(inJoints, inMesh, progressBar=None)

    return sk


def setInitialWeights(inMesh, inJoints, iterations=3, projection=0, blend=False, blendMethod=None, progressBar=None):
    """
    The set initial weights function will set the skin weights on a mesh and
    the isolate only the provided components of any. Each vertex will only
    have one influence, the best influence is determined by generating lines
    for each of the joints and determining the line closest to the vertex. The
    vertex points can be altered as well using laplacian smoothing operations
    to details or overlapping and the project can be used to project the point
    along its normal to get it closer to the preferred joints.

    :param mesh:
    :type mesh:str
    :param joints:
    :type joints:list
    :param iterations: Number of smoothing iterations
    :type iterations:int
    :param projection: Value between 0-1
    :type projection:float
    """
    sk = buildSkinCluster(inMesh, inJoints)
    dag = shared.getDagpath(inMesh)
    projection = mathUtils.clamp(projection, 0.0, 1.0)

    lines = jointsToLines(inJoints)
    connections = shared.getConnectedVerticesMapper(dag)
    points = shared.getPoints(dag)
    components = range(len(points))

    normals = shared.getNormals(inMesh)
    points = mathUtils.laplacianSmoothing(points, connections, iterations)
    normals = mathUtils.laplacianSmoothing(normals, connections, iterations)
    blendMethod = mathUtils.getTweeningMethod(blendMethod) if blendMethod else None
    percentage = 99.0 / len(points)
    allJoints = joints.getInfluencingJoints(sk)
    amountJoints = len(allJoints)

    utils.setProgress(0, progressBar, "building weights for %s" % inMesh)
    weightData = [0] * (len(allJoints) * len(points))
    for i in components:
        point = points[i]
        normal = normals[i].normal()
        vertex = "{}.vtx[{}]".format(inMesh, i)

        names, closestPoints = closestLineToPoint(lines, point)

        if projection:
            closestPoint = closestPoints[0]
            closestDistance = (point - closestPoint).length()

            point = point + (normal * closestDistance * projection * -1)

            names, closestPoints = closestLineToPoint(lines, point)

        influenceName = names[0]
        influenceParent, influenceChild = influenceName.split("@")

        # transformValue = [[influenceParent, 1]]
        parameter = 0
        if blend:
            a, b = lines.get(influenceName)
            parameter = mathUtils.parameterOfPointOnLine(a, b, closestPoints[0])

            if blendMethod:
                parameter = blendMethod(parameter)

        weightData[(i * amountJoints) + allJoints.index(influenceParent)] = 1 - parameter
        weightData[(i * amountJoints) + allJoints.index(influenceChild)] = parameter
        utils.setProgress(i * percentage, progressBar, "processing: %s" % vertex)
    shared.setWeights(inMesh, weightData)
    utils.setProgress(100, progressBar, "build setup for %s" % inMesh)
