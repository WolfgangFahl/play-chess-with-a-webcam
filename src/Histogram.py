#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see:
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
# https://giusedroid.blogspot.com/2015/04/using-python-and-k-means-in-hsv-color.html

import cv2
import numpy as np
from matplotlib import pyplot as plt

class Histogram:
    debug=True
    
    # construct me 
    def __init__(self,image,video,title):
        self.image=image
        self.video=video
        self.title=title
        
    def plotChannel(self,img, channel, col, rows, plotNum, title):
        cImg = img[:, :, channel]
        plt.subplot(rows, col, plotNum)
        plt.hist(np.ndarray.flatten(cImg), bins=256)
        plt.title(title)    
                
    def show(self,waitTime):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        plt.figure(figsize=(10, 8))
        plt.suptitle('HSV Histogramm', fontsize=16)
        self.plotChannel(hsv, 0, 1, 4, 2, 'Hue')
        plt.subplots_adjust(hspace=.5)
        self.plotChannel(hsv, 1, 1, 4, 3, 'Saturation')
        self.plotChannel(hsv, 2, 1, 4, 4, 'Luminosity Value')
        fig = plt.figure(1)
        fig.canvas.set_window_title('Histogramm for %s' % (self.title))
        plt.show(block=False)
        if Histogram.debug:
            self.video.showImage(self.image,self.title,keyCheck=True,keyWait=waitTime)
        self.video.close()
            
