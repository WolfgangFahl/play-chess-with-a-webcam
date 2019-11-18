#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import numpy as np
import math
from enum import IntEnum
import cv2
import chess
from Video import Video
from RunningStats import RunningStats

class Transformation(IntEnum):
    """ Transformation kind"""
    RELATIVE=0 # 1.0 x 1.0
    IDEAL=1 # e.g. 640x640
    ORIGINAL=2 # whatever the image size is
    
class ChessTrapezoid:
    """ Chess board Trapezoid (UK) / Trapezium (US) / Trapez (DE)  as seen via a webcam image """

    debug=False
    showDebugImage=False
    rows=8
    cols=8
    # default radius of pieces
    PieceRadiusFactor=3
  
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft,idealSize=640,rotation=0,video=None):
        self.rotation=rotation
        trapezPoints=[topLeft,topRight,bottomRight,bottomLeft]
        shifts=self.rotation//90
        for shift in range(shifts):
            trapezPoints.append(trapezPoints.pop(0))
        topLeft,topRight,bottomRight,bottomLeft=trapezPoints
        self.setup(topLeft,topRight,bottomRight,bottomLeft,idealSize,video)
        
    def setup(self,topLeft,topRight,bottomRight,bottomLeft,idealSize=640,video=None):    
        """ construct me from the given corner points"""
        self.tl,self.tr,self.br,self.bl=topLeft,topRight,bottomRight,bottomLeft
        self.polygon=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
        # video access (for debugging and partly hiding open cv details)
        if video is None:
            self.video=Video()
        # prepare the perspective transformation
        # https://stackoverflow.com/questions/27585355/python-open-cv-perspectivetransform
        # https://stackoverflow.com/a/41768610/1497139
        # the destination
        pts_dst = np.asarray([topLeft,topRight,bottomRight,bottomLeft],dtype=np.float32)
        # the normed square described as a polygon in clockwise direction with an origin at top left
        self.pts_normedSquare = np.asarray([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],dtype=np.float32)
        self.transform=cv2.getPerspectiveTransform(self.pts_normedSquare,pts_dst)
        self.idealSize=idealSize
        s=idealSize
        self.pts_IdealSquare = np.asarray([[0.0, 0.0], [s, 0.0], [s, s], [0.0, s]],dtype=np.float32)
        self.inverseTransform=cv2.getPerspectiveTransform(pts_dst,self.pts_IdealSquare)
        self.rotation=0
        # dict for average Colors
        self.averageColors={}
        self.validChanges=0
        # trapezoid representation of squares
        self.tsquares={}
        for square in chess.SQUARES:
            tsquare=ChessTSquare(self,square)
            if ChessTrapezoid.debug:
                print(vars(tsquare))
            self.tsquares[tsquare.square]=tsquare
            
    def relativeToIdealXY(self,rx,ry):
        x=int(rx*self.idealSize)
        y=int(ry*self.idealSize)
        return x,y        
    
    def relativeToTrapezXY(self,rx,ry):
        """ convert a relative 0-1 based coordinate to a coordinate in the trapez"""
        # see https://math.stackexchange.com/questions/2084647/obtain-two-dimensional-linear-space-on-trapezoid-shape
        # https://stackoverflow.com/a/33303869/1497139
        rxry = np.asarray([[rx, ry]],dtype=np.float32)
        # target array - values are irrelevant because the will be overridden
        xya=cv2.perspectiveTransform(np.array([rxry]),self.transform)
        # example result:
        # ndarray: [[[20. 40.]]]
        xy=xya[0][0]
        x,y=xy[0],xy[1]
        return x,y

    def tSquareAt(self,row,col,rotation=0):
        """ get the trapezoid chessboard square for the given row and column"""
        row,col=self.rotateIndices(row, col,rotation)
        squareIndex = (ChessTrapezoid.rows-1-row) * ChessTrapezoid.cols + col;
        square = chess.SQUARES[squareIndex]
        return self.tsquares[square]

    def rotateIndices(self,row,col,rotation):
        """ rotate the indices or rows and columns according to the board rotation"""
        if rotation==0:
            return row,col
        elif rotation==90:
            return ChessTrapezoid.cols-1-col,row
        elif rotation==180:
            return ChessTrapezoid.rows-1-row,ChessTrapezoid.cols-1-col
        elif rotation==270:
            return col,ChessTrapezoid.rows-1-row
        else:
            raise Exception("invalid rotation %d for rotateIndices" % rotation)

    def genSquares(self):
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            yield tsquare
            
    def getEmptyImage(self,image,channels=1):
        """ prepare a trapezoid/polygon mask to focus on the square chess field seen as a trapezoid"""
        h, w = image.shape[:2]
        emptyImage=self.getEmtpyImage4WidthAndHeight(w, h, channels)
        return emptyImage
    
    def getEmtpyImage4WidthAndHeight(self,w,h,channels):    
        """ get an empty image with the given width height and channels"""
        emptyImage = np.zeros((h,w,channels), np.uint8)
        return emptyImage

    def drawPolygon(self,image,polygon,color):
        """ draw the given polygon onto the given image with the given color"""
        cv2.fillConvexPoly(image,polygon,color)
               
    def drawCircle(self,image,center,radius,color,thickness=-1):
        """ draw a circle onto the given image at the given center point with the given radius, color and thickness. """
        if color is not None:
            cv2.circle(image, center, radius, color=color, thickness=thickness)
    
    def drawRCircle(self,image,rcenter,rradius,color,thickness=-1):
        """ draw a circle with relative coordinates"""
        radius=int(rradius*self.idealSize)
        rx,ry=rcenter
        center=self.relativeToIdealXY(rx, ry)
        self.drawCircle(image,center,radius,color,thickness)
        
    def drawRCenteredText(self,image,text,rx,ry,color=(255,255,255)):
        x,y=self.relativeToIdealXY(rx, ry)    
        self.video.drawCenteredText(image, text, x, y,fontBGRColor=color)

    def maskImage(self,image,mask):
        """ return the masked image that filters the trapezoid view"""
        masked=cv2.bitwise_and(image,image,mask=mask)
        return masked

    def updatePieces(self,fen):
        """ update the piece positions according to the given FEN"""
        self.board=chess.Board(fen)
        for tsquare in self.genSquares():
            piece = self.board.piece_at(tsquare.square)
            tsquare.piece=piece
            tsquare.fieldState=tsquare.getFieldState()

    def drawFieldStates(self,image,fieldStates,transformation=Transformation.ORIGINAL,channels=3):
        """ draw the states for fields with the given field states e.g. to set the mask image that will filter the trapezoid view according to piece positions when using maskImage"""
        if self.board is not None:
            for square in chess.SQUARES:
                tsquare=self.tsquares[square]
                if tsquare.fieldState in fieldStates:
                    tsquare.drawState(image,transformation,channels)

    def warpedBoardImage(self,image):
        warped=cv2.warpPerspective(image,self.inverseTransform,(self.idealSize,self.idealSize))
        return warped
    
    def diffBoardImage(self,image,other):
        if image is None :
            raise Exception("image is None for diff")
        if other is None:
            raise Exception("other is None for diff")
        h, w = image.shape[:2]
        ho, wo = other.shape[:2]
        if not h==ho or not w==wo:
            raise Exception("image %d x %d has to have same size as other %d x %d for diff" % (w,h,wo,ho))
        #return np.subtract(self.image,other)
        return cv2.absdiff(image,other)   
    
    def diffSum(self,image,other):
        #diffImage=self.diff(other) 
        #return diffImage.sum()   
        # https://stackoverflow.com/questions/17829092/opencv-cv2-absdiffimg1-img2-sum-without-temporary-img
        diffSumValue=cv2.norm(image,other,cv2.NORM_L1)
        if ChessTrapezoid.debug:
            print("diffSum %.0f" % (diffSumValue))
        return diffSumValue

    def idealColoredBoard(self,w,h,transformation=Transformation.IDEAL):
        """ draw an 'ideal' colored board according to a given set of parameters e.g. fieldColor, pieceColor, pieceRadius"""
        idealImage=self.getEmtpyImage4WidthAndHeight(w,h,3)
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            tsquare.drawState(idealImage,transformation,3)
        return idealImage
    
    def drawDebug(self,image,color=(255,255,255)):
        """ draw debug information e.g. piecel symbol and an onto the given image"""
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            tsquare.drawDebug(image,color)
  
    def byFieldState(self):
        # get a dict of fields sorted by field state
        sortedTSquares={}
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            if not tsquare.fieldState in sortedTSquares:
                sortedTSquares[tsquare.fieldState]=[]
            sortedTSquares[tsquare.fieldState].append(tsquare)
        return sortedTSquares

    def analyzeColors(self,image):
        """ get the average colors per fieldState """
        warped=self.warpedBoardImage(image)
        byFieldState=self.byFieldState()
        for fieldState in FieldState:
            mask=self.getEmptyImage(warped)
            self.drawFieldStates(mask,[fieldState],Transformation.IDEAL,1)
            masked=self.maskImage(image,mask)
            countedFields=len(byFieldState[fieldState])
            averageColor=Color(masked)
            self.averageColors[fieldState]=averageColor
            if ChessTrapezoid.showDebugImage:
                self.video.showImage(masked,fieldState.title())
            if ChessTrapezoid.debug:
                b,g,r=averageColor.color
                bs,gs,rs=averageColor.stds
                print("%15s (%2d): %3d, %3d, %3d ± %3d, %3d, %3d " % (fieldState.title(),countedFields,b,g,r,bs,gs,rs))
                
    def detectChanges(self,diffImage):
        """ detect the changes of the given differential image """
        changes={}
        validChanges=0
        for tsquare in self.genSquares():
            squareChange=tsquare.squareChange(diffImage)
            changes[tsquare.an]=squareChange
            if squareChange.valid:
                validChanges+=1
        changes["valid"]=validChanges
        # trigger statistics push if valid
        if (validChanges>=60):
            for tsquare in self.genSquares():
                squareChange=changes[tsquare.an]
                squareChange.push(tsquare.changeStats,squareChange.value)
            
        return changes    

