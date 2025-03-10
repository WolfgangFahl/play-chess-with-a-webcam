"""
Created on 2019-12-29

@author: wf
"""

import getpass

from pcwawc.environment4test import Environment4Test

# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.videoanalyze import VideoAnalyzer

testEnv = Environment4Test()

from unittest import TestCase


class VideoAnalyzerTest(TestCase):
    def test_videoanalyzer(self):
        if getpass.getuser() == "wf2":
            argv = [
                "--input",
                "/Users/wf/Documents/py-workspace/BobbyFischerVsDonaldByrne.mkv",
                "--autowarp",
                "--debug",
                "--startframe",
                "2250",
                "--speedup",
                "5",
            ]
        else:
            testVideo = "scholarsMate2019-12-18.avi"
            path = testEnv.testMedia + testVideo
            # argv=["--input",path,"--nowarp","--nomove"]
            argv = ["--input", path, "--nowarp", "--debug"]
        videoAnalyzer = VideoAnalyzer.fromArgs(argv)
        pgn = videoAnalyzer.analyze()
        # print (pgn)
        assert "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0" in pgn
