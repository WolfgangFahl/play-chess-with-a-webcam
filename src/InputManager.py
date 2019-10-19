#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
from Args import Args
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
    def __init__(self):
        self.args=Args().args

        self.cam = cv2.VideoCapture(self.args.input)
        #self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, CHESSCAM_WIDTH)
        #self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CHESSCAM_HEIGHT)
        # https://stackoverflow.com/a/11332129/1497139
        #self.cam.set(cv2.CAP_PROP_FORMAT, cv2.CV_16S)

        if not self.cam:
            raise Exception("Could not initialize capturing...")

        diffs = []

        # Initialize capture threshold
        for i in range(30):
            ret, capture1 = self.cam.read()
            ret, capture2 = self.cam.read()
            diff = sum(cv2.integral(cv2.absdiff(capture1, capture2))[-1][-1])
            diffs.append(diff)

        self.threshold = sum(diffs)/len(diffs)
        self.threshold *= 1.05

    def getFrame(self):
        diff = float("inf")
        while(diff > self.threshold):
            ret, capture1 = self.cam.read()
            ret, capture2 = self.cam.read()
            capture3 = capture2.copy()
            diff = sum(cv2.integral(cv2.absdiff(capture1, capture2))[-1][-1])
            time.sleep(0.5)
        return capture3

if __name__ == "__main__":
    print("init")
    imngr = inputManager()
    while True:
        frame=imngr.getFrame()
        print("got a frame!")