class FieldState(IntEnum):
    """ the state of a field is a combination of the field color with a piece color + two empty field color options"""
    WHITE_EMPTY = 0
    WHITE_WHITE = 1
    WHITE_BLACK = 2
    BLACK_EMPTY = 3
    BLACK_WHITE = 4
    BLACK_BLACK = 5

    def title(self,titles=["white empty", "white on white", "black on white","black empty","white on black","black on black"]):
        return titles[self]

class Color:
    """ Color definitions with maximum lightness difference and calculation of average color for a sample of square with a given fieldState """
    white=(255,255,255)
    lightgrey=(170,170,170)
    darkgrey=(85,85,85)
    black=(0,0,0)
    debug=False
    
    def __init__(self,image):
        """ pick the an average color from the given image"""
        #https://stackoverflow.com/a/43112217/1497139 
        (means, stds) = cv2.meanStdDev(image)
        #https://stackoverflow.com/a/55163686/1497139
        b = image[:,:,0]
        g = image[:,:,1]
        r = image[:,:,2]
        h, w = image.shape[:2]
        pixels=h*w
        nonzerotupel= cv2.countNonZero(b),cv2.countNonZero(g),cv2.countNonZero(r)
        nonzero=max(nonzerotupel)
        # exotic case of a totally black picture
        if nonzero==0:
            self.color(0,0,0)
        else:    
            self.color,self.stds=self.fixMeans(means, stds, pixels, nonzero)
            
    def fixMeans(self,means,stds,pixels,nonzero):
        """ fix the zero based means to nonzero based see https://stackoverflow.com/a/58891531/1497139"""
        gmean,bmean,rmean=means.flatten()
        gstds,bstds,rstds=stds.flatten()
        if Color.debug:
            print ("means %.2f %.2f %.2f " % (gmean,bmean,rmean))
            print ("stds  %.2f %.2f %.2f " % (gstds,bstds,rstds))
        factor=pixels/nonzero
        fgmean=gmean*factor
        fbmean=bmean*factor
        frmean=rmean*factor
        if Color.debug:
            print ("non-zero means %.2f %.2f %.2f" % (fgmean,fbmean,frmean))
        fsqsumb=(bstds*bstds+bmean*bmean)*pixels
        fsqsumg=(gstds*gstds+gmean*gmean)*pixels
        fsqsumr=(rstds*rstds+rmean*rmean)*pixels
        if (Color.debug):
            print ("fsqsum %.2f %.2f %.2f" % (fsqsumb,fsqsumg,fsqsumr))
        fstdsb=math.sqrt(max(fsqsumb/nonzero-fbmean*fbmean,0))
        fstdsg=math.sqrt(max(fsqsumg/nonzero-fgmean*fgmean,0))
        fstdsr=math.sqrt(max(fsqsumr/nonzero-frmean*frmean,0))   
        if Color.debug:
            print ("non-zero stds %.2f %.2f %.2f" % (fstdsb,fstdsg,fstdsr))
        fixedmeans=fgmean,fbmean,frmean
        fixedstds=fstdsb,fstdsg,fstdsr
        return fixedmeans,fixedstds

