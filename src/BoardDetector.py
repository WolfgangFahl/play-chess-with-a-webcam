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

  def analyzeColors(self,image,distance=3,step=1):
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
           field.analyzeColor(self.hsv,distance,step)

  # analyze the given image
  def analyze(self,image,frameIndex,distance=3,step=1):
      self.analyzeColors(image,distance,step)
      sortedFields=sorted(self.board.fieldsByAn.values(),key=lambda field:field.hsvStats.colorKey())
      if BoardDetector.debug:
          overlay = image.copy()
          for index,field in enumerate(sortedFields):
              print ("frame %5d %2d: %s %.0f" % (frameIndex,index,field.an,field.hsvStats.colorKey()))
              color=field.getColor()
              if index<16:
                  color=Field.darkGrey
              elif index<32:
                  color=Field.black
              elif index<48:
                  color=Field.white
              else:
                  color=Field.lightGrey
              field.drawDebug(self.video,overlay,color)
          alpha = 0.6  # Transparency factor.
          # Following line overlays transparent rectangle over the image
          image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
          image=image_new
      return image
