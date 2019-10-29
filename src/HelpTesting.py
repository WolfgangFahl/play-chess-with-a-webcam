#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
# get image with the given number


def getImage(num):
    video=Video()
    filename="testMedia/chessBoard%03d.jpg" % (num)
    image=video.readImage(filename)
    height, width = image.shape[:2]
    print ("read image %s: %dx%d" % (filename,width,height))
    return image
