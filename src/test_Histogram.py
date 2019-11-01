#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Histogram import Histogram
from Environment import Environment
from timeit import default_timer as timer
from WebApp import WebApp,Warp
from webchesscam import  WebChessCamArgs
testEnv = Environment()

def test_Histogram():
    webApp = WebApp(WebChessCamArgs([]).args)
    warpPointList=[
        ([427,180],[ 962,180],[ 952, 688],[430, 691]),
        ([288, 76],[1057, 93],[1050, 870],[262, 866]),
        ([132, 89],[ 492, 90],[ 497, 451],[122, 462]),
        ([143, 18],[ 511, 13],[ 511, 387],[147, 386]),
        ([260,101],[ 962,133],[ 950, 815],[250, 819]),
        ([250,108],[ 960,135],[ 947, 819],[242, 828]),
        ([277,106],[ 972,129],[ 957, 808],[270, 800]),
        ([278, 88],[ 999, 88],[1072, 808],[124, 786]),
        ([360,238],[2380,224],[2385,2251],[407,2256]),
        ([483,132],[1338,124],[1541, 936],[255, 953]),
        ([  8,  1],[ 813,  1],[ 817, 812],[  3, 809])
        ]
    rotations=[0,0,0,0,270,270,270,0,0,0,0]
    rlen=len(rotations)
    wlen=len(warpPointList)
    if rlen != wlen:
        raise Exception("%d rotations for %d warpPoints" %(rlen,wlen))
    rlen=4
    histogram=Histogram("Chessboard Colors",rlen,turned=True,pages=2)
    for index in range(1,rlen+1):
        start = timer()
        warpPoints=warpPointList[index-1]
        webApp.warp = Warp(list(warpPoints))
        webApp.warp.rotation=rotations[index-1]
        image,video = testEnv.getImageWithVideo(index)
        webApp.video=video
        bgr = webApp.warpAndRotate(image)
        height, width = bgr.shape[:2]
        end = timer()
        print("%.3fs for loading image %d: %4d x %4d" % ((end-start),index,width,height))
        title="image%03d" % (index)
        histogram.addPlot(bgr,title)
    histogram.save('/tmp/chessboardColors')

test_Histogram()
    