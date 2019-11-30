#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

# Global imports
import cv2
from timeit import default_timer as timer

# Board Finder
class BoardFinder(object):
    """ find a chess board in the given image """
    debug=False
   
    # construct me from the given input Image
    def __init__(self, image):
        self.image=image
        self.height, self.width = self.image.shape[:2]
       
    def find(self,limit=1,searchWidth=640):
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
        for rows in range(8,2,-1):
            for cols in range(8,rows-1,-1):
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