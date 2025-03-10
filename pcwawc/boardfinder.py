#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# <uml>
# BoardFinder -- Corners
# </uml>

import math
from timeit import default_timer as timer

import chess

# Global imports
import cv2
import numpy as np
from _operator import pos

from pcwawc.chesstrapezoid import Trapez2Square
from pcwawc.environment import Environment
from pcwawc.histogram import Histogram
from pcwawc.video import Video


class Corners(object):
    """Chess board corners"""

    debug = False
    debugSorting = False
    """ pixel margin for masked polygons"""
    safetyMargin = 5

    def __init__(self, pattern, video):
        """initialize me with the given rows and columns"""
        self.pattern = pattern
        self.rows, self.cols = pattern
        self.video = video
        # prepare the dict for my polygons
        self.polygons = {}

    @staticmethod
    def genChessPatterns():
        """generate the patterns 7x7, 5x7, 3x7, 5x5, 5x3, 3x3"""
        for rows in range(7, 2, -2):
            for cols in range(7, rows - 2, -2):
                yield (rows, cols)

    @staticmethod
    def sortXY(xy):
        x, y = xy[0]
        return x, y

    def sort(self):
        """sort the corners - this step is currently not implemented so the corners stay rotated"""
        if Corners.debugSorting:
            print("trying to sort %d points" % (len(self.corners)))
        cornerssorted = sorted(self.corners, key=Corners.sortXY)
        if Corners.debugSorting:
            print(cornerssorted)
        # self.corners = np.empty(shape=(len(self.corners),2),dtype=np.float32)
        # for i,val in enumerate(cornerssorted):
        #    self.corners[i]=val
        pass

    def findPattern(self, image):
        """try finding the chess board corners in the given image with the given pattern"""
        self.h, self.w = image.shape[:2]

        start = timer()
        ret, self.corners = cv2.findChessboardCorners(image, self.pattern, None)
        end = timer()
        if Corners.debug:
            print(
                "%dx%d in %dx%d after %.3f s: %s"
                % (
                    self.rows,
                    self.cols,
                    self.w,
                    self.h,
                    (end - start),
                    "✔" if ret else "❌",
                )
            )
        return ret

    def safeXY(self, x, y, dx, dy):
        """return the given x,y tuple shifted by dx,dy making sure the result is not out of my width and height bounds"""
        x = x + dx
        y = y + dy
        if y >= self.h:
            y = self.h - 1
        if y < 0:
            y = 0
        if x >= self.w:
            x = self.w - 1
        if x < 0:
            x = 0
        return (x, y)

    def asPolygons(self, safetyMargin):
        """get the polygons for my corner points"""
        # reshape the array
        cps = np.reshape(self.corners, (self.cols, self.rows, 2))
        polygons = {}
        m = safetyMargin
        for col in range(self.cols - 1):
            for row in range(self.rows - 1):
                x1, y1 = cps[col, row]  # top left
                x2, y2 = cps[col + 1, row]  # left bottom
                x3, y3 = cps[col + 1, row + 1]  # right bottom
                x4, y4 = cps[col, row + 1]  # top right
                clockwise = BoardFinder.sortPoints(
                    [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                )
                (x1, y1), (x2, y2), (x3, y3), (x4, y4) = clockwise
                # https://stackoverflow.com/questions/19190484/what-is-the-opencv-findchessboardcorners-convention
                polygon = np.array(
                    [
                        self.safeXY(x1, y1, +m, +m),
                        self.safeXY(x2, y2, -m, +m),
                        self.safeXY(x3, y3, -m, -m),
                        self.safeXY(x4, y4, +m, -m),
                    ],
                    dtype=np.int32,
                )
                polygons[(col, self.rows - 2 - row)] = polygon
        return polygons

    def calcPolygons(self, *safetyMargins):
        """calculate polygons for the given safety margins"""
        for safetyMargin in safetyMargins:
            self.polygons[safetyMargin] = self.asPolygons(safetyMargin)

    def calcTrapez(self):
        """calculate the relevant quadrilaterals"""
        corners = self.corners
        l = len(self.corners)
        rowend = self.rows - 1
        self.topLeft = corners[0]
        self.topRight = corners[rowend]
        self.bottomRight = corners[l - 1]
        self.bottomLeft = corners[l - 1 - rowend]
        self.trapez2Square = Trapez2Square(
            self.topLeft, self.topRight, self.bottomRight, self.bottomLeft
        )
        self.trapez8x8 = self.trapezColRows(8, 8)
        self.trapez10x10 = self.trapezColRows(10, 10)
        self.trapez = self.trapez2Square.relativeTrapezToTrapezXY(0, 0, 1, 1)
        pass

    def trapezColRows(self, cols, rows):
        """return an expanded trapez with the given number of columns and rows"""
        relDeltaRows = (rows / (self.rows - 1) - 1) / 2
        relDeltaCols = (cols / (self.cols - 1) - 1) / 2
        trapez = self.trapez2Square.relativeTrapezToTrapezXY(
            -relDeltaRows, -relDeltaCols, 1 + relDeltaRows, 1 + relDeltaCols
        )
        return trapez

    def showTrapezDebug(self, image, title, corners):
        """'show' a debug picture with the extrapolated quadrilaterals by writing an image to the debugImagePath"""
        overlay = image.copy()
        # draw polytons from outer to inner
        cv2.fillConvexPoly(overlay, self.trapez10x10, (0, 165, 255))  # orange
        cv2.fillConvexPoly(overlay, self.trapez8x8, (128, 128, 128))  # grey
        cv2.fillConvexPoly(overlay, self.trapez, (225, 105, 65))  # royal blue
        alpha = 0.8  # Transparency factor.
        # overlay the
        imageAlpha = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        corners.writeDebug(imageAlpha, title, "trapez")

    def showDebug(self, image, title):
        """'show' the debug picture of the chessboard corners by drawing the corners and writing the result to the given testImagePath"""
        imageCopy = image.copy()
        cv2.drawChessboardCorners(
            imageCopy, self.pattern, self.corners, patternWasFound=True
        )
        if Corners.debugSorting:
            index = 0
            for point in self.topLeft, self.topRight, self.bottomRight, self.bottomLeft:
                text = "%d" % (index)
                x, y = point[0]
                self.video.drawCenteredText(
                    imageCopy, text, int(x), int(y), fontScale=1, fontBGRColor=(0, 0, 0)
                )
                index += 1
        # if Corners.debugSorting:
        #    for index,corner in enumerate(self.corners):
        #        x,y=corner[0]
        #        text="%d" % (index)
        #        self.video.drawCenteredText(imageCopy, text, int(x), int(y), fontScale=0.5,fontBGRColor=(128,128,128))
        # cv2.imshow('corners', self.image)
        # cv2.waitKey(50)
        self.writeDebug(imageCopy, title, "corners")

    def writeDebug(self, image, title, prefix):
        Environment.checkDir(Environment.debugImagePath)
        cv2.imwrite(
            Environment.debugImagePath
            + "%s-%s-%dx%d.jpg" % (title, prefix, self.rows, self.cols),
            image,
        )


# Board Finder
class BoardFinder(object):
    """find a chess board in the given image"""

    debug = False
    black = (0, 0, 0)
    white = (255, 255, 255)
    darkGrey = (256 // 3, 256 // 3, 256 / 3)
    lightGrey = (256 * 2 // 3, 256 * 2 // 3, 256 * 2 // 3)

    def __init__(self, image, video=None):
        """construct me from the given input image"""
        if video is None:
            video = Video()
        self.video = video
        self.image = image
        # guess the topleft color
        self.topleft = chess.WHITE
        self.height, self.width = self.image.shape[:2]

    @staticmethod
    def centerXY(xylist):
        x, y = zip(*xylist)
        l = len(x)
        return sum(x) / l, sum(y) / l

    @staticmethod
    def sortPoints(xylist):
        """sort points clockwise see https://stackoverflow.com/a/59115565/1497139"""
        cx, cy = BoardFinder.centerXY(xylist)
        xy_sorted = sorted(xylist, key=lambda x: math.atan2((x[1] - cy), (x[0] - cx)))
        return xy_sorted

    def findOuterCorners(self, searchWidth=640):
        """find my outer corners as limited by the OpenCV findChessBoard algorithm - to be later expanded"""
        found = self.findCorners(self.image, limit=1, searchWidth=searchWidth)
        # we expected to find a board
        if len(found) != 1:
            raise Exception("no corners found")
        chesspattern = next(iter(found))
        corners = found[chesspattern]
        corners.calcPolygons(0, Corners.safetyMargin)
        corners.calcTrapez()
        return corners

    def preparefindCorners(self, image, searchWidth=640):
        sw = self.width
        sh = self.height
        if sw > searchWidth:
            sw = searchWidth
            sh = self.height * sw // self.width
        searchimage = cv2.resize(self.image, (sw, sh))
        if BoardFinder.debug:
            print(
                "BoardFinder for %dx%d image resized to %dx%d"
                % (self.width, self.height, sw, sh)
            )

        gray = cv2.cvtColor(searchimage, cv2.COLOR_BGR2GRAY)
        fullSizeGray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return gray, fullSizeGray

    def findCorners(self, image, limit=1, searchWidth=640):
        """start finding the chessboard with the given limit and the given maximum width of the search image"""
        startt = timer()
        gray, fullSizeGray = self.preparefindCorners(image, searchWidth)
        self.found = {}
        for chesspattern in Corners.genChessPatterns():
            corners = Corners(chesspattern, self.video)
            if corners.findPattern(gray) and corners.findPattern(fullSizeGray):
                corners.sort()
                self.found[chesspattern] = corners
            if len(self.found) >= limit:
                break
        endt = timer()
        if BoardFinder.debug:
            print("found %d patterns in %.1f s" % (len(self.found), (endt - startt)))
        return self.found

    def findChessBoard(self, image, title):
        """find a chess board in the given image and return the trapez polygon for it"""
        corners = self.findOuterCorners()
        histograms = self.getHistograms(image, title, corners)
        self.expand(image, title, histograms, corners)
        return corners

    def fieldColor(self, pos):
        """determine the field color at the given position"""
        row, col = pos
        # the color of the topleft field might be different then A8=WHITE when we have a rotated image
        oddeven = 1 if self.topleft == chess.WHITE else 0
        # calculate the chessboard color of the given position based on the topleft color
        color = chess.WHITE if (col + row) % 2 == oddeven else chess.BLACK
        return color

    def maskPolygon(self, image, polygon):
        """mask the given image with the given polygon"""
        mask = self.video.getEmptyImage(image)
        cv2.fillConvexPoly(mask, polygon, BoardFinder.white)
        masked = self.video.maskImage(image, mask)
        return masked

    def maskCornerPolygons(self, image, corners, filterColor):
        """mask the polygons derived from the given corner points"""
        mask = self.video.getEmptyImage(image)
        polygons = corners.polygons[Corners.safetyMargin]
        for pos, polygon in polygons.items():
            posColor = self.fieldColor(pos)
            if not posColor == filterColor:
                self.drawPolygon(
                    mask, pos, polygon, BoardFinder.white, BoardFinder.white
                )
        # if BoardFinder.debug:
        #    cv2.imshow("mask",mask)
        #    cv2.waitKey(1000)
        masked = self.video.maskImage(image, mask)
        return masked

    def getHistograms(self, image, title, corners):
        """get the two histograms for the given corners we don't no what the color of the topleft corner is so we start with a guess"""
        histograms = {}
        for filterColor in (True, False):
            imageCopy = image.copy()
            masked = self.maskCornerPolygons(imageCopy, corners, filterColor)
            if BoardFinder.debug:
                prefix = "masked-O-" if filterColor else "masked-X-"
                corners.writeDebug(masked, title, prefix)
            histograms[filterColor] = Histogram(masked, histRange=(1, 256))

        # do we need to fix our guess?
        # is the mean color of black (being filtered) higher then when white is filtered?
        if histograms[chess.BLACK].color > histograms[chess.WHITE].color:
            self.topleft = chess.BLACK
            # swap entries
            tmp = histograms[chess.BLACK]
            histograms[chess.BLACK] = histograms[chess.WHITE]
            histograms[chess.WHITE] = tmp
        return histograms

    def getColorFiltered(self, image, histograms, title, corners):
        """get color filtered images based on the given histograms"""
        colorFiltered = {}
        colorMask = {}
        for filterColor in (chess.WHITE, chess.BLACK):
            histogram = histograms[filterColor]
            imageCopy = image.copy()
            lowerColor, upperColor = histogram.range(1.0)
            # make sure the colors are numpy arrays
            lowerColor = np.array(lowerColor, dtype=np.uint8)
            upperColor = np.array(upperColor, dtype=np.uint8)
            # if we would know that the empty fields would be the extreme colors we could do the following:
            # if filterColor==chess.WHITE:
            #    upperColor=(255,255,255)
            # else:
            #    lowerColor=(0,0,0)
            # lower,upper=histogram.mincolor, histogram.maxcolor
            colorMask[filterColor] = cv2.inRange(imageCopy, lowerColor, upperColor)
            # colorMask[filterColor]=histogram.colorMask(imageCopy, 1.5)
            colorFiltered[filterColor] = self.video.maskImage(
                imageCopy, colorMask[filterColor]
            )
            if BoardFinder.debug:
                colorName = "white" if filterColor == chess.WHITE else "black"
                bl, gl, rl = lowerColor
                bu, gu, ru = upperColor
                print(
                    "bgr %s: %3d-%3d, %3d-%3d, %3d-%3d"
                    % (colorName, bl, bu, gl, gu, rl, ru)
                )
                prefix = "colorFiltered-%s-" % (colorName)
                corners.writeDebug(colorFiltered[filterColor], title, prefix)
        backGroundFilter = cv2.bitwise_not(
            cv2.bitwise_or(colorMask[chess.WHITE], colorMask[chess.BLACK])
        )
        imageCopy = image.copy()
        colorFiltered["background"] = self.video.maskImage(imageCopy, backGroundFilter)
        if BoardFinder.debug:
            corners.writeDebug(
                colorFiltered["background"], title, "colorFiltered-background-"
            )
        # side effect - add background histogram
        histograms["background"] = Histogram(
            colorFiltered["background"], histRange=(1, 256)
        )
        return colorFiltered

    def expand(self, image, title, histograms, corners):
        """expand the image finding to 8x8 with the given histograms and corners that are e.g. 7x7,7x5,5x5, ..."""
        if BoardFinder.debug:
            corners.showTrapezDebug(image, title, corners)
        # create a mask for the
        masked8x8 = self.maskPolygon(image, corners.trapez8x8)
        if BoardFinder.debug:
            corners.writeDebug(masked8x8, title, "trapez-masked")
        # draw a 10x10 sized white trapez
        white10x10 = self.video.getEmptyImage(image)
        cv2.fillConvexPoly(white10x10, corners.trapez10x10, BoardFinder.white)
        cv2.fillConvexPoly(white10x10, corners.trapez8x8, BoardFinder.black)
        masked10x10 = white10x10 + masked8x8
        if BoardFinder.debug:
            corners.writeDebug(masked10x10, title, "trapez-white")
        # 9x9 test fails due to a few pixels which are in the way
        # commented out to speed up
        # gray8x8,fullSizeGray8x8=self.preparefindCorners(masked10x10)
        # corners8x8=Corners((9,9),self.video)
        # if corners8x8.findPattern(fullSizeGray8x8):
        #    if BoardFinder.debug:
        #        print("Successfully found 8x8 for %s"+title)
        self.colorFiltered = self.getColorFiltered(
            masked8x8, histograms, title, corners
        )

    def drawPolygon(self, image, pos, polygon, whiteColor, blackColor):
        posColor = self.fieldColor(pos)
        color = blackColor if posColor else whiteColor
        cv2.fillConvexPoly(image, polygon, color)

    def showPolygonDebug(self, image, title, corners):
        """draw polygons for debugging on a copy of the given image with the given corners and write result to the debugImagePath with the given title"""
        imagecopy = image.copy()
        polygons = corners.polygons[0]
        for pos, polygon in polygons.items():
            self.drawPolygon(
                imagecopy, pos, polygon, BoardFinder.lightGrey, BoardFinder.darkGrey
            )
            if Corners.debugSorting:
                row, col = pos
                text = "%d,%d" % (row, col)
                x, y = BoardFinder.centerXY(polygon)
                self.video.drawCenteredText(
                    imagecopy, text, int(x), int(y), fontBGRColor=(255, 0, 0)
                )
        corners.writeDebug(imagecopy, title, "polygons")

    def showHistogramDebug(self, histograms, title, corners):
        """'show' the debug information for the given histograms by writing a plotted histogram image to the debugImagePath"""
        Environment.checkDir(Environment.debugImagePath)
        fig, axes = histograms[True].preparePlot(3, 2)
        histograms[True].plotRow(axes[0, 0], axes[0, 1])
        histograms[False].plotRow(axes[1, 0], axes[1, 1])
        histograms["background"].plotRow(axes[2, 0], axes[2, 1])
        prefix = "histogram"
        filepath = Environment.debugImagePath + "%s-%s-%dx%d.jpg" % (
            title,
            prefix,
            corners.rows,
            corners.cols,
        )
        histograms[False].savefig(fig, filepath)
