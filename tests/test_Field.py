#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

from pcwawc.board import Board
from pcwawc.field import Field


class FieldTest(TestCase):

    def test_FieldAlgebraicNotation(self):
        board = Board()
        anstr = ""
        for row in range(0, 8):
            for col in range(0, 8):
                field = Field(board, row, col)
                anstr = anstr + field.an
        # print (anstr)
        assert (
            anstr
            == "a8b8c8d8e8f8g8h8a7b7c7d7e7f7g7h7a6b6c6d6e6f6g6h6a5b5c5d5e5f5g5h5a4b4c4d4e4f4g4h4a3b3c3d3e3f3g3h3a2b2c2d2e2f2g2h2a1b1c1d1e1f1g1h1"
        )

    def test_hsv2rgb(self):
        hsvs = [(128, 128, 128)]
        rgbs = [(63, 127, 128)]

        for i, hsv in enumerate(hsvs):
            h, s, v = hsv
            rgb = Field.hsv255_to_rgb255(h, s, v)
            assert rgbs[i] == rgb
