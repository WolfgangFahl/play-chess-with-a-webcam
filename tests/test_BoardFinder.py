#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.boardfinder import BoardFinder
from pcwawc.Environment import Environment
from pcwawc.Environment4Test import Environment4Test
from pcwawc.histogram import Histogram
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
        assert(len(found)>0)
        if BoardFinder.debug:
            finder.showDebug(title)
            finder.showPolygonDebug(title)
        foundPolygons=finder.toPolygons()
        for chesspattern in foundPolygons.keys():
            rows,cols=chesspattern
            polygons=foundPolygons[chesspattern]
            for filterColor in (True,False):
                imageCopy=image.copy()
                masked=finder.maskPolygon(imageCopy, polygons, filterColor)
                if BoardFinder.debug:
                    prefix="masked-O-" if filterColor else "masked-X-"
                    finder.writeDebug(masked,title, prefix, chesspattern)
                histogram=Histogram(masked,histRange=(1,256))
                if BoardFinder.debug:
                    Environment.checkDir(finder.debugImagePath)  
                    prefix=prefix+"histogram"
                    filepath=finder.debugImagePath+'%s-%s-%dx%d.jpg' % (title,prefix,rows,cols)
                    histogram.save(filepath)  
                imageCopy=image.copy()
                colorMask=histogram.colorMask(imageCopy, 1.5)
                colorFiltered=video.maskImage(imageCopy,colorMask)
                if BoardFinder.debug:
                    prefix="colorFiltered-O-" if filterColor else "colorFiltered-X-"
                    finder.writeDebug(colorFiltered, title, prefix, chesspattern)
                
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
