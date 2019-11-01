#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
from BoardFinder import BoardFinder
from mathUtils import getIndexRange
from Environment4Test import Environment4Test

testEnv = Environment4Test()

# test finding a chess board
def test_findBoard():
    # for index in range(5,8):
    image = testEnv.getImage(7)
    finder = BoardFinder(image)
    finder.prepare()


# test which side is black
def test_getBlackMaxSide():
    # fixme - this is not really the expected result
    expected = [1, 0, 3, 1, 0]
    for index in range(0, 5):
        image = testEnv.getImage(index + 1)
        finder = BoardFinder(image)
        side = finder.getBlackMaxSide(image)
        print ("black is at %d for index %d" % (side, index))
        assert expected[index] == side


# test hough transformation
def test_houghTransform():
    expected = [98, 46, 26, 20, 36, 38, 36, 120, 23440]
    for index in range(0, 9):
        video = Video()
        image = testEnv.getImage(index + 1)
        lines = video.houghTransform(image)
        print ("found %d lines in chessBoard%03d" % (lines.size, index + 1))
        assert expected[index] == lines.size
        video.drawLines(image, lines)
        video.showImage(image, "hough lines", True, 500)


def test_Dot():
    video = Video()
    dotImage = video.readImage(testEnv.testMedia+"greendot.jpg")
    image = testEnv.getImage(7)
    finder = BoardFinder(image)
    dotHSVRanges = finder.calibrateCornerMarker(dotImage)
    assert dotHSVRanges == [(79, 108), (91, 122), (51, 86)]


def test_histRange():
    hist = [0, 0, 0, 1, 2, 4, 2, 1, 0, 0, 0, 0]
    indexRange = getIndexRange(hist, 1, 10)
    print (indexRange)
    assert indexRange == (3, 7)


test_histRange()
test_Dot()
test_findBoard()
test_getBlackMaxSide()
test_houghTransform()
