#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Environment4Test import Environment4Test
from Video import Video
from ChessTrapezoid import ChessTrapezoid
from timeit import default_timer as timer

testEnv = Environment4Test()

speedup=4
waitAtEnd=True

def test_ChessTrapezoid():
    video=Video()
    video.open(testEnv.testMedia + 'scholarsmate.avi')
    frames=334
    start=timer()  
    trapezoid=ChessTrapezoid((140,5),(506,10),(507,377),(137,374))
    for frame in range(frames):
        ret, bgr, quitWanted = video.readFrame(show=False)
        if frame==0:
            trapezoid.prepareMask(bgr)
        masked=trapezoid.maskImage(bgr)
        if frame % speedup==0:
            keyWait=5
            if frame>=frames-speedup and waitAtEnd:
                keyWait=10000
            video.showImage(masked, "masked", keyWait=keyWait)
        #print(frame)
        assert ret
        assert bgr is not None         
    end=timer()
    print('read %3d frames in %.3f s at %.0f fps' % (frames,end-start,(frames/(end-start))))    
        
test_ChessTrapezoid()