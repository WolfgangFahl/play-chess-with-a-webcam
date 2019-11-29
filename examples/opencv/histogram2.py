#!/usr/bin/python3
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam

'''
Created on 2019-11-29

@author: wf

see https://docs.opencv.org/master/d1/db7/tutorial_py_histogram_begins.html
'''
import sys
import cv2
from matplotlib import pyplot as plt
from timeit import default_timer as timer

class Histogram:
    """ Image Histogram """
    color = ('blue','green','red')
    
    def __init__(self,image):
        self.hist={}
        self.image=image
        self.rgb=cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        start=timer()
        for i in range(len(Histogram.color)):
            self.hist[i] = cv2.calcHist([image],[i],None,[256],[0,256])
        end=timer()
        self.time=end-start
        
    def plot(self):    
        fig,(ax1,ax2)=plt.subplots(1,2)
        fig.suptitle('color histogram', fontsize=20)
        ax1.imshow(self.rgb), ax1.axis('off')
        for i,col in enumerate(Histogram.color):
            ax2.plot(self.hist[i],color = col)
            #ax2.xlim([0,256])
        plt.show()

def main(argv):
    default_file = '../../testMedia/chessBoard013.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv2.imread(filename)
    #cv2.imshow('chessboard', image)
    # refresh
    #cv2.waitKey(10)
    h=Histogram(image)
    h.plot()

if __name__ == "__main__":
    main(sys.argv[1:])