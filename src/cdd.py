#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Color Distribution detector
from Video import Video
from Environment import Environment
from Board import Board
from Field import Field, FieldROI, Grid
from BoardDetector import BoardDetector
import argparse
import cv2 as cv
 
class CDDA:
    """ Color Distribution Analysis """
    windowName='Color Distribution'
    
    def __init__(self,video,image, roiLambda,xsteps=3, ysteps=10,rois=7):
        self.video=video
        self.image=image       
        self.board=Board()
        self.roiLambda=roiLambda
        self.xsteps=xsteps
        self.ysteps=ysteps
        self.rois=rois
        self.boardDetector=BoardDetector(self.board,video)
        self.boardDetector.divideInFields(image)
        
    def showFields(self,image):
        for row in range(Field.rows):
            for col in range (Field.cols):
                field = self.board.fieldAt(row, col)
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
        for roiIndex in range(self.rois):
            grid=Grid(roiIndex,self.rois,self.xsteps,self.ysteps)
            hroi=FieldROI(field,grid,self.roiLambda)
            self.showROI(hroi,image)
            
    def showROI(self,roi,image):         
        for pixel in roi.pixelList():
            x,y=pixel
            h, w = image.shape[:2]
            if (x>=0 and x<w) and (y>=0 and y<h):
                image[y,x]=Field.green
          
    def show(self):    
        cdImage=self.image.copy()
        self.showFields(cdImage)
        cv.imshow(CDDA.windowName, cdImage)
        
lambdas=[
    lambda grid,xstep,ystep:(grid.dofs()+grid.d()*grid.xstep(xstep),grid.ystep(ystep)),
    lambda grid,xstep,ystep:(grid.xstep(xstep),grid.dofs()+grid.d()*grid.ystep(ystep))
]        

env=Environment()
parser = argparse.ArgumentParser(description='Code for Harris corner detector tutorial.')
parser.add_argument('--input', help='Path to input image.', default=env.testMedia+'chessboard012.jpg')
args = parser.parse_args()
video=Video()
src=video.readImage(args.input)
if src is None:
    print('Could not open or find the image:', args.input)
    exit(0)

def showXSteps(xsteps):
    cdda.xsteps=xsteps
    cdda.show() 
    
def showYSteps(ysteps):
    cdda.ysteps=ysteps
    cdda.show()      
  
def showROIs(rois):
    cdda.rois=rois
    cdda.show()      
  
def showLambda(roiLambdaIndex):
    cdda.roiLambda=lambdas[roiLambdaIndex]
    cdda.show()    
    
 
source_window=args.input
# Showing the result
cv.namedWindow(CDDA.windowName)
cv.namedWindow(source_window)
xSteps=3
maxXSteps=20
ySteps=10
maxYSteps=20
rois=7
maxRois=20
lambdaIndex=0


cdda=CDDA(video,src,lambdas[0])
cv.createTrackbar('xsteps: ', source_window, xSteps, maxXSteps, showXSteps)
cv.createTrackbar('ysteps: ', source_window, ySteps, maxYSteps, showYSteps)
cv.createTrackbar('rois: '  , source_window, rois,   maxRois, showROIs)
cv.createTrackbar('lambda'  , source_window, lambdaIndex, len(lambdas)-1,showLambda)
cv.imshow(source_window, src)
showROIs(rois)
cv.waitKey()    
    
    
