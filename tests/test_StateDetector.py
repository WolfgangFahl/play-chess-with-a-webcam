#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from pcwawc.StateDetector import StateDetector
from pcwawc.StateDetector import  CannotBuildStateException
from pcwawc.Environment4Test import Environment4Test

testEnv = Environment4Test()


# test the StateDetector
def test_StateDetector():
    for index in range(0, 9):
        image = testEnv.getImage(index + 1)
        stateDetector = StateDetector()
        try:
            stateDetector.detectState(image)
        except  CannotBuildStateException as cbse:
            print(cbse)
            pass


test_StateDetector()
