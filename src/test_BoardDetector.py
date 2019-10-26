#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from BoardDetector import BoardDetector
from Board import Board
from Video import Video
from timeit import default_timer as timer

def test_BoardDetector():
    video=Video()
    board=Board()
    image=video.readImage("testMedia/chessBoard011.jpg")
    BoardDetector.debug=True
    boardDetector=BoardDetector(board,video)
    for distance in range(1,21,2):
        testImage=image.copy()
        start = timer()
        boardDetector.analyze(testImage,distance)
        end = timer()
        print("%.3fs for distance %d" % (end - start,distance)) # Time in seconds, e.g. 5.38091952400282
        video.showImage(testImage,"fields",True,500)

test_BoardDetector()
