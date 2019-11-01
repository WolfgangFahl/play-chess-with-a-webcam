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
from matplotlib.backends.backend_pdf import PdfPages

class Histogram(object):
    '''
    show color channel histograms of images
    '''


    def __init__(self, title, pagesize, imagesPerPage=4):
        '''
        Constructor
        '''
        self.title=title
        self.pagesize=pagesize
        self.pagewidth,self.pageheight=self.pagesize
        self.imagesPerPage=imagesPerPage
        self.images=[]
        
        
    @staticmethod   
    def A4(turned=False):
        # A4 canvas
        fig_width_cm =21                                  # A4 page size in cm
        fig_height_cm = 29.7                             
        inches_per_cm = 1 / 2.54                          # Convert cm to inches
        fig_width = fig_width_cm * inches_per_cm          # width in inches
        fig_height = fig_height_cm * inches_per_cm        # height in inches
        fig_size = [fig_width, fig_height]
        if turned:
            fig_size=fig_size[::-1]
        return fig_size    
        
    def addPlot(self,image,imageTitle):
        self.images.append((image,imageTitle))
        
    def plotImage(self,ax,image,imageTitle,thumbNailSize):
        thumbNail = cv2.resize(image, (thumbNailSize,thumbNailSize))
        th,tw=thumbNail.shape[:2]
        ax.imshow(thumbNail)
        ax.title.set_text(imageTitle)
        ax.axis("off")
        pass
    
    def plotChannel(self,img, ax,channel):
        cImg = img[:, :, channel]
        ax.hist(np.ndarray.flatten(cImg), bins=256)
          
    def plotHistogramm(self,image,axarr,rowIndex):  
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 
        rgb=image
        self.plotChannel(hsv,axarr[rowIndex+0,1], 0) # hue
        self.plotChannel(hsv,axarr[rowIndex+0,2], 1) # saturation
        self.plotChannel(hsv,axarr[rowIndex+0,3], 2) # value
        self.plotChannel(rgb,axarr[rowIndex+1,1], 0) # red
        self.plotChannel(rgb,axarr[rowIndex+1,2], 1) # green
        self.plotChannel(rgb,axarr[rowIndex+1,3], 2) # blue
        
          
    def pixel(self,fig,inch):
        return int(inch*fig.dpi)
        
    def save(self,path,infos={}):
        if not path.endswith(".pdf"):
            path=path+".pdf"
        imageIndex=0    
        with PdfPages(path) as pdf:
            self.pages=len(self.images)//self.imagesPerPage
            for page in range(self.pages+1):
                cols=4
                fig, axarr = plt.subplots(self.imagesPerPage*2,cols, figsize=self.pagesize)
                thumbNailSize=self.pixel(fig,self.pageheight)
                for pageImageIndex in range(0,self.imagesPerPage):
                    if imageIndex<len(self.images):
                        image,imageTitle=self.images[imageIndex]
                        ax0=axarr[pageImageIndex*2  ,0]
                        ax1=axarr[pageImageIndex*2+1,0]
                        self.plotImage(ax0,image,imageTitle ,thumbNailSize)
                        self.plotHistogramm(image, axarr,pageImageIndex*2)
                        ax1.remove()
                    else:
                        for col in range(cols):
                            axarr[pageImageIndex*2  ,col].remove()
                            axarr[pageImageIndex*2+1,col].remove()  
                    imageIndex=imageIndex+1
                pdf.savefig()
                plt.close()
            pdfinfo=pdf.infodict()
            for key,info in infos.items():
                pdfinfo[key]=info
                    