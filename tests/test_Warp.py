#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import tempfile

from pcwawc.chessimage import Warp
from pcwawc.jsonablemixin import JsonAbleMixin
from pcwawc.yamlablemixin import YamlAbleMixin

debug = False
from unittest import TestCase


class WarpTest(TestCase):

    def getTestWarp(self):
        warp = Warp([])
        warp.addPoint(678, 25)
        warp.addPoint(1406, 270)
        warp.addPoint(1136, 1048)
        warp.addPoint(236, 666)
        return warp

    def test_Rotation(self):
        warp = Warp()
        warp.rotate(80)
        warp.rotate(300)
        assert warp.rotation == 20

    def test_WarpPoints(self):
        warp = self.getTestWarp()
        print(warp.pointList)
        print(warp.points)
        assert warp.pointList == [[678, 25], [1406, 270], [1136, 1048], [236, 666]]
        # simulate clear click
        warp.addPoint(0, 0)
        warp.addPoint(679, 25)
        warp.addPoint(1408, 270)
        warp.addPoint(1136, 1049)
        warp.addPoint(236, 667)
        print(warp.pointList)
        print(warp.points)
        assert warp.pointList == [[679, 25], [1408, 270], [1136, 1049], [236, 667]]

    def test_Persistence(self):
        if debug:
            YamlAbleMixin.debug = True
        temp = tempfile.gettempdir()
        warp = self.getTestWarp()
        warp.writeYaml(temp + "/warp")
        ywarp = Warp.readYaml(temp + "/warp")
        assert ywarp.pointList == warp.pointList
        if debug:
            JsonAbleMixin.debug = True
        warp.writeJson(temp + "/warp")
        jwarp = Warp.readJson(temp + "/warp")
        assert jwarp.pointList == warp.pointList
