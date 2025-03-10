#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# <uml>
#   Trapez2Square <|-- ChessTrapezoid
#   ChessTrapezoid -- ChessTSquare
#   ChessTSquare -- SquareChange
#   ChessTSquare -- FieldState
# </uml>
import math
from enum import IntEnum
from timeit import default_timer as timer

import chess
import cv2
import numpy as np
from zope.interface import implementer

from pcwawc.chessimage import ChessBoardImage
from pcwawc.chessvision import FieldState, ISquare
from pcwawc.runningstats import MinMaxStats, MovingAverage
from pcwawc.video import Video


class Transformation(IntEnum):
    """Transformation kind"""

    RELATIVE = 0  # 1.0 x 1.0
    IDEAL = 1  # e.g. 640x640
    ORIGINAL = 2  # whatever the image size is


class Trapez2Square:
    """transform a trapez to a square and back as needed"""

    def __init__(self, topLeft, topRight, bottomRight, bottomLeft):
        """construct me from the given corner points"""
        self.tl, self.tr, self.br, self.bl = topLeft, topRight, bottomRight, bottomLeft
        self.polygon = np.array(
            [topLeft, topRight, bottomRight, bottomLeft], dtype=np.int32
        )
        # prepare the perspective transformation
        # https://stackoverflow.com/questions/27585355/python-open-cv-perspectivetransform
        # https://stackoverflow.com/a/41768610/1497139
        # the destination
        self.pts_dst = np.asarray(
            [topLeft, topRight, bottomRight, bottomLeft], dtype=np.float32
        )
        # the normed square described as a polygon in clockwise direction with an origin at top left
        self.pts_normedSquare = np.asarray(
            [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32
        )
        self.transform = cv2.getPerspectiveTransform(
            self.pts_normedSquare, self.pts_dst
        )

    def relativeToTrapezXY(self, rx, ry):
        """convert a relative 0-1 based coordinate to a coordinate in the trapez"""
        # see https://math.stackexchange.com/questions/2084647/obtain-two-dimensional-linear-space-on-trapezoid-shape
        # https://stackoverflow.com/a/33303869/1497139
        rxry = np.asarray([[rx, ry]], dtype=np.float32)
        # target array - values are irrelevant because the will be overridden
        xya = cv2.perspectiveTransform(np.array([rxry]), self.transform)
        # example result:
        # ndarray: [[[20. 40.]]]
        xy = xya[0][0]
        x, y = xy[0], xy[1]
        return x, y

    def relativeTrapezToTrapezXY(self, rx1, ry1, rx2, ry2):
        return np.asarray(
            [
                self.relativeToTrapezXY(rx1, ry1),
                self.relativeToTrapezXY(rx2, ry1),
                self.relativeToTrapezXY(rx2, ry2),
                self.relativeToTrapezXY(rx1, ry2),
            ],
            dtype=np.int32,
        )


class ChessTrapezoid(Trapez2Square):
    """Chess board Trapezoid (UK) / Trapezium (US) / Trapez (DE)  as seen via a webcam image"""

    debug = False
    colorDebug = False
    showDebugImage = False
    rows = 8
    cols = 8
    # default radius of pieces
    PieceRadiusFactor = 3
    DiffSumMovingAverageLength = 5

    def __init__(self, trapezPoints, idealSize=640, rotation=0, video=None):
        self.rotation = rotation
        # trapezPoints=[topLeft,topRight,bottomRight,bottomLeft]
        shifts = self.rotation // 90
        for shift in range(shifts):
            left = trapezPoints.pop(0)
            trapezPoints.append(left)
        topLeft, topRight, bottomRight, bottomLeft = trapezPoints
        super().__init__(topLeft, topRight, bottomRight, bottomLeft)
        self.setup(idealSize, video)

    def setup(self, idealSize=640, video=None):
        # video access (for debugging and partly hiding open cv details)
        if video is None:
            self.video = Video()
        self.idealSize = idealSize
        s = idealSize
        self.pts_IdealSquare = np.asarray(
            [[0.0, 0.0], [s, 0.0], [s, s], [0.0, s]], dtype=np.float32
        )
        self.inverseTransform = cv2.getPerspectiveTransform(
            self.pts_dst, self.pts_IdealSquare
        )
        self.rotation = 0
        # dict for average Colors
        self.averageColors = {}
        self.diffSumAverage = MovingAverage(ChessTrapezoid.DiffSumMovingAverageLength)
        # trapezoid representation of squares
        self.tsquares = {}
        for square in chess.SQUARES:
            tsquare = ChessTSquare(self, square)
            if ChessTrapezoid.debug:
                print(vars(tsquare))
            self.tsquares[tsquare.square] = tsquare

    def relativeToIdealXY(self, rx, ry):
        x = int(rx * self.idealSize)
        y = int(ry * self.idealSize)
        return x, y

    def tSquareAt(self, row, col, rotation=0):
        """get the trapezoid chessboard square for the given row and column"""
        row, col = self.rotateIndices(row, col, rotation)
        squareIndex = (ChessTrapezoid.rows - 1 - row) * ChessTrapezoid.cols + col
        square = chess.SQUARES[squareIndex]
        return self.tsquares[square]

    def rotateIndices(self, row, col, rotation):
        """rotate the indices or rows and columns according to the board rotation"""
        if rotation == 0:
            return row, col
        elif rotation == 90:
            return ChessTrapezoid.cols - 1 - col, row
        elif rotation == 180:
            return ChessTrapezoid.rows - 1 - row, ChessTrapezoid.cols - 1 - col
        elif rotation == 270:
            return col, ChessTrapezoid.rows - 1 - row
        else:
            raise Exception("invalid rotation %d for rotateIndices" % rotation)

    def genSquares(self):
        """generator for all chess squares"""
        for square in chess.SQUARES:
            tsquare = self.tsquares[square]
            yield tsquare

    def drawCircle(self, image, center, radius, color, thickness=-1):
        """draw a circle onto the given image at the given center point with the given radius, color and thickness."""
        if color is not None:
            cv2.circle(image, center, radius, color=color, thickness=thickness)

    def drawRCircle(self, image, rcenter, rradius, color, thickness=-1):
        """draw a circle with relative coordinates"""
        radius = int(rradius * self.idealSize)
        rx, ry = rcenter
        center = self.relativeToIdealXY(rx, ry)
        self.drawCircle(image, center, radius, color, thickness)

    def drawRCenteredText(self, image, text, rx, ry, color=(255, 255, 255)):
        x, y = self.relativeToIdealXY(rx, ry)
        self.video.drawCenteredText(image, text, x, y, fontBGRColor=color)

    def updatePieces(self, fen):
        """update the piece positions according to the given FEN"""
        self.board = chess.Board(fen)
        for tsquare in self.genSquares():
            piece = self.board.piece_at(tsquare.square)
            tsquare.piece = piece
            tsquare.fieldState = tsquare.getFieldState()

    def drawFieldStates(
        self, image, fieldStates, transformation=Transformation.ORIGINAL, channels=3
    ):
        """draw the states for fields with the given field states e.g. to set the mask image that will filter the trapezoid view according to piece positions when using maskImage"""
        if self.board is not None:
            for tsquare in self.genSquares():
                if tsquare.fieldState in fieldStates:
                    tsquare.drawState(image, transformation, channels)

    def prepareImageSet(self, cbImageSet):
        """prepare the image set"""
        cbWarped = self.warpedBoardImage(cbImageSet.cbImage.image)
        averageColors = self.analyzeColors(cbWarped)
        cbImageSet.cbWarped = cbWarped
        cbIdeal = self.idealColoredBoard(cbWarped.width, cbWarped.height)
        cbImageSet.cbIdeal = cbIdeal
        cbImageSet.cbPreMove = self.preMoveBoard(cbWarped.width, cbWarped.height)
        cbImageSet.cbDiff = cbWarped.diffBoardImage(cbIdeal)
        return averageColors

    def warpedBoardImage(self, image):
        warped = cv2.warpPerspective(
            image, self.inverseTransform, (self.idealSize, self.idealSize)
        )
        return ChessBoardImage(warped, "warped")

    def diffSum(self, image, other):
        # diffImage=self.diff(other)
        # return diffImage.sum()
        # https://stackoverflow.com/questions/17829092/opencv-cv2-absdiffimg1-img2-sum-without-temporary-img
        diffSumValue = cv2.norm(image, other, cv2.NORM_L1)
        if ChessTrapezoid.debug:
            print("diffSum %.0f" % (diffSumValue))
        return diffSumValue

    def idealColoredBoard(self, w, h, transformation=Transformation.IDEAL):
        """draw an 'ideal' colored board according to a given set of parameters e.g. fieldColor, pieceColor, pieceRadius"""
        idealImage = self.video.getEmptyImage4WidthAndHeight(w, h, 3)
        for tsquare in self.genSquares():
            tsquare.drawState(idealImage, transformation, 3)
        return ChessBoardImage(idealImage, "ideal")

    def preMoveBoard(self, w, h):
        """get an image of the board as it was before any move"""
        refImage = self.video.getEmptyImage4WidthAndHeight(w, h, 3)
        for tsquare in self.genSquares():
            tsquare.addPreMoveImage(refImage)
        return ChessBoardImage(refImage, "preMove ref")

    def drawDebug(self, image, color=(255, 255, 255)):
        """draw debug information e.g. piecel symbol and an onto the given image"""
        for square in chess.SQUARES:
            tsquare = self.tsquares[square]
            tsquare.drawDebug(image, color)

    def byFieldState(self):
        # get a dict of fields sorted by field state
        sortedTSquares = {}
        for fieldState in FieldState:
            sortedTSquares[fieldState] = []
        for tsquare in self.genSquares():
            sortedTSquares[tsquare.fieldState].append(tsquare)
        return sortedTSquares

    def analyzeColors(self, cbImage):
        """get the average colors per fieldState"""
        byFieldState = self.byFieldState()
        for fieldState in byFieldState.keys():
            mask = self.video.getEmptyImage(cbImage.image)
            self.drawFieldStates(mask, [fieldState], Transformation.IDEAL, 1)
            masked = self.video.maskImage(cbImage.image, mask)
            countedFields = len(byFieldState[fieldState])
            averageColor = Color(masked)
            self.averageColors[fieldState] = averageColor
            if ChessTrapezoid.showDebugImage:
                self.video.showImage(masked, fieldState.title())
            if ChessTrapezoid.colorDebug:
                print(
                    "%15s (%2d): %s" % (fieldState.title(), countedFields, averageColor)
                )
        return self.averageColors

    def optimizeColorCheck(self, cbImage, averageColors, debug=False):
        optimalSelectivity = -100
        colorStats = None
        for factor in [x * 0.05 for x in range(20, 41)]:
            """optimize the factor for the color check"""
            startc = timer()
            fieldColorStatsCandidate = self.checkColors(cbImage, averageColors, factor)
            endc = timer()
            fieldColorStatsCandidate.analyzeStats(factor, endc - startc)
            if fieldColorStatsCandidate.minSelectivity > optimalSelectivity:
                optimalSelectivity = fieldColorStatsCandidate.minSelectivity
                colorStats = fieldColorStatsCandidate
                if debug:
                    print(
                        "selectivity %5.1f white: %5.1f black: %5.1f "
                        % (
                            self.minSelectivity,
                            self.whiteSelectivity,
                            self.blackSelectivity,
                        )
                    )
        return colorStats

    def checkColors(self, cbImage, averageColors, rangeFactor=1.0):
        """check the colors against the expectation"""
        byFieldState = self.byFieldState()
        colorStats = FieldColorStats()
        for fieldState in byFieldState.keys():
            # https://stackoverflow.com/questions/54019108/how-to-count-the-pixels-of-a-certain-color-with-opencv
            if fieldState in [
                FieldState.WHITE_BLACK,
                FieldState.WHITE_EMPTY,
                FieldState.WHITE_WHITE,
            ]:
                averageColor = averageColors[FieldState.WHITE_EMPTY]
            else:
                averageColor = averageColors[FieldState.BLACK_EMPTY]
            fields = byFieldState[fieldState]
            lower, upper = averageColor.colorRange(rangeFactor)
            if ChessTrapezoid.colorDebug:
                print(
                    "%25s (%2d): %s -> %s - %s"
                    % (fieldState.title(), len(fields), averageColor, lower, upper)
                )
            for tsquare in fields:
                squareImage = tsquare.getSquareImage(cbImage)
                asExpected = cv2.inRange(squareImage, lower, upper)
                h, w = squareImage.shape[:2]
                pixels = h * w
                nonzero = cv2.countNonZero(asExpected)
                colorStats.push(fieldState, tsquare.an, nonzero / pixels * 100)
                # self.video.showImage(asExpected,tsquare.an)
        return colorStats

    def detectChanges(self, cbImageSet, detectState):
        """detect the changes of the given imageset using the given detect state machine"""
        detectState.nextFrame()
        changes = {}
        validChanges = 0
        diffSum = 0
        cbImage = cbImageSet.cbImage
        cbDiff = cbImageSet.cbDiff
        for tsquare in self.genSquares():
            squareChange = tsquare.squareChange(cbImage.image, cbDiff.image)
            changes[tsquare.an] = squareChange
            diffSum += abs(squareChange.diff)
            if squareChange.valid:
                validChanges += 1
            # if self.frames==1:
            #    tsquare.preMoveImage=np.copy(tsquare.squareImage)

        self.diffSumAverage.push(diffSum)
        diffSumDelta = self.diffSumAverage.mean() - diffSum
        detectState.check(
            validChanges, diffSum, diffSumDelta, squareChange.meanFrameCount
        )
        for tsquare in self.genSquares():
            squareChange = changes[tsquare.an]
            tsquare.checkMoved(detectState)

        changes["validBoard"] = detectState.validBoard
        changes["valid"] = validChanges
        changes["diffSum"] = diffSum
        changes["diffSumDelta"] = diffSumDelta
        changes["validFrames"] = detectState.validFrames
        changes["invalidFrames"] = detectState.invalidFrames
        return changes


class FieldColorStats(object):
    """Color statistics for Fields"""

    def __init__(self):
        self.stats = {}
        self.colorPercent = {}
        for fieldState in FieldState:
            self.stats[fieldState] = MinMaxStats()

    def push(self, fieldState, an, percent):
        self.colorPercent[an] = percent
        self.stats[fieldState].push(percent)

    def analyzeStats(self, factor, time, debug=False):
        self.factor = factor
        self.whiteEmptyMin = self.stats[FieldState.WHITE_EMPTY].min
        self.whiteFilledMax = max(
            self.stats[FieldState.WHITE_BLACK].max,
            self.stats[FieldState.WHITE_WHITE].max,
        )
        self.whiteSelectivity = self.whiteEmptyMin - self.whiteFilledMax
        self.blackEmptyMin = self.stats[FieldState.BLACK_EMPTY].min
        self.blackFilledMax = max(
            self.stats[FieldState.BLACK_BLACK].max,
            self.stats[FieldState.BLACK_WHITE].max,
        )
        self.blackSelectivity = self.blackEmptyMin - self.blackFilledMax
        self.minSelectivity = min(self.whiteSelectivity, self.blackSelectivity)
        if debug:
            self.showDebug(time)

    def showDebug(self, time):
        print("color check %.3f s with factor %.2f" % ((time), self.factor))
        for fieldState in FieldState:
            self.showFieldStateDebug(fieldState)

    def showFieldStateDebug(self, fieldState):
        print(
            "%20s: %s"
            % (
                fieldState.title(),
                self.stats[fieldState].formatMinMax(
                    formatR="%2d: %4.1f ± %4.1f", formatM=" %4.1f - %4.1f"
                ),
            )
        )

    def showStatsDebug(self, time):
        print(
            "%.3fs for color check optimization factor: %5.1f selectivity min %5.1f,white: %5.1f black: %5.1f"
            % (
                time,
                self.factor,
                self.minSelectivity,
                self.whiteSelectivity,
                self.blackSelectivity,
            )
        )


class Color:
    """Color definitions with maximum lightness difference and calculation of average color for a sample of square with a given fieldState"""

    white = (255, 255, 255)
    lightgrey = (170, 170, 170)
    darkgrey = (85, 85, 85)
    black = (0, 0, 0)
    debug = False

    def __init__(self, image):
        """pick the average color from the given image"""
        # https://stackoverflow.com/a/43112217/1497139
        (means, stds) = cv2.meanStdDev(image)
        pixels, nonzero = Color.countNonZero(image)
        # exotic case of a totally black picture
        if nonzero == 0:
            self.color = (0, 0, 0)
            self.stds = (0, 0, 0)
        else:
            self.color, self.stds = self.fixMeans(means, stds, pixels, nonzero)

    @staticmethod
    def countNonZero(image):
        # https://stackoverflow.com/a/55163686/1497139
        b = image[:, :, 0]
        g = image[:, :, 1]
        r = image[:, :, 2]
        h, w = image.shape[:2]
        pixels = h * w
        nonzerotupel = cv2.countNonZero(b), cv2.countNonZero(g), cv2.countNonZero(r)
        nonzero = max(nonzerotupel)
        return pixels, nonzero

    def __str__(self):
        b, g, r = self.color
        bs, gs, rs = self.stds
        s = "%3d, %3d, %3d ± %3d, %3d, %3d " % (b, g, r, bs, gs, rs)
        return s

    def fix(self, value):
        return 0 if value < 0 else 255 if value > 255 else value

    def colorRange(self, rangeFactor):
        b, g, r = self.color
        bs, gs, rs = self.stds
        rf = rangeFactor
        lower = np.array(
            [self.fix(b - bs * rf), self.fix(g - gs * rf), self.fix(r - rs * rf)],
            dtype="uint8",
        )
        upper = np.array(
            [self.fix(b + bs * rf), self.fix(g + gs * rf), self.fix(r + rs * rf)],
            dtype="uint8",
        )
        return lower, upper

    def fixMeans(self, means, stds, pixels, nonzero):
        """fix the zero based means to nonzero based see https://stackoverflow.com/a/58891531/1497139"""
        gmean, bmean, rmean = means.flatten()
        gstds, bstds, rstds = stds.flatten()
        if Color.debug:
            print("means %.2f %.2f %.2f " % (gmean, bmean, rmean))
            print("stds  %.2f %.2f %.2f " % (gstds, bstds, rstds))
        factor = pixels / nonzero
        fgmean = gmean * factor
        fbmean = bmean * factor
        frmean = rmean * factor
        if Color.debug:
            print("non-zero means %.2f %.2f %.2f" % (fgmean, fbmean, frmean))
        fsqsumb = (bstds * bstds + bmean * bmean) * pixels
        fsqsumg = (gstds * gstds + gmean * gmean) * pixels
        fsqsumr = (rstds * rstds + rmean * rmean) * pixels
        if Color.debug:
            print("fsqsum %.2f %.2f %.2f" % (fsqsumb, fsqsumg, fsqsumr))
        fstdsb = math.sqrt(max(fsqsumb / nonzero - fbmean * fbmean, 0))
        fstdsg = math.sqrt(max(fsqsumg / nonzero - fgmean * fgmean, 0))
        fstdsr = math.sqrt(max(fsqsumr / nonzero - frmean * frmean, 0))
        if Color.debug:
            print("non-zero stds %.2f %.2f %.2f" % (fstdsb, fstdsg, fstdsr))
        fixedmeans = fgmean, fbmean, frmean
        fixedstds = fstdsb, fstdsg, fstdsr
        return fixedmeans, fixedstds


class SquareChange:
    """keep track of changes of a square over time"""

    meanFrameCount = 10
    treshold = 0.2

    def __init__(self, value, stats):
        """construct me from the given value with the given running stats"""
        self.value = value
        self.mean = stats.mean()
        self.diff = value - self.mean
        self.variance = stats.variance()
        if stats.n < SquareChange.meanFrameCount:
            stats.push(value)
            self.valid = False
            self.diff = 0
        else:
            self.valid = abs(self.diff) < SquareChange.treshold

    def push(self, stats, value):
        if self.valid:
            stats.push(value)


@implementer(ISquare)
class ChessTSquare:
    """a chess square in it's trapezoidal perspective"""

    # relative position and size of original square
    rw = 1 / (ChessTrapezoid.rows)
    rh = 1 / (ChessTrapezoid.cols)

    showDebugChange = []

    def __init__(self, trapez, square):
        """construct me from the given trapez  and square"""
        self.trapez = trapez
        self.changeStats = MinMaxStats()
        self.square = square
        self.an = chess.SQUARE_NAMES[square]
        # rank are rows in Algebraic Notation from 1 to 8
        self.row = ChessTrapezoid.rows - 1 - chess.square_rank(square)
        # files are columns in Algebraic Notation from A to H
        self.col = chess.square_file(square)
        # https://gamedev.stackexchange.com/a/44998/133453
        self.fieldColor = chess.WHITE if (self.col + self.row) % 2 == 1 else chess.BLACK
        self.fieldState = None
        self.piece = None
        self.preMoveImage = None
        self.postMoveImage = None

        self.rPieceRadius = ChessTSquare.rw / ChessTrapezoid.PieceRadiusFactor

        self.rx, self.ry = self.col * ChessTSquare.rw, self.row * ChessTSquare.rh
        self.rcx = self.rx + ChessTSquare.rw * 0.5
        self.rcy = self.ry + ChessTSquare.rh * 0.5
        self.x, self.y = trapez.relativeToTrapezXY(self.rx, self.ry)
        self.setPolygons(
            trapez,
            self.rx,
            self.ry,
            self.rx + ChessTSquare.rw,
            self.ry,
            self.rx + ChessTSquare.rw,
            self.ry + ChessTSquare.rh,
            self.rx,
            self.ry + ChessTSquare.rh,
        )

    def setPolygons(
        self, trapez, rtl_x, rtl_y, rtr_x, rtr_y, rbr_x, rbr_y, rbl_x, rbl_y
    ):
        """set my relative and warped polygons from the given relative corner coordinates from top left via top right, bottom right to bottom left"""
        self.rpolygon = np.array(
            [(rtl_x, rtl_y), (rtr_x, rtr_y), (rbr_x, rbr_y), (rbl_x, rbl_y)]
        )
        self.idealPolygon = (self.rpolygon * trapez.idealSize).astype(np.int32)
        # function to use to calculate polygon
        r2t = trapez.relativeToTrapezXY
        self.polygon = np.array(
            [r2t(rtl_x, rtl_y), r2t(rtr_x, rtr_y), r2t(rbr_x, rbr_y), r2t(rbl_x, rbl_y)]
        )
        self.ipolygon = self.polygon.astype(np.int32)

    def getPolygon(self, transformation):
        if transformation == Transformation.ORIGINAL:
            return self.ipolygon
        elif transformation == Transformation.RELATIVE:
            return self.rpolygon
        elif transformation == Transformation.IDEAL:
            return self.idealPolygon
        else:
            raise Exception("invalid transformation %d for getPolygon", transformation)

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

    def drawState(self, image, transformation, channels):
        """draw my state onto the given image with the given transformation and number of channels"""
        # default is drawing a single channel mask
        squareImageColor = 64
        pieceImageColor = squareImageColor
        if channels == 3:
            if self.fieldColor == chess.WHITE:
                if FieldState.WHITE_EMPTY in self.trapez.averageColors:
                    squareImageColor = self.trapez.averageColors[
                        FieldState.WHITE_EMPTY
                    ].color
                else:
                    squareImageColor = Color.white
            else:
                if FieldState.BLACK_EMPTY in self.trapez.averageColors:
                    squareImageColor = self.trapez.averageColors[
                        FieldState.BLACK_EMPTY
                    ].color
                else:
                    squareImageColor = Color.black

        if not (channels == 1 and self.piece is not None):
            self.trapez.video.drawPolygon(
                image, self.getPolygon(transformation), squareImageColor
            )

        if self.piece is not None:
            if channels == 3:
                if self.fieldState in self.trapez.averageColors:
                    pieceImageColor = self.trapez.averageColors[self.fieldState].color
                else:
                    pieceImageColor = (
                        Color.darkgrey
                        if self.piece.color == chess.BLACK
                        else Color.lightgrey
                    )
            rcenter = self.rcenter()
            self.trapez.drawRCircle(image, rcenter, self.rPieceRadius, pieceImageColor)

    def rcenter(self):
        rcx = self.rx + ChessTSquare.rw / 2
        rcy = self.ry + ChessTSquare.rh / 2
        return (rcx, rcy)

    def rxy2xy(self, image):
        h, w = image.shape[:2]
        x = int(self.rx * w)
        y = int(self.ry * h)
        dh = h // ChessTrapezoid.rows
        dw = w // ChessTrapezoid.cols
        return h, w, x, y, dh, dw

    def addPreMoveImage(self, image):
        if self.preMoveImage is not None:
            h, w, x, y, dh, dw = self.rxy2xy(image)
            np.copyto(image[y : y + dh, x : x + dw], self.preMoveImage)

    def drawDebug(self, image, color=(255, 255, 255)):
        """draw debug information onto the given image using the given color"""
        symbol = ""
        if self.piece is not None:
            symbol = (
                self.piece.symbol()
            )  # @TODO piece.unicode_symbol() - needs other font!
        squareHint = self.an + " " + symbol
        rcx, rcy = self.rcenter()
        self.trapez.drawRCenteredText(image, squareHint, rcx, rcy, color=color)

    def getSquareImage(self, cbImage):
        """get the image of me within the given image"""
        h, w, x, y, dh, dw = self.rxy2xy(cbImage.image)
        squareImage = cbImage.image[y : y + dh, x : x + dw]
        return squareImage

    def squareChange(self, image, diffImage):
        """check the changes analyzing the difference image of this square"""
        h, w, x, y, dh, dw = self.rxy2xy(image)

        self.squareImage = image[y : y + dh, x : x + dw]
        self.diffImage = diffImage[y : y + dh, x : x + dw]
        diffSum = np.sum(self.diffImage)
        # the value is 64 times lower then the per pixel value
        self.currentChange = SquareChange(diffSum / (h * w), self.changeStats)
        return self.currentChange

    def checkMoved(self, detectState):
        """check a figure has been moved, so that the state of this square has changed"""
        squareChange = self.currentChange
        # if the whole board is valid
        if detectState.validBoard:
            # if we come from an stable invalid period then this is likely a move
            if detectState.invalidStable and self.preMoveImage is not None:
                if not squareChange.valid:
                    self.postMoveImage = self.squareImage
                    if detectState.onPieceMoveDetected is not None:
                        detectState.onPieceMoveDetected(self)
                    self.changeStats.clear()
                    self.preMoveImage = None

            detectState.invalidEnd()
            # add the current change statistics to my statistics
            squareChange.push(self.changeStats, squareChange.value)
            # if we have been valid for a long enough period of time
            if detectState.validStable:
                # remember my image - we are ready to detect a move
                self.preMoveImage = self.squareImage
                pass
        else:
            if detectState.invalidStarted:
                detectState.validEnd()
