#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import getpass
import math
import os
from timeit import default_timer as timer

import chess
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

from pcwawc.args import Args
from pcwawc.chessimage import ChessBoardVision
from pcwawc.chesstrapezoid import (
    ChessTrapezoid,
    ChessTSquare,
    Color,
    FieldState,
    SquareChange,
)
from pcwawc.detectstate import DetectColorState, DetectState
from pcwawc.environment4test import Environment4Test
from pcwawc.video import Video

testEnv = Environment4Test()
speedup = 5  # times
waitAtEnd = 0  # msecs
debug = False
debugPlotHistory = False
displayDebug = True

from unittest import TestCase


class ExampleVideo:
    """an example video to be used in tests"""

    def __init__(
        self, frames, totalFrames, path, points, rotation=270, idealSize=800, ans=None
    ):
        self.path = path
        self.title = Video.title(path)
        self.frames = frames
        self.totalFrames = (totalFrames,)
        self.points = points
        self.rotation = rotation
        self.idealSize = idealSize
        self.ans = ans

    def setup(self):
        self.trapezoid = ChessTrapezoid(
            self.points, rotation=self.rotation, idealSize=self.idealSize
        )
        if self.ans is None:
            self.ans = []
            for tsquare in self.trapezoid.genSquares():
                self.ans.append(tsquare.an)
        return self


