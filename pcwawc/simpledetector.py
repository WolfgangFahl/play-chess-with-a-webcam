'''
Created on 2019-12-07

@author: tk
'''
from pcwawc.chessvision import IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.detectstate import ChangeState
from pcwawc.eventhandling import Observable
from pcwawc.runningstats import MinMaxStats,MovingAverage
import cv2
from zope.interface import implementer
from timeit import default_timer as timer
from collections import OrderedDict

class ImageChange:
    """ detect change of a single image """
    
    thresh=150
    gradientDelta=0.725
    averageWindow=4
    
    def __init__(self):
        self.stats=MinMaxStats()
        self.movingAverage=MovingAverage(ImageChange.averageWindow)
        self.clear()
        
    def clear(self,newState=ChangeState.CALIBRATING):
        self.cbReferenceBW=None
        self.stats.clear()
        self.changeState=newState
        self.stableCounter=0

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
        
    def updateReference(self,cbImageBW, force=False):
        self.hasReference=not self.cbReferenceBW is None
        if not self.hasReference or force:
            self.cbReferenceBW=cbImageBW
        
    def calcPixelChanges(self):
        self.pixelChanges=cv2.norm(self.cbImageBW.image, self.cbReferenceBW.image, cv2.NORM_L1) / self.cbImageBW.pixels
        self.movingAverage.push(self.pixelChanges)
        self.stats.push(self.pixelChanges)
        
    def isStable(self):
        delta=abs(self.movingAverage.gradient())
        stable=delta<ImageChange.gradientDelta
        if stable:
            self.stableCounter+=1
        else:
            self.stableCounter=0    
        return stable  
        
    def __str__(self):    
        delta=self.movingAverage.gradient()
        text="%14s: %5.1f Δ: %5.1f Ø: %s/%s, Σ: %d" % (self.changeState.title(),self.pixelChanges,delta,self.movingAverage.format(formatM="%5.1f"),self.stats.formatMinMax(formatR="%4d: %5.1f ± %5.1f",formatM=" %5.1f - %5.1f"),self.cbImageBW.pixels)
        return text
    
@implementer(IMoveDetector) 
class SimpleDetector(Observable):
    """ a simple treshold detector """
    def __init__(self):
        """ construct me """
        # make me observable
        super(SimpleDetector,self).__init__()
        self.debug=False
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
                self.updateState(cbImageSet)
                if self.debug:
                    print ('Frame %5d %.3f s:%s' % (cbImageSet.frameIndex,endt-start,ic))               
                    
    def updateState(self,cbImageSet):
        calibrationWindow=5
        
        ic=self.imageChange
        ics=ic.changeState
        if ics==ChangeState.CALIBRATING:
            # leave calibrating when enough stable values are available
            if ic.isStable() and ic.stableCounter>=calibrationWindow:
                ic.changeState=ChangeState.PRE_MOVE
                ic.minInMove=ic.pixelChanges
                ic.maxInMove=ic.pixelChanges
        elif ics==ChangeState.PRE_MOVE:
            if not ic.isStable():
                ic.changeState=ChangeState.IN_MOVE
            else:   
                ic.minInMove=ic.pixelChanges
                ic.maxInMove=ic.pixelChanges
        elif ics==ChangeState.IN_MOVE:
            ic.maxInMove=max(ic.maxInMove,ic.pixelChanges)
            peak=ic.maxInMove-ic.minInMove
            dist=ic.pixelChanges-ic.minInMove
            if peak>0:
                relativePeak=dist/peak
                if ic.isStable():
                    if relativePeak<0.16:
                        self.onMoveDetected(cbImageSet)
            
    def onMoveDetected(self,cbImageSet):
        self.imageChange.clear()
        pass                   

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
        ic=self.imageChange
        cs=ic.changeState
        if vision.warp.warping and cs==ChangeState.PRE_MOVE:
            self.calcChanges(cbImageSet)
            ic.updateReference(ic.cbImageBW, force=True)
        
    def calcChanges(self,cbImageSet):
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
                #if self.vision.debug:
                    #print ("%4d %s: %s" % (cbImageSet.frameIndex,square.an,ic))
    
    def showDebug(self):
        for square in self.board.genSquares():
            ic=self.imageChanges[square.an]
            print ("%s: %s" % (square.an,ic))  
                    
    def onMoveDetected(self,cbImageSet):
        self.calcChanges(cbImageSet)
        changesByValue=OrderedDict(sorted(self.imageChanges.items(),key=lambda x:x[1].pixelChanges,reverse=True))
        keys=list(changesByValue.keys())
        change=(keys[0],keys[1])
        if self.vision.debug:
            print ("frame %4d: potential move for squares %s" % (cbImageSet.frameIndex,str(change))) 
            if self.debug:
                self.showDebug()
        move=self.vision.board.changeToMove(change)
        if move is None:
            if self.vision.debug:
                print ("change %s has no valid move" % (str(change)))
        else:
            super().onMoveDetected(cbImageSet)  
            for square in self.board.genSquares():
                ic=self.imageChanges[square.an]
                ic.clear()
            self.fire(move=move)    