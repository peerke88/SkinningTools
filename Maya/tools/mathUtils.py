from maya.api.OpenMaya import MVector, MPoint, MMatrix, MQuaternion
from maya import cmds
from SkinningTools.Maya.tools import enumerators
import math

def toVec3(inObject):
    """ convert a list or tuple to an MVector

    :param inObject: list of floats or ints
    :type inObject: list
    :return: vector created from list
    :rtype: MVector
    """
    return MVector(inObject[0], inObject[1], inObject[2])


def toVec3List(inList):
    """ convenience function convert a list of floatlists or intlists to a list of MVectors

    :param inList: list of lists
    :type inList: list
    :return: list of MVectors
    :rtype: list
    """
    veclist = []
    for obj in inList:
        veclist.append(toVec3(obj))
    return veclist


def toPoint(inObject):
    """ convert a list or tuple to an MPoint

    :param inObject: list of floats or ints
    :type inObject: list
    :return: point created from list
    :rtype: MPoint
    """
    vec3 = toVec3(inObject)
    retVec = MPoint(vec3)
    return retVec


def matrixToFloatList(matrix):
    """ convert MMatrix to a list of 16 floats

    :param matrix: OpenMaya MMatrix to convert
    :type matrix: MMAtrix
    :return: list of 16 floats gathered from a matrix
    :rtype: list
    """
    return [matrix[i] for i in range(16)]


def floatToMatrix(floatList):
    """ convert list of 16 floats to an OpenMaya MMatrix

    :param floatList: list of at least 16 floats/ints to convert to a matrix
    :type floatList: list
    :return: the OpenMaya MMatrix to be used in matrix calculations
    :rtype: MMatrix
    """
    vec1 = toVec3(floatList[0: 3])
    vec2 = toVec3(floatList[4: 7])
    vec3 = toVec3(floatList[8: 11])
    vec4 = toVec3(floatList[12: 15])
    return vectorsToMatrix((vec1, vec2, vec3, vec4))


def vectorsToMatrix(vectorList):
    """ convert list of OpenMaya MVector to an OpenMaya MMatrix

    :param vectorList: list of at least 3 MVectors (to make sure the rotation matrix is set)
    :type vectorList: list
    :return: the OpenMaya MMatrix to be used in matrix calculations
    :rtype: MMatrix
    """
    baseMatrix = MMatrix()
    for i, vector in enumerate(vectorList):
        for j in range(3):
            baseMatrix.setElement(i, j, vector[j])
    return baseMatrix


def setMatPos(matrix, vector):
    """ set the positon of a given OpenMaya MMatrix by a vector/ float list

    :param matrix: the matrix to translate
    :type matrix: MMatrix
    :param vector: the vector position to give the matrix
    :type vector: MVector
    :return: the OpenMaya MMatrix to be used in matrix calculations
    :rtype: MMatrix
    """
    for i in range(3):
        matrix.setElement(3, i, vector[i])
    return matrix


def getVectorFromMatrix(matrix, index):
    """ get the vectors of which the matrix is made (index 3 will give the position)

    :param matrix: the matrix to translate
    :type matrix: MMatrix
    :param index: index of row to grab information from
    :type index: int
    :return: the MVector that represents the row of given index from the matrix
    :rtype: MVector
    """
    if isinstance(matrix, MMatrix):
        vec = toVec3([matrix.getElement(index, 0), matrix.getElement(index, 1), matrix.getElement(index, 2)])
    else:
        vec = toVec3([matrix.get(index, 0), matrix.get(index, 1), matrix.get(index, 2)])
    return vec


def measureLength(object1, object2):
    """ get the length bewtween 2 given objects translations

    :param object1: 1st object to get transformation data from
    :type object1: string
    :param object2: 2nd object to get transformation data from
    :type object2: string
    :return: length between 2 given objects
    :rtype: float
    """
    pos1 = MVector(*cmds.xform(object1, q=True, ws=True, t=True))
    pos2 = MVector(*cmds.xform(object2, q=True, ws=True, t=True))
    return (pos1 - pos2).length()