class SquareChange:
    """ keep track of changes of a square over time """
    medianFrameCount=10
    treshold=0.2*64
    
    def __init__(self,value,stats):
        """ construct me from the given value with the given running stats"""
        self.value=value
        self.mean=stats.mean()
        self.diff=value-self.mean
        if stats.n<SquareChange.medianFrameCount:
            stats.push(value)
            self.valid=False
            self.diff=0
        else:
            self.valid=abs(self.diff)<SquareChange.treshold
                
    def push(self,stats,value):
        if self.valid:
            stats.push(value)
        
class ChessTSquare:
    """ a chess square in it's trapezoidal perspective """
    # relative position and size of original square
    rw=1/(ChessTrapezoid.rows)
    rh=1/(ChessTrapezoid.cols)
    
    showDebugChange=[]

    def __init__(self,trapez,square):
        ''' construct me from the given trapez  and square '''
        self.trapez=trapez
        self.changeStats=RunningStats()
        self.square=square
        self.an=chess.SQUARE_NAMES[square]
        # rank are rows in Algebraic Notation from 1 to 8
        self.row=ChessTrapezoid.rows-1-chess.square_rank(square)
        # files are columns in Algebraic Notation from A to H
        self.col=chess.square_file(square)
        # https://gamedev.stackexchange.com/a/44998/133453
        self.fieldColor=chess.WHITE if (self.col+self.row) % 2 == 1 else chess.BLACK
        self.fieldState=None
        self.piece=None
        
        self.rPieceRadius=ChessTSquare.rw/ChessTrapezoid.PieceRadiusFactor

        self.rx,self.ry=self.col*ChessTSquare.rw,self.row*ChessTSquare.rh
        self.x,self.y=trapez.relativeToTrapezXY(self.rx, self.ry)
        self.setPolygons(trapez,self.rx,self.ry,self.rx+ChessTSquare.rw,self.ry,self.rx+ChessTSquare.rw,self.ry+ChessTSquare.rh,self.rx,self.ry+ChessTSquare.rh)

    def setPolygons(self,trapez,rtl_x,rtl_y,rtr_x,rtr_y,rbr_x,rbr_y,rbl_x,rbl_y):
        """ set my relative and warped polygons from the given relative corner coordinates from top left via top right, bottom right to bottom left """
        self.rpolygon=np.array([(rtl_x,rtl_y),(rtr_x,rtr_y),(rbr_x,rbr_y),(rbl_x,rbl_y)])
        self.idealPolygon=(self.rpolygon*trapez.idealSize).astype(np.int32)
        # function to use to calculate polygon
        r2t=trapez.relativeToTrapezXY
        self.polygon=np.array([r2t(rtl_x,rtl_y),r2t(rtr_x,rtr_y),r2t(rbr_x,rbr_y),r2t(rbl_x,rbl_y)])
        self.ipolygon=self.polygon.astype(np.int32)

    def getPolygon(self,transformation):
        if transformation==Transformation.ORIGINAL:
            return self.ipolygon
        elif transformation==Transformation.RELATIVE:
            return self.rpolygon
        elif transformation==Transformation.IDEAL:
            return self.idealPolygon
        else:
            raise Exception("invalid transformation %d for getPolygon",transformation)   
        
    def getFieldState(self):
        piece = self.piece
        if piece is None:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_EMPTY
            else:
                return FieldState.BLACK_EMPTY
        elif piece.color == chess.WHITE:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_WHITE
            else:
                return FieldState.BLACK_WHITE
        else:
            if self.fieldColor == chess.WHITE:
                return FieldState.WHITE_BLACK
            else:
                return FieldState.BLACK_BLACK
        # this can't happen
        return None

    def drawState(self,image,transformation,channels):
        """ draw my state onto the given image with the given transformation and number of channels"""
        # default is drawing a single channel mask
        squareImageColor=64
        pieceImageColor=squareImageColor
        if channels==3:
            if self.fieldColor==chess.WHITE:
                if FieldState.WHITE_EMPTY in self.trapez.averageColors:
                    squareImageColor=self.trapez.averageColors[FieldState.WHITE_EMPTY].color
                else:
                    squareImageColor=Color.white    
            else:
                if FieldState.BLACK_EMPTY in self.trapez.averageColors:
                    squareImageColor=self.trapez.averageColors[FieldState.BLACK_EMPTY].color
                else:
                    squareImageColor=Color.black
        
        if not (channels==1 and self.piece is not None): 
            self.trapez.drawPolygon(image,self.getPolygon(transformation),squareImageColor)
        
        
        if self.piece is not None:
            if channels==3:
                if self.fieldState in self.trapez.averageColors:
                    pieceImageColor=self.trapez.averageColors[self.fieldState].color
                else:    
                    pieceImageColor=Color.darkgrey if self.piece.color==chess.BLACK else Color.lightgrey
            rcenter=self.rcenter()        
            self.trapez.drawRCircle(image,rcenter,self.rPieceRadius,pieceImageColor)
    
    def rcenter(self):        
        rcx=(self.rx+ChessTSquare.rw/2)
        rcy=(self.ry+ChessTSquare.rh/2)
        return (rcx,rcy)
            
    def drawDebug(self,image,color=(255,255,255)):
        """ draw debug information onto the given image using the given color""" 
        symbol=""
        if self.piece is not None:
            symbol=self.piece.symbol() # @TODO piece.unicode_symbol() - needs other font!
        squareHint=self.an+" "+symbol
        rcx,rcy=self.rcenter()
        self.trapez.drawRCenteredText(image,squareHint,rcx,rcy,color=color)   
             
    def squareChange(self,diffImage):
        """ check the changes analyzing the difference image of this square"""
        h, w = diffImage.shape[:2]
        x=int(self.rx*w)
        y=int(self.ry*h)
         
        dh=h//ChessTrapezoid.rows
        dw=w//ChessTrapezoid.cols
        squareImage=diffImage[y:y +dh, x:x +dw]
        diffSum=np.sum(squareImage)
                
        squareChange=SquareChange(diffSum/(dh*dw),self.changeStats)
        if self.an in ChessTSquare.showDebugChange:
            self.trapez.video.showImage(squareImage,self.an)
            print("%s: %s" %(self.an,vars(squareChange)))
        return squareChange