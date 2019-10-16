#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
from math import sin, cos, sqrt, pi, atan2
import sys
import cv2.cv as cv
import cv2
import numpy as np
from collections import defaultdict, deque
import time
import bisect
import argparse

# Local imports
from mathUtils import (intersect, distance, median, findBoundingSkewedSquare,
                       getRotationAndTranslationMatrix)
from MovementDetector import MovementDetector

CHESSCAM_WIDTH = 640
CHESSCAM_HEIGHT = 480
CHESSCAM_PARZEN_THRESHOLD = 5
CHESSCAM_ORIENTATION_SMOOTHING = 5
CHESSCAM_COORDINATES_SMOOTHING = 8

smoothFunc = lambda x: sum(x) / float(len(x))


class inputManager(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='ChessCam Argument Parser')
        parser.add_argument('--nouci',
                            action='store_true',
                            help="Don't use the UCI interface.")
        parser.add_argument('--input',
                            type=int,
                            default=0,
                            help="Manually set the input device.")
        args = parser.parse_args()
        
        self.cam = cv2.VideoCapture(args.input)
        self.cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, CHESSCAM_WIDTH)
        self.cam.set(cv.CV_CAP_PROP_FRAME_HEIGHT, CHESSCAM_HEIGHT)
        self.cam.set(cv.CV_CAP_PROP_FORMAT, cv.IPL_DEPTH_16S)

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
        return cv.fromarray(capture3)

if __name__ == "__main__":
    print("init")
    imngr = inputManager()
    while True:
        imngr.getFrame()
        print("got a frame!")