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
        finder = BoardFinder(image)
        found=finder.find(limit=1,searchWidth=360)
        assert(len(found)>0)
        if BoardFinder.debug:
            finder.showDebug(title)
            finder.showPolygonDebug(title)
        foundPolygons=finder.toPolygons()
        for chesspattern in foundPolygons.keys():
            polygons=foundPolygons[chesspattern]
            for filterColor in (True,False):
                imageCopy=image.copy()
                masked=finder.maskPolygon(imageCopy, polygons, filterColor)
                if BoardFinder.debug:
                    prefix="masked-O-" if filterColor else "masked-X-"
                    finder.writeDebug(masked,title, prefix, chesspattern)
    endt=timer()
    if BoardFinder.debug:
        print ("found %d chessboards in %.1f s" % (len(testEnv.imageInfos),(endt-startt)))
        
test_findBoard()
