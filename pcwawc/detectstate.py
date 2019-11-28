# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 27.11.2019

we could have used:
see https://github.com/pytransitions/transitions
see https://www.zeolearn.com/magazine/writing-maintainable-code-using-sate-machines-in-python
but we don't for the time being

@author: wf
'''
from timeit import default_timer as timer
from pcwawc.ChessTrapezoid import FieldState

class DetectState(object):
    '''
    keeps track of the detections state
    '''

    def __init__(self,validDiffSumTreshold,invalidDiffSumTreshold,diffSumDeltaTreshold,onPieceMoveDetected=None,onMoveDetected=None):
        """ construct me """
        self.frames=0
        self.validFrames=0
        self.invalidFrames=0
        self.validDiffSumTreshold=validDiffSumTreshold
        self.invalidDiffSumTreshold=invalidDiffSumTreshold
        self.diffSumDeltaTreshold=diffSumDeltaTreshold
        self.onPieceMoveDetected=onPieceMoveDetected
        self.onMoveDetecte=onMoveDetected
        
    def check(self,validChanges,diffSum,diffSumDelta,meanFrameCount):
        """ check the detection state given the current diffSum and diffSumDelta"""
        self.invalidStarted=self.invalidFrames>3
        self.invalidStable=self.invalidFrames>=meanFrameCount,
        self.validStable=self.validFrames>=meanFrameCount     
        # trigger statistics push if valid
        if self.invalidStable:
            self.validBoard=diffSum<self.invalidDiffSumTreshold and abs(diffSumDelta)<self.diffSumDeltaTreshold and validChanges>=62
        else:
            self.validBoard=diffSum<self.validDiffSumTreshold
        if self.validBoard:
            self.validFrames+=1
        else:
            self.invalidFrames+=1      
            
    def nextFrame(self):
        self.frames+=1      
    
    def invalidEnd(self):
        self.invalidFrames=0    
        
    def validEnd(self): 
        self.validFrames=0      
        
class DetectColorState(object):
    """ detect state from Color Distribution """
    imgPath="/tmp/"
    
    def __init__(self,trapez):
        self.frames=0
        self.trapez=trapez
        
    def check(self,image,averageColors,drawDebug=False):
        self.frames+=1
        startco=timer()
        self.averageColors=averageColors
        self.image=image
        self.fieldColorStats=self.trapez.optimizeColorCheck(image,averageColors)
        endco=timer()
        if drawDebug:
            self.fieldColorStats.showStatsDebug(endco-startco)
            self.drawDebug()
        valid=self.fieldColorStats.minSelectivity>0
        if not valid:
            for tSquare in self.trapez.genSquares():
                if drawDebug:
                    self.fieldColorStats.showFieldStateDebug(tSquare.fieldState)
                state=self.squareState(tSquare, self.fieldColorStats.colorPercent[tSquare.an])
        
    def squareState(self,tSquare,percent):
        
        #if tSquare.fieldState in FieldState.
        return True     
    
    def drawDebug(self):
        for tSquare in self.trapez.genSquares():
            state=self.squareState(tSquare, self.fieldColorStats.colorPercent[tSquare.an])
            percent="%.0f" % (self.fieldColorStats.colorPercent[tSquare.an]) 
            self.trapez.drawRCenteredText(self.image, percent, tSquare.rcx,tSquare.rcy,(0,255,0))  
        filepath="%s/colorState-%04d.jpg" % (DetectColorState.imgPath,self.frames)    
        self.trapez.video.writeImage(self.image,filepath)          