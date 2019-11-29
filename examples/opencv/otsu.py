#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
'''
Created on 2019-11-29

@author: wf

see https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html

'''
import sys
import cv2 as cv
from matplotlib import pyplot as plt
from timeit import default_timer as timer

def main(argv):
    default_file = '../../testMedia/chessBoard012.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv.imread(filename)
    cv.imshow('chessboard', image)
    # refresh
    cv.waitKey(5)
    img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # global thresholding
    start1=timer()
    ret1,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
    end1=timer()
    print ("binary treshold took %.4f s" % (end1-start1))
    # Otsu's thresholding
    start2=timer()
    ret2,th2 = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    end2=timer()
    print ("otsu's treshold took %.4f s" % (end2-start2))
    # Otsu's thresholding after Gaussian filtering
    start3=timer()
    blur = cv.GaussianBlur(img,(5,5),0)
    ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    end3=timer()
    print ("otsu's treshold + gauss took %.4f s" % (end3-start3))
    # plot all the images and their histograms
    images = [img, 0, th1,
              img, 0, th2,
              blur, 0, th3]
    titles = ['Original Noisy Image','Histogram','Global Thresholding (v=127)',
              'Original Noisy Image','Histogram',"Otsu's Thresholding",
              'Gaussian filtered Image','Histogram',"Otsu's Thresholding"]
    for i in range(3):
        plt.subplot(3,3,i*3+1),plt.imshow(images[i*3],'gray')
        plt.title(titles[i*3]), plt.xticks([]), plt.yticks([])
        plt.subplot(3,3,i*3+2),plt.hist(images[i*3].ravel(),256)
        plt.title(titles[i*3+1]), plt.xticks([]), plt.yticks([])
        plt.subplot(3,3,i*3+3),plt.imshow(images[i*3+2],'gray')
        plt.title(titles[i*3+2]), plt.xticks([]), plt.yticks([])
    plt.show()
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])