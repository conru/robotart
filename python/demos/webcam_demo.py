#!/usr/bin/python3

import sys
sys.path.append('../library')

import cv2
import numpy as np

from drawwindow import DrawWindow
from webcam import Webcam
from shapes import Shapes, RectangleShape

# demo to show how webcam can be used to give feedback on what places still
# need to be painted ... assuming that the brush color is black

def colorClose(c1, c2, max_distance=10):

    if np.linalg.norm(c1 - c1, ord=1) < max_distance:
        return 1; 
    else: 
        return 0

# mostly to just have something to cycle waitKey (w/o a window, waitKey doesn't work?)
intro = DrawWindow(400,80,'Webcam Tool Instructions'); 
intro.drawText((10,10),'f=get webcam frame')
intro.drawText((10,20),'F=get ave of 10 webcam frames')
intro.drawText((10,30),'m=get mapped webcam frame')
intro.drawText((10,40),'c=calibrate webcam(1-4,arrows,s=save,esc=done)')
intro.drawText((10,50),'s=save mapping data')
intro.drawText((10,60),'l=load mapping data')
intro.show(); 

width=300
height=400

W = Webcam()
W.setMapSize(width,height)

DW = DrawWindow(width,height,'Desired Painting')

DW.setPenColor([0,0,0])
DW.drawRectangle2(.4*width,.2*height,.65*width,.9*height, True)
DW.drawRectangle2(.2*width,.5*height,.8*width,.7*height, True)
DW.moveWindow(20,150)
DW.show()

EW = DrawWindow(width,height,'Error Window')
EW.moveWindow(2*(width+5)+20,150)

map_window = 'Mapped Webcam'
cv2.namedWindow(map_window, cv2.WINDOW_AUTOSIZE)


while True:   
    k = cv2.waitKey(33)
    if k != -1:
        print(repr(chr(k%256)))
    if k==27:
        break   # Esc key to stop
    if k == ord('c'):
        W.calibrateWebcam()

    if k == ord('s'): # make the desired painting be a snap of the webcam
        frame = W.getMappedFrame()
        DW.grid = frame
        DW.show()


    if k == ord('m'):

        while True:
            frame = W.getMappedFrame()
          
            cv2.moveWindow(map_window,1*(width+5)+20,150)
            cv2.imshow(map_window, frame)
            #cvtColor( frame, frame, CV_RGB2GRAY )
        
            pen_color = (0,0,0)

            right=0
            wrong=0
            EW.setCanvasColor(0,0,0)

            for x in range(width):
                for y in range(height):
                    desired_color = DW.getColor(x,y)
                    #pen_color = DW.getColor(i,j)

                    if colorClose(desired_color, pen_color, 100): #if the captured frame maps to black
                        webcam_color = frame[y, x]

                        if colorClose(desired_color, webcam_color, 200): #if the captured frame is < 200 from the actual
                            right += 1
                            EW.setPenColor(desired_color)
                            EW.drawPixel((x,y))
                        else: #if the captured frame is > 200 from the actual (FAILURE...)
                            wrong += 1
                            EW.setPenColor((0,0,255))
                            EW.drawPixel(x,y)
                                
                    else: #the pixel maps to white, and is assumed to be correct.
                        EW.setPenColor((0,255,0))
                        EW.drawPixel(x,y)
                      
            
    
          
            EW.setPenColor((0,0,0))
            text = '{}  OK:{} TODO:{}'.format(100*right/(right+wrong), right, wrong)
            EW.drawText((10,10),text)
            EW.show()
            #print('%i OK, %i bad pixels',right,wrong)
          
            k = cv2.waitKey(33)
            if k==27 or k == ord('m'): 
                break
    
  

    if k == ord('f'):
        print('showing frame')
        frame = W.getFrame()
        cv2.imshow('webcam', frame)


    if k == ord('d'):
        print('showing merge of 10 frames')
        frame = W.getFrame(10)
        cv2.imshow('webcam', frame)


    if k == ord('s'): # 'save'
        points = W.getWebcamZoom()
        print('Here are the coordinates of 4 corners of webcam zoom')
        for i in range(4):
            print('Corner %i = (%f,%f)',i,points[2*i],points[2*i+1])
 


    if k == ord('l'): # 'load'
        delx=0.1
        dely=0.2
        frame = W.getFrame()
        width = frame.shape[1]
        height = frame.shape[0]
        
        W.setWebcamZoom(delx*width, dely*height,
                          (1-delx)*width, dely*height,
                          (1-delx)*width, (1-dely)*height,
                          delx*width, (1-dely)*height)
        print("zoom defined... type 'm' to see mapped capture")
  


