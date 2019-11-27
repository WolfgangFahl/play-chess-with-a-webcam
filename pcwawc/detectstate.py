# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 27.11.2019

we could have used:
see https://github.com/pytransitions/transitions
see https://www.zeolearn.com/magazine/writing-maintainable-code-using-sate-machines-in-python
but we don't for the time being

@author: wf
'''

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
        