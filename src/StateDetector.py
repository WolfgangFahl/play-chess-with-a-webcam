#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
import sys
import cv2
import numpy as np
from Cell import Cell
from Board import Board
from collections import defaultdict
from mathUtils import intersectHoughLines, distance
from math import pi
from Video import Video

class CannotBuildStateException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class StateDetector(object):
    debug=True
    maxLines=1000
    minCellSize=20

    def detectState(self, colorImage):
        """Returns a board (key = address, value = cell) according to the given colorImage.
        If the given image make it impossible to detect the hole board (if corners of the board are truncated)
        then Exception will be raised (Unsufficient Data)."""

        self.image = colorImage;
        self.video = Video()

        #find the intersections of the hough lines
        self.intersects = self._findIntersects()

        #Use previoulsy acquired data to create a board, that is, a dictionary of cells [Cell Class]
        self._divideInCells()

        return self.board, self.image

    def _findIntersects(self):
        """ Performs an Hough Transform to the actual self.image. """
        self.lines=self.video.houghTransformP(self.image)
        H,W = self.image.shape[:2]

        # Gets the Hough line intersections
        intersects = []
        distanceBetweenIntersectionsThreshold = 60
        # this algorithm has quadratic effort
        lineCount=len(self.lines)
        if StateDetector.debug:
            print ("found %d lines to intersect" % (lineCount))
        if lineCount>StateDetector.maxLines:
           msg='Found %d lines which is more than StateDetector.maxLines=%d' % (lineCount,StateDetector.maxLines)
           if StateDetector.debug:
               print (msg)
           raise CannotBuildStateException(msg)
        if self.lines is not None:
            for lineIndex,line in enumerate(self.lines):
                for crosslineIndex,crossline in enumerate(self.lines):
                    if lineIndex != crosslineIndex:
                        thisIntersect = intersectHoughLines(line,crossline)

                        if thisIntersect and \
                        all([a > 0 for a in thisIntersect]) and \
                        all([thisIntersect[0] < W, thisIntersect[1] < H]):
                            intersectSecondary = intersectHoughLines(line,crossline)
                            found=False
                            for intersectPrimary in intersects:
                                if found:
                                    continue
                                if distance(intersectPrimary, intersectSecondary) < distanceBetweenIntersectionsThreshold:
                                    found=True
                            if found == False:
                                intersects.append(intersectSecondary)
        intersects.sort()
        return intersects

    def _divideInCells(self):
        self.board = {}
        H,W = self.image.shape[:2]
        #find the diagonal in the chess intersection
        cellWidth = W
        cellHeight = H
        diagonal = []
        if len(self.intersects) == 0:
            raise CannotBuildStateException("no intersection points")
        diagonal.append(self.intersects[0])

        #Estimate smallest cell size
        for pt in self.intersects:
            if pt[0] > diagonal[-1][0]+20 and pt[1] > diagonal[-1][1]+20 and \
            ((np.float64(pt[1] - diagonal[-1][1]) / np.float64(H - diagonal[-1][1])) / (np.float64(pt[0] - diagonal[-1][0]) / np.float64(W - diagonal[-1][0]))) < 1.2 and \
            ((np.float64(pt[1] - diagonal[-1][1]) / np.float64(H - diagonal[-1][1])) / (np.float64(pt[0] - diagonal[-1][0]) / np.float64(W - diagonal[-1][0]))) > 0.8:
                diagonal.append(pt)
                x = diagonal[-1][0] - diagonal[-2][0]
                y = diagonal[-1][1] - diagonal[-2][1]
                if x < cellWidth :
                    cellWidth = x
                if y < cellHeight :
                    cellHeight = y


        #Calculate our cell's ROI size
        cellWidth = np.int32((np.float64(cellWidth)/8*(np.float64(W-diagonal[0][0])/np.float64(cellWidth)))) - 1
        cellHeight = np.int32((np.float64(cellHeight)/8*(np.float64(H-diagonal[0][1])/np.float64(cellHeight)))) - 1

        #A problem can be encountered while cv2.GetSubRect if cellWidth or cellHeight are too low
        if cellWidth < StateDetector.minCellSize or cellHeight < StateDetector.minCellSize:
            raise CannotBuildStateException("cellWidth %d or cellHeight %d too low (<%d): Image error" % (cellWidth,cellHeight,StateDetector.minCellSize))

        #build an 8 points list to set the fulldiagonal.
        current = 0
        next = 1
        fulldiag = []
        fulldiag.append(diagonal[0])
        while next < len(diagonal):
            x = fulldiag[current][0]
            y = fulldiag[current][1]
            if x + 1.8*cellWidth < diagonal[next][0] and y + 1.8*cellHeight < diagonal[next][1]:
                fulldiag.append((x+cellWidth, y + cellHeight))
            else:
                fulldiag.append(diagonal[next])
                next += 1
            current += 1

        #When had not enough intersections in the diagonal, so we add points to it at the end.
        while len(fulldiag) < 8:
            x = fulldiag[-1][0]
            y = fulldiag[-1][1]
            fulldiag.append((x+cellWidth, y + cellHeight))
            if(x+cellWidth+(cellWidth*9/10) >= W or y+cellHeight+(cellHeight*9/10) >= H): #cutting cells step would cut further the image borders
                raise CannotBuildStateException('Insufficient Data: Cannot Build Current State.')

        diagonal = fulldiag
        #Create cells from diagonal
        chessBoard=Board()
        for row in range(0,8):
            for col in range (0,8):
                #Raise error if cell would be outside image
                if(diagonal[col][0] + 7*cellWidth/10 > W or diagonal[row][1] + 7*cellHeight/10 > H):
                    raise CannotBuildStateException('Cell Overflow: a cell would be outside board')
                coords = (diagonal[col][0] + 3*cellWidth/10, diagonal[row][1] + 3*cellHeight/10, cellWidth*2/5, cellHeight*2/5)
                newCell = Cell(coords)
                self.board[chessBoard.GetCellName(col,7-row)] = newCell

if __name__ == "__main__":
    sys.stderr.write("Not a stand alone")
