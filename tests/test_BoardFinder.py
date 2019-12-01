#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.boardfinder import BoardFinder
from pcwawc.Environment4Test import Environment4Test
from timeit import default_timer as timer

testEnv = Environment4Test()

# test finding a chess board
def test_findBoard():
    BoardFinder.debug=True
    startt=timer()
    for imageInfo in testEnv.imageInfos:
        title=imageInfo["title"]
        fen=imageInfo["fen"]
        image,video,warp=testEnv.prepareFromImageInfo(imageInfo)      
        finder = BoardFinder(image,video=video)
        found=finder.find(limit=1,searchWidth=360)
        # we expected to find a board
        assert(len(found)==1)
        if BoardFinder.debug:
            finder.showDebug(title)
            finder.showPolygonDebug(title)
        finder.expand(image,title)               
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
