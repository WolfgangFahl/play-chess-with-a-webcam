'''
Created on 2019-12-07

@author: tk
'''
from pcwawc.chessvision import IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.runningstats import MinMaxStats,MovingAverage
import cv2
from zope.interface import implementer
from timeit import default_timer as timer

class ImageChange:
    """ detect change of a single image """
    
    thresh=150
    averageWindow=4
    def __init__(self):
        self.cbReferenceBW=None
        self.movingAverage=MovingAverage(ImageChange.averageWindow)
        self.stats=MinMaxStats()

    def check(self,cbImage):
        self.makeGray(cbImage)
        self.calcDifference()
        if self.hasReference:
            self.calcPixelChanges()
    
    def makeGray(self,cbImage):
        self.cbImage=cbImage
        image=cbImage.image
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.cbImageGray=ChessBoardImage(cv2.cvtColor(imageGray,cv2.COLOR_GRAY2BGR),"gray")
        # @TODO Make the treshold 150 configurable
        thresh=ImageChange.thresh
        (thresh, self.imageBW) = cv2.threshold(imageGray, thresh, 255, cv2.THRESH_TRUNC)
        self.cbImageBW=ChessBoardImage(cv2.cvtColor(self.imageBW,cv2.COLOR_GRAY2BGR),"bw")
    
    def calcDifference(self):    
        self.updateReference(self.cbImageBW)
        self.cbDiffImage=self.cbImageBW.diffBoardImage(self.cbReferenceBW)
        
    def updateReference(self,cbImageBW):
        self.hasReference=not self.cbReferenceBW is None
        if not self.hasReference:
            self.cbReferenceBW=cbImageBW
        
    def calcPixelChanges(self):
        self.pixelChanges=cv2.norm(self.cbImageBW.image, self.cbReferenceBW.image, cv2.NORM_L1) / self.cbImageBW.pixels
        self.movingAverage.push(self.pixelChanges)
        self.stats.push(self.pixelChanges)
        
    def __str__(self):    
        text="change: %5.1f, average: %s/%s, pixels: %d" % (self.pixelChanges,self.movingAverage.format(formatM="%5.1f"),self.stats.formatMinMax(formatR="%4d: %5.1f ± %5.1f",formatM=" %5.1f - %5.1f"),self.cbImageBW.pixels)
        return text
    
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
            self.imageChange.check(cbWarped)
            ic=self.imageChange
            endt=timer()   
            cbImageSet.cbDebug=cbImageSet.debugImage2x2(cbWarped,ic.cbImageGray,ic.cbImageBW,ic.cbDiffImage)
            if self.imageChange.hasReference: 
                if vision.debug:
                    print ('Frame %5d %.3f s:%s' % (cbImageSet.frameIndex,endt-start,ic))  

@implementer(IMoveDetector) 
class Simple8x8Detector(SimpleDetector):
    """ a simple treshold per field detector  """
    # construct me 
    def __init__(self):
        super().__init__()
    
    def setup(self,name,vision):
        super().setup(name,vision)
        self.board=self.vision.board
        self.imageChanges={}
        for square in self.board.genSquares():
            self.imageChanges[square.an]=ImageChange()
        
    def onChessBoardImage(self,imageEvent):
        super().onChessBoardImage(imageEvent)
        cbImageSet=imageEvent.cbImageSet
        vision=cbImageSet.vision
        if vision.warp.warping:
            cbWarped=cbImageSet.cbWarped
            # TODO only do once ...
            self.board.divideInSquares(cbWarped.width,cbWarped.height)
            # calculate pixelChanges per square based on parts of the bigger images created by the super class
            for square in self.board.genSquares():
                ic=self.imageChanges[square.an]
                ic.cbImageBW=ChessBoardImage(square.getSquareImage(self.imageChange.cbImageBW),square.an)
                ic.updateReference(ic.cbImageBW)
                if ic.hasReference:
                    ic.calcPixelChanges()
                    if self.vision.debug:
                        print ("%4d %s: %s" % (cbImageSet.frameIndex,square.an,ic))