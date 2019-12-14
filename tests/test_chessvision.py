'''
Created on 2019-12-10

@author: wf
'''
from pcwawc.args import Args
from pcwawc.chessimage import ChessBoardVision
from pcwawc.environment4test import Environment4Test

testEnv = Environment4Test()

# test reading video as jpg frames
def test_ReadAvi():
    debug=False
    titles=['scholarsmate','emptyBoard001']
    expectedFrames=[334,52]
    for index,title in enumerate(titles):
        args=Args("test")
        args.parse(["--input",testEnv.testMedia +title+".avi"])
        vision=ChessBoardVision(args.args)
        vision.showDebug=debug
        vision.open(args.args.input)
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
