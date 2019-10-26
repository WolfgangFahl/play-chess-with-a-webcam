#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

from Video import Video
from Board import Board
from Field import Field
import cv2

class BoardDetector:
  """ detect a chess board's state from the given image """
  debug=False

  # construct me from a board and video
  def __init__(self,board,video):
      self.board=board
      self.video=video
      self.hsv=None

  # analyze the given image
  def analyze(self,image,distance=3,step=1):
     # guess where the centers of the fields are
     # height
     height, width = image.shape[:2]
     fieldHeight=height/Field.rows
     fieldWidth=width/Field.cols
     self.hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
     for row in range(Field.rows):
        for col in range (Field.cols):
           pcx=int(fieldWidth*(2*col+1)//2)
           pcy=int(fieldHeight*(2*row+1)//2)
           field=self.board.fields[row][col]
           field.pcx=pcx
           field.pcy=pcy
           color=field.analyzeColor(self.hsv,distance,step)
           if BoardDetector.debug:
               x1,y1,x2,y2=field.pcx-distance*step,field.pcy-distance*step,field.pcx+distance*step,field.pcy+distance*step
               self.video.drawRectangle(image,(x1-1,y1-1),(x2+1,y2+1),thickness=1,color=(0,0,0))
               self.video.drawRectangle(image,(x1  ,y1  ),(x2  ,y2  ),thickness=-1,color=color)
