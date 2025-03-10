"""
Created on 2019-12-10

@author: wf
"""

from unittest import TestCase

from pcwawc.args import Args
from pcwawc.chessimage import ChessBoardVision
from pcwawc.environment4test import Environment4Test
from pcwawc.video import Video

testEnv = Environment4Test()


class ChessVisionTest(TestCase):
    # test reading video as jpg frames
    def test_ReadAvi(self):
        debug = False
        # "0","1"
        titles = ["scholarsmate", "emptyBoard001"]
        expectedFrames = [334, 52]
        # (1920,1080),(1280,720),
        expectedSize = [(640, 480), (640, 480)]
        for index, title in enumerate(titles):
            args = Args("test")
            if Video.is_int(title):
                device = title
            else:
                device = testEnv.testMedia + title + ".avi"
            args.parse(["--input", device])
            vision = ChessBoardVision(args.args)
            vision.showDebug = debug
            vision.open(args.args.input)
            frameIndex = 0
            while True:
                cbImageSet = vision.readChessBoardImage()
                if not vision.hasImage:
                    break
                frameIndex += 1
                cbImage = cbImageSet.cbImage
                if debug:
                    print("%d x %d" % (cbImage.width, cbImage.height))
                assert (cbImage.width, cbImage.height) == expectedSize[index]
                assert cbImageSet.frameIndex == frameIndex
                if debug:
                    print("%3d %.2fs" % (cbImageSet.frameIndex, cbImageSet.timeStamp))
            assert frameIndex == expectedFrames[index]
            vision.save()
