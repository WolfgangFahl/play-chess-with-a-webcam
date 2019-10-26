#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import math

# see https://stackoverflow.com/a/17637351/1497139
class RunningStats:
    """ calculate mean, variance and standard deviation in one pass using Welfford's algorithm """
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
        x=float(xvalue)

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

class ColorStats:
    """ calculate the RunningStats for 3 color channels like RGB or HSV simultaneously"""

    def __init__(self):
        self.c1Stats=RunningStats()
        self.c2Stats=RunningStats()
        self.c3Stats=RunningStats()

    def push(self,c1,c2,c3):
        self.c1Stats.push(c1)
        self.c2Stats.push(c2)
        self.c3Stats.push(c3)

    def mean(self):
        return (self.c1Stats.mean(),self.c2Stats.mean(),self.c3Stats.mean())

    def variance(self):
        return (self.c1Stats.variance(),self.c2Stats.variance(),self.c3Stats.variance())

    def standard_deviation(self):
        return (self.c1Stats.standard_deviation(),self.c2Stats.standard_deviation(),self.c3Stats.standard_deviation())
