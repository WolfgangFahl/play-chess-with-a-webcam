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
        
    def plot3Channels(self,img,rows,plotNum,c1title,c2title,c3title):        
        self.plotChannel(img, 0, 1, rows, plotNum+1, c1title)
        plt.subplots_adjust(hspace=.7)
        self.plotChannel(img, 1, 1, rows, plotNum+2, c2title)
        self.plotChannel(img, 2, 1, rows, plotNum+3, c3title)
                
    def show(self,waitTime,close=False):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        plt.figure(figsize=(10, 8))
        localTitle='Histogram for %s' % (self.title)
        plt.suptitle(localTitle, fontsize=16)
        self.plot3Channels(hsv,6,0,'Hue','Saturation','Luminosity Value')
        self.plot3Channels(self.image,6,3,'Blue','Green','Red')
        fig = plt.figure(1)
        fig.canvas.set_window_title(localTitle)
        plt.show(block=False)
        plt.savefig('/tmp/'+self.title)
        if Histogram.debug:
            self.video.showImage(self.image,self.title,keyCheck=True,keyWait=waitTime)
        self.video.close()
            
