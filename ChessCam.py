#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
from math import sin, cos, sqrt, pi, atan2
import urllib.request, urllib.error, urllib.parse
import sys
import cv2
import numpy as np
import math
from collections import defaultdict, deque
import bisect

# Local imports
from mathUtils import intersect, distance, median, findBoundingSkewedSquare, getRotationAndTranslationMatrix
from InputManager import InputManager
from BoardFinder import BoardFinder, BadSegmentation
from MovementDetector import MovementDetector, BadImage
from Video import Video


class UserExit(Exception):
    pass


class ChessCam(object):
    def __init__(self):
        self.captureHdl = InputManager()
        self.args=self.captureHdl.args

        # Create window(s)
        cv2.namedWindow("chessCam", 1)
        #cv2.resizeWindow("chessCam", CHESSCAM_WIDTH, CHESSCAM_HEIGHT)
        if self.args.fullScreen:
            #https://stackoverflow.com/a/34337534/1497139
            cv2.setWindowProperty("chessCam",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        #cv.NamedWindow("chessCamDebug", 1)
        #cv.ResizeWindow("chessCamDebug", CHESSCAM_WIDTH, CHESSCAM_HEIGHT)

        #Initialize the MovementDetector
        success = False
        while not success:
            success = True
            frame = self.captureHdl.getFrame()

            BoardFinder.debug=self.args.debug
            self.finder = BoardFinder(frame)
            if self.args.cornermarker is not None:
                video=Video()
                cornerMarkerImage=video.readImage(self.args.cornermarker)
                self.finder.calibrateCornerMarker(cornerMarkerImage)
            self.finder.prepare()
            try:
                processedImages = self.finder.GetFullImageBoard()
                self.moveDetector = MovementDetector(processedImages[0])
            except (BadImage, BadSegmentation):
                success = False

    def getNextMove(self):
        """Get a frame from the camera, analyze it and produce the movement
        descriptor performed by the player."""
        move = []
        while len(move) == 0 :
            self.frame = self.captureHdl.getFrame()

            if self.frame is not None:
                self.finder.updateImage(self.frame)
                try:
                    processedImages = self.finder.GetFullImageBoard()
                except BadSegmentation:
                    sys.stderr.write("Badly segmented image (could not find 4"
                                     " coordinates of the board)")
                    continue

                cv.ShowImage("chessCam", processedImages[2])

                try:
                    move = self.moveDetector.detectMove(processedImages[0])
                except BadImage as e:
                    #print str(e)
                    pass
                except cv2.error as e:
                    print(str(e))
                    pass

            if cv.WaitKey(10) != -1:
                raise UserExit

        return move

    def getDominatorOffset(self):
        return self.finder.getDominatorOffset()


if __name__ == "__main__":
    thisInstance = ChessCam()
    try:
        while True:
            move = thisInstance.getNextMove()
            if len(move) != 0:
                print("Move")
                print(move)

    except UserExit:
        pass
