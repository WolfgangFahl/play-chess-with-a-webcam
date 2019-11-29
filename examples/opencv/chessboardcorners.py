'''
Created on 2019-11-29

@author: wf
'''
import sys
import cv2
from timeit import default_timer as timer

def main(argv):
    file_pattern = '../../testMedia/chessBoard%03d.jpg'
    for i in range(1,14):
        filename = file_pattern % (i)
        org = cv2.imread(filename)
        gray = cv2.cvtColor(org, cv2.COLOR_BGR2GRAY)
        for rows in range(3,9):
            for cols in range(3,9):
                chesspattern=(rows,cols)
                image=org.copy()           
                # Find the chessboard corners
                start=timer()
                ret, corners = cv2.findChessboardCorners(gray, chesspattern, None)
                end=timer()
                
                #If found, add object points, image points
                if ret == True:
                    print ("finding corners with %d x %d pattern took %.4f s for chessboard %03d" % (rows,cols,(end-start),i))
                    # Draw and display the corners
                    cv2.drawChessboardCorners(image, chesspattern, corners, ret)
                    #write_name = 'corners_found'+str(idx)+'.jpg'
                    #cv2.imwrite(write_name, img)
                    #cv2.imshow('img', image)
                    #cv2.waitKey(50)
                    cv2.imwrite('/tmp/corners%03d-%dx%d.jpg' % (i,rows,cols),image)    
                else:
                    print ("no corners with %d x %d pattern detected in %s" % (rows,cols,filename))    
        
if __name__ == "__main__":
    main(sys.argv[1:])       