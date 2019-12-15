'''
Created on 2019-12-07

@author: tk
'''
from pcwawc.chessvision import IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.runningstats import MovingAverage
import cv2
from zope.interface import implementer
from timeit import default_timer as timer

@implementer(IMoveDetector) 
class SimpleDetector:
    """ a simple treshold detector """
    # construct me 
    def __init__(self):
        pass
    
    def setup(self,name,vision):
        self.name=name
        self.vision=vision
        self.imageChange=ImageChange()
        
    def onChessBoardImage(self,imageEvent):
        cbImageSet=imageEvent.cbImageSet
        vision=cbImageSet.vision
        if vision.warp.warping:
            cbWarped=cbImageSet.cbWarped
            start=timer()
            cbWarpedGray,cbWarpedBW,cbDiffImage,pixelChanges=self.imageChange.check(cbWarped)
            cbImageSet.cbDebug=cbImageSet.debugImage2x2(cbWarped,cbWarpedGray,cbWarpedBW,cbDiffImage)
            endt=timer()    
            print ('Frame: %5d %.3f s, change: %4.1f, average: %4.1f, pixels: %d' % (cbImageSet.frameIndex,endt-start,pixelChanges,self.imageChange.movingAverage.mean(),cbWarped.pixels))  

class ImageChange:
    """ change of a single image """
    def __init__(self):
        self.cbPreviousBW=None
        # @TODO make lenght of moving average configurable
        self.movingAverage=MovingAverage(4)
    
    def check(self,cbImage):
        image=cbImage.image
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cbImageGray=ChessBoardImage(cv2.cvtColor(imageGray,cv2.COLOR_GRAY2BGR),"gray")
        # @TODO Make the treshold 150 configurable
        thresh=150
        (thresh, imageBW) = cv2.threshold(imageGray, thresh, 255, cv2.THRESH_TRUNC)
        cbImageBW=ChessBoardImage(cv2.cvtColor(imageBW,cv2.COLOR_GRAY2BGR),"bw")
        if self.cbPreviousBW is None:
            self.previousBW=imageBW
            self.cbPreviousBW=cbImageBW
        cbDiffImage=cbImageBW.diffBoardImage(self.cbPreviousBW)
        self.pixelChanges=cv2.norm(imageBW, self.previousBW, cv2.NORM_L1) / cbImage.pixels
        self.movingAverage.push(self.pixelChanges)
        return cbImageGray,cbImageBW,cbDiffImage,self.pixelChanges
    
@implementer(IMoveDetector) 
class Simple8x8Detector:
    """ a simple treshold per field detector  """
    # construct me 
    def __init__(self):
        pass
    
    def setup(self,name,vision):
        self.name=name
        self.vision=vision
        self.board=vision.board
        self.imageChanges={}
        for square in self.board.genSquares():
            self.imageChanges[square.an]=ImageChange()
        
    def onChessBoardImage(self,imageEvent):
        cbImageSet=imageEvent.cbImageSet
        vision=cbImageSet.vision
        if vision.warp.warping:
            cbWarped=cbImageSet.cbWarped
            # TODO only do once ...
            start=timer()
            self.board.divideInSquares(cbWarped.width,cbWarped.height)
            for square in self.board.genSquares():
                squareImage=ChessBoardImage(square.getSquareImage(cbWarped),square.an)
                for square in self.board.genSquares():
                    self.imageChanges[square.an].check(squareImage)
            endt=timer()      
            print ("%4d: %.2f s" % (cbImageSet.frameIndex,endt-start))  
  