#!/usr/bin/python3

import cv2
import time

import sys
sys.path.append('../library')

from bot import Bot

# where is the canvas 
canvas_location = [20, 5, .5] # cm upper/left corner is (0,0,0)
canvas_dimensions = [40, 30] # cm of canvas in x and y direction

# where is the paint
paint_location_up = [10, 25, 5] # x, y, z (above paint) in cm
paint_location_down = [10, 25, 1] # x, y, z (dipped in paint) in cm

# where is the input image
filename = "images/pig.png"

mybot = Bot()
mybot.setCanvasLocation(canvas_location)
mybot.setCanvasDimensions(canvas_dimensions) 
mybot.setPenRadius(0.8) # cm
mybot.setPenColor([20,20,250]) # b, g, r
mybot.setPenColor([220,20,50]) # b, g, r
mybot.setMaxSpeed(20) # cm/sec

# if want to send commands to bot_server, set true.  otherwise, will 
use_bot_server = False
#use_bot_server = True

if use_bot_server:
  mybot.setHostPort("localhost",9999)
else:
  mybot.openDrawSimulation();
  mybot.openBotSimulation();

#mybot.setDebug(True)

# load input image
image = cv2.imread(filename,0)
if image is None:
   print("Unable to load: ", filename)
   exit(1)

# calculate map between image pixels and canvas cm
height, width = image.shape
scale = min(canvas_dimensions) / max(height, width) # maps points on image to x,y of canvas
#print("IMAGE: width:", width, "height:", height, " scale:", scale)

# convert the photo into simple lines
ret,thresh = cv2.threshold(image,127,255,0)
image_contour,contours,hierarchy = cv2.findContours(thresh, 1, 2)
lines = contours[0]

print ("going to paint", len(contours), "lines")
mybot.go_up()

for i in range(len(contours) - 1):
  print("getting paint")
  mybot.go_to_xyz(paint_location_up)
  mybot.go_to_xyz(paint_location_down)
  mybot.go_to_xyz(paint_location_up)
  time.sleep(1)

  points = contours[i] 
  print("drawing line:", i, " points:", len(points))

  # draw the first point
  pt = canvas_location[0:2] + scale * points[0][0]

  mybot.go_to_xy(pt.tolist()) # move to start of line
  mybot.go_to_z(canvas_location[2])
  mybot.simulatePenDown()

  # draw the rest of the line
  for p in range(1, len(points) - 1):
    pt = canvas_location[0:2] + scale * points[p][0]
    mybot.go_to_xy(pt.tolist()) # move to start of line 
  
  mybot.simulatePenUp()
  mybot.go_up()
  mybot.go_to_xyz(paint_location_up)

print("Finished drawing.  Press esc to quit.")

while True:
    k = cv2.waitKey(33)
    #if (k>0) { printf("key = %d\n",k); 
    if k==27:
        break  # Esc key to stop
