#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

from Video import Video
from Board import Board
from Field import Field, FieldState
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
           field=self.board.fieldAt(row,col)
           field.pcx=pcx
           field.pcy=pcy
           field.analyzeColor(image,self.hsv,distance,step)

  # analyze the given image
  def analyze(self,image,frameIndex,distance=3,step=1):
      self.analyzeColors(image,distance,step)
      # sort by color colorKey,luminance or rgbColorKey
      sortedFields=sorted(self.board.fieldsByAn.values(),key=lambda field:field.rgbColorKey)

      if BoardDetector.debug:
          overlay = image.copy()
          counts=self.board.fieldStateCounts()

          for index,field in enumerate(sortedFields):
              lmean,lstdv=field.luminance
              #print ("frame %5d %2d: %s luminance: %3.0f ± %3.0f rgbColorKey: %3.0f colorKey: %.0f" % (frameIndex,index,field.an,lmean,lstdv,field.rgbColorKey,field.colorKey))
              color=field.getColor()
              darkGreyLimit=counts[FieldState.BLACK_BLACK]
              blackLimit=darkGreyLimit+counts[FieldState.BLACK_EMPTY]
              #lightGreyLimit=darkGreyLimit+counts[FieldState.WHITE_BLACK]
              if index<darkGreyLimit:
                  color=Field.darkGrey
              elif index<blackLimit:
                  color=Field.black
              elif index>=64-counts[FieldState.WHITE_EMPTY]:
                  color=Field.white
              #else:
              #  color=Field.lightGrey
              field.drawDebug(self.video,overlay,color)
          alpha = 0.6  # Transparency factor.
          # Following line overlays transparent rectangle over the image
          image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
          image=image_new
      return image
