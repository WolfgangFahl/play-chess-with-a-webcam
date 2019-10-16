#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Global imports
import sys
import cv2.cv as cv
import cv2
import numpy as np
from StateDetector import StateDetector, CannotBuildStateException
from collections import defaultdict


class BadImage(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class MovementDetector(object):
    """This class used to detect if a move has occured in the board. 
    It also needs to be tolerant to sudden lighting changes"""
    
    def __init__(self, colorImage):
        """To be built correctly, this class need the image of the starting position"""
        initialBoard = {}
        initialImage = None
        try:
            self.StateDetector = StateDetector()
            initialBoard, initialImage = self.StateDetector.detectState(colorImage)
        except CannotBuildStateException as e:
            raise BadImage("Initialisation Failed" + str(e))
            
        self.images = [initialImage, initialImage]
        self.board = initialBoard
        
    def detectMove(self, colorImage):
        """This public function receives a clean image.
            It will try to detect if a move have been played.
            If image is clean, the function returns an the move that was played, or an empty list.
            Returns a list containing the movements that were detected."""
        newBoard = {}
        newImage = None
        try:
            newBoard, newImage = self.StateDetector.detectState(colorImage)
        except CannotBuildStateException as e:
            raise BadImage(str(e))
        
        self._changeState(newBoard, newImage)
        return self._getMovements()
    
    def _changeState(self, newBoard, newImage):
        self.board = newBoard
        self.images[1] = newImage
        
    def _getMovements(self):
        movements = []
        currentBoard = self.board
        
        pastImage = np.asarray(self.images[0][:,:])
        currentImage = np.asarray(self.images[1][:,:])
        
        diff = cv2.absdiff(pastImage, currentImage)
        cv.ShowImage("chessCamDebug", cv.fromarray(diff))
        
        for key in currentBoard.keys():
            coords = currentBoard[key].GetCoords()
            region = cv.GetSubRect(cv.fromarray(diff), coords)
                
            variance = sum(cv2.integral(np.asarray(region))[-1][-1])
            if variance > 35000:
                movements.append(key)
        
        if len(movements) < 2: #at least two cells must be moved
            movements = []
            
        self.images[0] = self.images[1] #Recalibrate
        return movements
        
if __name__ == "__main__":
    sys.stderr.write("This module is not designed to be run standalone.")
