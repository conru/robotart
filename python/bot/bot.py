import cv2
import time # sleep
import datetime
import numpy as np
import re # parsing commands

import socket, sys
import socketserver

from drawwindow import DrawWindow

class Bot:

    def print(self, newline = True):
        print("P[", self.x, ",", self.y, ",", self.z, "]", end='')
        if newline:
           print()

    def setDebug(self,debug):
        self.debug = debug

    def go_up(self):
        self.go_to_xyz(None, None, self.z_max)

    def go_to_z(self,z):
        self.go_to_xyz(None, None, z)

    def go_to_xy(self, x=None, y=None):
        if (isinstance(x,list)):
           gx = x[0]
           gy = x[1]
        else:
           gx = x
           gy = y
        self.go_to_xyz(gx, gy, None)

    def go_to_xyz(self, x=None, y=None, z=None):
        # Qin: don't use -1, use None.

        if (isinstance(x,list)):
           gx = x[0]
           gy = x[1]
           gz = x[2]
        else:
           gx = x
           gy = y
           gz = z

        orig_location = (self.x, self.y, self.z)

        # Qin: software limits are implemented in grbl firmware,
        # no need to code.
        # modified here to skip the unreasonable min/max limits.

        # if self.is_number(gx) and gx != -1 and gx <= self.x_max : self.x = gx
        # if self.is_number(gy) and gy != -1 and gy <= self.y_max : self.y = gy
        # if self.is_number(gz) and gz != -1 and gz <= self.z_max : self.z = gz
        if gx is not None: self.x = gx
        if gy is not None: self.y = gy
        if gz is not None: self.z = gz

        ########### TO DO ####################
        # the linear feed command is G1
        self.doCommand("G1 X{x:.3f} Y{y:.3f} Z{z:.3f}".format(x = self.x, y = self.y, z = self.z))

        if self.simDraw and self.simPenDown:
           self.doSimulateDraw(orig_location, (self.x, self.y, self.z))
        if self.simBot:
           self.doSimulateBot(orig_location, (self.x, self.y, self.z))

        if self.debug:
           print("Moving to ", end='')
           self.print()

    def home(self):
        self.doCommand('$H')

    def setSpeed(self,s): # mm/min
        self.doCommand('G1 F{:1.3f}'.format(s))

    def is_number(self, n):
        is_number = True
        try:
            num = float(n)
            # check for "nan" floats
            is_number = num == num   # or use `math.isnan(num)`
        except ValueError:
            is_number = False
        return is_number

    ########### TO DO ####################

    def startSerialPort(self):
        # start a serial client that connects to a controller board running
        # grbl v1.1 firmware.
        from grbl import grbl
        self.grbl = grbl()

    def sendCommandToBot(self, command, debug = False):
        if debug: print("SENDING",command,"TO BOT");

        # send via serial only if serial connection established
        if hasattr(self, 'grbl'):
            self.grbl.command_ok(command, timeout=10)
            # send command and wait for ack

        return 1

    def processServerCommand(self, command, debug = False):
        print("PROC:",command)

        p = re.compile("GO X([\.\d-]+) Y([\.\d-]+) Z([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           z = float(p.search(command).group(3))
           #print("got X:",x,"Y:",y,"Z:",z);
           self.go_to_xyz(x,y,z)

        p = re.compile("SPEED V([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           speed = float(p.search(command).group(1))
           #print("got SPEED:",speed);
           self.setMaxSpeed(speed)

    def doCommand(self, command):
        if self.use_socket_server:
           self.sendToSocketServer(command)
        else:  # is socket server or connected to bot directly
           self.sendCommandToBot(command)

    def setHostPort(self, host, port):
        self.host = host
        self.port = port
        self.use_socket_server = True
        if (not self.sendToSocketServer("ping")):
           print("Sorry, you must first start bot_server.py")
           self.use_socket_server = False

    def sendToSocketServer(self, command):
        if (self.host == '' or self.port == ''):
            print("Please call set_host_port()")
            return

        start_time = datetime.datetime.now()

        HOST, PORT = self.host, self. port
        if self.debug: print('Sending to socket server: %s' %command)

        # create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
           sock.connect((HOST, PORT)) # connect to server
        except:
           return 0
        finally:
           sock.sendall(bytes(command, 'utf8')) # send data
           # receive data back from the server
		   #received = str(sock.recv(1024))
           sock.close() # shut down

        end_time = datetime.datetime.now();
        time_spent = end_time - start_time
        elapsed_seconds = time_spent.total_seconds()
        if self.debug: print("COMMAND",command,"TIME:",elapsed_seconds)
        return 1


    def doSimulateDraw(self, from_pt, to_pt):
        pt1 = self.simDrawWindowScale * (np.array(from_pt[0:2]) - np.array(self.canvasLocation)[0:2])
        pt2 = self.simDrawWindowScale * (np.array(to_pt[0:2]) - np.array(self.canvasLocation)[0:2])
        self.simDrawWindow.setPenColor(self.simulatePenColor)
        self.simDrawWindow.drawLine(pt1,pt2)
        self.simDrawWindow.show()
        k = cv2.waitKey(1)
        k = cv2.waitKey(1)

    def clearDrawSimulation(self):
        c = self.canvasColor
        self.simDrawWindow.clearWindow(c[0],c[1],c[2], False) # default background is white
        print(self.canvasColor)

    def simulatePenDown(self):
        self.simPenDown = True

    def simulatePenUp(self):
        self.simPenDown = False

    def openDrawSimulation(self):
        self.simDraw = True

        w,h = self.canvasDimensions;
        if (w > h):
           self.simDrawWindowDimensions = [500, int(500 * h / w)]
        else:
           self.simDrawWindowDimensions = [int(500 * w / h), 500]
        w,h = self.simDrawWindowDimensions;
        self.simDrawWindowScale = max(self.simDrawWindowDimensions) / max(self.canvasDimensions) # maps x,y of canvas to sim window
        #print("W:",w,"H:",h,"Scale:",self.simDrawWindowScale)

        self.simDrawWindow = DrawWindow(w, h, "Simulated Drawing",border_width = 10, hide_window=False)
        self.clearDrawSimulation()
        self.simDrawWindow.setPenColor([0,0,0])
        offset = 520 if self.simBot else 10
        self.simDrawWindow.moveWindow(offset, 20)
        self.simDrawWindow.drawBorder()
        self.simDrawWindow.show()
        k = cv2.waitKey(1)
        k = cv2.waitKey(1)

    def setCanvasLocation(self, canvas_location):
        self.canvasLocation = canvas_location

    def setCanvasDimensions(self, canvas_dimensions):
        self.canvasDimensions = canvas_dimensions

    def setBotDimensions(self, bot_dimensions):
        self.botDimensions = bot_dimensions

    def setMaxSpeed(self, cm_per_sec):
        self.maxSpeed = cm_per_sec

    def setPenRadius(self, r):
        self.simulatePenRadius = r

    def setPenColor(self, color): # [b,g,r]
        self.simulatePenColor = color

    # unused function - was going to rotate bot simulation
    def rotateSim(self, x, y, z = 0):
        return int(x), int(y)

    def doSimulateBot(self, from_pt, to_pt):

        off_x = 20 # to inside corner of box (pixels)
        off_y = 50
        overhang = 2 # of bar (cm)
        floor_to_bottom = 8 # (cm)
        floor_y = self.simBotWindow.height - 20
        rail_w = 3
        rail_d = 6
        head_w = 8
        head_h = 10
        head_d = 10
        pen_total_d = 12 # total length of pen/brush
        pen_d = 5 # depth below base of head
        pen_radius = self.simulatePenRadius # cm

        inside_x = self.botDimensions[0] + rail_w + head_w

        scale = self.simBotWindowScale # cm to pixels

        delta = 0.25 # how much to move per simulation (cm)
        distance = max(delta + 0.01, cv2.norm(from_pt, to_pt))
        steps = max(1,int(distance/delta))
        delta_time = delta / self.maxSpeed
        #print("D:",distance, "Steps:",steps)

        for step in range(0,steps):

           start_time = datetime.datetime.now()
           self.simBotWindow.clearWindow(255,255,255)
           p1 = np.array(from_pt[0:3]);
           p2 = np.array(to_pt[0:3]);
           p = p1 + (p2 - p1) * (step + 1) / steps
           x = p[0]
           y = p[1]
           z = p[2]

           if (self.simDraw):
              cw, ch = self.canvasDimensions
              cx, cy, cz = self.canvasLocation
              cpx = int(off_x + scale * (rail_w + head_w + cx)) # pixels of corner of canvas
              cpy = int(off_y + scale * cy)
              pt1 = self.rotateSim(cpx, cpy)
              pt2 = self.rotateSim(off_x + scale * (rail_w + head_w + cx + cw), off_y + scale * (cy + ch))
              self.simBotWindow.setPenColor(self.canvasColor)
              self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # top

              # transfer drawing onto bot simulation
              dw = int(self.simDrawWindow.width * scale / self.simDrawWindowScale)
              dh = int(self.simDrawWindow.height * scale / self.simDrawWindowScale)
              drawing_image = cv2.resize(self.simDrawWindow.getGrid(), (dw, dh));
              self.simBotWindow.grid[cpy:cpy+drawing_image.shape[0], cpx:cpx+drawing_image.shape[1]] = drawing_image

              # draw canvas on side view
              cpx = int(off_x + scale * (rail_w + head_w + cx)) # pixels of corner of canvas
              cpy = int(floor_y - scale * cz) - 2
              pt1 = self.rotateSim(cpx, cpy)
              pt2 = self.rotateSim(off_x + scale * (rail_w + head_w + cx + cw), floor_y)
              self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # top

           # draw top view of bot
           self.simBotWindow.setPenColor([180,180,180])

           pt1 = self.rotateSim(off_x - scale * rail_w, off_y - scale * rail_w)
           pt2 = self.rotateSim(off_x + scale * (inside_x + rail_w), off_y + scale)
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # top

           pt1 = self.rotateSim(off_x - scale * rail_w, off_y - scale * rail_w)
           pt2 = self.rotateSim(off_x, off_y + scale * (self.botDimensions[1] + rail_w))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # left

           pt1 = self.rotateSim(off_x + scale * inside_x, off_y - scale * rail_w)
           pt2 = self.rotateSim(off_x + scale * (inside_x + rail_w), off_y + scale * (self.botDimensions[1] + rail_w))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # right

           pt1 = self.rotateSim(off_x, off_y + scale * self.botDimensions[1])
           pt2 = self.rotateSim(off_x + scale * (inside_x + rail_w), off_y + scale * (self.botDimensions[1] + rail_w))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # right

           self.simBotWindow.setPenColor([210,210,210])
           pt1 = self.rotateSim(off_x + scale * x , off_y - scale * (rail_w + overhang))
           pt2 = self.rotateSim(off_x + scale * (x + rail_w), off_y + scale * (self.botDimensions[1] + rail_w + overhang))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # bar

           self.simBotWindow.setPenColor([230,230,230])
           pt1 = self.rotateSim(off_x + scale * x , off_y + scale * (y - head_h/2.))
           pt2 = self.rotateSim(off_x + scale * (head_w + x), off_y + scale * (y + head_h/2.))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # head

           self.simBotWindow.setPenColor(self.simulatePenColor)
           pt1 = self.rotateSim(off_x + scale * (head_w + pen_radius + x), off_y + scale * y)
           self.simBotWindow.drawCircle(pt1, int(scale * pen_radius), fill = True) # pen/brush

           # draw side view of bot

           self.simBotWindow.setPenColor([80,100,180])
           self.simBotWindow.drawRectangle2(0, floor_y, self.simBotWindow.width, self.simBotWindow.height, fill = True) # ground

           self.simBotWindow.setPenColor([230,230,230])
           pt1 = self.rotateSim(off_x + scale * x , floor_y - scale * (rail_d + pen_d + head_d))
           pt2 = self.rotateSim(off_x + scale * (x + head_w), floor_y - scale * (z + pen_d))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # head

           self.simBotWindow.setPenColor(self.simulatePenColor)
           pt1 = self.rotateSim(off_x + scale * (x + head_w), floor_y - scale * (z + pen_total_d))
           pt2 = self.rotateSim(off_x + scale * (x + head_w + 2 * pen_radius), floor_y - scale * (z))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # pen/brush

           self.simBotWindow.setPenColor([180,180,180])
           pt1 = self.rotateSim(off_x - scale * rail_w, floor_y - scale * (floor_to_bottom + rail_d))
           pt2 = self.rotateSim(off_x + scale * (inside_x + rail_w), floor_y - scale * (floor_to_bottom))
           self.simBotWindow.setLineThickness(2)
           self.simBotWindow.drawRectangle(pt1, pt2, fill = False) # horizontal

           self.simBotWindow.setPenColor([210,210,210])
           pt1 = self.rotateSim(off_x + scale * x , floor_y - scale * (floor_to_bottom + rail_d + rail_d))
           pt2 = self.rotateSim(off_x + scale * (x + rail_w), floor_y - scale * (floor_to_bottom + rail_d))
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # end bar

           self.simBotWindow.setPenColor([80,60,80])
           pt1 = self.rotateSim(off_x - scale * rail_w, floor_y - scale * (floor_to_bottom))
           pt2 = self.rotateSim(off_x, floor_y)
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # left foot
           pt1 = self.rotateSim(off_x + scale * inside_x, floor_y - scale * (floor_to_bottom))
           pt2 = self.rotateSim(off_x + scale * (inside_x + rail_w), floor_y)
           self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # right foot

           #pt1 = scale * np.array(from_pt[0:2]);
           #pt2 = scale * np.array(to_pt[0:2]);
           self.simBotWindow.show()
           k = cv2.waitKey(1)
           k = cv2.waitKey(1)

           # sleep a bit if simulated it too quickly
           end_time = datetime.datetime.now();
           time_spent = end_time - start_time
           elapsed_seconds = time_spent.total_seconds()
           if (elapsed_seconds < delta_time):
              time.sleep(delta_time - elapsed_seconds)


    def openBotSimulation(self, title = "Simulated Bot"):
        self.simBot = True
        self.simBotWindowW = 500;
        self.simBotWindowH = 500;
        self.simBotWindowScale = 400 / max(self.botDimensions) # maps x,y of bot to bot sim window
        self.simBotWindow = DrawWindow(self.simBotWindowW, self.simBotWindowH, title, border_width = 0, hide_window=False)
        self.simBotWindow.clearWindow(230,230,230) # default background is white
        offset = 520 if self.simDraw else 10
        self.simBotWindow.moveWindow(offset, 20)
        self.simBotWindow.setPenColor([0,0,0])
        self.simBotWindow.drawBorder()
        self.simBotWindow.show()
        self.go_to_xyz(0,0,5);
        k = cv2.waitKey(1)

    def __init__(self):
        self.debug = False
        self.queue = False
        self.x_max = 90 # cm
        self.y_max = 60
        # self.z_max = 10
        self.z_max = 5
        self.x = 0
        self.y = 0
        self.z = 0
        self.canvasLocation = -1
        self.canvasDimensions = -1
        self.canvasColor = [220,230,240]
        self.simulatePenColor = [0,0,0]
        self.simulatePenRadius = 1.0 # cm
        self.maxSpeed = 10 # cm/s
        self.botDimensions = np.array([90,60,6])
        self.simDraw = False
        self.simBot = False
        self.simPenDown = False
        self.host = ''
        self.port = ''
        self.use_socket_server = False
