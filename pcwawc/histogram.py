'''
Created on 2019-11-29

@author: wf
'''
import cv2
from timeit import default_timer as timer
from matplotlib import pyplot as plt
import numpy as np
import math

class Stats:
    """ Calculate Histogram statistics see https://math.stackexchange.com/questions/857566/how-to-get-the-standard-deviation-of-a-given-histogram-image """
    def __init__(self,histindexed):
        self.n=len(histindexed)
        self.sum=0
        self.prod=0
        self.sqsum=0
        for x,y in histindexed:
            self.sum+=y
            self.prod+=x*y
        self.mean=self.prod/self.sum
        for x,y in histindexed:
            dx=x-self.mean
            self.sqsum+=y*dx*dx
        # σ²
        self.variance=self.sqsum/self.sum
        self.stdv=math.sqrt(self.variance)    

class Histogram:
    """ Image Histogram """
    color = ('blue','green','red')
    
    def __init__(self,image):
        self.hist={}
        self.stats={}
        self.image=image
        self.rgb=cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        start=timer()
        histSize = 256
        histRange = (0, 256)  # the upper boundary is exclusive
        for channel in range(len(Histogram.color)):
            self.hist[channel] = cv2.calcHist([image], [channel], None, [histSize], histRange, accumulate=False)
            histindexed=list(enumerate(np.reshape(self.hist[channel],histSize)))
            self.stats[channel] = Stats(histindexed)
        end=timer()
        self.time=end-start
        
    def showDebug(self):
        print("calculation took %.4f s" % (self.time))   
        for channel in range(len(Histogram.color)):
            print (vars(self.stats[channel])) 
        
    def plot(self):    
        fig,(ax1,ax2)=plt.subplots(1,2)
        fig.suptitle('color histogram', fontsize=20)
        ax1.imshow(self.rgb), ax1.axis('off')
        for i,col in enumerate(Histogram.color):
            ax2.plot(self.hist[i],color = col)
            #ax2.xlim([0,256])
        return fig    
            
    def save(self,filepath):
        fig=self.plot()
        fig.savefig(filepath)    
        
    def show(self):
        self.plot()        
        plt.show()
        