#!/usr/bin/python3
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import colorsys
#from colormath.color_objects import sRGBColor, LabColor
#from colormath.color_conversions import convert_color
#from colormath.color_diff import delta_e_cie2000
from RunningStats import ColorStats
from Video import Video

class Field:
    """ a single Field of a chessboard as observed from a WebCam"""
    rows=8
    cols=8
    white=(255,255,255)
    lightGrey=(64,64,64)
    darkGrey=(192,192,192)
    black=(0,0,0)

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
        self.distance=None
        self.step=None
        self.hsvStats=None

    # analyze the color arround my center pixel to the given
    # distance
    def analyzeColor(self,hsv,distance=1,step=1):
        self.distance=distance
        self.step=step
        self.hsvStats=ColorStats()
        for dx in range(-distance*step,distance*step+1,step):
          for dy in range(-distance*step,distance*step+1,step):
            ph,ps,pv = hsv[self.pcy+dy, self.pcx+dx]
            #print ("(%3d,%3d)=(%3d,%3d,%3d)" % (self.pcx+dx,self.pcy+dy,ph,ps,pv))
            self.hsvStats.push(ph,ps,pv)

    def getColor(self):
        h,s,v=self.hsvStats.mean()
        r,g,b=Field.hsv255_to_rgb255(h,s,v)
        bgr=(b,g,r)
        #print("(%3d,%3d)=(%3d,%3d,%3d) (%3d,%3d,%3d)" % (self.pcx,self.pcy,h,s,v,r,g,b))
        return bgr

    def drawDebug(self,video,image,color):
        pcx=self.pcx
        pcy=self.pcy
        distance=self.distance
        step=self.step
        x1,y1,x2,y2=pcx-distance*step,pcy-distance*step,pcx+distance*step,pcy+distance*step
        video.drawRectangle(image,(x1-1,y1-1),(x2+1,y2+1),thickness=1,color=(0,0,0))
        video.drawRectangle(image,(x1  ,y1  ),(x2  ,y2  ),thickness=-1,color=color)
