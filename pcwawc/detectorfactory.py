"""
Created on 2019-12-14

@author: wf
"""

from pcwawc.boarddetector import BoardDetector
from pcwawc.simpledetector import Simple8x8Detector, SimpleDetector


class MoveDetectorFactory:
    detectors = {}

    @staticmethod
    def register(detectorName, detector):
        MoveDetectorFactory.detectors[detectorName] = detector

    """ factory for move detectors"""

    @staticmethod
    def create(detectorname, vision):
        if detectorname in MoveDetectorFactory.detectors:
            moveDetector = MoveDetectorFactory.detectors[detectorname]
            moveDetector.setup(detectorname, vision)
        else:
            raise Exception(
                "MoveDetectorFactory create: unknown detectorname %s" % (detectorname)
            )
        return moveDetector


# MoveDetectorFactory.register("simple", SimpleDetector())
MoveDetectorFactory.register("simple8x8", Simple8x8Detector())
MoveDetectorFactory.register("luminance", BoardDetector())
