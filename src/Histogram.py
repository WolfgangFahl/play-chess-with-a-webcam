#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see:
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
# https://giusedroid.blogspot.com/2015/04/using-python-and-k-means-in-hsv-color.html

import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

class Histogram:
    debug=True
    
    # construct me 
    def __init__(self,title,rows=1,turned=False,pages=1): 
        self.title=title
        self.rows=rows*2
        self.row=0
        self.cols=5
        self.plt=plt
        self.setUpSubPlots(turned,pages)
     
    def setUpSubPlots(self,turned,pages):
        self.fig,self.axes=plt.subplots(nrows=self.rows,ncols=self.cols,figsize=self.A4(turned,pages))
        cols=['image','','h/b','s/g','v/r']
        rowdict={}
        for row in range(self.rows):
            if row%2==0:             
                rowdict[row]=str(row//2)
            else:
                rowdict[row]='' 
        rows=list(rowdict)        
        for ax, col in zip(self.axes[0], cols):
            ax.set_title(col)
        for ax, row in zip(self.axes[:,0], rows):
            ax.set_ylabel(row, rotation=0, size='large')    
        plt.subplots_adjust(hspace=0.5)
        self.gs = gridspec.GridSpec(self.rows,self.cols)    
        
    def A4(self,turned=False,pages=1):
        # A4 canvas
        fig_width_cm =21                                 # A4 page
        fig_height_cm = 29.7
        if turned:
            fw=fig_height_cm
            fh=fig_width_cm
            fig_height_cm=fh
            fig_width_cm=fw
            
        inches_per_cm = 1 / 2.54                          # Convert cm to inches
        fig_width = fig_width_cm * inches_per_cm          # width in inches
        fig_height = fig_height_cm * inches_per_cm*pages  # height in inches
        fig_size = [fig_width, fig_height]   
        return fig_size
            
    def plotChannel(self,img, channel, row,col):
        cImg = img[:, :, channel]
        plt.subplot(self.gs[row,col])
        plt.hist(np.ndarray.flatten(cImg), bins=256)
        
    def plot3Channels(self,img,row,startCol):        
        self.plotChannel(img, 0, row,startCol+0)
        self.plotChannel(img, 1, row,startCol+1)
        self.plotChannel(img, 2, row,startCol+2)
                
    def addPlot(self,image,localTitle):
        thumbNail = cv2.resize(image, (512, 512))
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        plt.suptitle(localTitle, fontsize=16)
        # in the first cell draws the target image
        plt.subplot(self.gs[self.row:self.row+1,0:1])
        plt.imshow(thumbNail)
        plt.title('image')
       
        self.plot3Channels(hsv  ,self.row  ,2)
        self.plot3Channels(image,self.row+1,2)
        self.row=self.row+2
        
    def close(self):    
        if self.plt is not None and self.fig is not None:
            plt.close(self.fig)
     
    def show(self,block=False):  
        canvasfig = plt.figure(1)
        canvasfig.canvas.set_window_title(self.title)
        plt.show(block=block)
     
    def save(self,path,block=False,keyWait=5):
        self.fig.tight_layout()
        self.show(block=block)    
        self.plt.savefig(path)
        cv2.waitKey(keyWait)
        self.close()
