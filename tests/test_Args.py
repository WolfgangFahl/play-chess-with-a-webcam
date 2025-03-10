#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

from pcwawc.webchesscam import WebChessCamArgs


class ArgsTest(TestCase):

    def test_WebChessCamArgs(self):
        argv = [
            "--port=5004",
            "--rotation=90",
            "--debug",
            "--warp",
            "[[1408, 270], [1136, 1049], [236, 667]]",
        ]
        args = WebChessCamArgs(argv).args
        assert args.rotation == 90
        assert args.port == 5004
        assert args.debug
        expected = [[1408, 270], [1136, 1049], [236, 667]]
        assert args.warpPointList == expected

    # https://stackoverflow.com/questions/1894269/convert-string-representation-of-list-to-list
    def test_StringRepresentationOfList(self):
        import ast

        warpPointList = ast.literal_eval("[[1408, 270], [1136, 1049], [236, 667]]")
        expected = [[1408, 270], [1136, 1049], [236, 667]]
        assert warpPointList == expected
