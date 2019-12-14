#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.args import Args
from pcwawc.board import Board
from pcwawc.boarddetector import BoardDetector
from pcwawc.environment4test import Environment4Test
from pcwawc.video import Video
from pcwawc.chessvision import FieldState
from pcwawc.runningstats import ColorStats
from timeit import default_timer as timer
import cv2
from pcwawc.videoanalyze import VideoAnalyzer

testEnv = Environment4Test()
frameDebug = True

def test_BoardFieldColorDetector():
    imageInfo=testEnv.imageInfos[10]
    analyzer=testEnv.analyzerFromImageInfo(imageInfo)
    analyzer.open
    cbImageSet=analyzer.nextImageSet()
    boardDetector=analyzer.moveDetector
    video=analyzer.vision.video
    warped=cbImageSet.cbWarped.image
    maxDistance = 5
    maxSteps = 7
    stepSteps = 1
    # how long to show results (e.g. 2 secs)
    totalWaitTime = 2000
    # wait only a fraction of the totalWaitTime
    waitTime = int(totalWaitTime / (maxDistance * maxSteps / stepSteps))
    for distance in range(1, maxDistance + 1, 1):
        for step in range(1, maxSteps + 1, stepSteps):
            cbImageSet.cbWarped.image=warped.copy()
            start = timer()
            testImage = boardDetector.analyze(cbImageSet, distance, step)
            end = timer()
            count = (2 * distance + 1) * (2 * distance + 1)
            size = distance * (step + 1)
            if frameDebug:
                print("%.3fs for distance %2d with %4d pixels %2d x %2d " % (end - start, distance, count, size, size))  # Time in seconds, e.g. 5.38091952400282
            video.showImage(testImage, "fields", True, waitTime)
    video.close()

def test_FieldDetector():
    frames = None
    for boardIndex in range(2):
        # setup webApp params to reuse warp method
        if boardIndex == 1:
            path=testEnv.testMedia + 'emptyBoard001.avi'
            fen=Board.EMPTY_FEN
            frames = 16
        if boardIndex == 0:
            path=testEnv.testMedia + 'scholarsmate.avi'
            fen=Board.START_FEN
            frames = 20
            # @TODO speed up and test all frames again
            # frames=334
        args=Args("test")
        args.parse(["--debug","--speedup=4","--input",path,"--fen",fen])
        analyzer=VideoAnalyzer(args.args)
        warp=analyzer.vision.warp    
        warp.rotation = 270
        warp.pointList = []
        warp.addPoint(140, 5)
        warp.addPoint(506, 10)
        warp.addPoint(507, 377)
        warp.addPoint(137, 374)
        analyzer.open()
        vision=analyzer.vision
        video=vision.video
        for frame in range(0, frames):
            cbImageSet=vision.readChessBoardImage()
            assert analyzer.hasImage()
            start = timer()
            analyzer.processImageSet(cbImageSet)
            video.showImage(cbImageSet.debugImage().image, "BoardDetector", keyWait=200)
            end = timer()
        analyzer.close()


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
    boardDetector = BoardDetector()
    boardDetector.setup("luminance",board, video,None)
    boardDetector.debug = True
    checkFieldStates(boardDetector, board)

def test_MaskFieldStates():
    #video=Video()
    #webApp = WebApp(WebChessCamArgs([]).args)
    #boardDetector=webApp.videoAnalyzer.moveDetector
    for imageInfo in testEnv.imageInfos:
        analyzer=testEnv.analyzerFromImageInfo(imageInfo)
        video=analyzer.vision.video
        cbImageSet=analyzer.vision.readChessBoardImage()
        assert analyzer.hasImage()
        analyzer.processImageSet(cbImageSet)
        rgba=cv2.cvtColor(cbImageSet.cbWarped.image,cv2.COLOR_RGB2RGBA)
        waitTime=1000
        board=analyzer.board
        sortedFields=checkFieldStates(analyzer.moveDetector, board)
        whiteFields=sortedFields[FieldState.WHITE_EMPTY]
        print ("%d white fields for %s"  % (len(whiteFields),board.fen))
        for field in whiteFields:
            print("%s: %3d,%3d" % (field.an,field.pcx,field.pcy))
        video.showImage(rgba, imageInfo.title,keyWait=waitTime)
        video.close()
        

test_ColorDistance()
test_FieldStates()
test_MaskFieldStates()
test_BoardFieldColorDetector()
test_FieldDetector()
