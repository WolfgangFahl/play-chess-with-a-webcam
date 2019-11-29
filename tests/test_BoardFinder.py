#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.boardfinder import BoardFinder
from pcwawc.Environment4Test import Environment4Test

testEnv = Environment4Test()

# test finding a chess board
def test_findBoard():
    BoardFinder.debug=True
    for imageInfo in testEnv.imageInfos:
        fen=imageInfo["fen"]
        image,video,warp=testEnv.prepareFromImageInfo(imageInfo)      
        finder = BoardFinder(image)
        found=finder.find()
        assert(len(found)>0)

test_findBoard()
