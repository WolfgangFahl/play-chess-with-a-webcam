# see:
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
# https://giusedroid.blogspot.com/2015/04/using-python-and-k-means-in-hsv-color.html

import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys

def plotChannel(hsv, channel, col, rows, plotNum, title):
    cImg = hsv[:, :, channel]
    plt.subplot(rows, col, plotNum)
    plt.hist(np.ndarray.flatten(cImg), bins=256)
    plt.title(title)

def main(argv):
    default_file = '../../testMedia/chessBoard012.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv2.imread(filename)
    cv2.imshow('chessboard', image)
    # refresh
    cv2.waitKey(10)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    plt.figure(figsize=(10, 8))
    plt.suptitle('HSV Histogramm', fontsize=16)
    plotChannel(hsv, 0, 1, 4, 2, 'Hue')
    plt.subplots_adjust(hspace=.5)
    plotChannel(hsv, 1, 1, 4, 3, 'Saturation')
    plotChannel(hsv, 2, 1, 4, 4, 'Luminosity Value')
    fig = plt.figure(1)
    fig.canvas.set_window_title('Histogramm for %s' % (filename))
    plt.show()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
