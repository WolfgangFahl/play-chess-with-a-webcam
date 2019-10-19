#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from Args import Args
from Video import Video
from math import sin, cos, sqrt, pi, atan2
import sys
import cv2
import numpy as np
from collections import defaultdict, deque
import time
import bisect

# Local imports
from mathUtils import (intersect, distance, median, findBoundingSkewedSquare,
                       getRotationAndTranslationMatrix)
from MovementDetector import MovementDetector

#CHESSCAM_WIDTH = 640
#CHESSCAM_HEIGHT = 480
CHESSCAM_PARZEN_THRESHOLD = 5
CHESSCAM_ORIENTATION_SMOOTHING = 5
CHESSCAM_COORDINATES_SMOOTHING = 8

smoothFunc = lambda x: sum(x) / float(len(x))

class InputManager(object):
    def __init__(self,args):
        self.args=Args(args).args
        self.video=Video()
        input=self.args.input
        if self.is_int(input):
           self.video.capture(int(input))
        else:
           self.video.open(input)
        #self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CHESSCAM_WIDTH)
        #self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CHESSCAM_HEIGHT)
        # https://stackoverflow.com/a/11332129/1497139
        #self.cam.set(cv2.CAP_PROP_FORMAT, cv2.CV_16S)

        if not self.video.cap:
            raise Exception("Could not initialize capturing...")

        diffs = []

        # Initialize capture threshold
        for i in range(30):
            ret, capture1,quit = self.video.readFrame()
            ret, capture2,quit = self.video.readFrame()
            diff = sum(cv2.integral(cv2.absdiff(capture1, capture2))[-1][-1])
            diffs.append(diff)

        self.threshold = sum(diffs)/len(diffs)
        self.threshold *= 1.05

    def is_int(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def getFrame(self):
        diff = float("inf")
        while(diff > self.threshold):
            ret1, capture1, quit = self.video.readFrame(True)
            if ret1:
                ret2, capture2,quit = self.video.readFrame(True)
            if ret2:
                capture3 = capture2.copy()
            if ret1 and ret2:
                diff = sum(cv2.integral(cv2.absdiff(capture1, capture2))[-1][-1])
            time.sleep(0.5)
        return capture3

if __name__ == "__main__":
    print("init")
    imngr = inputManager()
    while True:
        frame=imngr.getFrame()
        print("got a frame!")
