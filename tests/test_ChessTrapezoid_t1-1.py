#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.Environment4Test import Environment4Test
from pcwawc.Video import Video
from pcwawc.ChessTrapezoid import ChessTrapezoid,ChessTSquare, FieldState, Color, SquareChange
from pprint import pprint
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import cv2
from matplotlib.collections import PatchCollection
import math
import os
import numpy as np
import pytest
import chess
import getpass

testEnv = Environment4Test()
speedup=5 # times
waitAtEnd=0 # msecs
debug=False
debugChangeHistory=False
debugPlotHistory=False
displayImage=True
displayDebug=True

def test_RankAndFile():
    csquare=ChessTrapezoid([(0,0),(100,0),(100,100),(0,100)])
    for tsquare in csquare.genSquares():
        assert tsquare.an==chess.FILE_NAMES[tsquare.col]+chess.RANK_NAMES[7-tsquare.row]

def test_Rotation():
    csquare=ChessTrapezoid([(0,0),(100,0),(100,100),(0,100)])
    rotations=[0,90,180,270]
    indices=[(0,0),(7,0),(7,7),(0,7)]
    expected=[(0,0),(7,0),(7,7),(0,7),
              (7,0),(7,7),(0,7),(0,0),
              (7,7),(0,7),(0,0),(7,0),
              (0,7),(0,0),(7,0),(7,7)]
    index=0
    for rotation in rotations:
        csquare.rotation=rotation
        anstr=""
        for row in range(ChessTrapezoid.rows):
            for col in range(ChessTrapezoid.cols):
                tsquare=csquare.tSquareAt(row, col)
                anstr=anstr+tsquare.an
            anstr=anstr+'\n'
        print (anstr)
        for rowcol in indices:
            row,col=rowcol
            rotated=csquare.rotateIndices(row,col,rotation)
            print (rotation,rowcol,rotated,expected[index])
            assert rotated==expected[index]
            index=index+1

def test_Transform():
    trapez=ChessTrapezoid([(20,40),(44,38),(60,8),(10,10)])
    #if debug:
    #    plt.figure()
    #    plt.plot(trapez.pts_normedSquare[[0,1,2,3,0], 0],trapez.pts_normedSquare[[0,1,2,3,0], 1], '-')
    squarePatches = []
    tSquarePatches = []
    # https://stackoverflow.com/questions/26935701/ploting-filled-polygons-in-python
    for tsquare in trapez.genSquares():
        color=[1,1,1,1] if tsquare.fieldColor else [0.1,0.1,0.1,1]
        polygon=Polygon(tsquare.rpolygon,color=color)
        tpolygon=Polygon(tsquare.polygon,color=color)
        squarePatches.append(polygon)
        tSquarePatches.append(tpolygon)
    # https://stackoverflow.com/questions/44725201/set-polygon-colors-matplotlib
    squareP = PatchCollection(squarePatches,match_original=True)
    tSquareP = PatchCollection(tSquarePatches,match_original=True)

    if debug:
        fig, ax = plt.subplots(2)
        ax1=ax[0]
        ax1.set_title("relative normed square")
        ax1.add_collection(squareP)
        ax1.set_ylim(ax1.get_ylim()[::-1])
        ax2=ax[1]

        ax2.set_title("trapezoidal warp")
        ax2.add_collection(tSquareP)
        ax2.autoscale()
        plt.show()

def test_RelativeToTrapezXY():
    trapez=ChessTrapezoid([(20,40),(40,40),(60,10),(10,10)])
    rxrys=[(0,0),(1,0),(1,1),(0,1),(0,0.5),(0.5,0.5),(1,0.5)]
    expected=[(20,40),(40,40),(60,10),(10,10),(17.1,31.4),(31.4,31.4),(45.7,31.4)]
    for index,rxry in enumerate(rxrys):
        rx,ry=rxry
        x,y=trapez.relativeToTrapezXY(rx,ry)
        ex,ey=expected[index]
        print ("%d r:(%.1f,%.1f) e:(%.1f,%.1f) == (%.1f,%.1f)?" % (index,rx,ry,ex,ey,x,y))
        assert x ==pytest.approx(ex,0.1)
        assert y ==pytest.approx(ey,0.1)

def test_SortedTSquares():
    trapezoid=ChessTrapezoid([(140,5),(506,10),(507,377),(137,374)])
    trapezoid.updatePieces(chess.STARTING_FEN)
    sortedTSquares=trapezoid.byFieldState()
    expected=[16,8,8,16,8,8]
    for fieldState,tsquareList in sortedTSquares.items():
        l=len(tsquareList)
        if debug:
            print(fieldState.title(),l)
        assert expected[fieldState]==l

