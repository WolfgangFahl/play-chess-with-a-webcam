#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
import sys

class Cell(object):
        
    def __init__(self, coords):
        self.coords = coords
                
    def __repr__(self):
        return "coords=" + str(self.coords)
    
    def GetCoords(self):
        return self.coords
        
if __name__ == "__main__":
    sys.stderr.write("Not a stand alone")