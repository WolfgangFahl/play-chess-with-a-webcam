#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import cv2
from unittest import TestCase

class OpenCV_VersionTest(TestCase):
    def test_Version(self):
        version = cv2.__version__
        print (version)
        # compare with requirements.txt
        assert version == "4.1.2"