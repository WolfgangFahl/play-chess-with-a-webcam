#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

import cv2


class OpenCV_VersionTest(TestCase):
    """
    test the OpenCV Version being used
    """

    def test_Version(self):
        version = cv2.__version__
        print(version)
        # compare with pyproject.toml
        assert version == "4.10.0"