class ChessTrapezoidTest(TestCase):
    """
    test the chess Trapezoid
    """

    def test_RankAndFile(self):
        csquare = ChessTrapezoid([(0, 0), (100, 0), (100, 100), (0, 100)])
        for tsquare in csquare.genSquares():
            assert (
                tsquare.an
                == chess.FILE_NAMES[tsquare.col] + chess.RANK_NAMES[7 - tsquare.row]
            )

    def test_Rotation(self):
        csquare = ChessTrapezoid([(0, 0), (100, 0), (100, 100), (0, 100)])
        rotations = [0, 90, 180, 270]
        indices = [(0, 0), (7, 0), (7, 7), (0, 7)]
        expected = [
            (0, 0),
            (7, 0),
            (7, 7),
            (0, 7),
            (7, 0),
            (7, 7),
            (0, 7),
            (0, 0),
            (7, 7),
            (0, 7),
            (0, 0),
            (7, 0),
            (0, 7),
            (0, 0),
            (7, 0),
            (7, 7),
        ]
        index = 0
        for rotation in rotations:
            csquare.rotation = rotation
            anstr = ""
            for row in range(ChessTrapezoid.rows):
                for col in range(ChessTrapezoid.cols):
                    tsquare = csquare.tSquareAt(row, col)
                    anstr = anstr + tsquare.an
                anstr = anstr + "\n"
            print(anstr)
            for rowcol in indices:
                row, col = rowcol
                rotated = csquare.rotateIndices(row, col, rotation)
                print(rotation, rowcol, rotated, expected[index])
                assert rotated == expected[index]
                index = index + 1

    def test_Transform(self):
        trapez = ChessTrapezoid([(20, 40), (44, 38), (60, 8), (10, 10)])
        # if debug:
        #    plt.figure()
        #    plt.plot(trapez.pts_normedSquare[[0,1,2,3,0], 0],trapez.pts_normedSquare[[0,1,2,3,0], 1], '-')
        squarePatches = []
        tSquarePatches = []
        # https://stackoverflow.com/questions/26935701/ploting-filled-polygons-in-python
        for tsquare in trapez.genSquares():
            color = [1, 1, 1, 1] if tsquare.fieldColor else [0.1, 0.1, 0.1, 1]
            polygon = Polygon(tsquare.rpolygon, color=color)
            tpolygon = Polygon(tsquare.polygon, color=color)
            squarePatches.append(polygon)
            tSquarePatches.append(tpolygon)
        # https://stackoverflow.com/questions/44725201/set-polygon-colors-matplotlib
        squareP = PatchCollection(squarePatches, match_original=True)
        tSquareP = PatchCollection(tSquarePatches, match_original=True)

        if debug:
            fig, ax = plt.subplots(2)
            ax1 = ax[0]
            ax1.set_title("relative normed square")
            ax1.add_collection(squareP)
            ax1.set_ylim(ax1.get_ylim()[::-1])
            ax2 = ax[1]

            ax2.set_title("trapezoidal warp")
            ax2.add_collection(tSquareP)
            ax2.autoscale()
            plt.show()

    def test_RelativeToTrapezXY(self):
        trapez = ChessTrapezoid([(20, 40), (40, 40), (60, 10), (10, 10)])
        rxrys = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0.5), (0.5, 0.5), (1, 0.5)]
        expected = [
            (20, 40),
            (40, 40),
            (60, 10),
            (10, 10),
            (17.1, 31.4),
            (31.4, 31.4),
            (45.7, 31.4),
        ]
        for index, rxry in enumerate(rxrys):
            rx, ry = rxry
            x, y = trapez.relativeToTrapezXY(rx, ry)
            ex, ey = expected[index]
            print(
                "%d r:(%.1f,%.1f) e:(%.1f,%.1f) == (%.1f,%.1f)?"
                % (index, rx, ry, ex, ey, x, y)
            )
            assert x == pytest.approx(ex, 0.1)
            assert y == pytest.approx(ey, 0.1)

    def test_SortedTSquares(self):
        trapezoid = ChessTrapezoid([(140, 5), (506, 10), (507, 377), (137, 374)])
        trapezoid.updatePieces(chess.STARTING_FEN)
        sortedTSquares = trapezoid.byFieldState()
        expected = [16, 8, 8, 16, 8, 8]
        for fieldState, tsquareList in sortedTSquares.items():
            l = len(tsquareList)
            if debug:
                print(fieldState.title(), l)
            assert expected[fieldState] == l

    def test_Stats(self):
        h = 2
        w = 2
        channels = 3

        image = np.zeros((h, w, channels), np.uint8)
        image[0, 0] = (100, 50, 200)
        image[0, 1] = (120, 60, 220)
        avgcolor = Color(image)
        gmean, bmean, rmean = avgcolor.color
        gstds, bstds, rstds = avgcolor.stds
        if debug:
            print("means %.2f %.2f %.2f " % (gmean, bmean, rmean))
            print("stds  %.2f %.2f %.2f " % (gstds, bstds, rstds))
        assert avgcolor.color == (110.00, 55.00, 210.00)
        assert avgcolor.stds == (5.00, 10.00, 10.00)

    def test_ColorDistribution(self):
        imgPath = "/tmp/"
        for imageInfo in testEnv.imageInfos:
            fen = imageInfo.fen
            if not fen == chess.STARTING_BOARD_FEN:
                continue
            start = timer()
            image, video, warp = testEnv.prepareFromImageInfo(imageInfo)
            title = imageInfo.title
            trapez = ChessTrapezoid(
                warp.pointList, rotation=warp.rotation, idealSize=800
            )
            warped = trapez.warpedBoardImage(image)
            end = timer()
            video.writeImage(warped.image, imgPath + title + "-warped.jpg")
            # startd = timer()
            # denoised=video.getEmptyImage(warped, 3)
            # cv2.fastNlMeansDenoisingColored(warped,denoised)
            # endd = timer()
            # print("%.3fs for loading %.3fs for denoising image %s: %4d x %4d" % ((end-start),(endd-startd),title,width,height))
            # video.writeImage(denoised,imgPath+title+"-denoised.jpg")
            print(
                "%.3fs for loading image %s: %4d x %4d"
                % ((end - start), title, warped.width, warped.height)
            )

            trapez.updatePieces(fen)
            # ChessTrapezoid.colorDebug=True
            averageColors = trapez.analyzeColors(warped)
            startc = timer()
            fcs = trapez.optimizeColorCheck(warped, averageColors)
            endc = timer()
            fcs.showStatsDebug(endc - startc)
            idealImage = trapez.idealColoredBoard(warped.width, warped.height)
            diffImage = warped.diffBoardImage(idealImage)
            for tSquare in trapez.genSquares():
                percent = "%.0f" % (fcs.colorPercent[tSquare.an])
                trapez.drawRCenteredText(
                    diffImage.image, percent, tSquare.rcx, tSquare.rcy, (0, 255, 0)
                )
            # video.showImage(warped,title,keyWait=15000)
            video.writeImage(diffImage.image, imgPath + title + "-colors.jpg")

    def onPieceMoveDetected(self, tSquare):
        print("pieced %s moved: %s" % (tSquare.an, vars(tSquare.currentChange)))
        if tSquare.an in ChessTSquare.showDebugChange:
            tSquare.trapez.video.showImage(tSquare.preMoveImage, tSquare.an + " pre")
            tSquare.trapez.video.showImage(tSquare.postMoveImage, tSquare.an + " post")

    def test_ChessTrapezoid(self):
        # ans=["e2","e4","e7","e5","d1","h5","b8","c6","f1","c4","c8","f6","f7","a1","h8"]
        tk = testEnv.testMedia + "../../Chess-Testmedia/"
        videos = testEnv.testMedia + "../games/videos/"
        testVideos = [
            ExampleVideo(
                1000,
                10000,
                1,
                [[427, 44], [1425, 52], [1406, 1023], [431, 1029]],
                270,
                ans=["e2", "e4"],
            ),
            ExampleVideo(
                334,
                334,
                testEnv.testMedia + "scholarsmate.avi",
                [(140, 5), (506, 10), (507, 377), (137, 374)],
                270,
                ans=None,
            ),  # ans=["e2","e4"]),
            ExampleVideo(
                75,
                503,
                testEnv.testMedia + "scholarsMate2019-11-18.avi",
                [[0, 0], [611, 0], [611, 611], [0, 611]],
                0,
                ans=["e2", "e4"],
            ),
            ExampleVideo(
                300,
                5000,
                "/Users/wf/source/python/play-chess-with-a-webcam/media/chessVideo2019-10-17_185821.avi",
                [(210, 0), (603, 6), (581, 391), (208, 378)],
                rotation=270,
            ),
            ExampleVideo(
                240,
                240,
                "/Users/wf/Documents/pyworkspace/PlayChessWithAWebCam/scholarsMate2019-11-17.avi",
                [],
                270,
            ),
            ExampleVideo(
                165,
                438,
                tk + "TK_scholarsmate4.avi",
                [[147, 129], [405, 123], [418, 385], [148, 390]],
                0,
                ans=None,
            ),  # ["e2","e4","e7","e5"]),
            ExampleVideo(
                250,
                1392,
                tk + "TK_scholarsmate7.avi",
                [[0, 0], [404, 0], [404, 404], [0, 404]],
                0,
                ans=None,
            ),  # ["e2","e4","e7","e5"]),
            ExampleVideo(
                62,
                91,
                videos + "chessgame_2019-11-19_203104.avi",
                [[0, 0], [618, 0], [618, 618], [0, 618]],
                0,
                ans=None,
            ),  # ["e2","e4","e7","e5"])
            ExampleVideo(
                45,
                45,
                videos + "chessgame_2019-11-23_133629.avi",
                [[0, 0], [607, 0], [607, 607], [0, 607]],
                0,
                ans=None,
            ),  # ["e2","e4"])
            ExampleVideo(
                244,
                244,
                videos + "chessgame_2019-11-26_145653.avi",
                [[0, 0], [925, 0], [925, 925], [0, 925]],
                0,
                ans=None,
            ),  # ["e2","e4"])
            ExampleVideo(
                250,
                250,
                videos + "chessgame_2019-11-28_172745.avi",
                [[0, 0], [983, 0], [983, 983], [0, 983]],
                0,
                ans=None,
            ),  # ["e2","e4"])
        ]
        # select a testVideo
        if getpass.getuser() == "travis":
            testVideo = testVideos[1]
            debugMoveDetected = False
            debugChangeHistory = False
        else:
            testVideo = testVideos[1]
            # debugMoveDetected=False
            # debugChangeHistory=False
            # testVideo=testVideos[10]
            debugChangeHistory = False
            debugMoveDetected = False
            ChessTrapezoid.debug = False

        trapezoid = testVideo.setup().trapezoid
        frames = testVideo.frames
        # SquareChange.meanFrameCount=12
        SquareChange.treshold = 0.1
        detectState = DetectState(
            validDiffSumTreshold=1.4,
            invalidDiffSumTreshold=4.8,
            diffSumDeltaTreshold=0.2,
        )
        detectColorState = DetectColorState(trapezoid)
        if debugMoveDetected:
            detectState.onPieceMoveDetected = self.onPieceMoveDetected
        ChessTSquare.showDebugChange = ["e2", "e4", "e7", "e5"]
        args = Args("test")
        args.parse(["--input", testVideo.title])
        vision = ChessBoardVision(args.args)
        vision.open(testVideo.path)
        start = timer()
        colorHistory = {}
        changeHistory = {}
        while True:
            cbImageSet = vision.readChessBoardImage()
            if not vision.hasImage:
                break
            frame = cbImageSet.frameIndex - 1
            if frame == 0:
                # trapezoid.prepareMask(bgr)
                # trapezoid.maskPolygon(trapezoid.polygon)
                trapezoid.updatePieces(chess.STARTING_BOARD_FEN)
            startc = timer()
            averageColors = trapezoid.prepareImageSet(cbImageSet)
            squareChanges = trapezoid.detectChanges(cbImageSet, detectState)
            changeHistory[frame] = squareChanges
            # diffSum=trapezoid.diffSum(warped,idealImage)
            endc = timer()
            cbImage = cbImageSet.cbImage
            cbWarped = cbImageSet.cbWarped
            print(
                "%dx%d frame %5d in %.3f s with %2d ✅ %5.1f Δ %5.1f ΣΔ %4d ✅/%4d ❌"
                % (
                    cbImage.width,
                    cbImage.height,
                    frame,
                    endc - startc,
                    squareChanges["valid"],
                    squareChanges["diffSum"],
                    squareChanges["diffSumDelta"],
                    squareChanges["validFrames"],
                    squareChanges["invalidFrames"],
                )
            )
            detectColorState.check(cbWarped, averageColors, drawDebug=True)
            colorHistory[frame] = trapezoid.averageColors.copy()

            if frame % speedup == 0:
                if displayDebug:
                    trapezoid.drawDebug(cbImageSet.cbDiff.image)
                    cbImageSet.showDebug(video=vision.video)

        end = timer()
        print(
            "read %3d frames in %.3f s at %.0f fps"
            % (frames, end - start, (frames / (end - start)))
        )
        if debugChangeHistory:
            self.plotChangeHistory(
                changeHistory, testVideo, "square changes over time", detectState
            )
        if debugPlotHistory:
            self.plotColorHistory(colorHistory)
        if waitAtEnd > 0:
            cbWarped.showDebug(video=vision.video, keyWait=waitAtEnd)

    def plotChangeHistory(self, changeHistory, testVideo, title, detectState):
        # plot=PlotLib("Move Detection",PlotLib.A4(turned=True))
        basename = os.path.basename(testVideo.path).replace(".avi", "")
        ans = testVideo.ans
        # pdf=plot.startPDF("/tmp/"+basename+".pdf")
        """ plot the changeHistory for the field with the given algebraic notations"""
        l = len(changeHistory)
        anIndex = 0
        # fig,axes=plt.subplots(7,figsize=plot.pagesize)
        fig, axes = plt.subplots(7)
        ax0 = axes[0]
        ax0.set_title("value")
        ax1 = axes[1]
        ax1.set_title("mean")
        ax2 = axes[2]
        ax2.set_title("diff")
        ax3 = axes[3]
        ax3.set_title("validdiff")
        ax4 = axes[4]
        ax4.set_title("detected")
        ax5 = axes[5]
        ax5.set_title("diffsum")
        ax6 = axes[6]
        ax6.set_title("diffsumdelta")
        for an in ans:
            x = np.empty(l)
            value = np.empty(l)
            mean = np.empty(l)
            stdv = np.empty(l)
            diff = np.empty(l)
            validdiff = np.empty(l)
            detected = np.empty(l)
            diffSum = np.empty(l)
            diffSumDelta = np.empty(l)
            found = False
            detectedFound = False
            for frame, changes in changeHistory.items():
                x[frame] = frame
                squareChange = changes[an]
                value[frame] = squareChange.value
                mean[frame] = squareChange.mean
                stdv[frame] = math.sqrt(squareChange.variance)
                diff[frame] = squareChange.diff
                diffSum[frame] = changes["diffSum"]
                validdiff[frame] = (
                    0
                    if diffSum[frame] > detectState.validDiffSumTreshold
                    else squareChange.diff
                )
                detected[frame] = squareChange.diff if changes["validBoard"] else 0
                if validdiff[frame] > squareChange.treshold * 1.5:
                    found = True
                if detected[frame] > squareChange.treshold * 1.5:
                    detectedFound = True
            ax0.plot(x, value, label=an)
            ax1.plot(x, mean, label=an)
            ax2.plot(x, diff, label=an)
            if found:
                ax3.plot(x, validdiff, label=an)
            else:
                ax3.plot(x, validdiff)
            if detectedFound:
                ax4.plot(x, detected, label=an)
            else:
                ax4.plot(x, detected)
            anIndex += 1
        for frame, changes in changeHistory.items():
            x[frame] = frame
            diffSum[frame] = changes["diffSum"]
            delta = changes["diffSumDelta"]
            diffSumDelta[frame] = delta if abs(delta) < 2 else 0
        ax5.plot(x, diffSum, label="diffSum")
        ax6.plot(x, diffSumDelta)
        if len(ans) < 10:
            ax0.legend(loc="upper right")
            ax1.legend(loc="upper right")
            ax2.legend(loc="upper right")
        ax3.legend(loc="upper right")
        ax4.legend(loc="upper right")

        plt.title(title)
        plt.legend()
        plt.show()
        # plot.finishPDFPage(pdf)
        # plot.finishPDF(pdf, infos={'Title': 'Chessboard Movement Detection'})

    def plotColorHistory(self, colorHistory):
        l = len(colorHistory)
        print("color  history for %d frames" % (l))
        # fig,ax=plt.subplots(len(FieldState))
        markers = ["s", "o", "v", "^", "<", ">"]
        dist = 10
        for fieldState in FieldState:
            size = l // dist
            x = np.empty(size)
            r = np.empty(size)
            g = np.empty(size)
            b = np.empty(size)
            for frame, avgColors in colorHistory.items():
                avgColor = avgColors[fieldState]
                if frame % dist == 0:
                    index = frame // dist
                    if index < size:
                        x[index] = frame
                        b[index], g[index], r[index] = avgColor.color
            # ax[fieldState].set_title(fieldState.title())
            plt.plot(x, r, c="r", marker=markers[fieldState])
            plt.plot(x, g, c="g", marker=markers[fieldState])
            plt.plot(x, b, c="b", marker=markers[fieldState], label=fieldState.title())
            # ax[fieldState].autoscale()
        plt.legend()
        plt.show()
