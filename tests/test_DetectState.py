# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.detectstate import DetectState

def testDetectState():
    detectState=DetectState(validDiffSumTreshold=1.4,invalidDiffSumTreshold=4.8,diffSumDeltaTreshold=0.2)
    values=[
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0),
        (0,0)
    ]
    meanFrameCount=10
    for value in values:
        diffSum, diffSumDelta=value
        detectState.nextFrame()
        detectState.check(64,diffSum, diffSumDelta, meanFrameCount)
    assert detectState.frames==10    
    #print (vars(detectState))
    assert detectState.validFrames==10

testDetectState()