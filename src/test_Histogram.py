#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Histogram import Histogram
from Environment import TestEnvironment
from timeit import default_timer as timer
from WebApp import WebApp,Warp
from webchesscam import  WebChessCamArgs
import cv2
testEnv = TestEnvironment()

def test_Histogram():
    webApp = WebApp(WebChessCamArgs([]).args)
    
    histogram=Histogram("Chessboard Colors",Histogram.A4(turned=True))
    for imageInfo in testEnv.imageInfos:
        warpPoints=imageInfo['warpPoints']
        webApp.warp = Warp(list(warpPoints))
        webApp.warp.rotation=imageInfo['rotation']
        image,video = testEnv.getImageWithVideo(imageInfo['index'])
        webApp.video=video
        start = timer()
        bgr = webApp.warpAndRotate(image)
        height, width = bgr.shape[:2]
        end = timer()
        title=imageInfo["title"]
        print("%.3fs for loading image %s: %4d x %4d" % ((end-start),title,width,height))
       
        rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        histogram.addPlot(rgb,title)  
    histogram.save('/tmp/chessboardColors',{'Title': 'Chessboard Histogram'})
    
def test_A4():
    a4=Histogram.A4()
    a4w,a4h=a4
    assert round(a4w,2)==8.27
    assert round(a4h,2)==11.69
    a4t=Histogram.A4(turned=True)
    a4wt,a4ht=a4t
    assert round(a4ht,2)==8.27
    assert round(a4wt,2)==11.69
    

test_A4()
test_Histogram()
    