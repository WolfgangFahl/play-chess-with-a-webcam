'''
Created on 2019-12-14

@author: wf
'''
from pcwawc.args import Args
from pcwawc.videoanalyze import VideoAnalyzer
from pcwawc.environment4test import Environment4Test

testEnv=Environment4Test()

def test_SimpleDetector():
    for testVideo in testEnv.getTestVideos():       
        path=testEnv.testMedia+testVideo
        cmdlineArgs=Args("test")
        cmdlineArgs.parse(["--debug","--input",path,"--detect","simple8x8"])
        analyzer=VideoAnalyzer(cmdlineArgs.args)
        analyzer.open()
        analyzer.nextImageSet()
        analyzer.findChessBoard()
        analyzer.setUpDetector()
        analyzer.analyze()       

test_SimpleDetector()
    
