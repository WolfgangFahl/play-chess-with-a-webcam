#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import sys
import cv2

# Local imports
from pcwawc.InputManager import InputManager
from pcwawc.Video import Video
from pcwawc.BoardFinder import BoardFinder, BadSegmentation
from pcwawc.MovementDetector import MovementDetector, BadImage


class UserExit(Exception):
    pass


class ChessCam(object):
    """ Chess Camera get next move by analyzing movements."""

    def __init__(self):
        self.video = Video()
        pass

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

                quit = not self.video.showImage(processedImages[2], "chessCam")
                if quit:
                   raise UserExit

                try:
                    move = self.moveDetector.detectMove(processedImages[0])
                except BadImage as e:
                    # print str(e)
                    pass
                except cv2.error as e:
                    print(str(e))
                    pass
        return move

    def getDominatorOffset(self):
        return self.finder.getDominatorOffset()

    def prepare(self, argv):
        self.captureHdl = InputManager(argv)
        self.args = self.captureHdl.args

        # Create window(s)
        cv2.namedWindow("chessCam", 1)
        # cv2.resizeWindow("chessCam", CHESSCAM_WIDTH, CHESSCAM_HEIGHT)
        if self.args.fullScreen:
            # https://stackoverflow.com/a/34337534/1497139
            cv2.setWindowProperty("chessCam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # cv.NamedWindow("chessCamDebug", 1)
        # cv.ResizeWindow("chessCamDebug", CHESSCAM_WIDTH, CHESSCAM_HEIGHT)

        BoardFinder.debug = self.args.debug
        if self.args.cornermarker is not None:
            video = Video()
            cornerMarkerImage = video.readImage(self.args.cornermarker)
            indexRanges = BoardFinder.calibrateCornerMarker(cornerMarkerImage)
            BoardFinder.dotHSVRanges = indexRanges
        # initialize my board finder
        self.analyzeFrame()

    def analyzeFrame(self):
        frame = self.captureHdl.getFrame()
        self.finder = BoardFinder(frame)
        self.finder.prepare()

    def detectMovement(self):
        # Initialize the MovementDetector
        success = False

        while not success:
            success = True
            self.analyzeFrame()
            try:
                processedImages = self.finder.GetFullImageBoard()
                self.moveDetector = MovementDetector(processedImages[0])
            except (BadImage, BadSegmentation):
                success = False

    def playChessWithCam(self, args):
        self.prepare(args)
        self.detectMovement()
        self.playChessWithCamMoves()

    def playChessWithCamMoves(self):
        try:
            while True:
                move = self.getNextMove()
                if len(move) != 0:
                    print("Move")
                    print(move)

        except UserExit:
            pass


if __name__ == "__main__":
    chessCam = ChessCam()
    chessCam.playChessWithCam(sys.argv[1:])
