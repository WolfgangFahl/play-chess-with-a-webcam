#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import argparse
import math
import os
import sys
import threading
from threading import Thread
from time import strftime

import cv2
import numpy as np
from imutils import perspective

from pcwawc.environment import Environment
from pcwawc.fpscheck import FPSCheck


class Video:
    """Video handling e.g. recording/writing"""

    @staticmethod
    def getVideo():
        video = Video()
        video.headless = Environment.inContinuousIntegration()
        return video

    # construct me with no parameters
    def __init__(self, title="frame"):
        self.title = title
        self.cap = None
        self.frames = 0
        self.ispaused = False
        # current Frame
        self.frame = None
        self.processedFrame = None
        self.maxFrames = sys.maxsize
        # still image ass video feature for jpg
        self.autoPause = False
        self.fpsCheck = None
        self.debug = False
        self.headless = False
        pass

    # check whether s is an int
    @staticmethod
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def title(device):
        if not Video.is_int(device):
            deviceTitle = os.path.basename(device)
        else:
            deviceTitle = "camera %s" % (device)
        return deviceTitle

    # return if video is paused
    def paused(self):
        return self.ispaused

    # pause the video
    def pause(self, ispaused):
        self.ispaused = ispaused

    # capture from the given device
    def capture(self, device):
        if Video.is_int(device):
            self.device = int(device)
        else:
            self.device = device
            self.open(device)
            if device.endswith(".jpg"):
                self.maxFrames = 1
                self.autoPause = True
        self.setup(cv2.VideoCapture(self.device))

    def setup(self, cap):
        """setup the capturing from the given device"""
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.cap = cap
        self.fpsCheck = FPSCheck()
        self.fpsCheck.start()

    def checkFilePath(self, filePath, raiseException=True):
        ok = os.path.exists(filePath)
        if raiseException and not ok:
            raise Exception("file %s does not exist" % (filePath))
        return ok

    # capture from the given video filePath
    def open(self, filePath):
        self.checkFilePath(filePath)
        self.setup(cv2.VideoCapture(filePath))

    def showImage(self, image, title: str, keyCheck: bool = True, keyWait: int = 5):
        """
        show the image with the given title

        Args:
            image: the image to show
            title(str): the title of the image
            keyCheck(bool): wait for a a key stroke before continuing?
            keyWait(int): maximum number of seconds to wait for a key stroke
        """
        if not threading.current_thread() is threading.main_thread():
            if self.debug:
                print("can't show image %s since not on mainthread" % (title))
            return True
        if self.headless:
            return True
        cv2.imshow(title, image)
        if keyCheck:
            return not cv2.waitKey(keyWait) & 0xFF == ord("q")
        else:
            return True

    def showAndWriteImage(
        self, image, title, path="/tmp/", imageFormat=".jpg", keyCheck=True, keyWait=5
    ):
        result = self.showImage(image, title, keyCheck, keyWait)
        if image is not None:
            cv2.imshow(title, image)
            cv2.imwrite(path + title + imageFormat, image)
        return result

    # encode the image
    def imencode(self, frame, imgformat=".jpg"):
        # encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(imgformat, frame)
        return flag, encodedImage

    # return a video frame as a jpg image
    def readJpgImage(self, show=False, postProcess=None):
        ret, frame, quitWanted = self.readFrame(show, postProcess)
        encodedImage = None
        # ensure the frame was read
        if ret:
            (flag, encodedImage) = self.imencode(frame)
            # ensure the frame was successfully encoded
            if not flag:
                ret = False
        return ret, encodedImage, quitWanted

    # return a video frame as a numpy array
    def readFrame(self, show=False, postProcess=None):
        # when pausing repeat previous frame
        if self.ispaused:
            # simply return the current frame again
            ret = self.frame is not None
        else:
            ret, self.frame = self.cap.read()
        quitWanted = False
        if ret == True:
            if not self.ispaused:
                self.frames = self.frames + 1
                if self.frames >= self.maxFrames and self.autoPause:
                    self.ispaused = True
                self.fpsCheck.update()
            if not postProcess is None:
                try:
                    self.processedFrame = postProcess(self.frame)
                except BaseException as e:
                    # @TODO log exception
                    print("processing error " + str(e))
                    self.processedFrame = self.frame
            else:
                self.processedFrame = self.frame
            if show:
                quitWanted = not self.showImage(self.frame, self.title)
        return ret, self.processedFrame, quitWanted

    # play the given capture
    def play(self):
        while self.cap.isOpened():
            ret, frame, quitWanted = self.readFrame(True)
            if ret == True:
                if quitWanted:
                    break
                if frame is None:
                    # TODO decide whether to log a warning here
                    pass
            else:
                break
        self.close()

    def fileTimeStamp(self):
        return self.timeStamp(separator="_", timeseparator="")

    def timeStamp(self, separator=" ", timeseparator=":"):
        return strftime(
            "%Y-%m-%d" + separator + "%H" + timeseparator + "%M" + timeseparator + "%S"
        )

    def close(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def checkCap(self):
        if self.cap is None:
            raise "Capture is not initialized"

    # get a still image
    def still(
        self,
        prefix,
        imgformat="jpg",
        close=True,
        printHints=True,
        show=False,
        postProcess=None,
    ):
        filename = "%s%s.%s" % (prefix, self.fileTimeStamp(), imgformat)
        return self.still2File(
            filename,
            format=format,
            close=close,
            printHints=printHints,
            show=show,
            postProcess=postProcess,
        )

    # get a still image
    def still2File(
        self,
        filename,
        format="jpg",
        close=True,
        printHints=True,
        show=False,
        postProcess=None,
    ):
        self.checkCap()
        ret = False
        frame = None
        if self.cap.isOpened():
            ret, frame, quitWanted = self.readFrame(show, postProcess)
            if ret == True:
                if printHints:
                    print("capture %s with %dx%d" % (filename, self.width, self.height))
                self.writeImage(frame, filename)
            if close:
                self.close()
        return ret, frame

    # read an image
    def readImage(self, filePath):
        self.checkFilePath(filePath)
        image = cv2.imread(filePath, 1)
        return image

    def writeImage(self, image, filepath):
        cv2.imwrite(filepath, image)

    def prepareRecording(self, filename, width, height, fps=None):
        self.checkCap()
        if fps is None:
            fps = self.fps
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        return out

    # record the capture to a file with the given prefix using a timestamp
    def record(self, prefix, printHints=True, fps=None):
        filename = "%s%s.avi" % (prefix, self.timeStamp())
        out = self.prepareRecording(filename, self.width, self.height, fps)

        if printHints:
            print(
                "recording %s with %dx%d at %d fps press q to stop recording"
                % (filename, self.width, self.height, self.fps)
            )

        while self.cap.isOpened():
            ret, frame, quitWanted = self.readFrame(True)
            if ret == True:
                # flip the frame
                # frame = cv2.flip(frame,0)
                if quitWanted:
                    break
                # write the  frame
                out.write(frame)
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
        image = self.getEmptyImage4WidthAndHeight(width, height, 3)

        # Since OpenCV uses BGR, convert the color first
        color = tuple(reversed(rgb_color))
        # Fill image with color
        image[:] = color

        return image

    def getEmptyImage4WidthAndHeight(self, w, h, channels):
        """get an empty image with the given width height and channels"""
        emptyImage = np.zeros((h, w, channels), np.uint8)
        return emptyImage

    def getEmptyImage(self, image, channels=1):
        """prepare a trapezoid/polygon mask to focus on the square chess field seen as a trapezoid"""
        h, w = image.shape[:2]
        emptyImage = self.getEmptyImage4WidthAndHeight(w, h, channels)
        return emptyImage

    def maskImage(self, image, mask):
        """return the masked image that filters with the given mask"""
        masked = cv2.bitwise_and(image, image, mask=mask)
        return masked

    # was: http://www.robindavid.fr/opencv-tutorial/chapter5-line-edge-and-contours-detection.html
    # is: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    # https://docs.opencv.org/3.4/d9/db0/tutorial_hough_lines.html
    def houghTransform(self, image):
        """Performs an Hough Transform to given image.

        Returns: lines"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        return lines

    def houghTransformP(self, image):
        """Performs a probabilistic Hough Transform to given image.

        Returns: lines"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        h, w = image.shape[:2]
        minLineLength = h / 16
        maxLineGap = h / 24
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength, maxLineGap)
        return lines

    def drawTrapezoid(self, image, points, color):
        """loop over the given points and draw them on the image"""
        if points is None:
            return
        prev = None
        # if there is exactly four points then close the loop
        if len(points) == 4:
            points.append(points[0])
        for x, y in points:
            cv2.circle(image, (x, y), 10, color, -1)
            if prev is not None:
                cv2.line(image, (x, y), prev, color, 3, cv2.LINE_AA)
            prev = (x, y)

    def drawCircle(self, image, center, radius=10, color=(0, 255, 0), thickness=1):
        cv2.circle(image, center, radius, color=color, thickness=thickness)

    def drawRectangle(self, image, pt1, pt2, color=(0, 255, 0), thickness=1):
        cv2.rectangle(image, pt1, pt2, color, thickness)

    def drawPolygon(self, image, polygon, color):
        """draw the given polygon onto the given image with the given color"""
        cv2.fillConvexPoly(image, polygon, color)

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

    def rotate(self, image, angle, center=None, scale=1.0):
        # grab the dimensions of the image
        (h, w) = image.shape[:2]

        # if the center is None, initialize it as the center of
        # the image
        if center is None:
            center = (w // 2, h // 2)

        # perform the rotation (clockwise)
        M = cv2.getRotationMatrix2D(center, -angle, scale)
        rotated = cv2.warpAffine(image, M, (w, h))

        # return the rotated image
        return rotated

    def warp(self, image, pts, squared=True):
        """apply the four point transform to obtain a birds eye view of the given image"""
        warped = perspective.four_point_transform(image, pts)
        if squared:
            height, width = warped.shape[:2]
            side = min(width, height)
            warped = cv2.resize(warped, (side, side))
        return warped

    def as2x2(self, row1col1, row1col2, row2col1, row2col2, downScale=2):
        height, width = row1col1.shape[:2]
        image1, image2, image3, image4 = row1col1, row1col2, row2col1, row2col2
        if downScale > 1:
            image1 = cv2.resize(image1, (width // downScale, height // downScale))
            image2 = cv2.resize(image2, (width // downScale, height // downScale))
            image3 = cv2.resize(image3, (width // downScale, height // downScale))
            image4 = cv2.resize(image4, (width // downScale, height // downScale))

        combined1 = np.concatenate((image1, image2), axis=0)
        combined2 = np.concatenate((image3, image4), axis=0)
        combined = np.concatenate((combined1, combined2), axis=1)
        return combined

    @staticmethod
    def getSubRect(image, rect):
        x, y, w, h = rect
        return image[y : y + h, x : x + w]

    # get the intensity sum of a hsv image
    def sumIntensity(self, image):
        h, s, v = cv2.split(image)
        height, width = image.shape[:2]
        sumResult = np.sum(v)
        return sumResult

    # add a timeStamp to the given frame fontScale 1.0
    def addTimeStamp(
        self,
        frame,
        withFrames=True,
        withFPS=True,
        fontBGRColor=(0, 255, 0),
        fontScale=1.0,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        lineThickness=1,
    ):
        if frame is not None:
            height, width = frame.shape[:2]
            # grab the current time stamp and draw it on the frame
            now = self.timeStamp()
            if withFrames:
                now = now + " %d" % (self.frames)
            if withFPS and self.fpsCheck is not None:
                now = now + "@%.0f fps" % (self.fpsCheck.fps())
            fontFactor = width / 960
            text_width, text_height = cv2.getTextSize(
                now, font, fontScale * fontFactor, lineThickness
            )[0]
            # https://stackoverflow.com/a/34273603/1497139
            # frame = frame.copy()
            self.drawText(
                frame,
                now,
                (width - int(text_width * 1.1), int(text_height * 1.2)),
                font,
                fontScale * fontFactor,
                fontBGRColor,
                lineThickness,
            )
        return frame

    def drawCenteredText(
        self,
        frame,
        text,
        x,
        y,
        fontBGRColor=(0, 255, 0),
        fontScale=1.0,
        font=cv2.FONT_HERSHEY_SIMPLEX,
        lineThickness=1,
    ):
        height, width = frame.shape[:2]
        fontFactor = width / 960
        text_width, text_height = cv2.getTextSize(
            text, font, fontScale * fontFactor, lineThickness
        )[0]
        self.drawText(
            frame,
            text,
            (x - text_width // 2, y + text_height // 2),
            font,
            fontScale * fontFactor,
            fontBGRColor,
            lineThickness,
        )

    def drawText(
        self,
        frame,
        text,
        bottomLeftCornerOfText,
        font,
        fontScale,
        fontBGRColor,
        lineThickness,
    ):
        cv2.putText(
            frame,
            text,
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontBGRColor,
            lineThickness,
        )


# see https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
class VideoStream(object):
    """run videograbbing in separate stream"""

    def __init__(self, video, show=False, postProcess=None, name="VideoStream"):
        self.video = video
        self.show = show
        self.quit = False
        self.frame = None
        # initialize the thread name
        self.name = name
        self.postProcess = postProcess

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            ret, frame, quitWanted = video.readFrame(self.show, self.postProcess)
            if quitWanted:
                return

            if ret:
                self.frame = frame

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video")

    parser.add_argument(
        "--record", action="store_true", help="record a video from the given input"
    )

    parser.add_argument(
        "--still", action="store_true", help="record a still image from the given input"
    )

    parser.add_argument(
        "--input", type=int, default=0, help="Manually set the input device."
    )
    args = parser.parse_args()
    # record a video from the first capture device
    video = Video()
    video.capture(args.input)
    if args.record:
        video.record("chessVideo")
    if args.still:
        video.still("chessImage")
