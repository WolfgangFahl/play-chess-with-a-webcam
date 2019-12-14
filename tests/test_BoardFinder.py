#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.boardfinder import BoardFinder,Corners
from pcwawc.environment4test import Environment4Test
from pcwawc.environment import Environment
from pcwawc.chesstrapezoid import Trapez2Square
from pcwawc.video import Video
from timeit import default_timer as timer
import chess
testEnv = Environment4Test()

# test finding a chess board
def test_findBoard():
    BoardFinder.debug=True
    Corners.debug=True
    #Corners.debugSorting=True
    startt=timer()
    for imageInfo in testEnv.imageInfos:
        title=imageInfo.title
        fen=imageInfo.fen
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
            # wait for background histogram to be available -- see a few lines below
            #finder.showHistogramDebug(histograms,title,corners)
            finder.showPolygonDebug(image,title,corners)

        finder.expand(image,title,histograms,corners)

        if BoardFinder.debug:
            finder.showHistogramDebug(histograms,title,corners)
        endt=timer()
    if BoardFinder.debug:
        print ("found %d chessboards in %.1f s" % (len(testEnv.imageInfos),(endt-startt)))

def test_SortPoints():
    points=[(0,0),(0,1),(1,1),(1,0)]
    center=BoardFinder.centerXY(points)
    assert center==(0.5,0.5)
    sortedPoints=BoardFinder.sortPoints(points)
    assert sortedPoints==[(0, 0), (1, 0), (1, 1), (0, 1)]

def test_Trapez2Square():
    t2s=Trapez2Square((100,100),(200,100),(100,0),(0,0))
    assert t2s.relativeToTrapezXY(0,0)==(100.0,100.0)
    assert t2s.relativeToTrapezXY(1,0)==(200.0,100.0)
    assert t2s.relativeToTrapezXY(1,1)==(100.0,  0.0)
    assert t2s.relativeToTrapezXY(0,1)==(  0.0,  0.0)

def test_MovingBoard():
    video=Video()
    testvideos=['emptyBoard001','baxter']
    expected=[51,155]
    imagePath=Environment.debugImagePath+"testMovingBoard/"
    Environment.checkDir(imagePath)
    for testindex,testvideo in enumerate(testvideos):
        video.open(testEnv.testMedia + testvideo+".avi")
        ret=True
        speedup=5
        frames=0
        found=0
        while ret:
            ret, image, quitWanted = video.readFrame(show=False)
            frames+=1
            if quitWanted:
                break
            if ret:
                try:
                    title="corners-%s-%04d" % (testvideo,frames)
                    startt=timer()
                    finder = BoardFinder(image,video=video)
                    corners=finder.findChessBoard(image,title)
                    warped=video.warp(image.copy(), corners.trapez8x8)
                    video.drawTrapezoid(image,corners.trapez8x8.tolist(),(255,0,0))
                    video.showImage(warped,"warped")
                    endt=timer()
                    video.writeImage(image, imagePath+title+".jpg")
                    video.writeImage(warped, imagePath+title+"-warped.jpg")
                    found+=1
                    print("%3d/%3d: %dx%d in %.1f s" % (found,frames,corners.rows,corners.cols,(endt-startt)))
                except Exception as ex:
                    print ("%3d/%3d: %s" % (found,frames,ex))
            if frames%speedup==0:
                video.showImage(image,"original")
        video.close()
        assert found==expected[testindex]

test_SortPoints()
test_Trapez2Square()
test_findBoard()
test_MovingBoard()
