import math
from math import sin, cos, pi
import numpy as np

def intersect(A, B, C, D):
    """ Finds the intersection of two lines represented by four points. 

    @parameter A: point #1, belongs to line #1
    @parameter B: point #2, belongs to line #1
    @parameter C: point #3, belongs to line #2
    @parameter D: point #4, belongs to line #2

    @returns: None if lines are parallel, tuple (x, y) with intersection point"""
    Pxn = (A[0]*B[1] - A[1]*B[0])*(C[0] - D[0]) - (A[0] - B[0])*(C[0]*D[1] - C[1]*D[0])
    Pyn = (A[0]*B[1] - A[1]*B[0])*(C[1] - D[1]) - (A[1] - B[1])*(C[0]*D[1] - C[1]*D[0])
    Pdenom = float((A[0] - B[0]) * (C[1] - D[1]) - (A[1] - B[1]) * (C[0] - D[0]))
    try:
        Px = Pxn / Pdenom
        Py = Pyn / Pdenom
    except ZeroDivisionError:
        return None

    return (int(Px), int(Py))
    
def distance(A, B):
    """ Finds the distance between two points
    
    @parameter A: point #1
    @parameter B: point #2
    
    @returns: distance between the points A and B"""
    return math.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)
    
def middlePoint(A, B):
    """ Finds the point between two points
    
    @parameter A: point #1
    @parameter B: point #2
    
    @returns: typle(x,y) halfway from A toward B"""
    return (int((B[0]+A[0])/2), int((B[1]+A[1])/2))

def median(inList):
    """ Computes the median of a list.
    NOTE: The list must be sorted!!! """
    if len(inList) == 1:
        return inList[0]
    if len(inList) == 0:
        return 0.
    if not len(inList) % 2:
        return (inList[len(inList) / 2] + inList[len(inList) / 2 - 1]) / 2.0
    return inList[len(inList) / 2]

def getRotationAndTranslationMatrix(rotation, translation):
    """Get a numpy transform matrix representing a rotation followed by a
    translation.

    rotation: angle (radians)
    translation: 2-tuple representing (x, y)"""
    return np.array([cos(-rotation), -sin(-rotation), translation[0],
                     sin(-rotation),  cos(-rotation), translation[1],
                     0,               0,               1]
                    ).reshape((3,3))

def findBoundingSkewedSquare(pt1, pt2, rotations):
    """Finds the 4 points forming the polygon bounding the two points and the
    rotation.

    pt1 & pt2: (x, y)
    rotation: radian angle between -pi/2 and pi/2"""
    
    # Define the reference and transform matrixes
    points = np.transpose(np.array(
        [pt1[0], pt1[1], 1,
         pt2[0], pt2[1], 1]
        ).reshape((2,3)))
    chRepereM1 = getRotationAndTranslationMatrix(-rotations[0], (-pt1[0], -pt1[1]))
    chRepereM2 = getRotationAndTranslationMatrix(rotations[0], (pt1[0], pt1[1]))

    # Difference between angle1 - pi/2 and angle2.
    # pi/24 is a random magic number that seems to approximate the difference between
    # the angles at the center of the image and at the edge.
    # (Poor-man inverse projective transform)
    shearFactor = -(rotations[0] - (rotations[0] - pi/2 - rotations[1])/2.)
    shearYFactor = -(rotations[0] - (rotations[0] - pi/2 - rotations[1])/2.)
    print(shearFactor, shearYFactor)
    shearM = np.array(
        [1,            shearFactor, 0,
         shearYFactor, 1,           0,
         0,            0,           1]
        ).reshape((3,3))

    # Rotate the pt2 to a rotation-free reference
    chRepereM1 = np.dot(chRepereM1, shearM)
    homoPt2 = np.dot(chRepereM1, points)
    homoPt2 = np.array(
        [homoPt2[0][1], homoPt2[1][0],
         homoPt2[0][0], homoPt2[1][1],
         1,             1]
        ).reshape((3,2))

    # Rotate the new coordinates to get to the original reference
    newpt1, newpt2 = np.transpose(np.dot(chRepereM2, homoPt2))
    return (pt1,
            (newpt1[0], newpt1[1]),
            (newpt2[0], newpt2[1]),
            pt2)