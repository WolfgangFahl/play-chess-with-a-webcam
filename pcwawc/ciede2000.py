# https://raw.githubusercontent.com/sumtype/CIEDE2000/master/ciede2000.py
# Copyright (c) 2017, JAMES MASON
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL JAMES MASON BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np


# Converts RGB pixel array to XYZ format.
# Implementation derived from http://www.easyrgb.com/en/math.php
def rgb2xyz(rgb):

    def format(c):
        c = c / 255.0
        if c > 0.04045:
            c = ((c + 0.055) / 1.055) ** 2.4
        else:
            c = c / 12.92
        return c * 100

    rgb = list(map(format, rgb))
    xyz = [None, None, None]
    xyz[0] = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    xyz[1] = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    xyz[2] = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505
    return xyz


# Converts XYZ pixel array to LAB format.
# Implementation derived from http://www.easyrgb.com/en/math.php
def xyz2lab(xyz):

    def format(c):
        if c > 0.008856:
            c = c ** (1.0 / 3.0)
        else:
            c = (7.787 * c) + (16.0 / 116.0)
        return c

    xyz[0] = xyz[0] / 95.047
    xyz[1] = xyz[1] / 100.00
    xyz[2] = xyz[2] / 108.883
    xyz = list(map(format, xyz))
    lab = [None, None, None]
    lab[0] = (116.0 * xyz[1]) - 16.0
    lab[1] = 500.0 * (xyz[0] - xyz[1])
    lab[2] = 200.0 * (xyz[1] - xyz[2])
    return lab


# Converts RGB pixel array into LAB format.
def rgb2lab(rgb):
    return xyz2lab(rgb2xyz(rgb))


def ciede2000FromRGB(rgb1, rgb2):
    lab1 = rgb2lab(rgb1)
    lab2 = rgb2lab(rgb2)
    return ciede2000(lab1, lab2)


# Returns CIEDE2000 comparison results of two LAB formatted colors.
# Translated from CIEDE2000 implementation in https://github.com/markusn/color-diff
def ciede2000(lab1, lab2):

    def degrees(n):
        return n * (180.0 / np.pi)

    def radians(n):
        return n * (np.pi / 180.0)

    def hpf(x, y):
        if x == 0 and y == 0:
            return 0
        else:
            tmphp = degrees(np.arctan2(x, y))
            if tmphp >= 0:
                return tmphp
            else:
                return tmphp + 360.0
        return None

    def dhpf(c1, c2, h1p, h2p):
        if c1 * c2 == 0:
            return 0
        elif np.abs(h2p - h1p) <= 180:
            return h2p - h1p
        elif h2p - h1p > 180:
            return (h2p - h1p) - 360.0
        elif h2p - h1p < 180:
            return (h2p - h1p) + 360.0
        else:
            return None

    def ahpf(c1, c2, h1p, h2p):
        if c1 * c2 == 0:
            return h1p + h2p
        elif np.abs(h1p - h2p) <= 180:
            return (h1p + h2p) / 2.0
        elif np.abs(h1p - h2p) > 180 and h1p + h2p < 360:
            return (h1p + h2p + 360.0) / 2.0
        elif np.abs(h1p - h2p) > 180 and h1p + h2p >= 360:
            return (h1p + h2p - 360.0) / 2.0
        return None

    L1 = lab1[0]
    A1 = lab1[1]
    B1 = lab1[2]
    L2 = lab2[0]
    A2 = lab2[1]
    B2 = lab2[2]
    kL = 1
    kC = 1
    kH = 1
    C1 = np.sqrt((A1**2.0) + (B1**2.0))
    C2 = np.sqrt((A2**2.0) + (B2**2.0))
    aC1C2 = (C1 + C2) / 2.0
    G = 0.5 * (1.0 - np.sqrt((aC1C2**7.0) / ((aC1C2**7.0) + (25.0**7.0))))
    a1P = (1.0 + G) * A1
    a2P = (1.0 + G) * A2
    c1P = np.sqrt((a1P**2.0) + (B1**2.0))
    c2P = np.sqrt((a2P**2.0) + (B2**2.0))
    h1P = hpf(B1, a1P)
    h2P = hpf(B2, a2P)
    dLP = L2 - L1
    dCP = c2P - c1P
    dhP = dhpf(C1, C2, h1P, h2P)
    dHP = 2.0 * np.sqrt(c1P * c2P) * np.sin(radians(dhP) / 2.0)
    aL = (L1 + L2) / 2.0
    aCP = (c1P + c2P) / 2.0
    aHP = ahpf(C1, C2, h1P, h2P)
    T = (
        1.0
        - 0.17 * np.cos(radians(aHP - 39))
        + 0.24 * np.cos(radians(2.0 * aHP))
        + 0.32 * np.cos(radians(3.0 * aHP + 6.0))
        - 0.2 * np.cos(radians(4.0 * aHP - 63.0))
    )
    dRO = 30.0 * np.exp(-1.0 * (((aHP - 275.0) / 25.0) ** 2.0))
    rC = np.sqrt((aCP**7.0) / ((aCP**7.0) + (25.0**7.0)))
    sL = 1.0 + ((0.015 * ((aL - 50.0) ** 2.0)) / np.sqrt(20.0 + ((aL - 50.0) ** 2.0)))
    sC = 1.0 + 0.045 * aCP
    sH = 1.0 + 0.015 * aCP * T
    rT = -2.0 * rC * np.sin(radians(2.0 * dRO))
    return np.sqrt(
        ((dLP / (sL * kL)) ** 2.0)
        + ((dCP / (sC * kC)) ** 2.0)
        + ((dHP / (sH * kH)) ** 2.0)
        + rT * (dCP / (sC * kC)) * (dHP / (sH * kH))
    )
