#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

from Field import Field, FieldState
import cv2

class BoardDetector:
    """ detect a chess board's state from the given image """
    debug=False
    frameDebug=False

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
                l=field.luminance
                if BoardDetector.frameDebug:
                    print ("frame %5d %2d: %s luminance: %3.0f ± %3.0f (%d) rgbColorKey: %3.0f colorKey: %.0f" % (frameIndex,index,field.an,l.mean(),l.standard_deviation(),l.n,field.rgbColorKey,field.colorKey))
                limit1=counts[FieldState.BLACK_BLACK]
                limit2=limit1+counts[FieldState.BLACK_WHITE]
                limit3=limit2+counts[FieldState.BLACK_EMPTY]
                limit4=limit3+counts[FieldState.WHITE_BLACK]
                limit5=limit4+counts[FieldState.WHITE_BLACK]
                fieldState=None
                if index<limit1:
                    fieldState=FieldState.BLACK_BLACK
                elif index<limit2:
                    fieldState=FieldState.BLACK_WHITE
                elif index<limit3:
                    fieldState=FieldState.BLACK_EMPTY
                elif index<limit4:
                    fieldState=FieldState.WHITE_BLACK
                elif index<limit5:
                    fieldState=FieldState.WHITE_WHITE
                else:
                    fieldState=FieldState.WHITE_EMPTY
                field.drawDebug(self.video,overlay,fieldState)
            alpha = 0.6  # Transparency factor.
            # Following line overlays transparent rectangle over the image
            image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
            image=image_new
        return image
