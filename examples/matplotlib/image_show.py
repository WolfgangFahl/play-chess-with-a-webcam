#!/usr/bin/python
# -*- encoding: utf-8 -*-
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see https://stackoverflow.com/questions/43372792/matplotlib-opencv-image-subplot
import matplotlib.pyplot as plt
import sys
import cv2

def main(argv):
    # get the square chessbord file as an example
    default_file = '../../testMedia/chessBoard011.jpg'
    filename = argv[0] if len(argv) > 0 else default_file
    image = cv2.imread(filename)
    image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    
    # resize it to fit at the default 100 dpi
    w=320
    h=320
    x=50
    y=50
    image = cv2.resize(image,(w,h))
    # 6 x 4 inch figure
    figsize=(6, 4)
    fig = plt.figure(figsize=figsize)
    
    # add the image at position x=50, y=50 (in image coordinates)
    ax=addImage(fig,image,x,y)
    im = ax.imshow(image)
    
    subboard2x2=image[w//4:w//2,h//4:h//2,:]
    yLegendOffset=100
    ax2=addImage(fig,subboard2x2,w+yLegendOffset,h//2)
    im2=ax2.imshow(subboard2x2) 
    
    ax.axis("off")

    plt.show()
    
def addImage(fig,image,x,y):    
    dpi=fig.dpi
    fw,fh=fig.get_size_inches()[:2]
    ih,iw=image.shape[:2]
    ax = fig.add_axes([x/dpi/fw,y/dpi/fh,iw/dpi/fw,ih/dpi/fh])
    return ax  

if __name__ == "__main__":
    main(sys.argv[1:])
