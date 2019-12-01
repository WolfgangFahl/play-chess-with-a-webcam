#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import cv2
from timeit import default_timer as timer
from pcwawc.Environment import Environment
from pcwawc.histogram import Histogram
from pcwawc.Video import Video
import numpy as np
import math
import chess

class Corners(object):
    """ Chess board corners """
    
    debug=False
    """ pixel margin for masked polygons"""
    safetyMargin=5
    
    def __init__(self,pattern):
        """ initialize me with the given rows and columns"""
        self.pattern=pattern
        self.rows,self.cols=pattern
        # prepare the dict for my polygons
        self.polygons={}
        
    @staticmethod
    def genChessPatterns():
        for rows in range(7,2,-2):
            for cols in range(7,rows-1,-2):  
                yield (rows,cols) 
    
    def findPattern(self,image):
        """ try finding the chess board corners in the given image with the given pattern """
        self.h,self.w = image.shape[:2]
    
        start=timer()
        ret, self.corners = cv2.findChessboardCorners(image, self.pattern, None)
        end=timer()
        if Corners.debug:
            print ("%dx%d in %dx%d after %.3f s: %s" % (self.rows,self.cols,self.w,self.h,(end-start),"✔" if ret else "❌"))
        return ret
    
    def safeXY(self,x,y,dx,dy):
        x=x+dx;
        y=y+dy
        if y>=self.h: y=self.h-1
        if y<0: y=0
        if x>=self.w: x=self.w-1
        if x<0: x=0
        return (x,y)
    
    def asPolygons(self,safetyMargin):   
        """ get the polygons for my corner points"""  
        # reshape the array 
        cps=np.reshape(self.corners,(self.cols,self.rows,2))
        polygons={}
        m=safetyMargin
        for col in range(self.cols-1):
                for row in range (self.rows-1):
                    x1,y1=cps[col,row]      # top left
                    x2,y2=cps[col+1,row]    # left bottom
                    x3,y3=cps[col+1,row+1]  # right bottom
                    x4,y4=cps[col,row+1]    # top right
                    clockwise=BoardFinder.sortPoints([(x1,y1),(x2,y2),(x3,y3),(x4,y4)])
                    (x1,y1),(x2,y2),(x3,y3),(x4,y4)=clockwise
                    # https://stackoverflow.com/questions/19190484/what-is-the-opencv-findchessboardcorners-convention
                    polygon=np.array([
                        self.safeXY(x1,y1,+m,+m),
                        self.safeXY(x2,y2,-m,+m),
                        self.safeXY(x3,y3,-m,-m),
                        self.safeXY(x4,y4,+m,-m)],dtype=np.int32)
                    polygons[(row,col)]=polygon
        return polygons 
    
    def calcPolygons(self,*safetyMargins):
        """ calculate polygons for the given safety margins """
        for safetyMargin in safetyMargins:
            self.polygons[safetyMargin]=self.asPolygons(safetyMargin)
            
    def showDebug(self,image,title):
        """ 'show' the debug picture of the chessboard corners by drawing the corners and writing the result to the given testImagePath"""
        imageCopy=image.copy()
        cv2.drawChessboardCorners(imageCopy, self.pattern, self.corners, patternWasFound=True)
        #cv2.imshow('corners', self.image)
        #cv2.waitKey(50)
        self.writeDebug(imageCopy,title,"corners")
        
    def writeDebug(self,image,title,prefix):        
        Environment.checkDir(BoardFinder.debugImagePath)    
        cv2.imwrite(BoardFinder.debugImagePath+'%s-%s-%dx%d.jpg' % (title,prefix,self.rows,self.cols),image)        
   