def getCenterPosition(inPositions):
    """ get the center position from all input positions

    :param inPositions: list of vectors that represent a cluster of positions
    :type inPositions: list
    :return: center position of current given positions
    :rtype: MVector
    """
    amount = len(inPositions)
    baseVec = MVector()
    for pos in toVec3List(inPositions):
        baseVec += pos

    return baseVec / amount

def getSceneUp(asIndex=True):
    """function to get current scene up axis

    :param asIndex: if `True` will return the index of current upvector, if `False` will return string representation
    :type asIndex: bool
    :return: scene up axis
    :rtype: int,string
    """
    upAxis = cmds.upAxis(q=1, axis=True)
    if asIndex:
        return "xyz".index(upAxis)
    return upAxis

def lookAt(base, aim, up=None, primaryAxis=toVec3((1, 0, 0)), secondaryAxis=toVec3((0, 1, 0)), invertTerz=False):
    """convert a minimal of 2 positions to an aim matrix 

    :param Base: base position of the mmatrix 
    :type Base: MVector
    :param aim: position the matrix needs to point towards 
    :type aim: MVector
    :param up: poition that the matrix needs to identify the secondary lookat 
    :type up: MVector
    :param primaryAxis: vector used as the aim for current matrix 
    :type primaryAxis: MVector
    :param secondaryAxis: vector used as the up axis 
    :type secondaryAxis: MVector
    :return: the matrix created from 2 vectors
    :rtype: MMatrix
    """
    jointPos = toVec3(base)
    aimPos = toVec3(aim)

    upPos = toVec3((0, 0, 0))
    if isinstance(up, MVector):
        upPos = up
    else:
        upPos[getSceneUp()] += 1

    vAim = (aimPos - jointPos)
    vUp = (upPos - jointPos)

    vX = vAim.normal()
    if getSceneUp() == 1:
        if invertTerz:
            vZ = (vUp ^ vAim).normal()
            vY = vAim.normal() ^ vZ
        else:
            vZ = (vAim ^ vUp).normal()
            vY = vZ ^ vAim.normal()
    else:
        if invertTerz:
            vZ = (vAim.normal() ^ vUp.normal()).normal()
            vY = vZ ^ vAim.normal()
        else:
            vZ = (vUp.normal() ^ vAim.normal()).normal()
            vY = vAim.normal() ^ vZ

    rotations = [vX, vY, vZ]

    if enumerators.AxisEnumerator.isX(primaryAxis):
        if enumerators.AxisEnumerator.isY(secondaryAxis):
            rotations = [vX, vY, vZ]
        elif enumerators.AxisEnumerator.isZ(secondaryAxis):
            rotations = [vX, vZ, vY]
    elif enumerators.AxisEnumerator.isY(primaryAxis):
        if enumerators.AxisEnumerator.isX(secondaryAxis):
            rotations = [vY, vX, vZ]
        elif enumerators.AxisEnumerator.isZ(secondaryAxis):
            rotations = [vY, vZ, vX]
    elif enumerators.AxisEnumerator.isZ(primaryAxis):
        if enumerators.AxisEnumerator.isX(secondaryAxis):
            rotations = [vZ, vX, vY]
        elif enumerators.AxisEnumerator.isY(secondaryAxis):
            rotations = [vZ, vY, vX]

    if enumerators.AxisEnumerator.isNegative(primaryAxis):
        rotations[0] *= -1
    if enumerators.AxisEnumerator.isNegative(secondaryAxis):
        rotations[1] *= -1

    rotations.append(jointPos)

    return vectorsToMatrix(rotations)

def clamp( value, minValue, maxValue ):
    return max( min( value, maxValue ), minValue )
    
def closestPointOnLine(a, b, point):
    """
    Get the closest point on a line. The line is defined by the provided a
    and b point. The point is the point in space that is used to find the
    closest point on the line.

    :param a: point a of the line
    :type a: MVector
    :param b:  point b of the line
    :type b: MVector
    :param point: the point gather the information from
    :type point: MVector
    :return: Closest point on line
    :rtype: MVector
    """
    ap = point - a
    ab = b - a

    length = ab.length() ** 2
    dot = ap * ab
    distance = dot / length

    if distance < 0:
        return a
    elif distance > 1:
        return b
    else:
        return a + ab * distance


