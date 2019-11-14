#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Environment4Test import Environment4Test
from Environment import Environment
from Video import Video
from WebApp import WebApp
from webchesscam import WebChessCamArgs
from IdealBoard import IdealBoard
testEnv = Environment4Test()
from timeit import default_timer as timer
import cv2
import numpy as np
from PlotLib import PlotLib, PlotType

debug=True
shortTime=1000//20
    
def tryOptimization(chessboard,title):
    video=Video()
    if debug:
        plots=PlotLib("Ideal Colored Chessboard for "+title,PlotLib.A4(turned=True))
        plots.addPlot(chessboard,"original "+title,isBGR=True)
    #IdealBoard.debug=False
    video.showAndWriteImage(chessboard,title="original "+title,keyWait=shortTime)
    start=timer()      
    h, w = chessboard.shape[:2]
    board=IdealBoard.createIdeal(w,h)
    end=timer()
    print('ideal board created in %.3fs' % (end-start))
    video.showImage(board.image,title='idealboard',keyWait=shortTime)
    start=timer()  
    diffImage=board.diff(chessboard)
    end=timer()
    print('diff created in %.3fs' % (end-start))
    if debug:
        plots.addPlot(diffImage,"diff "+title,isBGR=True)
    video.showAndWriteImage(diffImage,title="diff "+title,keyWait=shortTime)   
    start=timer()
    minBoards=[]
    optimized=IdealBoard.optimizeIdeal(chessboard,minBoards)
    end=timer()
    print('optimized in %.3fs' % (end-start))
    if debug:
        for minBoard in minBoards:
            plots.addPlot(minBoard.image, minBoard.debugInfo,minBoard.values,minBoard.diffSums,isBGR=True)
        #video.showAndWriteImage(minBoard.image, minBoard.debugInfo, keyWait=1)
    video.showAndWriteImage(image=optimized.image,title="optimized "+title,keyWait=shortTime)
    video.showAndWriteImage(image=optimized.diff(chessboard),title="optimizedDiff "+title,keyWait=shortTime)
    video.writeImage(board.image,"/tmp/idealchessboard"+title+".jpg")
    if debug:
        plots.createPDF('/tmp/idealcoloredboard'+title,plotType=PlotType.PLOT,infos={'Title': 'Ideal colored board'})
    video.close()    
    
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

class Trapezoid:
    """ Trapezoid """
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft):
        self.poly=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        
    def prepareMask(self,image):    
        h, w = image.shape[:2]    
        self.mask = np.zeros((h,w,1), np.uint8)  
        color=(128)
        cv2.fillConvexPoly(self.mask,self.poly,color)
        
    def maskImage(self,image):
        masked=cv2.bitwise_and(image,image,mask=self.mask)
        return masked
     
def test_Video():
    video=Video()
    video.open(testEnv.testMedia + 'scholarsmate.avi')
    frames=334
    start=timer()  
    trapezoid=Trapezoid((140,5),(506,10),(507,377),(137,374))
    speedup=4
    for frame in range(frames):
        ret, bgr, quitWanted = video.readFrame(show=False)
        if frame==0:
            trapezoid.prepareMask(bgr)
        masked=trapezoid.maskImage(bgr)
        if frame % speedup==0:
            video.showImage(masked, "masked")
        #print(frame)
        assert ret
        assert bgr is not None         
    end=timer()
    print('read %3d frames in %.3f s at %.0f fps' % (frames,end-start,(frames/(end-start))))    
        
#test_ChessBoard12()
test_Video()
test_IdealBoard()
