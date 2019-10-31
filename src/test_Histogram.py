#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Histogram import Histogram
from Environment import Environment
from timeit import default_timer as timer
from WebApp import WebApp,Warp
from webchesscam import  WebChessCamArgs
import time

testEnv = Environment()


def test_Histogram():
    webApp = WebApp(WebChessCamArgs([]).args)
    warpPointList=[
        ([427,180],[ 962,180],[ 952,688],[430,691]),
        ([288, 76],[1057, 93],[1050,870],[262,866]),
        ([132, 89],[ 492, 90],[ 497,451],[122,462]),
        ([143, 18],[ 511, 13],[ 511,387],[147,386])
        ]
    for index in range(1,5):
        start = timer()
        warpPoints=warpPointList[index-1]
        webApp.warp = Warp(list(warpPoints))
        image,video = testEnv.getImageWithVideo(index)
        webApp.video=video
        bgr = webApp.warpAndRotate(image)
        height, width = bgr.shape[:2]
        end = timer()
        print("%.3fs for loading image %d: %4d x %4d" % ((end-start),index,width,height))
        title="image %d" % (index)
        histogram=Histogram(bgr,video,title)
        histogram.show(500)
        

test_Histogram()
    