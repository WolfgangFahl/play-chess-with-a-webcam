#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

"""
Created on 2019-11-29

@author: wf
"""
from unittest import TestCase

import chess

from pcwawc.chesstrapezoid import ChessTrapezoid
from pcwawc.environment import Environment
from pcwawc.environment4test import Environment4Test
from pcwawc.histogram import Histogram, Stats

testEnv = Environment4Test()


class ColorDistributionTest(TestCase):
    def test_Stats(self):
        # https://math.stackexchange.com/questions/857566/how-to-get-the-standard-deviation-of-a-given-histogram-image
        values = [
            (23, 3),
            (24, 7),
            (25, 13),
            (26, 18),
            (27, 23),
            (28, 17),
            (29, 8),
            (30, 6),
            (31, 5),
        ]
        stats = Stats(values)
        # print (vars(stats))
        assert stats.n == 9
        assert stats.sum == 100
        assert stats.prod == 2694
        assert stats.mean == 26.94
        assert stats.variance == 3.6364
        assert stats.stdv == 1.9069347130932406
        assert stats.min == 23
        assert stats.max == 31
        assert stats.maxdelta == 4.059999999999999
        assert stats.factor == 2.129071316455438
        assert stats.range(1.5) == (20.85, 33.03)
        assert stats.range(1.5, 21, 33) == (21.0, 33.0)

    def test_Histogram(self):
        for imageInfo in testEnv.imageInfos:
            fen = imageInfo.fen
            if not fen == chess.STARTING_BOARD_FEN:
                continue
            image, video, warp = testEnv.prepareFromImageInfo(imageInfo)
            title = imageInfo.title
            # cbImage=ChessBoardImage(image,"chessboard")
            trapez = ChessTrapezoid(
                warp.pointList, rotation=warp.rotation, idealSize=800
            )
            cbWarped = trapez.warpedBoardImage(image)
            histogram = Histogram(cbWarped.image)
            histogram.showDebug()
            Environment.checkDir(Environment.debugImagePath)
            histogram.save(Environment.debugImagePath + title + "-histogram.jpg")
