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
    titles=['scholarsmate','emptyBoard001']
    expectedFrames=[334,52]
    for index,title in enumerate(titles):
        vision=ChessBoardVision(title)
        vision.showDebug=debug
        vision.open(testEnv.testMedia +title+".avi")
        frameIndex=0
        while True:
            cbImageSet=vision.readChessBoardImage()
            if not vision.hasImage:
                break
            frameIndex+=1
            cbImage=cbImageSet.cbImage
            assert (cbImage.width,cbImage.height)==(640,480)
            assert (cbImageSet.frameIndex == frameIndex)
            if debug: print("%3d %.2fs" % (cbImageSet.frameIndex,cbImageSet.timeStamp))
        assert frameIndex==expectedFrames[index]   
        vision.save()
        
test_ReadAvi()    
