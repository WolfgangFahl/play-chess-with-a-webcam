#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import cv2
import numpy as np
import sys
from time import strftime
import argparse

# Video handling e.g. recording/writing
class Video:
    # construct me with no parameters
    def __init__(self):
        self.cap = None
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

    # play the given capture
    def play(self):
        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
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
    def still(self, prefix, format="jpg",printHints=True):
        self.checkCap()
        if (self.cap.isOpened()):
            ret, frame = self.cap.read()
            if ret == True:
                filename = "%s%s.%s" % (prefix, self.timeStamp(),format)
                if printHints:
                    print("capture %s with %dx%d" % (
                        filename, self.width, self.height))
                cv2.imwrite(filename, frame)
            self.close()

    # read an image
    def readImage(self,filePath):
        image=cv2.imread(filePath,1)
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

                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        # Release everything if job is finished
        self.close()
        out.release()
        cv2.destroyAllWindows()
        if printHints:
            print("finished")


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
