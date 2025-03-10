#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

import pytest

from pcwawc.runningstats import ColorStats, MovingAverage, RunningStats


class RunningStatsTest(TestCase):

    def test_RunningStats(self):
        rs = RunningStats()
        rs.push(17.0)
        rs.push(19.0)
        rs.push(24.0)

        mean = rs.mean()
        variance = rs.variance()
        stdev = rs.standard_deviation()
        print("mean=%f variance=%f stdev=%f" % (mean, variance, stdev))
        assert mean == 20.0
        assert variance == 13.0
        assert stdev == pytest.approx(3.605551, 0.00001)

    def test_ColorStats(self):
        colors = [(100, 100, 100), (90, 100, 90), (80, 90, 80), (110, 110, 120)]
        colorStats = ColorStats()
        for color in colors:
            r, g, b = color
            colorStats.push(r, g, b)
        cm = colorStats.mean()
        mR, mG, mB = cm
        vR, vG, vB = colorStats.variance()
        sR, sG, sB = colorStats.standard_deviation()
        print(
            "mean=%f,%f,%f variance=%f,%f,%f stdev=%f,%f,%f"
            % (mR, mG, mB, vR, vG, vB, sR, sG, sB)
        )
        assert cm == (95.0, 100.0, 97.5)
        prec = 0.000001
        assert vR == pytest.approx(166.666667, prec)
        assert vG == pytest.approx(66.666667, prec)
        assert vB == pytest.approx(291.666667, prec)
        assert sR == pytest.approx(12.909944, prec)
        assert sG == pytest.approx(8.164966, prec)
        assert sB == pytest.approx(17.078251, prec)

    def test_MovingAverage(self):
        values = [10, 12, 17, 19, 24, 17, 13, 12, 8]
        means = [10, 11, 13, 16, 20, 20, 18, 14, 11]
        gs = [0, 2, 3.5, 3.5, 3.5, -1, -5.5, -2.5, -2.5]
        ma = MovingAverage(3)
        index = 0
        for value in values:
            ma.push(value)
            print("%d: %f %f %f" % (index, value, ma.mean(), ma.gradient()))
            assert means[index] == ma.mean()
            assert gs[index] == ma.gradient()
            index += 1
