#!/usr/bin/python3

import cv2
import time

import sys
sys.path.append('../library')
#
from bot import Bot
# from cartman import bot as Bot

# where is the canvas
canvas_location = [200, 50, 5] # mm upper/left corner is (0,0,0)
canvas_dimensions = [400, 300] # cm of canvas in x and y direction

# where is the paint
paint_location_up = [100, 250, 50] # x, y, z (above paint) in mm
paint_location_down = [100, 250, 10] # x, y, z (dipped in paint) in m

# where is the input image
filename = "images/pig.png"

mybot = Bot()
mybot.setCanvasLocation(canvas_location)
mybot.setCanvasDimensions(canvas_dimensions)
mybot.setPenRadius(8) # mm
mybot.setPenColor([20,20,250]) # b, g, r
mybot.setPenColor([220,20,50]) # b, g, r
mybot.setMaxSpeed(500) # mm/sec

# if want to send commands to bot_server, set true.  otherwise, will
# use_bot_server = False
#use_bot_server = True

# parse parameters from command line
# e.g. "python bot_demo.py --mode serial"
import argparse as ap
p = ap.ArgumentParser()
p.add_argument('--mode', default='simulated')
p.add_argument('--debug', default=0, type=int)
args = p.parse_args()

# branch on mode
mode = args.mode
print('Mode:',mode)
if 'sim' in mode:
    mybot.openDrawSimulation();
    mybot.openBotSimulation();
elif 'serve' in mode:
    mybot.setHostPort("localhost",9999)
elif 'serial' in mode:
    mybot.startSerialPort()
    is_idle = mybot.isIdle()

# branch on debugness
print('Debug:', args.debug)
mybot.setDebug(True if args.debug!=0 else False)

# load input image
image = cv2.imread(filename,0)
if image is None:
   print("Unable to load: ", filename)
   exit(1)

# calculate map between image pixels and canvas mm
height, width = image.shape
scale = min(canvas_dimensions) / max(height, width) # maps points on image to x,y of canvas
#print("IMAGE: width:", width, "height:", height, " scale:", scale)

# convert the photo into simple lines
ret,thresh = cv2.threshold(image,127,255,0)
image_contour,contours,hierarchy = cv2.findContours(thresh, 1, 2)
lines = contours[0]

# floor height shorthands
floor = canvas_location[2]
above_floor = floor + 10

# speed shorthands
fast = 50000 # mm/minute
slow = 2000 # mm/minute

# always home on init
mybot.init()

print ("going to paint", len(contours), "lines")

for i in range(len(contours) - 1):
    print("getting paint")
    mybot.setSpeed(fast)
    mybot.go_to_xyz(paint_location_up)
    mybot.setSpeed(slow)
    mybot.go_to_xyz(paint_location_down)
    mybot.go_to_xyz(paint_location_up)
    mybot.setSpeed(fast)
    # time.sleep(1)

    points = contours[i]
    print("drawing line:", i, " points:", len(points))

    # draw the first point
    pt = canvas_location[0:2] + scale * points[0][0]

    mybot.go_to_xy(pt.tolist()) # move to start of line
    mybot.setSpeed(slow)

    # pendown
    mybot.go_to_z(floor)
    mybot.simulatePenDown()

    # draw the rest of the line
    for p in range(1, len(points) - 1):
        pt = canvas_location[0:2] + scale * points[p][0]
        mybot.go_to_xy(pt.tolist()) # move to start of line

    # penup
    mybot.go_to_z(above_floor)
    mybot.simulatePenUp()

# wait till all commands in the controller's buffer are consumed
mybot.grbl.wait_until_idle()
mybot.home()

print("Finished drawing.  Press esc to quit.")

while True:
    k = cv2.waitKey(33)
    #if (k>0) { printf("key = %d\n",k);
    if k==27:
        break  # Esc key to stop
