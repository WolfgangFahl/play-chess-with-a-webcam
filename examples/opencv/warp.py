#!/usr/bin/python
# -*- encoding: utf-8 -*-
# see https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
import sys
import cv2
from scipy.spatial import distance as dist
import numpy as np
# top left 437,328
# top right 1390,1042
# bottom left 142,107
# bottom right 1667,1250


def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def main(argv):
    default_file = '../../testMedia/chessBoard010.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv2.imread(filename)
    # load the image, clone it, and initialize the 4 points
    # that correspond to the 4 corners of the chessboard
    pts = np.array([(432, 103), (1380, 94), (1659, 1029), (138, 1052)])

    # loop over the points and draw them on the image
    for (x, y) in pts:
       cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

    # apply the four point tranform to obtain a "birds eye view" of
    # the chessboard
    warped = four_point_transform(image, pts)
    image = cv2.resize(image, (960, 540))

    # show the original and warped images
    cv2.imshow("Original", image)
    height, width = warped.shape[:2]
    warped = cv2.resize(warped, (width // 2, height // 2))
    cv2.imshow("Warped", warped)
    # refresh
    while not cv2.waitKey(10) & 0xFF == ord('q'):
       continue


if __name__ == "__main__":
    main(sys.argv[1:])