def test_Stats():
    h=2
    w=2
    channels=3

    image=np.zeros((h,w,channels), np.uint8)
    image[0,0]=(100,50,200)
    image[0,1]=(120,60,220)
    avgcolor=Color(image)
    gmean,bmean,rmean=avgcolor.color
    gstds,bstds,rstds=avgcolor.stds
    if debug:
        print ("means %.2f %.2f %.2f " % (gmean,bmean,rmean))
        print ("stds  %.2f %.2f %.2f " % (gstds,bstds,rstds))
    assert avgcolor.color==(110.00,55.00,210.00 )
    assert avgcolor.stds==(5.00,10.00,10.00)

class TestVideo:
    def __init__(self,frames,totalFrames,path,points,rotation=270,idealSize=800,ans=None):
        self.path=path
        self.frames=frames
        self.totalFrames=totalFrames,
        self.points=points
        self.rotation=rotation
        self.idealSize=idealSize
        self.ans=ans

    def setup(self):
        self.trapezoid=ChessTrapezoid(self.points,rotation=self.rotation,idealSize=self.idealSize)
        if self.ans is None:
            self.ans=[]
            for tsquare in self.trapezoid.genSquares():
                self.ans.append(tsquare.an)
        return self

def test_ChessTrapezoid():
    video=Video()

    #ans=["e2","e4","e7","e5","d1","h5","b8","c6","f1","c4","c8","f6","f7","a1","h8"]
    tk=testEnv.testMedia+'../../Chess-Testmedia/'
    wf="/Users/wf/source/python/play-chess-with-a-webcam/media/"
    testVideos=[
        TestVideo(250,1392,tk +"TK_scholarsmate7.avi",[[0, 0], [404,0], [404,404], [0,404]],0,
           ans=None), #["e2","e4","e7","e5"]),
        TestVideo(12392,12392,wf +"chessVideo2019-10-17_185821.avi",[(210, 0), (603, 6), (581, 391), (208, 378)],rotation=270),
        TestVideo(200,500,tk + 'TK_Trompowsky.avi',[[0, 0], [398,0], [398,398], [0,398]],0,
           ans=None)
    ]
    # select a testVideo
    averageDiff = []
    testVideo=testVideos[1]
    trapezoid=testVideo.setup().trapezoid
    frames=testVideo.frames
    TL,TR,BR,BL = testVideo.points[:4]
    SizeX = max(TR[0],TL[0],BR[0],BL[0]) - min(TR[0],TL[0],BR[0],BL[0])
    SizeY = max(TR[1],TL[1],BR[1],BL[1]) - min(TR[1],TL[1],BR[1],BL[1])
    MaxDistorsion = 163216 / (SizeX*SizeY) * 163216 / (SizeX*SizeY) * 1
    print ("TL,TR,BR,BL,SizeX,SizeY,MaxDistorsion",TL,TR,BR,BL,SizeX,SizeY,MaxDistorsion)
    #SquareChange.medianFrameCount=12
    SquareChange.treshold=0.2
    validDiffSumTreshold=1.4
    invalidDiffSumTreshold=4.8
    diffSumDeltaTreshold=0.2
    ChessTSquare.showDebugChange=["e2","e4","e7","e5"]
    video.open(testVideo.path)
    start=timer()
    colorHistory={}
    changeHistory={}
    for frame in range(frames):
        ret, bgr, quitWanted = video.readFrame(show=False)
        if quitWanted:
            break
        assert ret
        assert bgr is not None
        h,w = bgr.shape[:2]
        if frame==0:
            #trapezoid.prepareMask(bgr)
            #trapezoid.maskPolygon(trapezoid.polygon)
            trapezoid.updatePieces(chess.STARTING_BOARD_FEN)
            referenceFrame = trapezoid.warpedBoardImage(bgr) # das ist das erste Frame - das nehmen wir als referenz
            prewarped = referenceFrame
            slidingMean = 100
        startc=timer()
        warped=trapezoid.warpedBoardImage(bgr)
        warpedHeight, warpedWidth = warped.shape[:2]
        #trapezoid.analyzeColors(warped)
        #idealImage=trapezoid.idealColoredBoard(warpedWidth,warpedHeight)
        p1 = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        (thresh, p1bw) = cv2.threshold(p1, 150, 255, cv2.THRESH_TRUNC)
        p2 = cv2.cvtColor(prewarped, cv2.COLOR_BGR2GRAY)
        (thresh, p2bw) = cv2.threshold(p2, 150, 255, cv2.THRESH_TRUNC)
        diffImage=trapezoid.diffBoardImage(p1bw,p2bw)
        averageDiff.append(cv2.norm(p1bw, p2bw, cv2.NORM_L1) / SizeX / SizeY)
        if frame>3:
            # slidingMean=(averageDiff[fram-4]+averageDiff[frame-3]+averageDiff[frame-2]+averageDiff[frame-1]+averageDiff[frame]) / 5
            slidingMean=(averageDiff[frame-2]+averageDiff[frame-1]+averageDiff[frame]) / 3
        prewarped = warped
        print ('Frame: %5d, Norm: %f, SM: %f, H: %f, W: %f' % (frame,averageDiff[frame],slidingMean,SizeX,SizeY) )
        #trapezoid.analyzeColors(diffImage)
        #squareChanges=trapezoid.detectChanges(warped,diffImage,validDiffSumTreshold,invalidDiffSumTreshold,diffSumDeltaTreshold)
        #changeHistory[frame]=squareChanges
        # diffSum=trapezoid.diffSum(warped,idealImage)
        endc=timer()
        #print('%dx%d frame %5d in %.3f s with %2d ✅ %4.1f Δ %4d ✅/%4d ❌' % (w,h,frame,endc-startc,squareChanges["valid"],squareChanges["diffSum"],squareChanges["validFrames"],squareChanges["invalidFrames"]))
        colorHistory[frame]=trapezoid.averageColors.copy()
        # pprint(colorHistory[frame])

        #mask=trapezoid.getEmptyImage(bgr)
        #trapezoid.drawFieldStates(mask,[FieldState.BLACK_EMPTY,FieldState.WHITE_EMPTY])
        #masked=trapezoid.maskImage(bgr,mask)
        #warped=trapezoid.warpedBoard(masked)
        if frame % speedup==0:
            keyWait=5
            #trapezoid.drawDebug(warped)
            if slidingMean<MaxDistorsion and averageDiff[frame]<MaxDistorsion:
                print ('SM: %f, Diff: %f, MD: %f' % (slidingMean,averageDiff[frame],MaxDistorsion))
                video.showImage(warped, "warped", keyWait=keyWait)
            if displayDebug:
                #trapezoid.drawDebug(idealImage)
                #video.showImage(idealImage,"ideal")
                trapezoid.drawDebug(diffImage)
                video.showImage(diffImage,"diff")

    end=timer()
    print('read %3d frames in %.3f s at %.0f fps' % (frames,end-start,(frames/(end-start))))
    if debugChangeHistory:
        plotChangeHistory(changeHistory,testVideo.ans,"square changes over time")
    if debugPlotHistory:
        plotColorHistory(colorHistory)
    if waitAtEnd>0:
        video.showImage(warped, "warped", keyWait=waitAtEnd)

