#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
#
# Color Distribution detector
from pcwawc.PlotLib import PlotLib
from pcwawc.Video import Video
from pcwawc.Environment import Environment
from pcwawc.Board import Board
from pcwawc.Field import Field, Grid
from pcwawc.BoardDetector import BoardDetector
from timeit import default_timer as timer
import argparse
import cv2 as cv
 
class CDDA:
    """ Color Distribution Analysis """
    windowName='Color Distribution'
    
    def __init__(self,video,roiLambda,xsteps=3, ysteps=10,rois=7,safetyX=12,safetyY=5):
        self.video=video
        self.image=None    
        self.board=Board()
        self.roiLambda=roiLambda
        self.xsteps=xsteps
        self.ysteps=ysteps
        self.safetyX=safetyX
        self.safetyY=safetyY
        self.rois=rois
        self.boardDetector=BoardDetector(self.board,video)
        
    def newImage(self,image):   
        self.image=image
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
        self.video.drawRectangle(image, (x1 - ot, y1 - ot), (x2 + ot, y2 + ot), thickness=ot, color=Field.green)
        
            
    def showROI(self,roi,image):         
        for pixel in roi.pixelList():
            x,y=pixel
            h, w = image.shape[:2]
            if (x>=0 and x<w) and (y>=0 and y<h):
                image[y,x]=Field.green
                
    def showField(self,field,image):
        for roi in field.rois:
            self.showROI(roi,image)
        title=field.an
        piece = field.getPiece()
        if piece is not None:
            symbol=piece.symbol()#piece.unicode_symbol()
            title=title+":"+symbol
        self.video.drawCenteredText(image,title,field.pcx,field.pcy,fontBGRColor=Field.white)    
    
    def showFields(self,image):
        for field in self.boardDetector.genFields():
            self.showField(field,image)            
          
    def show(self):    
        cdImage=self.image.copy()
        start=timer()
        grid=Grid(self.rois,self.xsteps,self.ysteps,safetyX=self.safetyX,safetyY=self.safetyY)
        self.boardDetector.analyzeFields(self.image,grid,self.roiLambda)
        end=timer()    
        print ("analysis took %.3fs" % (end-start))
        self.showFields(cdImage)
        self.showColorStats()
        self.preView(cdImage,CDDA.windowName)
        
    def preView(self,image,title,height=640):
        h, w = image.shape[:2]
        preview=cv.resize(image,(int(w*height/h),height))
        self.video.showImage(preview,title)
        
    def onClick(self,event, x, y, flags, param):
        print ("mouseevent %s at %d,%d" %(event,x,y)) 
        
    def showColorStats(self):
        sortedFields= cdda.boardDetector.sortByFieldState()
        for fieldState,fields in sortedFields.items():
            for field in fields:
                for roi in field.rois:
                    mean=roi.colorStats.mean()
                    r,g,b=mean
                    print ("%s-%d (%15s): %3.0f %3.0f %3.0f" % (field.an,roi.roiIndex,fieldState.title(),r,g,b))    
            
lambdas=[
    lambda grid,roiIndex,xstep,ystep:(grid.dofs(roiIndex)+grid.d()*grid.xstep(xstep),grid.ystep(ystep)),
    lambda grid,roiIndex,xstep,ystep:(grid.xstep(xstep),grid.dofs(roiIndex)+grid.d()*grid.ystep(ystep)),
    lambda grid,roiIndex,xstep,ystep:(grid.xstep(xstep),grid.ystep(ystep))
]        

env=Environment()
parser = argparse.ArgumentParser(description='Color Distribution Detection')
parser.add_argument('--input', help='Path to input image.', default=env.testMedia+'chessBoard012.jpg')
args = parser.parse_args()
video=Video()
    
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
              
cdda=CDDA(video,lambdas[0])    
source_window=args.input
# Showing the result
cv.namedWindow(CDDA.windowName)
cv.namedWindow(source_window)
lambdaIndex=0

def histogram():
    start=timer()
    histogram=PlotLib("Chessboard Colors",PlotLib.A4(turned=True))
    rgb=cv.cvtColor(cdda.image,cv.COLOR_BGR2RGB)
    histogram.addPlot(rgb,'chessboard012')
    video=cdda.video
    sortedFields= cdda.boardDetector.sortByFieldState()
    for fieldState,fields in sortedFields.items():
        for field in fields:
            fieldImg=video.getSubRect(rgb, field.getRect())
            title="%s %s" % (field.an,fieldState.title())
            print (title)
            histogram.addPlot(fieldImg,title)
    histogram.save('/tmp/chessboard012',{'Title': 'Chessboard Histogram for Chessboard 012'})
    end=timer()
    print('histogram created in %.3fs' % (end-start))

def onChange(): 
    cdda.xsteps =Tracker.trackers['xsteps'].value
    cdda.ysteps =Tracker.trackers['ysteps'].value
    cdda.rois   =Tracker.trackers['rois'].value
    cdda.safetyX=Tracker.trackers['safetyX %'].value
    cdda.safetyY=Tracker.trackers['safetyY %'].value
    cdda.roiLambda=lambdas[Tracker.trackers['mode'].value]
    doHistogram=Tracker.trackers['histogram'].value
    if doHistogram==1:
        histogram()
    cdda.show()
    
xsteps=Tracker('xsteps'    ,source_window, cdda.xsteps ,20, onChange)
ysteps=Tracker('ysteps'    ,source_window, cdda.ysteps ,20, onChange)
rois  =Tracker('rois'      ,source_window, cdda.rois   ,20, onChange)
sx    =Tracker('safetyX %' ,source_window, cdda.safetyX,20, onChange)
sy    =Tracker('safetyY %' ,source_window, cdda.safetyY,20, onChange)
mode  =Tracker('mode'      ,source_window, lambdaIndex, len(lambdas)-1, onChange)
hist  =Tracker('histogram' ,source_window, 0,1,onChange)

frames=0
video.capture(args.input)


while True:
    ret, image, quitWanted = video.readFrame(show=False)
    if not ret:
        break;
    if quitWanted:
            break
    cdda.newImage(image)  
    cdda.preView(image,source_window)  
    if frames==0:
        cdda.show()
        cv.setMouseCallback(CDDA.windowName, cdda.onClick)
    onChange()
    frames+=1    