def parameterOfPointOnLine(a, b, point):
    """
    Get the parameter of a point on a line. For this function to give a
    correct result it is important that the provided point already lies on the
    line. The :func:`closestPointOnLine` can be used to get that point on the
    line.

    :param a: point a on the line
    :type a: MVector
    :param b: point b on the line
    :type b: MVector
    :param point: the position in space to check the parameter on the line
    :type point: MVector
    :return: Parameter of the point on the line
    :rtype: float
    """
    ap = point - a
    ab = b - a

    parameter = ap.length() / ab.length()
    return parameter

def sortByDistance(nodes, point, points):
    """
    Sort the provided nodes list based on the distance between the point and
    the points. With the nodes sorted from shortest distance to longest. It
    is expected that the order of the nodes link with the order of the points.

    :param nodes: 
    :type nodes: list
    :param point:
    :type point: MVector
    :param points:
    :type points: list
    :return: Sorted node list and sorted points list
    :rtype: tuple(list, list)
    """
    iter = zip(nodes, points)
    iter.sort(key=lambda x: (x[1] - point).length())

    nodes, points = zip(*iter)
    return list(nodes), list(points)

def laplacianSmoothing(vectors, connected, iterations=3):
    """ Perform a laplacian smoothing on the provided vectors based on a
    connection mapper. The position of the new vector is set based on the
    index of that vector and its connected vectors based on the connected
    indices. The new vector position is the average position of the connected
    vectors.

    :param vectors:
    :type vectors: list
    :param connected:
    :type connected: dict
    :param iterations:
    :type iterations: int
    :return: Smoothed vectors
    :rtype: list
    """
    length = len(vectors)
    vectors = vectors[:]

    for i in xrange(iterations):
        copy = vectors[:]

        for j in xrange(length):
            indices = connected.get(j)
            neighbours = [copy[i] for i in indices]
            vectors[j] = getCenterPosition(neighbours)

    return vectors

def getTweeningMethod(method):
    """Get the tweening method from a string, if the function doesn't exists
    None will be returned.

    :return: Tweening function
    :rtype: func/None
    """
    _dict = getTweeningMethods()
    return _dict[method] or None


def getTweeningMethods():
    """Get all of the available tweening methods.

    :return: Tweening methods
    :rtype: dict
    """
    _dict = { "easeInOutQuadratic" : easeInOutQuadratic, 
              "easeInOutCubic" : easeInOutCubic, 
              "easeInOutQuartic" : easeInOutQuartic, 
              "easeInOutQuintic" : easeInOutQuintic, 
              "easeInOutSinusoidal" : easeInOutSinusoidal, 
              "easeInOutExponential" : easeInOutExponential, 
              "easeInOutCircular" : easeInOutCircular}
    return _dict

def easeInOutQuadratic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**2
    else:
        n -= 1
        return -0.5 * (n*(n-2) - 1)


def easeInOutCubic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**3
    else:
        n -= 2
        return 0.5 * (n**3 + 2)


def easeInOutQuartic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**4
    else:
        n -= 2
        return -0.5 * (n**4 - 2)


def easeInOutQuintic(n):
    n *= 2
    if n < 1:
        return 0.5 * n**5
    else:
        n -= 2
        return 0.5 * (n**5 + 2)


def easeInOutSinusoidal(n):
    return -0.5 * (math.cos(math.pi * n) - 1)


def easeInOutExponential(n):
    n *= 2
    if n < 1:
        return 0.5 * math.pow(2, 10 * (n - 1))
    else:
        n -= 1
        return -math.pow( 2, -10 * n) + 2


def easeInOutCircular(n):
    n *= 2
    if n < 1:
        return -0.5 * (math.sqrt(1 - n**2) - 1)
    else:
        n = n - 2
        return 0.5 * (math.sqrt(1 - n**2) + 1)