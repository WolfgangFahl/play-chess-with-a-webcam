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

debug=False
shortTime=1000//20
    
def tryOptimization(chessboard,title):
    if debug:
        plots=PlotLib("Ideal Colored Chessboard for "+title,PlotLib.A4(turned=True))
    
    #IdealBoard.debug=False
    IdealBoard.showImage(chessboard,title="original "+title,waitTime=shortTime)
    start=timer()      
    h, w = chessboard.shape[:2]
    board=IdealBoard.createIdeal(w,h)
    end=timer()
    print('ideal board created in %.3fs' % (end-start))
    board.show(waitTime=shortTime)
    start=timer()  
    diffImage=board.diff(chessboard)
    end=timer()
    print('diff created in %.3fs' % (end-start))
    IdealBoard.showImage(diffImage,title="diff",waitTime=shortTime)   
    start=timer()
    minBoards=[]
    optimized=IdealBoard.optimizeIdeal(chessboard,minBoards)
    end=timer()
    print('optimized in %.3fs' % (end-start))
    for minBoard in minBoards:
        rgb=cv2.cvtColor(minBoard.image,cv2.COLOR_BGR2RGB)
        if debug:
            plots.addPlot(rgb, minBoard.debugInfo,minBoard.values,minBoard.diffSums)
        IdealBoard.showImage(minBoard.image, minBoard.debugInfo, waitTime=1)
    IdealBoard.showImage(image=optimized.image,title="optimized",waitTime=shortTime)
    IdealBoard.showImage(image=optimized.diff(chessboard),title="optimizedDiff",waitTime=shortTime)
    board.save("/tmp/idealchessboard"+title+".jpg")
    if debug:
        plots.createPDF('/tmp/idealcoloredboard'+title,plotType=PlotType.PLOT,infos={'Title': 'Ideal colored board'})
    
def test_ChessBoard12():
    env=Environment()
    chessboard12Path=env.testMedia+'chessBoard012.jpg'
    # print (chessboard12Path)
    chessboard12=cv2.imread(chessboard12Path)
    assert chessboard12 is not None
    tryOptimization(chessboard12,"chessboard12")
    

def test_IdealBoard():
    webApp = WebApp(WebChessCamArgs(["--speedup=4"]).args)
    for imageInfo in testEnv.imageInfos:
        bgr=testEnv.loadFromImageInfo(webApp,imageInfo)
        tryOptimization(bgr, imageInfo['title'])
        
        
#test_ChessBoard12()
test_IdealBoard()
