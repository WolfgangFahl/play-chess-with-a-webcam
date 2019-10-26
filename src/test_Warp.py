# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
from Video import Video
import numpy as np
import cv2

def test_Warp():
    video=Video()
    image=video.readImage("testMedia/chessBoard010.jpg")
    # load the image, clone it, and initialize the 4 points
    # that correspond to the 4 corners of the chessboard
    pts = np.array([(432,103), (1380, 94), (1659, 1029), (138, 1052)])

    # apply the four point tranform to obtain a "birds eye view" of
    # the chessboard
    warped=video.warp(image,pts)
    image = cv2.resize(image,(960,540))
    height, width = warped.shape[:2]
    print ("%d x %d " % (width,height))
    # show the original and warped images
    cv2.imshow("Original", image)
    cv2.imshow("Warped", warped)
    assert width==993
    assert height==993
    cv2.waitKey(1000)

test_Warp()
