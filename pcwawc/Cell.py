#!/usr/bin/python

# Global imports
import sys


class Cell(object):
        
    def __init__(self, coords):
        x1,y1,x2,y2=coords
        self.coords = (int(x1),int(y1),int(x2),int(y2))
                
    def __repr__(self):
        return "coords=" + str(self.coords)
    
    def GetCoords(self):
        return self.coords

        
if __name__ == "__main__":
    sys.stderr.write("Not a stand alone")
