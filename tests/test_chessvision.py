'''
Created on 2019-12-10

@author: wf
'''
from pcwawc.chessimage import ChessBoardVision
from pcwawc.environment4test import Environment4Test

testEnv = Environment4Test()

# test reading video as jpg frames
def test_ReadAvi():
    debug=False
    title='emptyBoard001'
    vision=ChessBoardVision(title)
    vision.showDebug=debug
    vision.open(testEnv.testMedia +title+".avi")
    frameIndex=0
    while True:
        cbImage=vision.readChessBoardImage()
        if not vision.hasImage:
            break
        frameIndex+=1
        assert (cbImage.width,cbImage.height)==(640,480)
        assert (cbImage.frameIndex == frameIndex)
        if debug: print("%3d %.2fs" % (cbImage.frameIndex,cbImage.timeStamp))
    assert frameIndex==52    
    vision.save()
    
test_ReadAvi()    
