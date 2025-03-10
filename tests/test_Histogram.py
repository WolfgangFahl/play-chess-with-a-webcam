#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

import cv2

from pcwawc.environment import Environment
from pcwawc.environment4test import Environment4Test
from pcwawc.plotlib import PlotLib, PlotType

testEnv = Environment4Test()


class HistogramTest(TestCase):

    def test_Histogram(self):

        histogram = PlotLib("Chessboard Colors", PlotLib.A4(turned=True))
        for imageInfo in testEnv.imageInfos:
            cbWarped = testEnv.loadFromImageInfo(imageInfo)
            rgb = cv2.cvtColor(cbWarped.image, cv2.COLOR_BGR2RGB)
            histogram.addPlot(rgb, imageInfo.title)
        Environment.checkDir(Environment.debugImagePath)
        histogram.createHistogramPDF(
            Environment.debugImagePath + "chessboardColors",
            plotType=PlotType.HISTOGRAMM,
            infos={"Title": "Chessboard Histogram"},
        )

    def test_A4(self):
        a4 = PlotLib.A4()
        a4w, a4h = a4
        assert round(a4w, 2) == 8.27
        assert round(a4h, 2) == 11.69
        a4t = PlotLib.A4(turned=True)
        a4wt, a4ht = a4t
        assert round(a4ht, 2) == 8.27
        assert round(a4wt, 2) == 11.69
