#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import cv2
from timeit import default_timer as timer
from pcwawc.Environment import Environment
from pcwawc.Video import Video
import numpy as np

# Board Finder
class BoardFinder(object):
    """ find a chess board in the given image """
    debug=False
    black=(0,0,0)
    white=(255,255,255)
    darkGrey=(256//3,256//3,256/3)
    lightGrey=(256*2//3,256*2//3,256*2//3)
   
    def __init__(self, image, video=None,debugImagePath="/tmp/pcwawc/"):
        """ construct me from the given input image"""
        if video is None:
            video=Video()
        self.video=video    
        self.image=image
        self.debugImagePath=debugImagePath
        self.height, self.width = self.image.shape[:2]
       
    def find(self,limit=1,searchWidth=640):
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
        for rows in range(7,2,-1):
            for cols in range(7,rows-1,-1):
                chesspattern=(rows,cols)       
                corners=self.findPattern(gray, chesspattern)
                if corners is not None:
                    fullSizeCorners=self.findPattern(fullSizeGray,chesspattern)
                    if fullSizeCorners is not None:
                        self.found[chesspattern]=fullSizeCorners
                if len(self.found)>=limit:
                    break
            if len(self.found)>=limit:
                    break                     
        endt=timer()
        if BoardFinder.debug:
            print ("found %d patterns in %.1f s" % (len(self.found),(endt-startt)))
        return self.found

    def findPattern(self,image,pattern):
        """ try finding the chess board corners in the given image with the given pattern """
        h,w = image.shape[:2]
        start=timer()
        ret, corners = cv2.findChessboardCorners(image, pattern, None)
        end=timer()
        if BoardFinder.debug:
            rows,cols=pattern
            print ("%dx%d in %dx%d after %.3f s: %s" % (rows,cols,w,h,(end-start),"✔" if ret else "❌"))
        if ret == True:
            return corners
        else:
            return None
        
    def toPolygons(self,safetyMargin=5):
        foundPolygons={}
        for chesspattern in self.found.keys():
            corners=self.found[chesspattern]
            foundPolygons[chesspattern]=self.asPolygons(chesspattern,corners,safetyMargin)
        return foundPolygons
    
    def safeXY(self,x,y,dx,dy):
        x=x+dx;
        y=y+dy
        if y>=self.height: y=self.height-1
        if y<0: y=0
        if x>=self.width: x=self.width-1
        if x<0: x=0
        return (x,y)
    
    def asPolygons(self,chesspattern,corners,safetyMargin=0):   
        """ get the polygons for the given list of corner points"""  
        rows,cols=chesspattern
        # reshape the array 
        cps=np.reshape(corners,(cols,rows,2))
        polygons={}
        m=safetyMargin
        for col in range(cols-1):
                for row in range (rows-1):
                    x1,y1=cps[col,row]      # top left
                    x4,y4=cps[col+1,row]    # left bottom
                    x3,y3=cps[col+1,row+1]  # right bottom
                    x2,y2=cps[col,row+1]    # top right
                    # https://stackoverflow.com/questions/19190484/what-is-the-opencv-findchessboardcorners-convention
                    polygon=np.array([
                        self.safeXY(x1,y1,+m,+m),
                        self.safeXY(x2,y2,-m,+m),
                        self.safeXY(x3,y3,-m,-m),
                        self.safeXY(x4,y4,+m,-m)],dtype=np.int32)
                    polygons[(row,col)]=polygon
        return polygons 
    
    def fieldColor(self,pos):
        row,col=pos
        color = (col + row) % 2 == 0
        return color
    
    def maskPolygon(self,image,polygons,filterColor):
        mask=self.video.getEmptyImage(image)
        for pos,polygon in polygons.items():
            posColor=self.fieldColor(pos)
            if not posColor==filterColor:
                self.drawPolygon(mask, pos, polygon, BoardFinder.white, BoardFinder.white)
        #if BoardFinder.debug:
        #    cv2.imshow("mask",mask)
        #    cv2.waitKey(1000)       
        masked=self.video.maskImage(image,mask)
        return masked
        
    def drawPolygon(self,image,pos,polygon,whiteColor,blackColor):    
        posColor=self.fieldColor(pos)
        color=blackColor if posColor else whiteColor
        cv2.fillConvexPoly(image,polygon,color)
        
    def showPolygonDebug(self,title):
        for chesspattern,corners in self.found.items():
            imagecopy=self.image.copy()
            polygons=self.asPolygons(chesspattern, corners)
            for pos,polygon in polygons.items():
                self.drawPolygon(imagecopy, pos, polygon, BoardFinder.lightGrey,BoardFinder.darkGrey)
            self.writeDebug(imagecopy,title, "polygons", chesspattern)     
               
    def showDebug(self,title):
        """ 'show' the debug picture of the chessboard corners by drawing the corners and writing the result to the given testImagePath"""
        for chesspattern in self.found.keys():
            corners=self.found[chesspattern]
            imageCopy=self.image.copy()
            cv2.drawChessboardCorners(imageCopy, chesspattern, corners, patternWasFound=True)
            #cv2.imshow('corners', self.image)
            #cv2.waitKey(50)
            self.writeDebug(imageCopy,title,"corners",chesspattern)
            
    def writeDebug(self,image,title,prefix,chesspattern):        
        Environment.checkDir(self.debugImagePath)    
        rows,cols=chesspattern   
        cv2.imwrite(self.debugImagePath+'%s-%s-%dx%d.jpg' % (title,prefix,rows,cols),image)       