#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Histogram import Histogram
from Environment4Test import Environment4Test
from WebApp import WebApp
from webchesscam import  WebChessCamArgs
import cv2
testEnv = Environment4Test()

def test_Histogram():
    webApp = WebApp(WebChessCamArgs([]).args)

    histogram=Histogram("Chessboard Colors",Histogram.A4(turned=True))
    for imageInfo in testEnv.imageInfos:
        bgr=testEnv.loadFromImageInfo(webApp,imageInfo)
        rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        histogram.addPlot(rgb,imageInfo['title'])
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