# Board Finder
class BoardFinder(object):
    """ find a chess board in the given image """
    debug=False
    black=(0,0,0)
    white=(255,255,255)
    darkGrey=(256//3,256//3,256/3)
    lightGrey=(256*2//3,256*2//3,256*2//3)
    debugImagePath="/tmp/pcwawc/"
   
    def __init__(self, image, video=None):
        """ construct me from the given input image"""
        if video is None:
            video=Video()
        self.video=video    
        self.image=image
        # guess the topleft color
        self.topleft=chess.WHITE
        self.height, self.width = self.image.shape[:2]
        
    @staticmethod    
    def centerXY(xylist):
        x, y = zip(*xylist)
        l = len(x)
        return sum(x) / l, sum(y) / l  
    
    @staticmethod    
    def sortPoints(xylist):  
        """ sort points clockwise see https://stackoverflow.com/a/59115565/1497139"""
        cx, cy = BoardFinder.centerXY(xylist)
        xy_sorted = sorted(xylist, key = lambda x: math.atan2((x[1]-cy),(x[0]-cx)))
        return xy_sorted
    
    def findOuterCorners(self,searchWidth=640):
        """ find my outer corners as limited by the OpenCV findChessBoard algorithm - to be later expanded"""
        found=self.findCorners(limit=1,searchWidth=searchWidth)
        # we expected to find a board
        if len(found)!=1:
            raise Exception("no corners found")
        chesspattern=next(iter(found))
        corners=found[chesspattern]
        corners.calcPolygons(0,Corners.safetyMargin)
        return corners
       
    def findCorners(self,limit=1,searchWidth=640):
        """ start finding the chessboard with the given limit and the given maximum width of the search image """
        startt=timer()
        sw=self.width
        sh=self.height
        if sw>searchWidth:
            sw=searchWidth
            sh=self.height*sw//self.width
        self.searchimage=cv2.resize(self.image,(sw,sh))
        if BoardFinder.debug:
            print("BoardFinder for %dx%d image resized to %dx%d" % (self.width, self.height,sw,sh))

        gray = cv2.cvtColor(self.searchimage, cv2.COLOR_BGR2GRAY)
        fullSizeGray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.found={}
        for chesspattern in Corners.genChessPatterns():
            corners=Corners(chesspattern)
            if corners.findPattern(gray) and corners.findPattern(fullSizeGray):
                self.found[chesspattern]=corners
            if len(self.found)>=limit:
                    break
        endt=timer()
        if BoardFinder.debug:
            print ("found %d patterns in %.1f s" % (len(self.found),(endt-startt)))
        return self.found
    
    def fieldColor(self,pos):
        row,col=pos
        oddeven=1 if self.topleft==chess.WHITE else 0
        color=chess.WHITE if (col+row) % 2 == oddeven else chess.BLACK
        return color
    
    def maskPolygon(self,image,corners,filterColor):
        mask=self.video.getEmptyImage(image)
        polygons=corners.polygons[Corners.safetyMargin]
        for pos,polygon in polygons.items():
            posColor=self.fieldColor(pos)
            if not posColor==filterColor:
                self.drawPolygon(mask, pos, polygon, BoardFinder.white, BoardFinder.white)
        #if BoardFinder.debug:
        #    cv2.imshow("mask",mask)
        #    cv2.waitKey(1000)       
        masked=self.video.maskImage(image,mask)
        return masked
    
    def getHistograms(self,image,title,corners):
        """ get the two histograms for the given corners we don't no what the color of the topleft corner is so we start with a guess"""
        histograms={}
        for filterColor in (True,False):
            imageCopy=image.copy()
            masked=self.maskPolygon(imageCopy, corners, filterColor)
            if BoardFinder.debug:
                prefix="masked-O-" if filterColor else "masked-X-"
                corners.writeDebug(masked,title, prefix)
            histograms[filterColor]=Histogram(masked,histRange=(1,256))
  
        # do we need to fix our guess?
        # is the mean color of black (being filtered) higher then when white is filtered?          
        if histograms[chess.BLACK].color>histograms[chess.WHITE].color:
            self.topleft=chess.BLACK
            # swap entries
            tmp=histograms[chess.BLACK]
            histograms[chess.BLACK]=histograms[chess.WHITE]
            histograms[chess.WHITE]=tmp
        return histograms    
    
    def getColorFiltered(self,image,histograms,title,corners):
        colorFiltered={}
        for filterColor in (chess.WHITE,chess.BLACK):
            histogram=histograms[filterColor]
            imageCopy=image.copy()
            colorMask=histogram.colorMask(imageCopy, 1.5)
            colorFiltered[filterColor]=self.video.maskImage(imageCopy,colorMask)
            if BoardFinder.debug:
                prefix="colorFiltered-white-" if filterColor==chess.WHITE else "colorFiltered-black-"
                corners.writeDebug(colorFiltered[filterColor], title, prefix)
        return colorFiltered        
           
    def expand(self,image,title,histograms,corners):
        self.colorFiltered=self.getColorFiltered(image,histograms,title,corners)                 
        
    def drawPolygon(self,image,pos,polygon,whiteColor,blackColor):    
        posColor=self.fieldColor(pos)
        color=blackColor if posColor else whiteColor
        cv2.fillConvexPoly(image,polygon,color)
        
    def showPolygonDebug(self,image,title,corners):
        imagecopy=image.copy()
        polygons=corners.polygons[0]
        for pos,polygon in polygons.items():
            self.drawPolygon(imagecopy, pos, polygon, BoardFinder.lightGrey,BoardFinder.darkGrey)
        corners.writeDebug(imagecopy,title, "polygons")          
        
    def showHistogramDebug(self,histograms,title,corners): 
        Environment.checkDir(self.debugImagePath)  
        fig,axes=histograms[True].preparePlot(2,2)
        histograms[True].plotRow(axes[0,0],axes[0,1])
        histograms[False].plotRow(axes[1,0],axes[1,1])
        prefix="histogram"
        filepath=self.debugImagePath+'%s-%s-%dx%d.jpg' % (title,prefix,corners.rows,corners.cols)
        histograms[False].savefig(fig,filepath)       
            
        