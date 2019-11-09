#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Color Distribution detector
from Video import Video
from Environment import Environment
from Board import Board
from Field import Field, FieldROI
from BoardDetector import BoardDetector
import argparse
import cv2 as cv
 
class CDDA:
    """ Color Distribution Analysis """
    windowName='Color Distribution'
    
    def __init__(self,video,image, distance=3, steps=3,roisPerField=7):
        self.video=video
        self.image=image       
        self.board=Board()
        self.distance=distance
        self.step=steps
        self.roisPerField=roisPerField
        self.boardDetector=BoardDetector(self.board,video)
        self.boardDetector.divideInFields(image)
        
    def showFields(self,image):
        for row in range(Field.rows):
            for col in range (Field.cols):
                field = self.board.fieldAt(row, col)
                field.distance=self.distance
                field.step=self.step
                self.showField(field,image)
              
    def showField1(self,field,image):
        pcx = field.pcx
        pcy = field.pcy       
        distance=self.distance
        step=self.step         
        x1, y1, x2, y2 = pcx - distance * step, pcy - distance * step, pcx + distance * step, pcy + distance * step
        # outer thickness for displaying detect state: green ok red - there is an issue
        ot = 1
        # inner thickness for displaying the field color
        video.drawRectangle(image, (x1 - ot, y1 - ot), (x2 + ot, y2 + ot), thickness=ot, color=Field.green)
        
    def showField(self,field,image):
        hsplit=FieldROI.split(self.roisPerField) 
        vsplit=FieldROI.split(self.roisPerField)
        roi=FieldROI(field,hsplit,vsplit)
        for pixel in roi.pixelList():
            x,y=pixel
            image[x,y]=Field.green
            
          
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
  
def showROIs(roisPerField):
    cdda.roisPerField=roisPerField
    cdda.show()      
    
def showSteps(steps):
    cdda.step=steps
    cdda.show()     

 
source_window=args.input
# Showing the result
cv.namedWindow(CDDA.windowName)
cv.namedWindow(source_window)
distance=3
maxDistance=50
steps=3
maxSteps=5
roisPerField=7
maxRoisPerField=28
cv.createTrackbar('distance: ', source_window, distance, maxDistance, showDistance)
cv.createTrackbar('steps: ', source_window, steps, maxSteps, showSteps)
cv.createTrackbar('roisPerField: ', source_window, roisPerField, maxRoisPerField, showROIs)
cv.imshow(source_window, src)
showDistance(distance)
cv.waitKey()    
    
    
