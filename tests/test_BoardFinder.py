#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.boardfinder import BoardFinder,Corners
from pcwawc.Environment4Test import Environment4Test
from timeit import default_timer as timer
import chess
testEnv = Environment4Test()

# test finding a chess board
def test_findBoard():
    BoardFinder.debug=True
    Corners.debug=True
    startt=timer()
    for imageInfo in testEnv.imageInfos:
        title=imageInfo["title"]
        fen=imageInfo["fen"]
        image,video,warp=testEnv.prepareFromImageInfo(imageInfo)      
        finder = BoardFinder(image,video=video)
        corners=finder.findOuterCorners(searchWidth=360)
        if fen==chess.STARTING_BOARD_FEN:
            assert corners.rows<=corners.cols
        else:
            assert corners.rows==corners.cols    
        
        if BoardFinder.debug:
            corners.showDebug(image,title)
            
        histograms=finder.getHistograms(image, title, corners)
        if BoardFinder.debug:
            finder.showHistogramDebug(histograms,title,corners)
            finder.showPolygonDebug(image,title,corners)
        finder.expand(image,title,histograms,corners)               
    endt=timer()
    if BoardFinder.debug:
        print ("found %d chessboards in %.1f s" % (len(testEnv.imageInfos),(endt-startt)))
    
def test_SortPoints():
    points=[(0,0),(0,1),(1,1),(1,0)]
    center=BoardFinder.centerXY(points)
    assert center==(0.5,0.5)
    sortedPoints=BoardFinder.sortPoints(points)
    assert sortedPoints==[(0, 0), (1, 0), (1, 1), (0, 1)]
            
test_SortPoints()        
test_findBoard()
