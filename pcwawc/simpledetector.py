'''
Created on 2019-12-07

@author: tk
'''
from pcwawc.chessvision import IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.runningstats import MovingAverage
import cv2
from zope.interface import implementer

@implementer(IMoveDetector) 
class SimpleDetector:
    """ a simple treshold detector """
    # construct me 
    def __init__(self):
        pass
    
    def setup(self,name,board,video,args):
        self.name=name
        self.board=board
        self.video=video
        self.args=args
        self.cbPreviousBW=None
        self.movingAverage=MovingAverage(4)
        
    def onChessBoardImage(self,imageEvent):
        cbImageSet=imageEvent.cbImageSet
        vision=cbImageSet.vision
        if vision.warp.warping:
            cbWarped=cbImageSet.cbWarped
            warped=cbWarped.image
            warpedGray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            cbWarpedGray=ChessBoardImage(cv2.cvtColor(warpedGray,cv2.COLOR_GRAY2BGR),"gray")
            (thresh, warpedBW) = cv2.threshold(warpedGray, 150, 255, cv2.THRESH_TRUNC)
            cbWarpedBW=ChessBoardImage(cv2.cvtColor(warpedBW,cv2.COLOR_GRAY2BGR),"bw")
            if self.cbPreviousBW is None:
                self.previousBW=warpedBW
                self.cbPreviousBW=cbWarpedBW
            cbDiffImage=cbWarpedBW.diffBoardImage(self.cbPreviousBW)
            cbImageSet.cbDebug=cbImageSet.debugImage2x2(cbWarped,cbWarpedGray,cbWarpedBW,cbDiffImage)
            pixelChanges=cv2.norm(warpedBW, self.previousBW, cv2.NORM_L1) / cbWarped.pixels
            self.movingAverage.push(pixelChanges)
            print ('Frame: %5d, change: %4.1f, average: %4.1f, pixels: %d' % (cbImageSet.frameIndex,pixelChanges,self.movingAverage.mean(),cbWarped.pixels))  

