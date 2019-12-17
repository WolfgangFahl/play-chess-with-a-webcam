'''
Created on 2019-12-07

@author: tk
'''
from pcwawc.chessvision import IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.detectstate import ChangeState
from pcwawc.runningstats import MinMaxStats,MovingAverage
import cv2
from zope.interface import implementer
from timeit import default_timer as timer
from collections import OrderedDict

class ImageChange:
    """ detect change of a single image """
    
    thresh=150
    averageWindow=4
    
    def __init__(self):
        self.stats=MinMaxStats()
        self.movingAverage=MovingAverage(ImageChange.averageWindow)
        self.validLowerLimit=None
        self.clear()
        
    def clear(self,newState=ChangeState.CALIBRATING):
        self.cbReferenceBW=None
        self.stats.clear()
        self.changeState=newState
        self.validCounter=0
        self.invalidCounter=0

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
        
    def setLowerLimit(self):   
        self.validMax=self.stats.max
        self.validStdv=self.stats.standard_deviation()    
        pass
    
    def isValid(self,factor=4):
        self.validLowerLimit=self.validMax+self.validStdv*factor
        valid=self.pixelChanges<=self.validLowerLimit
        return valid
    
    def setUpperLimit(self):
        if self.validLowerLimit is not None:
            self.invalidMin=(self.pixelChanges+self.validLowerLimit)/2
        else:
            self.invalidMin=self.pixelChanges    
        pass
        
    def isInvalid(self,factor=4):
        invalid=self.pixelChanges>=self.invalidMin-self.validStdv*factor
        return invalid
        
    def __str__(self):    
        delta=self.movingAverage.gradient()
        text="%14s: %5.1f Δ: %5.1f Ø: %s/%s, Σ: %d" % (self.changeState.title(),self.pixelChanges,delta,self.movingAverage.format(formatM="%5.1f"),self.stats.formatMinMax(formatR="%4d: %5.1f ± %5.1f",formatM=" %5.1f - %5.1f"),self.cbImageBW.pixels)
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
                self.updateState(cbImageSet)
                if vision.debug:
                    print ('Frame %5d %.3f s:%s' % (cbImageSet.frameIndex,endt-start,ic))               
                    
    def updateState(self,cbImageSet):
        calibrationWindow=5
        validWindow=4
        invalidWindow=3
        factor=3
        
        ic=self.imageChange
        if ic.changeState==ChangeState.CALIBRATING:
            # leave calibrating when enough values are available
            if ic.stats.n>calibrationWindow:
                ic.changeState=ChangeState.VALID
                ic.validCounter=1
                ic.setLowerLimit()
        elif ic.changeState==ChangeState.VALID:
            if ic.isValid(2.5):
                ic.validCounter+=1
                ic.setLowerLimit()
                if ic.validCounter>=validWindow:
                    ic.changeState=ChangeState.VALID_STABLE 
            else:    
                ic.changeState=ChangeState.INVALID
        elif ic.changeState==ChangeState.VALID_STABLE:
            if ic.isValid(factor):
                ic.validCounter+=1
            else:    
                ic.changeState=ChangeState.INVALID
                ic.invalidCounter=1
        elif ic.changeState==ChangeState.INVALID:
            if ic.isValid(factor):
                ic.changeState=ChangeState.VALID
                ic.validCounter=1
            else:
                ic.invalidCounter+=1
                if ic.invalidCounter==2:
                    ic.setUpperLimit()
                if ic.invalidCounter>=invalidWindow:
                    ic.changeState=ChangeState.INVALID_STABLE
                    ic.validCounter=0
        elif ic.changeState==ChangeState.INVALID_STABLE:
            if not ic.isInvalid(factor):
                ic.changeState=ChangeState.POTENTIAL_MOVE
                ic.validCounter=1
            else:    
                ic.invalidCounter+=1
        elif ic.changeState==ChangeState.POTENTIAL_MOVE:
            if not ic.isInvalid(factor):
                ic.validCounter+=1
                delta=abs(ic.movingAverage.gradient())
                if delta<0.5:
                    # This should be a move detect ....
                    self.onMoveDetected(cbImageSet)
            else:
                ic.changeState=ChangeState.INVALID_STABLE
                ic.validCounter=0    
            
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
        cs=self.imageChange.changeState
        if vision.warp.warping and cs==ChangeState.VALID_STABLE or cs==ChangeState.POTENTIAL_MOVE:
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
                        
    def onMoveDetected(self,cbImageSet):
        if self.vision.debug:
            print ("potential move detected")
            for square in self.board.genSquares():
                ic=self.imageChanges[square.an]
                print ("%4d %s: %s" % (cbImageSet.frameIndex,square.an,ic))
        changesByValue=OrderedDict(sorted(self.imageChanges.items(),key=lambda x:x[1].pixelChanges,reverse=True))
        keys=list(changesByValue.keys())
        ans=(keys[0],keys[1])
        print ("potential move for squares %s" % (str(ans))) 
        # TODO - check if move is legal before accepting it with the following call:
        super().onMoveDetected(cbImageSet)  
        for square in self.board.genSquares():
            ic=self.imageChanges[square.an]
            ic.clear()                  