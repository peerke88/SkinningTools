from maya.api.OpenMaya import MVector, MPoint, MMatrix, MQuaternion

def toVec3(inObject):
    return MVector(inObject[0], inObject[1], inObject[2])


def toVec3List(inList):
    veclist = []
    for obj in inList:
        veclist.append(toVec3(obj))
    return veclist


def toPoint(inObject):
    vec3 = toVec3(inObject)
    retVec = MPoint(vec3)
    return retVec


def matrixToFloatList(matrix):
    return [matrix[i] for i in xrange(16)]


def floatToMatrix(floatList):
    vec1 = toVec3(floatList[0: 3])
    vec2 = toVec3(floatList[4: 7])
    vec3 = toVec3(floatList[8: 11])
    vec4 = toVec3(floatList[12: 15])
    return vectorsToMatrix((vec1, vec2, vec3, vec4))

def vectorsToMatrix(vectorList):
    baseMatrix = MMatrix()
    for i, vector in enumerate(vectorList):
        for j in xrange(3):
            baseMatrix.setElement(i, j, vector[j])
    return baseMatrix

def setMatPos(matrix, vector):
    for i in xrange(3):
        matrix.setElement(3, i, vector[i])
    return matrix

def getVectorFromMatrix(matrix, index):
    if isinstance(matrix, MMatrix):
        vec = toVec3([matrix.getElement(index, 0), matrix.getElement(index, 1), matrix.getElement(index, 2)])
    else:
        vec = toVec3([matrix.get(index, 0), matrix.get(index, 1), matrix.get(index, 2)])
    return vec
