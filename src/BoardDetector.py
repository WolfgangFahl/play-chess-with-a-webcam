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
  def analyze(self,image,distance=3):
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
           color=field.analyzeColor(self.hsv,distance)
           if BoardDetector.debug:
               self.video.drawRectangle(image,(field.pcx-distance-1,field.pcy-distance-1),(field.pcx+distance+1,field.pcy+distance+1),thickness=1,color=(0,0,0))
               self.video.drawRectangle(image,(field.pcx-distance,field.pcy-distance),(field.pcx+distance,field.pcy+distance),thickness=-1,color=color)
