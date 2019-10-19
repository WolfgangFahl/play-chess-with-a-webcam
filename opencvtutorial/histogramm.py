# see:
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
# https://giusedroid.blogspot.com/2015/04/using-python-and-k-means-in-hsv-color.html

import cv2
import numpy as np
from matplotlib import pyplot as plt
import sys

def plotChannel(hsv,channel,rows,plotNum,title):
  cImg=hsv[:,:,channel]
  plt.subplot(rows,1,plotNum)
  plt.hist(np.ndarray.flatten(cImg),bins=256)
  plt.title(title)

def main(argv):
    default_file = '../testMedia/chessBoard001.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv2.imread(filename)
    cv2.imshow('chessboard',image)
    hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    plt.figure(figsize=(10,8))
    plotChannel(hsv,0,3,1,'Hue')
    plt.subplots_adjust(hspace=.5)
    plotChannel(hsv,1,3,2,'Saturation')
    plotChannel(hsv,2,3,3,'Luminosity Value')
    plt.show()

    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 27: break             # ESC key to exit
    cv2.destroyAllWindows()
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
