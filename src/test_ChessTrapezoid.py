#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Environment4Test import Environment4Test
from Video import Video
from ChessTrapezoid import ChessTrapezoid
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import numpy as np
import pytest

testEnv = Environment4Test()
speedup=4
waitAtEnd=False
debug=False

def test_Rotation():
    csquare=ChessTrapezoid((0,0),(100,0),(100,100),(0,100))
    rotations=[0,90,180,270]
    indices=[(0,0),(7,0),(7,7),(0,7)]
    expected=[(0,0),(7,0),(7,7),(0,7),
              (7,0),(7,7),(0,7),(0,0),
              (7,7),(0,7),(0,0),(7,0),
              (0,7),(0,0),(7,0),(7,7)]
    index=0
    for rotation in rotations:
        csquare.rotation=rotation
        for row in range(ChessTrapezoid.rows):
            for col in range(ChessTrapezoid.cols):
                tsquare=csquare.tSquareAt(row, col)
                print(tsquare['an'],end='')
            print()   
        for rowcol in indices:
            row,col=rowcol
            rotated=csquare.rotateIndices(row,col)
            print (rotation,rowcol,rotated,expected[index])
            assert rotated==expected[index]
            index=index+1
           
def test_Transform():
    trapez=ChessTrapezoid((20,40),(44,38),(60,8),(10,10))
    if debug:
        plt.figure()
        plt.plot(trapez.pts_normedSquare[[0,1,2,3,0], 0],trapez.pts_normedSquare[[0,1,2,3,0], 1], '-')
    squares=ChessTrapezoid.rows*ChessTrapezoid.cols
    xvalues=np.zeros(squares,np.float32)
    yvalues=np.zeros(squares,np.float32)
    rxvalues=np.zeros(squares,np.float32)
    ryvalues=np.zeros(squares,np.float32)
    index=0
    for row in range(ChessTrapezoid.rows):
        for col in range (ChessTrapezoid.cols):
            rx,ry=row/(ChessTrapezoid.rows-1),col/(ChessTrapezoid.cols-1)
            rxvalues[index]=rx
            ryvalues[index]=ry
            x,y=trapez.relativeXY(rx, ry)
            xvalues[index]=x
            yvalues[index]=y
            index=index+1
    
    if debug:        
        plt.plot(rxvalues,ryvalues,'o')        
        plt.figure()
        plt.plot(trapez.poly[[0,1,2,3,0], 0], trapez.poly[[0,1,2,3,0], 1], '-')
        plt.plot(xvalues,yvalues,'o')
        plt.show()               

def test_RelativeXY():
    trapez=ChessTrapezoid((20,40),(40,40),(60,10),(10,10))
    rxrys=[(0,0),(1,0),(1,1),(0,1),(0,0.5),(0.5,0.5),(1,0.5)]
    expected=[(20,40),(40,40),(60,10),(10,10),(17.1,31.4),(31.4,31.4),(45.7,31.4)]
    for index,rxry in enumerate(rxrys):
        rx,ry=rxry
        x,y=trapez.relativeXY(rx,ry)
        ex,ey=expected[index]
        print ("%d r:(%.1f,%.1f) e:(%.1f,%.1f) == (%.1f,%.1f)?" % (index,rx,ry,ex,ey,x,y))   
        assert x ==pytest.approx(ex,0.1) 
        assert y ==pytest.approx(ey,0.1)

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
        
test_Rotation()     
test_Transform() 
test_RelativeXY()  
test_ChessTrapezoid()