#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Environment4Test import Environment4Test
from Environment import Environment
from WebApp import WebApp
from webchesscam import WebChessCamArgs
from IdealBoard import IdealBoard
testEnv = Environment4Test()
from timeit import default_timer as timer
import cv2
from PlotLib import PlotLib, PlotType


def test_ChessBoard12():
    plots=PlotLib("Ideal Colored Chessboard",PlotLib.A4(turned=True))
    shortTime=500      
    #IdealBoard.debug=False
    env=Environment()
    chessboard12Path=env.testMedia+'chessboard012.jpg'
    chessboard12=cv2.imread(chessboard12Path)
    IdealBoard.showImage(chessboard12,title="original",waitTime=shortTime)
    start=timer()      
    board=IdealBoard.createIdeal(527,527)
    end=timer()
    print('ideal board created in %.3fs' % (end-start))
    board.show(waitTime=shortTime)
    start=timer()  
    diffImage=board.diff(chessboard12)
    end=timer()
    print('diff created in %.3fs' % (end-start))
    IdealBoard.showImage(diffImage,title="diff",waitTime=shortTime)   
    start=timer()
    minBoards=[]
    optimized=IdealBoard.optimizeIdeal(chessboard12,minBoards)
    end=timer()
    print('optimized in %.3fs' % (end-start))
    for minBoard in minBoards:
        rgb=cv2.cvtColor(minBoard.image,cv2.COLOR_BGR2RGB)
        plots.addPlot(rgb, minBoard.debugInfo,minBoard.values,minBoard.diffSums)
        IdealBoard.showImage(minBoard.image, minBoard.debugInfo, waitTime=1)
    IdealBoard.showImage(image=optimized.image,title="optimized",waitTime=shortTime)
    IdealBoard.showImage(image=optimized.diff(chessboard12),title="optimizedDiff", waitTime=shortTime)
    board.save("/tmp/idealchessboard.jpg")
    plots.createPDF('/tmp/idealcoloredboard',plotType=PlotType.PLOT,infos={'Title': 'Ideal colored board'})

def test_IdealBoard():
    webApp = WebApp(WebChessCamArgs(["--debug","--speedup=4"]).args)
    for imageInfo in testEnv.imageInfos:
        bgr=testEnv.loadFromImageInfo(webApp,imageInfo)
        
        
test_ChessBoard12()
#test_IdealBoard()