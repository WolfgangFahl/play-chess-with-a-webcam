#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import math
import sys
from collections import deque

import numpy as np
from zope.interface import Interface, implementer


class IStats(Interface):
    """statistics interface"""

    def push(self, value):
        """push a value to the statistics"""
        pass

    def mean(self):
        """get the mean value"""
        pass


@implementer(IStats)
class MovingAverage:
    """calculate a moving average"""

    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.d = deque(maxlen=maxlen)
        self.sum = 0
        self.n = 0
        self.value = None

    def push(self, value):
        """recalculate the Moving Average based on a new value"""
        self.value = value
        self.sum += value
        if self.n < self.maxlen:
            self.n += 1
        else:
            self.sum -= self.d.popleft()
        self.d.append(value)

    def gradient(self):
        if self.n >= 2:
            g = (self.d[self.n - 1] - self.d[0]) / (self.n - 1)
            return g
        else:
            return 0

    def mean(self):
        if self.n == 0:
            return None
        return self.sum / self.n

    def __str__(self):
        return self.format()

    def format(self, formatM="%.1f"):
        text = formatM % self.mean()
        return text


class MinMaxMixin(object):
    def initMinMax(self):
        self.min = sys.maxsize
        self.max = -sys.maxsize

    def pushMinMax(self, value):
        if value > self.max:
            self.max = value
        if value < self.min:
            self.min = value

    def __str__(self):
        return self.formatMinMax()

    def formatMinMax(self, formatM=" %.1f - %.1f"):
        text = formatM % (self.min, self.max)
        return text


# see https://stackoverflow.com/a/17637351/1497139
# see also https://gist.github.com/alexalemi/2151722
# see also https://www.johndcook.com/blog/standard_deviation/
@implementer(IStats)
class RunningStats:
    """calculate mean, variance and standard deviation in one pass using Welford's algorithm"""

    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, xvalue):
        self.n += 1
        x = float(xvalue)

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return math.sqrt(self.variance())

    def __str__(self):
        return self.format()

    def format(self, formatS="%d: %.1f ± %.1f"):
        m = self.mean()
        s = self.standard_deviation()
        text = formatS % (self.n, m, s)
        return text


class MinMaxStats(RunningStats, MinMaxMixin):
    """running statistics with minimum and maximum"""

    def __init__(self):
        super(MinMaxStats, self).__init__()
        super().initMinMax()

    def push(self, value):
        super().push(value)
        super().pushMinMax(value)

    def clear(self):
        super().clear()
        super().initMinMax()

    def formatMinMax(self, formatR="%d: %.1f ± %.1f", formatM=" %.1f - %.1f"):
        text = super().format(formatR)
        if self.n > 0:
            text += super().formatMinMax(formatM)
        return text


@implementer(IStats)
class ColorStats:
    """calculate the RunningStats for 3 color channels like RGB or HSV simultaneously"""

    def __init__(self):
        self.c1Stats = RunningStats()
        self.c2Stats = RunningStats()
        self.c3Stats = RunningStats()

    def clear(self):
        self.c1Stats.clear()
        self.c2Stats.clear()
        self.c3Stats.clear()

    def push(self, c1, c2, c3):
        self.c1Stats.push(c1)
        self.c2Stats.push(c2)
        self.c3Stats.push(c3)

    def mean(self):
        return (self.c1Stats.mean(), self.c2Stats.mean(), self.c3Stats.mean())

    def variance(self):
        return (
            self.c1Stats.variance(),
            self.c2Stats.variance(),
            self.c3Stats.variance(),
        )

    def standard_deviation(self):
        return (
            self.c1Stats.standard_deviation(),
            self.c2Stats.standard_deviation(),
            self.c3Stats.standard_deviation(),
        )

    @staticmethod
    def square(value):
        return value * value

    def colorKey(self):
        other = ColorStats()
        other.push(0, 0, 0)
        return ColorStats.distance(self, other)

    def rgbColorKey(self):
        from pcwawc import ciede2000

        value = ciede2000.ciede2000FromRGB(self.mean(), (0, 0, 0))
        return value

    @staticmethod
    def distance(this, other):
        """simple eucledian color distance see e.g. https://en.wikipedia.org/wiki/Color_difference"""
        c1s = ColorStats.square(this.c1Stats.mean() - other.c1Stats.mean())
        c2s = ColorStats.square(this.c2Stats.mean() - other.c2Stats.mean())
        c3s = ColorStats.square(this.c3Stats.mean() - other.c3Stats.mean())
        dist = c1s + c2s + c3s
        return dist
