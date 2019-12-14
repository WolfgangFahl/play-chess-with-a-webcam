#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.chessvision import FieldState, IMoveDetector
from pcwawc.chessimage import ChessBoardImage
from pcwawc.field import Field
import cv2
from zope.interface import implementer

@implementer(IMoveDetector) 
class BoardDetector:
    """ detect a chess board's state from the given image """
    frameDebug = False

    # construct me from a board and video
    def __init__(self):
        pass
    
    def setup(self,name,board, video,args):
        self.name=name
        self.board = board
        self.video = video
        self.speedup=args.speedup if args is not None else 1
        self.hsv = None
        self.previous=None
        self.debug = False
     
    def genFields(self):
        for row in range(Field.rows):
            for col in range (Field.cols):
                field = self.board.fieldAt(row, col)
                yield field    
           
    def divideInFields(self,image):
        # interpolate the centers of the 8x8 fields from a squared image
        height, width = image.shape[:2]
        fieldHeight = height / Field.rows
        fieldWidth = width / Field.cols
        for field in self.genFields():   
            pcx = int(fieldWidth * (2 * field.col + 1) // 2)
            pcy = int(fieldHeight * (2 * field.row + 1) // 2)
            field.width=fieldWidth
            field.height=fieldHeight
            field.pcx = pcx
            field.pcy = pcy
            field.maxX= width
            field.maxY= height
    
    def sortByFieldState(self):            
        # get a dict of fields sorted by field state
        sortedByFieldState = sorted(self.board.fieldsByAn.values(), key=lambda field:field.getFieldState())
        counts = self.board.fieldStateCounts()
        sortedFields={}
        fromIndex=0
        for fieldState in FieldState:
            toIndex=fromIndex+counts[fieldState]
            sortedFields[fieldState]=sortedByFieldState[fromIndex:toIndex]
            fromIndex=toIndex
        return sortedFields
    
    def analyzeFields(self,image,grid,roiLambda):    
        for field in self.genFields():
            field.divideInROIs(grid,roiLambda)
            for roi in field.rois:
                roi.analyze(image)
                    
    def analyzeColors(self, image, distance=3, step=1):
        self.hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        for field in self.genFields():
            field.analyzeColor(image, self.hsv, distance, step)
        
    def onChessBoardImage(self,imageEvent):
        cbImageSet=imageEvent.cbImageSet
        vision=cbImageSet.vision
        args=vision.args
        distance=args.distance
        step=args.step
        return self.analyze(cbImageSet,distance, step)    
    
    # analyze the given image
    def analyze(self, cbImageSet, distance=3, step=1):
        frameIndex=cbImageSet.frameIndex
        if (frameIndex % self.speedup==0):
            image=cbImageSet.cbWarped.image
            self.divideInFields(image)
            self.analyzeColors(image, distance, step)
            sortedFields=self.sortByFieldState()

            if self.debug:
                overlay = image.copy()
    
                for fieldState,fields in sortedFields.items():
                    for field in fields:
                        l = field.luminance
                        if BoardDetector.frameDebug:
                            print ("frame %5d: %s luminance: %3.0f ± %3.0f (%d) rgbColorKey: %3.0f colorKey: %.0f" % (frameIndex, field.an, l.mean(), l.standard_deviation(), l.n, field.rgbColorKey, field.colorKey))
                        field.drawDebug(self.video, overlay, fieldState)
                alpha = 0.6  # Transparency factor.
                # Following line overlays transparent rectangle over the image
                image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
                image = image_new
                cbImageSet.cbDebug=ChessBoardImage(image,"debug")
                self.previous=image
        else:
            if self.previous is not None:
                image=self.previous
                
        return image
