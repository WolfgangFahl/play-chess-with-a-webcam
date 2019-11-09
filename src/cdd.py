#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Color Distribution detector
from Video import Video
from Environment import Environment
from Board import Board
from Field import Field
from BoardDetector import BoardDetector
import argparse
import cv2 as cv
 
class CDDA:
    """ Color Distribution Analysis """
    windowName='Color Distribution'
    
    def __init__(self,video,image, distance=3, steps=3):
        self.video=video
        self.image=image       
        self.board=Board()
        self.distance=3
        self.step=3
        self.boardDetector=BoardDetector(self.board,video)
        self.boardDetector.divideInFields(image)
        
    def showFields(self,image):
        for row in range(Field.rows):
            for col in range (Field.cols):
                field = self.board.fieldAt(row, col)
                field.distance=self.distance
                field.step=self.step
                self.showField(field,image)
              
    def showField(self,field,image):
        pcx = field.pcx
        pcy = field.pcy       
        distance=self.distance
        step=self.step         
        x1, y1, x2, y2 = pcx - distance * step, pcy - distance * step, pcx + distance * step, pcy + distance * step
        # outer thickness for displaying detect state: green ok red - there is an issue
        ot = 2
        # inner thickness for displaying the field color
        video.drawRectangle(image, (x1 - ot, y1 - ot), (x2 + ot, y2 + ot), thickness=ot, color=Field.green)
      
    def show(self):    
        cdImage=self.image.copy()
        self.showFields(cdImage)
        cv.imshow(CDDA.windowName, cdImage)
        

env=Environment()
parser = argparse.ArgumentParser(description='Code for Harris corner detector tutorial.')
parser.add_argument('--input', help='Path to input image.', default=env.testMedia+'chessboard012.jpg')
args = parser.parse_args()
video=Video()
src=video.readImage(args.input)
if src is None:
    print('Could not open or find the image:', args.input)
    exit(0)
    
cdda=CDDA(video,src)       

def showDistance(distance):
    cdda.distance=distance
    cdda.show()  

 
source_window=args.input
# Showing the result
cv.namedWindow(CDDA.windowName)
cv.namedWindow(source_window)
distance=3
maxDistance=50
cv.createTrackbar('distance: ', source_window, distance, maxDistance, showDistance)
cv.imshow(source_window, src)
showDistance(distance)
cv.waitKey()    
    
    
