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
    for distance in range(0,7,1):
        for step in range(1,6,1):
            testImage=image.copy()
            start = timer()
            boardDetector.analyze(testImage,distance,step)
            end = timer()
            count=(2*distance+1)*(2*distance+1)
            size=distance*(step+1)
            print("%.3fs for distance %2d with %4d pixels %2d x %2d " % (end - start,distance,count,size,size)) # Time in seconds, e.g. 5.38091952400282
            video.showImage(testImage,"fields",True,500)

test_BoardDetector()
