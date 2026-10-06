# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from unittest import TestCase

from pcwawc.detectstate import DetectState


class DetectStateTest(TestCase):
    def testDetectState(self):
        detectState = DetectState(
            validDiffSumTreshold=1.4,
            invalidDiffSumTreshold=4.8,
            diffSumDeltaTreshold=0.2,
        )
        values = [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
        ]
        meanFrameCount = 10
        for value in values:
            diffSum, diffSumDelta = value
            detectState.nextFrame()
            detectState.check(64, diffSum, diffSumDelta, meanFrameCount)
        assert detectState.frames == 10
        # print (vars(detectState))
        assert detectState.validFrames == 10

    def testInvalidStable(self):
        """
        invalidStable needs at least meanFrameCount invalid frames
        see https://github.com/WolfgangFahl/play-chess-with-a-webcam/issues/55
        """
        detectState = DetectState(
            validDiffSumTreshold=1.4,
            invalidDiffSumTreshold=4.8,
            diffSumDeltaTreshold=0.2,
        )
        meanFrameCount = 3
        # invalid frames: diffSum above the validDiffSumTreshold
        for frame in range(meanFrameCount):
            detectState.check(64, 10.0, 0, meanFrameCount)
            assert detectState.invalidStable is False
        detectState.check(64, 10.0, 0, meanFrameCount)
        assert detectState.invalidStable is True

    def testOnMoveDetected(self):
        """
        the onMoveDetected callback is stored under its name
        see https://github.com/WolfgangFahl/play-chess-with-a-webcam/issues/56
        """

        def onMoveDetected(move):
            pass

        detectState = DetectState(
            validDiffSumTreshold=1.4,
            invalidDiffSumTreshold=4.8,
            diffSumDeltaTreshold=0.2,
            onMoveDetected=onMoveDetected,
        )
        assert detectState.onMoveDetected is onMoveDetected
