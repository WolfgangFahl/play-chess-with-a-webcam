#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import cv2

def test_Version():
    version=cv2.__version__
    print (version)
    assert version=="4.1.1"

test_Version()
