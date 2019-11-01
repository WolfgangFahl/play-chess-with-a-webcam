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
    def __init__(self,image,title):
        
        self.image=image
        self.title=title
        self.thumbNail = cv2.resize(image, (512, 512))
        self.rows=8
        self.cols=1
        self.plt=None
        
    def A4(self):
        # A4 canvas
        fig_width_cm = 21                                # A4 page
        fig_height_cm = 29.7
        inches_per_cm = 1 / 2.54                         # Convert cm to inches
        fig_width = fig_width_cm * inches_per_cm         # width in inches
        fig_height = fig_height_cm * inches_per_cm       # height in inches
        fig_size = [fig_width, fig_height]   
        return fig_size
            
    def plotChannel(self,img, channel, plotNum, title):
        cImg = img[:, :, channel]
        plt.subplot(self.rows, self.cols, plotNum)
        plt.hist(np.ndarray.flatten(cImg), bins=256)
        plt.title(title)
        
    def plot3Channels(self,img,plotNum,c1title,c2title,c3title):        
        self.plotChannel(img, 0, plotNum+1, c1title)
        plt.subplots_adjust(hspace=0.5)
        self.plotChannel(img, 1, plotNum+2, c2title)
        self.plotChannel(img, 2, plotNum+3, c3title)
                
    def createPlot(self):
        # only create once
        if self.plt is not None:
            return
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        plt.figure(figsize=self.A4())
        localTitle='Histogram for %s' % (self.title)
        plt.suptitle(localTitle, fontsize=16)
        # in the first cell draws the target image
        plt.subplot(self.rows, self.cols, 1)
        plt.imshow(self.thumbNail)
        plt.title('image')
        self.plot3Channels(hsv,1,'Hue','Saturation','Luminosity Value')
        self.plot3Channels(self.image,4,'Blue','Green','Red')
        self.fig = plt.figure(1)
        self.fig.canvas.set_window_title(localTitle)
        self.plt=plt
        
    def close(self):    
        self.plt.close(self.fig)
     
    def show(self,block=False):  
        self.createPlot() 
        self.plt.show(block=block)
     
    def save(self,path,withShow=False,block=False,keyWait=500):
        self.createPlot()
        self.show(block=block)    
        self.plt.savefig(path)
        self.close()
        
            
