#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Args import Args
from BoardDetector import BoardDetector
from Board import Board
from Video import Video
from timeit import default_timer as timer
from WebApp import WebApp
from RunningStats import ColorStats
import cv2

def test_BoardFieldColorDetector():
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

def test_FieldDetector():
    video=Video()
    board=Board()
    webApp=WebApp(Args([]))
    video.open('testMedia/scholarsmate.avi')
    BoardDetector.debug=True
    boardDetector=BoardDetector(board,video)
    distance=5
    step=3
    # setup webApp params to reuse warp method
    webApp.video=video
    webApp.warp.rotation=270
    webApp.warp.addPoint(140,5)
    webApp.warp.addPoint(506,10)
    webApp.warp.addPoint(507,377)
    webApp.warp.addPoint(137,374)

    for frame in range(0,334):
        ret,bgr,quit=video.readFrame(show=False)
        assert ret
        assert bgr is not None
        #bgr = cv2.cvtColor(jpgImage, cv2.COLOR_RGB2BGR)
        height, width = bgr.shape[:2]
        #print ("%d: %d x %d" % (frame,width,height))
        bgr=webApp.warpAndRotate(bgr)
        start = timer()
        bgr=boardDetector.analyze(bgr,frame,distance,step)
        image = cv2.resize(bgr,(int(width*1.5),int(height*1.5)))
        video.showImage(image,"BoardDetector",keyWait=200)
        end = timer()


def test_ColorDistance():
    assert 25==ColorStats.square(5)
    cStats=ColorStats()
    cStats.push(128,128,128)
    colorKey=cStats.colorKey()
    assert 49152==colorKey

#test_ColorDistance()
#test_BoardFieldColorDetector()
test_FieldDetector()
