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
    
    def __init__(self,video,image, roiLambda,xsteps=3, ysteps=10,rois=7,safetyX=5,safetyY=5):
        self.video=video
        self.image=image       
        self.board=Board()
        self.roiLambda=roiLambda
        self.xsteps=xsteps
        self.ysteps=ysteps
        self.safetyX=safetyX
        self.safetyY=safetyY
        self.rois=rois
        self.boardDetector=BoardDetector(self.board,video)
        self.boardDetector.divideInFields(image)
              
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
        
            
    def showROI(self,roi,image):         
        for pixel in roi.pixelList():
            x,y=pixel
            h, w = image.shape[:2]
            if (x>=0 and x<w) and (y>=0 and y<h):
                image[y,x]=Field.green
                
    def showField(self,field,image):
        for roi in field.rois:
            self.showROI(roi,image)            
    
    def analyzeFields(self,image):
        grid=Grid(self.rois,self.xsteps,self.ysteps,safetyX=self.safetyX,safetyY=self.safetyY)
        for field in self.genFields():
            field.divideInROIs(grid,self.roiLambda)
   
    def genFields(self):
        for row in range(Field.rows):
            for col in range (Field.cols):
                field = self.board.fieldAt(row, col)
                yield field
                        
    def showFields(self,image):
        for field in self.genFields():
            self.showField(field,image)            
          
    def show(self):    
        cdImage=self.image.copy()
        self.analyzeFields(self.image)
        self.showFields(cdImage)
        cv.imshow(CDDA.windowName, cdImage)
        
lambdas=[
    lambda grid,roiIndex,xstep,ystep:(grid.dofs(roiIndex)+grid.d()*grid.xstep(xstep),grid.ystep(ystep)),
    lambda grid,roiIndex,xstep,ystep:(grid.xstep(xstep),grid.dofs(roiIndex)+grid.d()*grid.ystep(ystep)),
    lambda grid,roiIndex,xstep,ystep:(grid.xstep(xstep),grid.ystep(ystep))
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
    
class Tracker:
    trackers={}
    
    def __init__(self,name,window,value,maxValue,onChange=None):
        self.name=name
        self.window=window
        self.value=value
        self.maxValue=maxValue
        self.onChange=onChange
        cv.createTrackbar(self.name, self.window, self.value, self.maxValue, Tracker.onChangeTrackbar)
        Tracker.trackers[name]=self
    
    @staticmethod
    def onChangeTrackbar(value):
        for name,tracker in Tracker.trackers.items():
            value=cv.getTrackbarPos(name,tracker.window)
            tracker.value=value
        if tracker.onChange is not None:
            tracker.onChange()
              
cdda=CDDA(video,src,lambdas[0])    
source_window=args.input
# Showing the result
cv.namedWindow(CDDA.windowName)
cv.namedWindow(source_window)
lambdaIndex=0

def onChange(): 
    cdda.xsteps =Tracker.trackers['xsteps'].value
    cdda.ysteps =Tracker.trackers['ysteps'].value
    cdda.rois   =Tracker.trackers['rois'].value
    cdda.safetyX=Tracker.trackers['safetyX %'].value
    cdda.safetyY=Tracker.trackers['safetyY %'].value
    cdda.roiLambda=lambdas[Tracker.trackers['mode'].value]
    cdda.show()
    
xsteps=Tracker('xsteps'    ,source_window, cdda.xsteps ,20, onChange)
ysteps=Tracker('ysteps'    ,source_window, cdda.ysteps ,20, onChange)
rois  =Tracker('rois'      ,source_window, cdda.rois   ,20, onChange)
sx    =Tracker('safetyX %' ,source_window, cdda.safetyX,20, onChange)
sy    =Tracker('safetyY %' ,source_window, cdda.safetyY,20, onChange)
mode  =Tracker('mode'      ,source_window, lambdaIndex, len(lambdas)-1, onChange)

cv.imshow(source_window, src)
cdda.show()
cv.waitKey()