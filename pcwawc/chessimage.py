"""
Created on 2019-12-10

@author: wf
"""

import os
from timeit import default_timer as timer

import cv2
import numpy as np
from zope.interface import implementer

from pcwawc.board import Board
from pcwawc.chessvision import (
    IChessBoardImage,
    IChessBoardImageSet,
    IChessBoardVision,
    IWarp,
)
from pcwawc.environment import Environment
from pcwawc.jsonablemixin import JsonAbleMixin
from pcwawc.video import Video
from pcwawc.yamlablemixin import YamlAbleMixin


@implementer(IChessBoardVision)
class ChessBoardVision(JsonAbleMixin):
    """implements access to chessboard images"""

    def __init__(self, args, board=None):
        self.device = args.input
        self.title = Video.title(self.device)
        self.video = Video(self.title)
        self.video.headless = Environment.inContinuousIntegration()
        self.args = args
        self.showDebug = args.debug
        self.start = None
        self.quitWanted = False
        self.hasImage = False
        self.timestamps = []
        self.debug = args.debug
        if board is None:
            board = Board(args=args)
        self.board = board
        if self.args.fen is not None:
            self.board.updatePieces(self.args.fen)
        self.warp = Warp(args.warpPointList)
        self.warp.rotation = args.rotation
        if self.args.nowarp:
            self.warp.warping = True
        self.firstFrame = True
        self.speedup = args.speedup
        pass

    def open(self, device):
        self.video.capture(device)
        self.device = device
        self.firstFrame = True

    def readChessBoardImage(self):
        for i in range(self.speedup):
            self.hasImage, image, self.quitWanted = self.video.readFrame(self.showDebug)
            if self.quitWanted:
                return self.previous
        frames = self.video.frames
        if self.firstFrame:
            self.start = timer()
        timestamp = timer() - self.start
        self.chessBoardImageSet = ChessBoardImageSet(
            self, image, frames // self.speedup, timestamp
        )
        self.firstFrame = False
        self.timestamps.append(timestamp)
        return self.chessBoardImageSet

    def close(self):
        self.video.close()

    def __getstate__(self):
        state = {}
        state["title"] = self.title
        device = self.device
        if not Video.is_int(device):
            cwd = os.getcwd()
            devicepath = os.path.dirname(device)
            root = os.path.commonpath([cwd, devicepath])
            device = os.path.relpath(devicepath, root) + "/" + os.path.basename(device)
        state["device"] = device
        state["timestamps"] = self.timestamps
        return state

    def __setstate__(self, state):
        self.title = state["title"]
        self.device = state["device"]
        self.timestamps = state["timestamps"]

    def save(self, path="games/videos"):
        env = Environment()
        savepath = str(env.projectPath) + "/" + path
        Environment.checkDir(savepath)
        jsonFile = savepath + "/" + self.title
        self.writeJson(jsonFile)


@implementer(IChessBoardImageSet)
class ChessBoardImageSet:
    """a set of images of the current chess board"""

    def __init__(self, vision, image, frameIndex, timeStamp):
        self.vision = vision
        self.frameIndex = frameIndex
        # see https://stackoverflow.com/questions/47743246/getting-timestamp-of-each-frame-in-a-video
        self.timeStamp = timeStamp
        self.cbImage = ChessBoardImage(image, "chessboard")
        self.cbGUI = self.cbImage
        self.cbWarped = None
        self.cbIdeal = None
        self.cbPreMove = None
        self.cbDiff = None
        self.cbDebug = None

    def placeHolder(self, cbImage):
        """return an empty image if the image is not available"""
        if cbImage is None:
            return self.vision.video.createBlank(
                self.cbWarped.width, self.cbWarped.height, (128, 128, 128)
            )
        else:
            return cbImage.image

    def debugImage(self):
        if self.cbDebug is None:
            self.cbDebug = self.debugImage2x2(
                self.cbWarped, self.cbIdeal, self.cbDiff, self.cbPreMove
            )
        return self.cbDebug

    def debugImage2x2(self, image1, image2, image3, image4):
        image = self.vision.video.as2x2(
            self.placeHolder(image1),
            self.placeHolder(image2),
            self.placeHolder(image3),
            self.placeHolder(image4),
        )
        return ChessBoardImage(image, "debug")

    def showDebug(self, video=None):
        video.showImage(self.debugImage().image, "debug")

    def warpAndRotate(self, nowarp=False):
        """warp and rotate the image as necessary - add timestamp if in debug mode"""
        video = self.vision.video
        warp = self.vision.warp
        if warp.warping or nowarp:
            if nowarp:
                warped = self.cbImage.image.copy()
            else:
                warped = video.warp(self.cbImage.image, warp.points)
            if warp.rotation > 0:
                warped = video.rotate(warped, warp.rotation)
        else:
            warped = self.cbImage.image.copy()
        self.cbWarped = ChessBoardImage(warped, "warped")

    def prepareGUI(self):
        video = self.vision.video
        warp = self.vision.warp
        if self.vision.debug:
            self.cbGUI = self.debugImage()
            video.addTimeStamp(self.cbGUI.image)
        else:
            self.cbGUI = ChessBoardImage(self.cbWarped.image.copy(), "gui")
            if not warp.warping:
                video.drawTrapezoid(self.cbGUI.image, warp.points, warp.bgrColor)


@implementer(IWarp)
class Warp(YamlAbleMixin, JsonAbleMixin):
    """holds the trapezoid points to be use for warping an image take from a peculiar angle"""

    # construct me from the given setting
    def __init__(self, pointList=[], rotation=0, bgrColor=(0, 255, 0)):
        self.rotation = rotation
        self.bgrColor = bgrColor
        self.pointList = pointList
        self.updatePoints()

    def rotate(self, angle):
        """rotate me by the given angle"""
        self.rotation = self.rotation + angle
        if self.rotation >= 360:
            self.rotation = self.rotation % 360

    def updatePoints(self):
        """update my points"""
        pointLen = len(self.pointList)
        if pointLen == 0:
            self.points = None
        else:
            self.points = np.array(self.pointList)
        self.warping = pointLen == 4

    def addPoint(self, px, py):
        """add a point with the given px,py coordinate
        to the warp points make sure we have a maximum of 4 warpPoints if warppoints are complete when adding reset them
        this allows to support click UIs that need an unwarped image before setting new warp points.
        px,py is irrelevant for reset"""
        if len(self.pointList) >= 4:
            self.pointList = []
        else:
            self.pointList.append([px, py])
        self.updatePoints()


@implementer(IChessBoardImage)
class ChessBoardImage:
    """a chessboard image and it's transformations"""

    def __init__(self, image, title):
        self.image = image
        self.title = title
        self.height, self.width = image.shape[:2]
        self.pixels = self.height * self.width

    def diffBoardImage(self, cbOther):
        if cbOther is None:
            raise Exception("other is None for diff")
        h, w = self.height, self.width
        ho, wo = cbOther.height, cbOther.width
        if not h == ho or not w == wo:
            raise Exception(
                "image %d x %d has to have same size as other %d x %d for diff"
                % (w, h, wo, ho)
            )
        # return np.subtract(self.image,other)
        diff = cv2.absdiff(self.image, cbOther.image)
        return ChessBoardImage(diff, "diff")

    def showDebug(self, video=None, keyWait=5):
        if video is None:
            video = Video()
        video.showImage(self.image, self.title, keyWait=keyWait)
