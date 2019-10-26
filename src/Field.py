#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import colorsys
from RunningStats import ColorStats
from Video import Video

class Field:
    """ a single Field of a chessboard as observed from a WebCam"""
    rows=8
    cols=8

    @staticmethod
    def hsv_to_rgb(h,s,v):
        return colorsys.hsv_to_rgb(h,s,v)

    @staticmethod
    def hsv255_to_rgb255(h, s, v):
        r,g,b=Field.hsv_to_rgb(h/255,s/255,v/255)
        return (int(r*255),int(g*255),int(b*255))

    # construct me
    def __init__(self,row,col):
        # row and column indices from 0-7
        self.row=row
        self.col=col
        # algrebraic notation of field
        # A1 to H8
        self.an=chr(ord('a')+col)+chr(ord('1')+row)
        # center pixel position of field
        self.pcx=None
        self.pcx=None

    # analyze the color arround my center pixel to the given
    # distance
    def analyzeColor(self,hsv,distance=1):
        hsvStats=ColorStats()
        for dx in range(-distance,distance+1):
          for dy in range(-distance,distance+1):
            ph,ps,pv = hsv[self.pcy+dy, self.pcx+dx]
            #print ("(%3d,%3d)=(%3d,%3d,%3d)" % (self.pcx+dx,self.pcy+dy,ph,ps,pv))
            hsvStats.push(ph,ps,pv)
        h,s,v=hsvStats.mean()
        r,g,b=Field.hsv255_to_rgb255(h,s,v)
        bgr=(b,g,r)
        #print("(%3d,%3d)=(%3d,%3d,%3d) (%3d,%3d,%3d)" % (self.pcx,self.pcy,h,s,v,r,g,b))
        return bgr

    # analyze the color arround my center pixel to the given
    # distance
    def analyzeColor1(self,hsv,distance=1):
        rect=Video.GetSubRect(hsv,self.px-distance,se)
