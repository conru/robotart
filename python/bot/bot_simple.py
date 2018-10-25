#!/usr/bin/python3

import cv2
import time
import sys
sys.path.append('../library')

from bot import Bot

# distance from tip of brush to floor
pen_to_floor = 28 # mm
pen_painting_depth = 3 # mm below the surface of the canvas the brush should be while painting

# where is the canvas (top surface)
# 8.5x11" paper (portrait)
canvas_location = [8.5 * 25.4, 54, 1] # mm upper/left corner is (0,0,0)
canvas_dimensions = [8.5 * 25.4, 11 * 25.4] # cm of canvas in x and y direction 

# 11x14" canvas board (landscape)
canvas_location = [8.5 * 25.4, 54, 3] # mm upper/left corner is (0,0,0)
canvas_dimensions = [14 * 25.4, 11 * 25.4] # cm of canvas in x and y direction (8.5x11" paper)

# info about where the paints are in mm, color bgr
paints = [{'up':[100, 50, 20], 'down':[100, 50, 5], 'color':[220,20,50]},
          {'up':[100, 100, 20], 'down':[100, 100, 5], 'color':[90,220,50]},
          {'up':[100, 150, 20], 'down':[100, 150, 5], 'color':[20,120,250]}]

mybot = Bot()

# if want to send commands to bot_server, set true.  otherwise, will
# use_bot_server = False
#use_bot_server = True

# parse parameters from command line
# e.g. "python bot_demo.py --mode serial"
import argparse as ap
p = ap.ArgumentParser()
p.add_argument('--mode', default='sim')
p.add_argument('--debug', default=0, type=int)
args = p.parse_args()

mybot.debug = True if (args.debug == 1) else False
#mybot.debug = True

# branch on mode
mode = args.mode
print('Mode:',mode)
if 'sim' in mode:
    mybot.openDrawSimulation();
    mybot.openBotSimulation();
elif 'socket' in mode: # connect to bot via socket server
    mybot.setHostPort("localhost",9999)
elif 'serial' in mode:
    mybot.openDrawSimulation();
    mybot.openBotSimulation();
    mybot.startSerialPort()
    mybot.setFlipXY(True) # if connect directly, must tell bot to flip x and y axes
    mybot.setZUpFromFloor(True)
    is_idle = mybot.isIdle()

mybot.setCanvasLocation(canvas_location)
mybot.setCanvasDimensions(canvas_dimensions)
mybot.setPenRadius(8) # mm
#mybot.setMaxSpeed(50000) # mm/sec
mybot.setPenToFloorDistance(pen_to_floor) # mm

for i in range(len(paints)):
    paint = paints[i]
    mybot.addPaintLocationByList(paint['up'],paint['down'],paint['color'])

# speed shorthands
fast = 50000 # mm/minute
slow = 2000 # mm/minute

# always home on init
mybot.init()

print ("outlining the canvas")
mybot.drawCanvasOutline()

print ("going to paint")

for i in range(3):
    print("getting paint:",i)
    paint = paints[i]
    mybot.getPaint(paint['up'],paint['down'],paint['color'],fast,slow)
    mybot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i)
    mybot.setSpeed(fast)
    mybot.penDown(canvas_location[2] - pen_painting_depth)
    mybot.doDwell(100); # ms
    mybot.go_to_canvas_xy(50 + 30 * i,10 + 50 * i)
    mybot.go_to_canvas_xy(50 + 30 * i,50 + 50 * i)
    mybot.go_to_canvas_xy(10 + 30 * i,50 + 50 * i)
    mybot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i)
    mybot.penUp(paint['up'][2])

mybot.go_to_canvas_xy(-20, 20)
mybot.home()

print("Finished drawing.  Press esc to quit.")

while True:
    k = cv2.waitKey(33)
    #if (k>0) { printf("key = %d\n",k);
    if k==27:
        break  # Esc key to stop
