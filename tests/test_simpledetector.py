'''
Created on 2019-12-14

@author: wf
'''
from pcwawc.args import Args
from pcwawc.videoanalyze import VideoAnalyzer
from pcwawc.environment4test import Environment4Test

testEnv=Environment4Test()

def test_SimpleDetector():
    warpPointList=[ ([0,610],[0,0],[610,0],[610, 610]),
                   ([143,9],[503,9],[505,375],[137,373]),
                   ([143,9],[503,9],[505,375],[137,373]),
                   ]
    index=0
    for testVideo in testEnv.getTestVideos():
        path=testEnv.testMedia+testVideo
        print (testVideo)
        cmdlineArgs=Args("test")
        cmdlineArgs.parse(["--debug","--input",path,"--detect","simple8x8"])
        analyzer=VideoAnalyzer(cmdlineArgs.args)
        analyzer.open()
        vision=analyzer.vision
        if index<len(warpPointList):
            vision.warp.pointList=warpPointList[index]
            vision.warp.updatePoints() 
        else:
            analyzer.nextImageSet()
            analyzer.findChessBoard()
        analyzer.setUpDetector()
        analyzer.analyze()      
        index+=1 

test_SimpleDetector()
    
