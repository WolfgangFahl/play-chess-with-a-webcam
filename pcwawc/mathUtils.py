import math
from math import sin, cos
import numpy as np


def intersectHoughLines(line, crossline):
    lx1, ly1, lx2, ly2 = line[0]
    cx1, cy1, cx2, cy2 = crossline[0]
    intersectLine = intersect((lx1, ly1), (lx2, ly2), (cx1, cy1), (cx2, cy2))
    return intersectLine


# see also https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
def intersect(A, B, C, D):
    """ Finds the intersection of two lines represented by four points.

    @parameter A: point #1, belongs to line #1
    @parameter B: point #2, belongs to line #1
    @parameter C: point #3, belongs to line #2
    @parameter D: point #4, belongs to line #2

    @returns: None if lines are parallel, tuple (x, y) with intersection point"""
    if A is None or B is None or C is None or D is None:
        return None
    Pxn = (A[0] * B[1] - A[1] * B[0]) * (C[0] - D[0]) - (A[0] - B[0]) * (C[0] * D[1] - C[1] * D[0])
    Pyn = (A[0] * B[1] - A[1] * B[0]) * (C[1] - D[1]) - (A[1] - B[1]) * (C[0] * D[1] - C[1] * D[0])
    Pdenom = float((A[0] - B[0]) * (C[1] - D[1]) - (A[1] - B[1]) * (C[0] - D[0]))
    np.seterr(all='raise')
    try:
        Px = Pxn / Pdenom
        Py = Pyn / Pdenom
    except FloatingPointError:
        return None
    except ZeroDivisionError:
        return None
    if np.isnan(Px) or np.isnan(Py):
        return None
    return (int(Px), int(Py))


def distance(A, B):
    """ Finds the distance between two points

    @parameter A: point #1
    @parameter B: point #2

    @returns: distance between the points A and B"""
    return math.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)


def middlePoint(A, B):
    """ Finds the point between two points

    @parameter A: point #1
    @parameter B: point #2

    @returns: typle(x,y) halfway from A toward B"""
    return (int((B[0] + A[0]) / 2), int((B[1] + A[1]) / 2))


def getIndexRange(hist, minValue, maxValue):
    """ # get the range of the histogramm where the value are between minValue and maxValue"""
    fromIndex = -1
    toIndex = len(hist)
    for index, value in enumerate(hist):
        if value >= minValue and fromIndex < 0:
            fromIndex = index
        if value >= minValue and value <= maxValue and index < len(hist):
            toIndex = index
    return (fromIndex, toIndex)


def median(inList):
    """ Computes the median of a list.
    NOTE: The list must be sorted!!! """
    if len(inList) == 1:
        return inList[0]
    if len(inList) == 0:
        return 0.
    if not len(inList) % 2:
        return (inList[len(inList) // 2] + inList[len(inList) // 2 - 1]) / 2.0
    return inList[len(inList) // 2]


def getRotationAndTranslationMatrix(rotation, translation):
    """Get a numpy transform matrix representing a rotation followed by a
    translation.

    rotation: angle (radians)
    translation: 2-tuple representing (x, y)"""
    return np.array([cos(-rotation), -sin(-rotation), translation[0],
                     sin(-rotation), cos(-rotation), translation[1],
                     0, 0, 1]
                    ).reshape((3, 3))
