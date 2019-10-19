#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from Video import Video
from math import sin, cos, sqrt, pi, atan2, degrees
import cv2
import cv2 as cv
import numpy as np
from collections import deque
import bisect

# Local imports
from MovementDetector import MovementDetector
from mathUtils import (intersect, distance, median, findBoundingSkewedSquare,
                       getRotationAndTranslationMatrix,getIndexRange)

CHESSCAM_PARZEN_THRESHOLD = 5
CHESSCAM_ORIENTATION_SMOOTHING = 5
CHESSCAM_COORDINATES_SMOOTHING = 8

smoothFunc = lambda x: sum(x) / float(len(x))


class BadSegmentation(Exception):
    pass

# Board Finder
class BoardFinder(object):
    debug=True
    debugShowTime=1000
    dotHSVRanges=[(70, 120), (85, 255), (0, 255)]

    # construct me from the given input Image
    def __init__(self, inImage):
        self.video=Video()
        self.frame = inImage
        self.height,self.width = self.frame.shape[:2]
        # Green indicator dot has hue between ~70 and ~120, saturation  between 85 and 255 and Luminosity value between 0 and 255.
        # take a picture or your own dot and calibrate using the commandline option
        if BoardFinder.debug:
            print("BoardFinder for %dx%d image" % (self.width,self.height))

    def prepare(self):
        # Init smoothing angle
        self.smoothOrientation = deque([], CHESSCAM_ORIENTATION_SMOOTHING)
        self.smoothCoordinates = deque([], CHESSCAM_COORDINATES_SMOOTHING)

        # Find the board the first time
        self.updateImage(self.frame)

        # Temporary rotation
        self.initialRotation = 0

        # Find the rotation of the board
        side = self.getBlackMaxSide(self.GetFullImageBoard()[0])

        # 0:top,1:left,2:bottom,3:right.
        optionsRotation = {0: 0,
                           1: -90,
                           2: 180,
                           3: 90}
        # 0:top,1:left,2:bottom,3:right. (x,y) offset of dominator
        optionsDominator = {0: (0, -1),
                            1: (-1, 0),
                            2: (0, 1),
                            3: (1, 0)}
        #Black's initial position sets the correction move to place black team at the top.
        self.initialRotation = optionsRotation[side]
        self.dominatorOffset = optionsDominator[side]

    def getDominatorOffset(self):
        return self.dominatorOffset

    def updateImage(self, inFrame):
        """Adds a new image to the boardFinder algorithms.
        This performs an Hough Transform and HSV conversion to the image and
        computes the orientation and coordinates from these."""

        if self.frame is not None:
            self.lines=self.video.houghTransform(self.frame)
            if BoardFinder.debug:
                print ("found %d lines" % (self.lines.size))
            self.BoardOrientation = self.DetectBoardOrientation()
            if all(self.BoardOrientation):
                self.boardCoordinates = self.GetChessBoardCoordinates(
                    smoothFunc(list(zip(*self.smoothOrientation))[0]))


    def DetectBoardOrientation(self):
        """Finds the two dominants angles of the Hough Transform.

        Returns: 2-tuple containing the two dominant angles. (None, None) if
                 none were found."""
        # Ensure Hough lines were already found
        if len(self.lines) <= 0:
            return (None, None)

        # https://answers.opencv.org/question/2966/how-do-the-rho-and-theta-values-work-in-houghlines/
        # get the theta values
        slopes = sorted([line[0][1] for line in self.lines])
        # Parzen window (KernelDensityEstimator) using a Rect function, comonly named a moving average
        # Perform frequence to time conversion, signal analysis FTW
        # KernelSize is the dynamic range kernel size (bin length)
        KernelSize = pi / 64.
        KDE = {}
        for slope in set(slopes):
            beginElement = bisect.bisect_left(slopes, slope - KernelSize)
            endElement = bisect.bisect_right(slopes, slope + KernelSize)
            # Threshold
            if endElement - beginElement > CHESSCAM_PARZEN_THRESHOLD:
                KDE[slope] = endElement - beginElement
        bins = sorted(KDE.items())
        if len(bins) <= 0:
            return (None, None)

        # Let's find the maximum number of lines in this range
        angleMostOftenDetected = max(bins, key=lambda x: x[1])
        if BoardFinder.debug:
            print ("the most often detected line angle is %d°" % degrees(angleMostOftenDetected[0]))

        # Theil-Sen estimator for noise robustness
        # why not use https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.mstats.theilslopes.html ?
        MaximumChanceAngle = median([a[0] for a in bins if a[1] == angleMostOftenDetected[1] and abs(a[0] - angleMostOftenDetected[0]) < KernelSize])

        # Get second angle
        try:
            otherAngle = max((a for a in bins if a[0] > angleMostOftenDetected[0] + 0.2 or a[0] < angleMostOftenDetected[0] - 0.2), key=lambda x: x[1])
            MaximumChanceAngle2 = median([a[0] for a in bins if a[1] == otherAngle[1] and abs(a[0] - otherAngle[0]) < KernelSize])
        except:
            # TODO: Don't write generic excepts!!!
            return (None, None)

        retValue = sorted([MaximumChanceAngle, -abs(MaximumChanceAngle2)],
                          key=lambda x: abs(x))

        if BoardFinder.debug:
            print ("Boardorientation %f.2° - %f.2°" % (degrees(retValue[0]),degrees(retValue[1])))
        # Record return value for smoothing purposes
        self.smoothOrientation.appendleft(retValue)
        return retValue

    def GetChessBoardCoordinates(self, rotation):
        """Gets the four points that defines the rectangle where the chessboard
        is bound.

        Returns: 4-tuple of 2-tuples containing (x, y) values of the 4 corners
                 of the chessboard."""
        # Blur image and convert it to HSV
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
        self.hsv =cv2.blur(self.frame,(4,4))
        if BoardFinder.debug:
            self.video.showImage(self.hsv,"blur",True,BoardFinder.debugShowTime)

        # De-Rotate the hsv version of the image to support rotated chessboards
        # Because marker detection is really cheaply done
        rotationMatrix = getRotationAndTranslationMatrix(-rotation, (0, 0))
        hsv2 = cv2.warpPerspective(np.asarray(self.hsv[:,:]),
                                   rotationMatrix,
                                   (self.width, self.height))
        if BoardFinder.debug:
            self.video.showImage(hsv2,"warp",True,BoardFinder.debugShowTime)
        self.hsv = cv2.cvtColor(hsv2, cv2.COLOR_BGR2HSV)
        # Threshold the HSV value according to the cornerMarker being used
        ht,st,vt=BoardFinder.dotHSVRanges
        # ignore the Luminosity range
        self.debugimg = cv2.inRange(self.hsv,
                                    np.array([ ht[0], st[0],   0], np.uint8),
                                    np.array([ ht[1], st[1], 255], np.uint8))
        contours, hierarchy = cv2.findContours(self.debugimg,
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        mini, maxi = (self.width, self.height), (0, 0)
        ur, ll = (0, 0), (0, 0)
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True)
            cnt = cv2.approxPolyDP(cnt, 0.01*cnt_len, True)
            for a in cnt:
                if sqrt(a[0][0]**2 + a[0][1]**2) < sqrt(mini[0]**2 + mini[1]**2):
                    mini = (a[0][0], a[0][1])
                if sqrt((a[0][0] - self.width)**2 + (a[0][1] - self.height)**2) < sqrt((maxi[0] - self.width)**2 + (maxi[1] - self.height)**2):
                    maxi = (a[0][0], a[0][1])
                if sqrt((a[0][0] - self.width)**2 + a[0][1]**2) < sqrt((ur[0] - self.width)**2 + ur[1]**2):
                    ur = (a[0][0], a[0][1])
                if sqrt(a[0][0]**2 + (a[0][1] - self.height)**2) < sqrt(ll[0]**2 + (ll[1] - self.height)**2):
                    ll = (a[0][0], a[0][1])

        if BoardFinder.debug:
            self.video.showImage(self.debugimg,"debug image",True,BoardFinder.debugShowTime)
        # Debug
        if BoardFinder.debug:
            rectImage=self.frame.copy()
            cv2.circle(rectImage, mini, 10, color=(255, 255, 0), thickness=6)
            cv2.circle(rectImage, maxi, 10, color=(255, 255, 0), thickness=3)
            self.video.showImage(rectImage,"board corners",True,BoardFinder.debugShowTime)

        # De-rotate the points computed
        points = np.array(
                    [mini[0], ur[0], ll[0], maxi[0],
                     mini[1], ur[1], ll[1], maxi[1],
                     1,       1,     1,     1]
                    ).reshape((3,4))
        deRotationMatrix = getRotationAndTranslationMatrix(rotation, (0, 0))
        mini, ur, ll, maxi = np.transpose(np.dot(deRotationMatrix, points))

        # Set return value and keep it for smoothing purposes
        retValue = (mini[0], mini[1]), \
                   (ur[0], ur[1]), \
                   (ll[0], ll[1]), \
                   (maxi[0], maxi[1])
        if BoardFinder.debug:
            rectImage=self.frame.copy()
            minx,miny=mini[:2]
            maxx,maxy=maxi[:2]
            print (retValue)
            cv2.rectangle(rectImage,(int(minx),int(miny)),(int(maxx),int(maxy)),color=(0, 255, 0), thickness=3)
            self.video.showImage(rectImage,"board coordinates",True,BoardFinder.debugShowTime)
        self.smoothCoordinates.appendleft(retValue)
        return retValue

    # calibrate the corner dot indicator from the given image
    def calibrateCornerMarker(self,dotImage):
        histSize = 256
        histRange = (0, 256) # the upper boundary is exclusive
        planes=cv2.split(dotImage)
        indexRanges=[]
        for channel in range(0,3):
            hist=cv2.calcHist(planes,[channel],None,[histSize], histRange, accumulate=False)
            indexRanges.append(getIndexRange(hist,1,255))
        if BoardFinder.debug:
            print(indexRanges)
        return indexRanges

    def GetFullImageBoard(self, rectCoordinates=None, rotations=None):
        """Applies the homography needed to make the bounding rectangle
        defined by rectCoordinates and rotation become the full size of the
        image.

        rectCoordinates: Position of the minimum and maximum point of the
            bounding rectangle. Must be of form: ((x1, y1), (x2, y2))
        rotation: Rotation angle in radians.

        Returns: A list of two images containing only the chessboard.
            The first one is a debug image and the second one is the original"""

        if rotations == None:
            rotations = [sum(y) / float(len(y)) for y in zip(*self.smoothOrientation)]
        if rectCoordinates == None:
            rectCoordinates = []
            for groupedCoordinates in zip(*self.smoothCoordinates):
                smoothDataTmp = [0, 0]
                for thisCoordinate in groupedCoordinates:
                    smoothDataTmp[0] += thisCoordinate[0]
                    smoothDataTmp[1] += thisCoordinate[1]
                rectCoordinates.append(tuple([a / float(len(groupedCoordinates)) for a in smoothDataTmp]))

        points = tuple(rectCoordinates)

        # Define homography references points sequences
        try:
            src = np.array(points, np.float32).reshape((4, 2))
        except ValueError:
            raise BadSegmentation
        dst = np.array([0, 0,
                        self.width, 0,
                        0, self.height,
                        self.width, self.height], np.float32).reshape((4, 2))

        # Find the homography matrix and apply it
        H, status = cv2.findHomography(src, dst, 0)
        self.debugimg = cv2.warpPerspective(self.frame,
                                            H,
                                            (self.width, self.height))

        cv2.circle(self.frame, (int(points[0][0]), int(points[0][1])), 1, color=(0, 255, 255),thickness=5)
        cv2.circle(self.frame, (int(points[1][0]), int(points[1][1])), 1, color=(0, 255, 0), thickness=5)
        cv2.circle(self.frame, (int(points[2][0]), int(points[2][1])), 1, color=(0, 0, 255), thickness=5)
        cv2.circle(self.frame, (int(points[3][0]), int(points[3][1])), 1, color=(255, 255, 255), thickness=5)

        self.debugimg = self.rotateImage(self.debugimg)
        if BoardFinder.debug:
            self.video.showImage(self.debugimg,"debug",True,BoardFinder.debugShowTime)
            self.video.showImage(self.frame,"frame",True,BoardFinder.debugShowTime)

        return [self.debugimg, self.frame]


    def getBlackMaxSide(self, colorImage):
        """This function returns the side of black's team, if game is at
        starting position. 0:top, 1:left, 2:bottom, 3:right"""

        # convert to HSV for simpler handling
        # see e.g. https://stackoverflow.com/questions/17063042/why-do-we-convert-from-rgb-to-hsv
        # Convert BGR to HSV
        tmp = cv2.cvtColor(colorImage, cv2.COLOR_BGR2HSV)

        H,W = tmp.shape[:2]

        top = self.video.getSubRect(tmp, (0, 0, W, H//4))
        left = self.video.getSubRect(tmp, (0, 0, W//4, H))
        bottom = self.video.getSubRect(tmp, (0, H*3//4, W, H//4))
        right = self.video.getSubRect(tmp, (W*3//4, 0, W//4, H))

        whitenesses = []
        whitenesses.append(self.video.sumIntensity(top))
        whitenesses.append(self.video.sumIntensity(left))
        whitenesses.append(self.video.sumIntensity(bottom))
        whitenesses.append(self.video.sumIntensity(right))
        if BoardFinder.debug:
           print (whitenesses)

        return whitenesses.index(min(whitenesses))

    # rotate the Image
    def rotateImage(self, image):
        """Flips the board in order to always have a1 on the top-left corner"""
        src = image.copy()

        if self.initialRotation == -90:
            #rotate left
            src = cv2.transpose(src);
            src = cv2.flip(src, 1);
        elif self.initialRotation == 90:
            #rotate right
            src = cv2.flip(src, 1);
            src = cv2.transpose(src);
        elif self.initialRotation == 180:
            #turn around
            src = cv2.flip(src, -1);

        return src
