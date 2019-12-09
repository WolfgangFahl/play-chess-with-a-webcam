#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.Board import Board
from pcwawc.BoardDetector import BoardDetector
from pcwawc.Environment4Test import Environment4Test
from pcwawc.Video import Video
from pcwawc.WebApp import WebApp
from pcwawc.webchesscam import WebChessCamArgs
from pcwawc.Field import FieldState
from pcwawc.runningstats import ColorStats
from timeit import default_timer as timer
import cv2

testEnv = Environment4Test()
frameDebug = True

def test_BoardFieldColorDetector():
    video = Video()
    board = Board()
    board.chessboard.clear()
    image = video.readImage(testEnv.testMedia + "chessBoard011.jpg")
    # this is a still image
    frameIndex = 1
    BoardDetector.debug = True
    boardDetector = BoardDetector(board, video)
    maxDistance = 5
    maxSteps = 7
    stepSteps = 1
    # how long to show results (e.g. 2 secs)
    totalWaitTime = 2000
    # wait only a fraction of the totalWaitTime
    waitTime = int(totalWaitTime / (maxDistance * maxSteps / stepSteps))
    for distance in range(1, maxDistance + 1, 1):
        for step in range(1, maxSteps + 1, stepSteps):
            testImage = image.copy()
            start = timer()
            testImage = boardDetector.analyze(testImage, frameIndex, distance, step)
            end = timer()
            count = (2 * distance + 1) * (2 * distance + 1)
            size = distance * (step + 1)
            if frameDebug:
                print("%.3fs for distance %2d with %4d pixels %2d x %2d " % (end - start, distance, count, size, size))  # Time in seconds, e.g. 5.38091952400282
            video.showImage(testImage, "fields", True, waitTime)
    video.close()


def test_FieldDetector():
    video = Video()
    webApp = WebApp(WebChessCamArgs(["--debug","--speedup=4"]).args)
    frames = None
    for boardIndex in range(2):
        BoardDetector.debug = True
        # setup webApp params to reuse warp method
        webApp.video = video
        if boardIndex == 1:
            video.open(testEnv.testMedia + 'emptyBoard001.avi')
            webApp.board.chessboard.clear_board()
            frames = 16
        if boardIndex == 0:
            video.open(testEnv.testMedia + 'scholarsmate.avi')
            frames = 20
            # @TODO speed up and test all frames again
            # frames=334
        warp=webApp.videoAnalyzer.warp    
        warp.rotation = 270
        warp.pointList = []
        warp.addPoint(140, 5)
        warp.addPoint(506, 10)
        warp.addPoint(507, 377)
        warp.addPoint(137, 374)

        for frame in range(0, frames):
            ret, bgr, quitWanted = video.readFrame(show=False)
            assert ret
            assert bgr is not None
            # bgr = cv2.cvtColor(jpgImage, cv2.COLOR_RGB2BGR)
            height, width = bgr.shape[:2]
            # print ("%d: %d x %d" % (frame,width,height))
            start = timer()
            bgr = webApp.videoAnalyzer.warpAndRotate(bgr)
            image = cv2.resize(bgr, (int(width * 1.5), int(height * 1.5)))
            video.showImage(image, "BoardDetector", keyWait=200)
            end = timer()
    video.close()


def test_ColorDistance():
    assert 25 == ColorStats.square(5)
    cStats = ColorStats()
    cStats.push(128, 128, 128)
    colorKey = cStats.colorKey()
    assert 49152 == colorKey
    
def checkFieldStates(boardDetector,board):
    sortedFields=boardDetector.sortByFieldState();
    counts = board.fieldStateCounts()
    for fieldState,fields in sortedFields.items():
        print ("%s: %2d" % (fieldState,len(fields)))
        assert counts[fieldState]==len(fields)
    return sortedFields    

def test_FieldStates():
    video=Video()
    board = Board()
    BoardDetector.debug = True
    boardDetector = BoardDetector(board, video)
    checkFieldStates(boardDetector, board)

def test_MaskFieldStates():
    video=Video()
    webApp = WebApp(WebChessCamArgs([]).args)
    boardDetector=webApp.boardDetector
    for imageInfo in testEnv.imageInfos:
        bgr=testEnv.loadFromImageInfo(webApp,imageInfo)
        rgba=cv2.cvtColor(bgr,cv2.COLOR_RGB2RGBA)
        waitTime=1000
        board=webApp.board
        sortedFields=checkFieldStates(boardDetector, board)
        whiteFields=sortedFields[FieldState.WHITE_EMPTY]
        print ("%d white fields for %s"  % (len(whiteFields),board.fen()))
        for field in whiteFields:
            print("%s: %3d,%3d" % (field.an,field.pcx,field.pcy))
        video.showImage(rgba, imageInfo['title'],keyWait=waitTime)
        video.close()
        

test_ColorDistance()
test_FieldStates()
test_MaskFieldStates()
test_BoardFieldColorDetector()
test_FieldDetector()
