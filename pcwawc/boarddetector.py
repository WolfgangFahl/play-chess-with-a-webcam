#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import cv2
from zope.interface import implementer

from pcwawc.chessimage import ChessBoardImage
from pcwawc.chessvision import FieldState, IMoveDetector
from pcwawc.eventhandling import Observable


@implementer(IMoveDetector)
class BoardDetector(Observable):
    """detect a chess board's state from the given image"""

    frameDebug = False

    def __init__(self):
        """construct me"""
        # make me observable
        super(BoardDetector, self).__init__()
        pass

    def setup(self, name, vision):
        self.name = name
        self.vision = vision
        self.board = vision.board
        self.video = vision.video
        self.hsv = None
        self.debug = False

    def sortByFieldState(self):
        # get a dict of fields sorted by field state
        sortedByFieldState = sorted(
            self.board.fieldsByAn.values(), key=lambda field: field.getFieldState()
        )
        counts = self.board.fieldStateCounts()
        sortedFields = {}
        fromIndex = 0
        for fieldState in FieldState:
            toIndex = fromIndex + counts[fieldState]
            sortedFields[fieldState] = sortedByFieldState[fromIndex:toIndex]
            fromIndex = toIndex
        return sortedFields

    def analyzeFields(self, image, grid, roiLambda):
        for field in self.board.genSquares():
            field.divideInROIs(grid, roiLambda)
            for roi in field.rois:
                roi.analyze(image)

    def analyzeColors(self, image, distance=3, step=1):
        self.hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        for field in self.board.genSquares():
            field.analyzeColor(image, self.hsv, distance, step)

    def onChessBoardImage(self, imageEvent):
        cbImageSet = imageEvent.cbImageSet
        vision = cbImageSet.vision
        args = vision.args
        distance = args.distance
        step = args.step
        return self.analyze(cbImageSet, distance, step)

    # analyze the given image
    def analyze(self, cbImageSet, distance=3, step=1):
        frameIndex = cbImageSet.frameIndex
        cbWarped = cbImageSet.cbWarped
        image = cbWarped.image
        self.board.divideInSquares(cbWarped.width, cbWarped.height)
        self.analyzeColors(image, distance, step)
        sortedFields = self.sortByFieldState()

        if self.debug:
            overlay = image.copy()

        for fieldState, fields in sortedFields.items():
            for field in fields:
                l = field.luminance
                if BoardDetector.frameDebug:
                    print(
                        "frame %5d: %s luminance: %3.0f ± %3.0f (%d) rgbColorKey: %3.0f colorKey: %.0f"
                        % (
                            frameIndex,
                            field.an,
                            l.mean(),
                            l.standard_deviation(),
                            l.n,
                            field.rgbColorKey,
                            field.colorKey,
                        )
                    )
                if self.debug:
                    field.drawDebug(self.video, overlay, fieldState)
                    alpha = 0.6  # Transparency factor.
                    # Following line overlays transparent rectangle over the image
                    image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
                    image = image_new
                    cbImageSet.cbDebug = ChessBoardImage(image, "debug")
        return image
