#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

'''
Created on 2019-11-29

@author: wf
'''
from pcwawc.Environment4Test import Environment4Test
from pcwawc.histogram import Histogram, Stats
from pcwawc.ChessTrapezoid import ChessTrapezoid
import chess
testEnv = Environment4Test()

def test_Stats():
    # https://math.stackexchange.com/questions/857566/how-to-get-the-standard-deviation-of-a-given-histogram-image
    values=[(23,3),(24,7),(25,13),(26,18),(27,23),(28,17),(29,8),(30,6),(31,5)]
    stats=Stats(values)
    #print (vars(stats))
    assert stats.n==9
    assert stats.sum==100
    assert stats.prod==2694
    assert stats.mean==26.94
    assert stats.variance==3.6364
    assert stats.stdv==1.9069347130932406
    assert stats.min==23
    assert stats.max==31
    
def test_Histogram():
    imgPath="/tmp/"
    for imageInfo in testEnv.imageInfos:
        fen=imageInfo["fen"]
        if not fen==chess.STARTING_BOARD_FEN:
            continue
        image,video,warp=testEnv.prepareFromImageInfo(imageInfo)  
        title=imageInfo["title"]
        trapez=ChessTrapezoid(warp.pointList,rotation=warp.rotation,idealSize=800)  
        warped=trapez.warpedBoardImage(image)
        histogram=Histogram(warped)
        histogram.showDebug()
        histogram.save(imgPath+title+"-histogram.jpg")
    
test_Stats()    
#test_Histogram()