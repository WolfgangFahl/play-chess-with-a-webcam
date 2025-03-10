#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import os
from timeit import default_timer as timer

from pcwawc.args import Args
from pcwawc.board import Board
from pcwawc.chessimage import Warp
from pcwawc.environment import Environment
from pcwawc.video import Video
from pcwawc.videoanalyze import VideoAnalyzer


class ImageInfo:
    """information about a chessboard test image"""

    def __init__(self, index, title, path, fen, rotation, warpPoints):
        """
        constructor
        """
        self.index = index
        self.title = title
        self.path = path
        self.fen = fen
        self.rotation = rotation
        self.warpPoints = warpPoints

    def warpPointsAsString(self):
        return str(self.warpPoints)


class Environment4Test(Environment):
    """Test Environment"""

    warpPointList = [
        ([427, 180], [962, 180], [952, 688], [430, 691]),
        ([288, 76], [1057, 93], [1050, 870], [262, 866]),
        ([132, 89], [492, 90], [497, 451], [122, 462]),
        ([143, 18], [511, 13], [511, 387], [147, 386]),
        ([260, 101], [962, 133], [950, 815], [250, 819]),
        ([250, 108], [960, 135], [947, 819], [242, 828]),
        ([277, 106], [972, 129], [957, 808], [270, 800]),
        ([278, 88], [999, 88], [1072, 808], [124, 786]),
        ([360, 238], [2380, 224], [2385, 2251], [407, 2256]),
        ([483, 132], [1338, 124], [1541, 936], [255, 953]),
        ([8, 1], [813, 1], [817, 812], [3, 809]),
        ([0, 0], [522, 0], [523, 523], [0, 523]),
        ([678, 33], [1582, 33], [1571, 923], [686, 896]),
    ]

    rotations = [0, 0, 0, 0, 270, 270, 270, 0, 0, 0, 0, 0, 270]

    fens = [
        Board.EMPTY_FEN,
        Board.EMPTY_FEN,
        Board.START_FEN,
        Board.EMPTY_FEN,
        Board.START_FEN,
        Board.START_FEN,
        Board.START_FEN,
        Board.EMPTY_FEN,
        Board.EMPTY_FEN,
        Board.EMPTY_FEN,
        Board.EMPTY_FEN,
        Board.START_FEN,
        Board.START_FEN,
    ]

    def __init__(self, headless=None):
        """
        constructor
        """
        super().__init__()
        if headless is None:
            self.headless = Environment.inContinuousIntegration()
        else:
            self.headless = headless
        rlen = len(Environment4Test.rotations)
        wlen = len(Environment4Test.warpPointList)
        fenlen = len(Environment4Test.fens)
        if rlen != wlen:
            raise Exception("%d rotations for %d warpPoints" % (rlen, wlen))
        if fenlen != wlen:
            raise Exception("%d FENs for %d images" % (fenlen, wlen))
        self.imageInfos = []
        for num in range(1, 1000):
            path = self.testMedia + "chessBoard%03d.jpg" % (num)
            if not os.path.isfile(path):
                break
            if num - 1 >= len(Environment4Test.rotations):
                raise Exception(
                    "%d test files for %d warpPoints/rotations" % (num, wlen)
                )
            imageInfo = ImageInfo(
                num,
                title="image%03d" % (num),
                path=path,
                fen=Environment4Test.fens[num - 1],
                rotation=Environment4Test.rotations[num - 1],
                warpPoints=Environment4Test.warpPointList[num - 1],
            )
            self.imageInfos.append(imageInfo)

    def getImage(self, num: int):
        """
        get the image with the given number

        Args:
            num(int): the index of the image
        """
        image, video = self.getImageWithVideo(num)
        if video is None:
            pass
        return image

    def getVideo(self) -> Video:
        """
        get a Video (potentially headless)

        Returns:
            Video: the video handler for openCV
        """
        video = Video()
        video.headless = self.headless
        return video

    def getImageWithVideo(self, num: int):
        """
        get the image and video

        Args:
            num(int): the number of the image

        Returns:
            image: the image
            video: the video display
        """
        video = self.getVideo()
        filename = self.testMedia + "chessBoard%03d.jpg" % (num)
        image = video.readImage(filename)
        height, width = image.shape[:2]
        print("read image %s: %dx%d" % (filename, width, height))
        return image, video

    def prepareFromImageInfo(self, imageInfo):
        """
        prepare a test environment from the given image Inforrmation
        """
        warp = Warp(list(imageInfo.warpPoints))
        warp.rotation = imageInfo.rotation
        image, video = self.getImageWithVideo(imageInfo.index)
        return image, video, warp

    def loadFromImageInfo(self, imageInfo):
        analyzer = self.analyzerFromImageInfo(imageInfo)
        start = timer()
        cbImageSet = analyzer.vision.readChessBoardImage()
        assert analyzer.hasImage()
        analyzer.processImageSet(cbImageSet)
        end = timer()
        cbWarped = cbImageSet.cbWarped
        print(
            "%.3fs for loading image %s: %4d x %4d"
            % ((end - start), imageInfo.title, cbWarped.width, cbWarped.height)
        )
        return cbImageSet.cbWarped

    def analyzerFromImageInfo(self, imageInfo):
        args = Args("test")
        args.parse(
            [
                "--input",
                imageInfo.path,
                "--fen",
                imageInfo.fen,
                "--warp",
                imageInfo.warpPointsAsString(),
            ]
        )
        analyzer = VideoAnalyzer(args.args)
        analyzer.setUpDetector()
        analyzer.setDebug(True)
        analyzer.open()
        return analyzer

    def getTestVideos(self, exclude=["baxter.avi"]):
        for file in os.listdir(self.testMedia):
            if file.endswith(".avi"):
                if file not in exclude:
                    yield file
