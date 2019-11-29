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
        if BoardFinder.debug:
            print("BoardFinder for %dx%d image" % (self.width, self.height))

    def find(self):
        startt=timer()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        found={}
        for rows in range(3,9):
            for cols in range(3,9):
                chesspattern=(rows,cols)       
                # Find the chessboard corners
                start=timer()
                ret, corners = cv2.findChessboardCorners(gray, chesspattern, None)
                end=timer()
                if ret == True:
                    found[chesspattern]=corners
                    if BoardFinder.debug:
                        print ("finding corners with %d x %d pattern took %.2f s" % (rows,cols,(end-start)))
        endt=timer()
        if BoardFinder.debug:
            print ("found %d patterns in %.1f s" % (len(found),(endt-startt)))
        return found        
