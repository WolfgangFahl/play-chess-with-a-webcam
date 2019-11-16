#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import numpy as np
import math
from enum import IntEnum
import cv2
import chess

class Transformation(IntEnum):
    """ Transformation kind"""
    RELATIVE=0 # 1.0 x 1.0
    IDEAL=1 # e.g. 640x640
    ORIGINAL=2 # whatever the image size is
    
class ChessTrapezoid:
    """ Chess board Trapezoid (UK) / Trapezium (US) / Trapez (DE)  as seen via a webcam image """

    debug=True
    showDebugImage=False
    rows=8
    cols=8
    # default radius of pieces
    PieceRadiusFactor=3
  
    def __init__(self,topLeft,topRight,bottomRight,bottomLeft,idealSize=640):
        """ construct me from the given corner points"""
        self.tl,self.tr,self.br,self.bl=topLeft,topRight,bottomRight,bottomLeft
        self.polygon=np.array([topLeft,topRight,bottomRight,bottomLeft],dtype=np.int32)
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
        # trapezoid representation of squares
        self.tsquares={}
        for square in chess.SQUARES:
            tsquare=ChessTSquare(self,square)
            if ChessTrapezoid.debug:
                print(vars(tsquare))
            self.tsquares[square]=tsquare

    def relativeXY(self,rx,ry):
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

    def tSquareAt(self,row,col):
        """ get the trapezoid chessboard square for the given row and column"""
        row,col=self.rotateIndices(row, col)
        squareIndex = (ChessTrapezoid.rows-1-row) * ChessTrapezoid.cols + col;
        square = chess.SQUARES[squareIndex]
        return self.tsquares[square]

    def rotateIndices(self,row,col):
        """ rotate the indices or rows and columns according to the board rotation"""
        if self.rotation==0:
            return row,col
        elif self.rotation==90:
            return ChessTrapezoid.cols-1-col,row
        elif self.rotation==180:
            return ChessTrapezoid.rows-1-row,ChessTrapezoid.cols-1-col
        elif self.rotation==270:
            return col,ChessTrapezoid.rows-1-row
        else:
            raise Exception("invalid rotation %d for rotateIndices" % self.rotation)

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
        x=int(rx*self.idealSize)
        y=int(ry*self.idealSize)
        center=x,y
        self.drawCircle(image,center,radius,color,thickness)

    def maskImage(self,image,mask):
        """ return the masked image that filters the trapezoid view"""
        masked=cv2.bitwise_and(image,image,mask=mask)
        return masked

    def updatePieces(self,fen):
        """ update the piece positions according to the given FEN"""
        self.board=chess.Board(fen)
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            tsquare=self.tsquares[square]
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
        h, w = image.shape[:2]
        warped=cv2.warpPerspective(image,self.inverseTransform,(w,h))
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

    def byFieldState(self):
        # get a dict of fields sorted by field state
        sortedTSquares={}
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            if not tsquare.fieldState in sortedTSquares:
                sortedTSquares[tsquare.fieldState]=[]
            sortedTSquares[tsquare.fieldState].append(tsquare)
        return sortedTSquares

    def analyzeColors(self,image,video):
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
                video.showImage(masked,fieldState.title())
            if ChessTrapezoid.debug:
                b,g,r=averageColor.color
                bs,gs,rs=averageColor.stds
                print("%15s (%2d): %3d, %3d, %3d ± %3d, %3d, %3d " % (fieldState.title(),countedFields,b,g,r,bs,gs,rs))
                
    def detectMove(self,diffImage,video):
        changes=0
        for square in chess.SQUARES:
            tsquare=self.tsquares[square]
            changes+=tsquare.changed(diffImage,video)
        if ChessTrapezoid.debug:
            print ("detected %d " % (changes))   

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
        
class ChessTSquare:
    """ a chess square in it's trapezoidal perspective """
    # relative position and size of original square
    rw=1/(ChessTrapezoid.rows)
    rh=1/(ChessTrapezoid.cols)
    
    showDebugChange=["e2","e4"]

    def __init__(self,trapez,square):
        ''' construct me from the given trapez  and square '''
        self.trapez=trapez
        self.square=square
        self.an=chess.SQUARE_NAMES[square]
        self.row=ChessTrapezoid.rows-1-chess.square_rank(square)
        self.col=chess.square_file(square)
        # https://gamedev.stackexchange.com/a/44998/133453
        self.fieldColor=chess.WHITE if (self.col+self.row) % 2 == 1 else chess.BLACK
        self.fieldState=None
        self.piece=None
        self.rPieceRadius=ChessTSquare.rw/ChessTrapezoid.PieceRadiusFactor

        self.rx,self.ry=self.row*ChessTSquare.rw,self.col*ChessTSquare.rh
        self.x,self.y=trapez.relativeXY(self.rx, self.ry)
        self.setPolygons(trapez,self.rx,self.ry,self.rx+ChessTSquare.rw,self.ry,self.rx+ChessTSquare.rw,self.ry+ChessTSquare.rh,self.rx,self.ry+ChessTSquare.rh)

    def setPolygons(self,trapez,rtl_x,rtl_y,rtr_x,rtr_y,rbr_x,rbr_y,rbl_x,rbl_y):
        """ set my relative and warped polygons from the given relative corner coordinates from top left via top right, bottom right to bottom left """
        self.rpolygon=np.array([(rtl_x,rtl_y),(rtr_x,rtr_y),(rbr_x,rbr_y),(rbl_x,rbl_y)])
        self.idealPolygon=(self.rpolygon*trapez.idealSize).astype(np.int32)
        self.polygon=np.array([trapez.relativeXY(rtl_x,rtl_y),trapez.relativeXY(rtr_x,rtr_y),trapez.relativeXY(rbr_x,rbr_y),trapez.relativeXY(rbl_x,rbl_y)])
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
        """ draw my state onto the given image with the given transformation and color """
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
            rcenter=(self.rx+ChessTSquare.rw/2),(self.ry+ChessTSquare.rh/2)
            self.trapez.drawRCircle(image,rcenter,self.rPieceRadius,pieceImageColor)
            
    def changed(self,diffImage,video):
        h, w = diffImage.shape[:2]
        x=int(self.rx*w)
        y=int(self.ry*h)
         
        dh=h//ChessTrapezoid.rows
        dw=w//ChessTrapezoid.cols
        squareImage=diffImage[y:y +dh, x:x +dw]        
        if self.an in ChessTSquare.showDebugChange:
            video.showImage(squareImage,self.an)
        return 0    
            
