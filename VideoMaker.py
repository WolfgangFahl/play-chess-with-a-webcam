import cv2
import cv2.cv as cv
import numpy as np
import sys

CHESSCAM_WIDTH = 640
CHESSCAM_HEIGHT = 480

capture = cv2.VideoCapture(0)
flag, frame = capture.read()
width = np.size(frame, 1)
height = np.size(frame, 0)
writer = cv2.VideoWriter(filename="cam.avi", 
fourcc = cv.CV_FOURCC('i','Y', 'U', 'V'), # This is the codec that works for me
fps = 15,
frameSize = (width, height))

for i in range(15*20):
    flag, frame = capture.read() # Flag returns 1 for success, 0 for failure.

    if flag == 0:
        # Something is wrong with your data, or the end of the video file was
        # reached
        break 
    
    writer.write(frame) #write to the video file