#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

from pcwawc.board import Board
from pcwawc.field import Field, FieldROI, Grid


class FieldROITest(TestCase):

    def test_PixelListGenerators(self):
        board = Board()
        field = Field(board, 0, 0)
        field.width = 100
        field.height = 100
        field.pcx = 50
        field.pcy = 50
        field.step = 7
        field.distance = 3
        fieldGrid = Grid(1, field.step, field.step)
        roi = FieldROI(
            field,
            fieldGrid,
            0,
            lambda grid, roiIndex, xstep, ystep: (grid.xstep(xstep), grid.ystep(ystep)),
        )
        # print (list(roi.pixelList()))
        assert list(roi.pixelList()) == [
            (13, 13),
            (13, 25),
            (13, 38),
            (13, 50),
            (13, 63),
            (13, 75),
            (13, 88),
            (25, 13),
            (25, 25),
            (25, 38),
            (25, 50),
            (25, 63),
            (25, 75),
            (25, 88),
            (38, 13),
            (38, 25),
            (38, 38),
            (38, 50),
            (38, 63),
            (38, 75),
            (38, 88),
            (50, 13),
            (50, 25),
            (50, 38),
            (50, 50),
            (50, 63),
            (50, 75),
            (50, 88),
            (63, 13),
            (63, 25),
            (63, 38),
            (63, 50),
            (63, 63),
            (63, 75),
            (63, 88),
            (75, 13),
            (75, 25),
            (75, 38),
            (75, 50),
            (75, 63),
            (75, 75),
            (75, 88),
            (88, 13),
            (88, 25),
            (88, 38),
            (88, 50),
            (88, 63),
            (88, 75),
            (88, 88),
        ]
        grid = Grid(1, 2, 2, 10, 10)
        assert grid.shiftSafety(1, 1) == (0.9, 0.9)
        assert grid.shiftSafety(0, 0) == (0.1, 0.1)
        assert grid.shiftSafety(0.5, 0.5) == (0.5, 0.5)
