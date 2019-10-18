#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import cv2
import numpy as np
import sys
import math
from time import strftime
import argparse

# Video handling e.g. recording/writing


class Video:
    # construct me with no parameters
    def __init__(self):
        self.cap = None
        self.frames = 0
        pass

    # capture from the given device
    def capture(self, device):
        self.device = device
        cap = cv2.VideoCapture(device)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.cap = cap

    # capture from the given vide filePath
    def open(self, filePath):
        self.cap = cv2.VideoCapture(filePath)

    # show the image with the given title
    def showImage(self, image, title, keyCheck=True, keyWait=1):
        cv2.imshow(title, image)
        if keyCheck:
            return not cv2.waitKey(keyWait) & 0xFF == ord('q')
        else:
            return True

    # play the given capture
    def play(self):
        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                self.frames = self.frames + 1
                if not self.showImage(frame, "frame"):
                    break
            else:
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def timeStamp(self):
        return strftime("%Y-%m-%d_%H%M%S")

    def close(self):
        if self.cap is not None:
            self.cap.release()

    def checkCap(self):
        if self.cap is None:
            raise "Capture is not initialized"

    # get a still image
    def still(self, prefix, format="jpg", printHints=True):
        self.checkCap()
        if (self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                filename = "%s%s.%s" % (prefix, self.timeStamp(), format)
                if printHints:
                    print("capture %s with %dx%d" % (
                        filename, self.width, self.height))
                cv2.imwrite(filename, frame)
            self.close()

    # read an image
    def readImage(self, filePath):
        image = cv2.imread(filePath, 1)
        return image

    # record the capture to a file with the given prefix using a timestamp
    def record(self, prefix, printHints=True):
        self.checkCap()
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = "%s%s.avi" % (prefix, self.timeStamp())

        out = cv2.VideoWriter(filename, fourcc, 20.0,
                              (self.width, self.height))
        if printHints:
            print("recording %s with %dx%d at %d fps press q to stop recording" % (
                filename, self.width, self.height, self.fps))

        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                # flip the frame
                # frame = cv2.flip(frame,0)

                # write the  frame
                out.write(frame)
                if not self.showImage(frame,'frame'):
                    break
            else:
                break

        # Release everything if job is finished
        self.close()
        out.release()
        cv2.destroyAllWindows()
        if printHints:
            print("finished")

    # https://stackoverflow.com/a/22921648/1497139
    def createBlank(self, width, height, rgb_color=(0, 0, 0)):
        """Create new image(numpy array) filled with certain color in RGB"""
        # Create black blank image
        image = np.zeros((height, width, 3), np.uint8)

        # Since OpenCV uses BGR, convert the color first
        color = tuple(reversed(rgb_color))
        # Fill image with color
        image[:] = color

        return image

    # was: http://www.robindavid.fr/opencv-tutorial/chapter5-line-edge-and-contours-detection.html
    # is: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    # https://docs.opencv.org/3.4/d9/db0/tutorial_hough_lines.html
    def houghTransform(self, image):
        """Performs an Hough Transform to the frame passed to updateImage().

        Returns: lines"""
        gray = cv2.cvtColor(image,  cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        return lines

    #  https://docs.opencv.org/4.1.2/d9/db0/tutorial_hough_lines.html
    def drawLines(self, image, lines):
        height, width = image.shape[:2]
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + width * (-b)), int(y0 + height * (a)))
            pt2 = (int(x0 - width * (-b)), int(y0 - height * (a)))
            cv2.line(image, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

    def getSubRect(self,image,rect):
        x=rect[0]
        y=rect[1]
        w=rect[2]
        h=rect[3]
        return image[y:y+h,x:x+h]

    # get the intensity sum of a hsv image
    def sumIntensity(self,image):
        h,s,v=cv2.split(image)
        height, width = image.shape[:2]
        sumResult=np.sum(v)
        return sumResult

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Video')

    parser.add_argument('--record',
                        action='store_true',
                        help="record a video from the given input")

    parser.add_argument('--still',
                        action='store_true',
                        help="record a still image from the given input")

    parser.add_argument('--input',
                        type=int,
                        default=0,
                        help="Manually set the input device.")
    args = parser.parse_args()
    # record a video from the first capture device
    video = Video()
    video.capture(args.input)
    if args.record:
        video.record("chessVideo")
    if args.still:
        video.still("chessImage")