def plotChangeHistory(changeHistory,ans,title):
    """ plot the changeHistory for the field with the given algebraic notations"""
    l=len(changeHistory)
    anIndex=0
    fig,axes=plt.subplots(5)
    ax0=axes[0]
    ax0.set_title('value')
    ax1=axes[1]
    ax1.set_title('median')
    ax2=axes[2]
    ax2.set_title('diff')
    ax3=axes[3]
    ax3.set_title('validdiff')
    ax4=axes[4]
    ax4.set_title('valid')
    for an in ans:
        x=np.empty(l)
        value=np.empty(l)
        mean=np.empty(l)
        diff=np.empty(l)
        validdiff=np.empty(l)
        found=False
        for frame,changes in changeHistory.items():
            x[frame]=frame
            squareChange=changes[an]
            value[frame]=squareChange.value
            mean[frame]=squareChange.mean
            diff[frame]=squareChange.diff
            validdiff[frame] = squareChange.diff if squareChange.valid or changes['valid']>60 else 0
            if validdiff[frame]>squareChange.treshold*1.5:
                found=True
        ax0.plot(x,value,label=an)
        ax1.plot(x,mean,label=an)
        ax2.plot(x,diff,label=an)
        if found:
            ax3.plot(x,validdiff,label=an)
        else:
            ax3.plot(x,validdiff)
        anIndex+=1
    for frame,changes in changeHistory.items():
        x[frame]=frame
        value[frame]=changes['valid']
    ax4.plot(x,value,label="valid")
    if len(ans)<10:
        ax0.legend(loc="upper right")
        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")
    ax3.legend(loc="upper right")

    plt.title(title)
    plt.legend()
    plt.show()

def plotColorHistory(colorHistory):
    l=len(colorHistory)
    print ("color  history for %d frames" % (l))
    #fig,ax=plt.subplots(len(FieldState))
    markers=['s','o','v','^','<','>']
    dist=10
    for fieldState in FieldState:
        size=l//dist
        x=np.empty(size)
        r=np.empty(size)
        g=np.empty(size)
        b=np.empty(size)
        for frame,avgColors in colorHistory.items():
            avgColor=avgColors[fieldState]
            if frame%dist==0:
                index=frame//dist
                if index<size:
                    x[index]=frame
                    b[index],g[index],r[index]=avgColor.color
        #ax[fieldState].set_title(fieldState.title())
        plt.plot(x,r,c='r',marker=markers[fieldState])
        plt.plot(x,g,c='g',marker=markers[fieldState])
        plt.plot(x,b,c='b',marker=markers[fieldState],label=fieldState.title())
        #ax[fieldState].autoscale()
    plt.legend()
    plt.show()

test_RankAndFile()
test_Rotation()
test_Transform()
test_RelativeToTrapezXY()
test_SortedTSquares()
test_Stats()
test_ChessTrapezoid()
