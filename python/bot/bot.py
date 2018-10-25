import cv2
import time # sleep
import datetime
import numpy as np
import re # parsing commands

import socket, sys
import socketserver

# universal gcode sender
# holder 32, 724 mm

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
        
    def go_to_canvas_xy(self, x=None, y=None):
        if (self.canvasLocation is None):
            print("Sorry, must define canvas location to use go_to_canvas_xy")
            return
        
        if (isinstance(x,list)):
           gx = x[0]
           gy = x[1]
        else:
           gx = x
           gy = y
        self.go_to_xyz(self.canvasLocation[0] + gx, self.canvasLocation[1] + gy, None)

    def go_to_xyz(self, x=None, y=None, z=None, skip_bot = 0):
        if (isinstance(x,list)):
           gx = x[0]
           gy = x[1]
           gz = x[2]
        else:
           gx = x
           gy = y
           gz = z

        orig_location = (self.x, self.y, self.z)

        # z normally goes up from home position but can be set to up from floor
        # if connected directly to bot & z is up from floor
        if (gz is not None and self.z_up_from_floor and self.hasSerialConnection()):
            gz = gz - self.pen_to_floor
            if (self.hasSerialConnection() and gz > 0.):
                print("Setting gz=0, was:",gz)
                gz = 0. # range check as bot thinks z starts from home and only goes negative
        
        # Qin: software limits are implemented in grbl firmware,
        # no need to code.
        # ABC: put back to have 2nd layer protection 
        # modified here to skip the unreasonable min/max limits.
        if gx is not None and gx >= 0 and gx <= self.x_max: self.x = gx
        if gy is not None and gy >= 0 and gy <= self.y_max: self.y = gy
        if gz is not None and gz <= self.z_max: self.z = gz

        ########### TO DO ####################
        
        # the linear feed command is G1
        if not skip_bot:
            if (self.flip_xy and not self.use_socket_server):
                self.doCommand("G1 X{x:.3f} Y{y:.3f} Z{z:.3f}".format(x = self.y, y = self.x, z = self.z))
            else:
                self.doCommand("G1 X{x:.3f} Y{y:.3f} Z{z:.3f}".format(x = self.x, y = self.y, z = self.z))

        if self.simDraw and self.simPenDown:
           self.doSimulateDraw(orig_location, (self.x, self.y, self.z))
        if self.simBot:
           self.doSimulateBot(orig_location, (self.x, self.y, self.z)) # note: z is always up from floor

        if self.debug:
           print("Moving to ", end='')
           self.print()

    def doDwell(self, millisec):
        self.doCommand("G4 P{s:.3f}".format(s = millisec/1000))
        if self.debug:
           print("Sleeping for",millisec,'ms')
           
    def home(self):
        if (self.isIdle()):
            self.doCommand('$H')

    def setSpeed(self,s): # mm/min
        if (s > self.maxSpeed): s = self.maxSpeed
        self.speed = s
        self.doCommand('G1 F{:1.3f}'.format(s))

    def init(self):
        self.setSpeed(5000) # mm/sec
        if self.debug:
            print('homing')
        self.home()
        
    def is_number(self, n):
        is_number = True
        try:
            num = float(n)
            # check for "nan" floats
            is_number = num == num   # or use `math.isnan(num)`
        except ValueError:
            is_number = False
        return is_number

    def isIdle(self):
        if (self.grbl is None): return 1
        return self.grbl.is_idle()
    
    ########### TO DO ####################

    def startSerialPort(self):
        # start a serial client that connects to a controller board running
        # grbl v1.1 firmware.
        # from grbl import grbl
        from cartman import bot as grbl
        self.grbl = grbl()

    def hasSerialConnection(self):
        res = True if (self.grbl is not None and hasattr(self, 'grbl')) else False;
        return res
        
    def sendCommandToBot(self, command, debug = False):
        if debug: print("SENDING",command,"TO BOT")
        ret = 0
        # send via serial only if serial connection established
        if self.hasSerialConnection():
            ret = self.grbl.command_ok(command, timeout=10)
            # send command and wait for ack

        return ret

    def processServerCommand(self, command, debug = False):
        print("PROC:",command)

        x = None
        y = None
        z = None

        p = re.compile("G1 X([a-zA-Z\.\d-]+) Y([a-zA-Z\.\d-]+) Z([a-zA-Z\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           z = float(p.search(command).group(3))
           print(" - got X:",x,"Y:",y,"Z:",z)
           return self.go_to_xyz(x,y,z)
       
        p = re.compile("G1 X([a-zA-Z\.\d-]+) Y([a-zA-Z\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           print(" - got X:",x,"Y:",y)
           return self.go_to_xy(x,y)

        p = re.compile("G1 Z([a-zA-Z\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           z = float(p.search(command).group(1))
           print(" - got Z:",z)
           return self.go_to_z(z)

        p = re.compile("G1 F([a-zA-Z\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           speed = float(p.search(command).group(1))
           print("got SPEED:",speed)
           return self.setSpeed(speed)
       
        p = re.compile("SPEED V([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           speed = float(p.search(command).group(1))
           print("got SPEED:",speed)
           return self.setSpeed(speed)

        p = re.compile("DWELL S([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           ms = float(p.search(command).group(1))
           print("got DWELL:",ms)
           return self.doDwell(ms)
           
        p = re.compile("PEN_RADIUS R([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           r = float(p.search(command).group(1))
           print("got PEN RADIUS:",r)
           return self.setPenRadius(r)
       
        p = re.compile("FLIP_XY F([\d]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           f = int(p.search(command).group(1))
           print("got FLIP_XY:",f)
           self.flip_xy = True if (f == 1) else False
           return 1;

        p = re.compile("SET_Z_UP_FROM_FLOOR Z([\d]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           z = int(p.search(command).group(1))
           print("got SET_Z_UP_FROM_FLOOR:",z)
           self.z_up_from_floor = True if (z == 1) else False
           return 1;

        p = re.compile("PEN_COLOR B([\d-]+) G([\d-]+) R([\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           b = int(p.search(command).group(1))
           g = int(p.search(command).group(2))
           r = int(p.search(command).group(3))
           print("got PEN COLOR:",r)
           return self.setPenColor([b,g,r])

        # set dimensions of the canvas
        p = re.compile("CANVAS_DIMENSION W([\.\d-]+) H([\.\d-]+)")
        if (p.search(command)) :
           w = float(p.search(command).group(1))
           h = float(p.search(command).group(2))
           print("got CANVAS DIMENSION W:",w,"H:",h)
           return self.setCanvasDimensions([w,h])

        # set location of canvas
        p = re.compile("CANVAS_LOCATION X([\.\d-]+) Y([\.\d-]+) Z([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           z = float(p.search(command).group(3))
           print("got CANVAS_LOCATION X:",x,"Y:",y,"Z:",z)
           return self.setCanvasLocation([x,y,z])

        # draw around the canvas
        p = re.compile("DRAW_CANVAS_OUTLINE")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           print("got DRAW_CANVAS_OUTLINE")
           return self.drawCanvasOutline()

        # open the draw simulator
        p = re.compile("OPEN_DRAW_SIMULATOR")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           print("got OPEN_DRAW_SIMULATOR")
           return self.openDrawSimulation()

        p = re.compile("SET_PEN_TO_FLOOR D([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           d = float(p.search(command).group(1))
           print("got SET_PEN_TO_FLOOR D:",d)
           return self.setPenToFloorDistance(d)
       
        p = re.compile("SIMULATE_PEN_DOWN")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           return self.simulatePenDown()
           
        #p = re.compile("IS_IDLE")
        #if (p.search(command)) :   # The result of this is referenced by variable name '_'
           #return self.isIdle()

        p = re.compile("SIMULATE_PEN_UP")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           return self.simulatePenUp()

        # set location of canvas
        p = re.compile("CANVAS_LOCATION X([\.\d-]+) Y([\.\d-]+) Z([\.\d-]+)")
        if (p.search(command)) :   # The result of this is referenced by variable name '_'
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           z = float(p.search(command).group(3))
           print("got CANVAS_LOCATION X:",x,"Y:",y,"Z:",z)
           return self.setCanvasLocation([x,y,z])
           
        # define locations for colors
        p = re.compile("ADD_PAINT_LOCATION X([\.\d-]+) Y([\.\d-]+) ZUP([\.\d-]+) ZDN([\.\d-]+) B([\d-]+) G([\d-]+) R([\d-]+)")
        if (self.simBot and p.search(command)) :  
           x = float(p.search(command).group(1))
           y = float(p.search(command).group(2))
           zup = float(p.search(command).group(3))
           zdown = float(p.search(command).group(4))
           b = int(p.search(command).group(5))
           g = int(p.search(command).group(6))
           r = int(p.search(command).group(7))
           print("got ADD PAINT LOCATION")
           return self.addPaintLocation(x,y,zup,zdown,b,g,r)
           
    def doCommand(self, command):
        if self.use_socket_server:
           self.sendToSocketServer(command)
        elif self.hasSerialConnection():  # is socket server or connected to bot directly
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

        end_time = datetime.datetime.now()
        time_spent = end_time - start_time
        elapsed_seconds = time_spent.total_seconds()
        if self.debug: print("COMMAND",command,"TIME:",elapsed_seconds)
        return 1


    def doSimulateDraw(self, from_pt, to_pt):
        pt1 = self.simDrawWindowScale * (np.array(from_pt[0:2]) - np.array(self.canvasLocation)[0:2])
        pt2 = self.simDrawWindowScale * (np.array(to_pt[0:2]) - np.array(self.canvasLocation)[0:2])
        if (self.debug): print("Drawing from",pt1/self.simDrawWindowScale,"to",pt2/self.simDrawWindowScale)
        self.simDrawWindow.setPenColor(self.simulatePenColor)
        self.simDrawWindow.setLineThickness(int(self.simulatePenRadius))
        self.simDrawWindow.drawLine(pt1,pt2)
        self.simDrawWindow.show()
        k = cv2.waitKey(1)
        k = cv2.waitKey(1)

    def clearDrawSimulation(self):
        c = self.canvasColor
        self.simDrawWindow.clearWindow(c[0],c[1],c[2], False) # default background is white
        print("Setting canvas to:",self.canvasColor)

    def simulatePenDown(self):
        self.simPenDown = True

    def simulatePenUp(self):
        self.simPenDown = False

    def openDrawSimulation(self):
        self.simDraw = True

        w,h = self.canvasDimensions
        if (w > h):
           self.simDrawWindowDimensions = [500, int(500 * h / w)]
        else:
           self.simDrawWindowDimensions = [int(500 * w / h), 500]
        w,h = self.simDrawWindowDimensions
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

    def setCanvasLocation(self, xyz):
        self.canvasLocation = xyz
        if self.use_socket_server:
            command = "CANVAS_LOCATION X{x:.3f} Y{y:.3f} Z{z:.3f}".format(x=xyz[0], y=xyz[1], z=xyz[2])
            self.sendToSocketServer(command)
        if (self.simDraw): self.clearDrawSimulation()
        #if (self.simBot): self.doSimulateBot([0,0,0],[0,0,1])

    def setCanvasDimensions(self, xy):
        x = xy[0]
        y = xy[1]
        if (self.flip_xy and self.use_socket_server):
            x = xy[1]
            y = xy[0]
        self.canvasDimensions = [x,y]
        #print("set canvas w = ",x," h = ",y)
        if self.use_socket_server:
            command = "CANVAS_DIMENSION W{x:.3f} H{y:.3f}".format(x=x, y=y)
            self.sendToSocketServer(command)
        if (self.simDraw): self.clearDrawSimulation()
        #if (self.simBot): self.doSimulateBot([0,0,0],[0,0,1])

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
        overhang = 20 # of bar (mm)
        floor_to_bottom = 80 # (mm)
        floor_y = self.simBotWindow.height - 20
        rail_w = 30
        rail_d = 60
        head_w = 100
        head_h = 100
        head_d = 150
        pen_total_d = 120 # total length of pen/brush
        pen_d = 50 # depth below base of head
        pen_radius = self.simulatePenRadius # mm

        inside_x = self.botDimensions[0] + rail_w + head_w

        scale = self.simBotWindowScale # mm to pixels

        delta = 25 # how much to move per simulation (mm)
        distance = max(delta + 0.01, cv2.norm(from_pt, to_pt))
        steps = max(1,int(distance/delta))
        delta_time = delta / self.maxSpeed
        #print("D:",distance, "Steps:",steps)

        for step in range(0,steps):

           start_time = datetime.datetime.now()
           self.simBotWindow.clearWindow(255,255,255)
           p1 = np.array(from_pt[0:3])
           p2 = np.array(to_pt[0:3])
           p = p1 + (p2 - p1) * (step + 1) / steps
           x = p[0]
           y = p[1]
           z = p[2]
           if (self.hasSerialConnection()): z = z + self.pen_to_floor

           if (self.simDraw):
              cw, ch = self.canvasDimensions
              cx, cy, cz = self.canvasLocation
              cpx = int(off_x + scale * (head_w + cx)) # - self.simulatePenRadius)) # pixels of corner of canvas (-pen_radius might not be right)
              cpy = int(off_y + scale * cy)
              pt1 = self.rotateSim(cpx, cpy)
              pt2 = self.rotateSim(off_x + scale * (rail_w + head_w + cx + cw), off_y + scale * (cy + ch))
              self.simBotWindow.setPenColor(self.canvasColor)
              self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # top

              # transfer drawing onto bot simulation
              dw = int(self.simDrawWindow.width * scale / self.simDrawWindowScale)
              dh = int(self.simDrawWindow.height * scale / self.simDrawWindowScale)
              drawing_image = cv2.resize(self.simDrawWindow.getGrid(), (dw, dh))
              #print("DW:",dw,"DH:",dh,'SDWW',self.simDrawWindow.width, 'SDWS',self.simDrawWindowScale, 'scale',scale)
              
              self.simBotWindow.grid[cpy:cpy+drawing_image.shape[0], cpx:cpx+drawing_image.shape[1]] = drawing_image

              # draw canvas on side view
              cpx = int(off_x + scale * (rail_w + head_w + cx)) # pixels of corner of canvas
              cpy = int(floor_y - scale * cz) - 2
              pt1 = self.rotateSim(cpx, cpy)
              pt2 = self.rotateSim(off_x + scale * (rail_w + head_w + cx + cw), floor_y)
              self.simBotWindow.drawRectangle(pt1, pt2, fill = True) # top

           for i in range(len(self.paintLocations)):
               paint = self.paintLocations[i]
               down = paint['down']
               color = paint['color']
               self.simBotWindow.setPenColor(color)
               pt1 = self.rotateSim(off_x + scale * (head_w + down[0]), off_y + scale * down[1])
               self.simBotWindow.drawCircle(pt1, 10, fill = True) 

           # draw workspace grid
           self.simBotWindow.setPenColor([0,0,0])
           self.simBotWindow.setLineThickness(1)
           pt1 = self.rotateSim(off_x + scale * (head_w + 0) + 2, off_y + scale * 0 + 2)
           pt2 = self.rotateSim(off_x + scale * (head_w + self.botDimensions[0]) - 2, off_y + scale * self.botDimensions[1] - 2)
           self.simBotWindow.drawRectangle(pt1, pt2, fill = False) 
               
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

           #pt1 = scale * np.array(from_pt[0:2])
           #pt2 = scale * np.array(to_pt[0:2])
           self.simBotWindow.show()
           k = cv2.waitKey(1)
           k = cv2.waitKey(1)

           # sleep a bit if simulated it too quickly
           end_time = datetime.datetime.now()
           time_spent = end_time - start_time
           elapsed_seconds = time_spent.total_seconds()
           if (elapsed_seconds < delta_time):
              time.sleep(delta_time - elapsed_seconds)


    def openBotSimulation(self, title = "Simulated Bot"):
        self.simBot = True
        self.simBotWindowW = 500
        self.simBotWindowH = 500
        self.simBotWindowScale = 400 / max(self.botDimensions) # maps x,y of bot to bot sim window
        self.simBotWindow = DrawWindow(self.simBotWindowW, self.simBotWindowH, title, border_width = 0, hide_window=False)
        self.simBotWindow.clearWindow(230,230,230) # default background is white
        offset = 520 if self.simDraw else 10
        self.simBotWindow.moveWindow(offset, 20)
        self.simBotWindow.setPenColor([0,0,0])
        self.simBotWindow.drawBorder()
        self.simBotWindow.show()
        self.go_to_xyz(0,0,5,1) # the extra term ensures no moving physical arm
        k = cv2.waitKey(1)


    # mostly used for simulation
    def setPenToFloorDistance(self,d):
        if (self.debug): print("Setting pen to floor distance to:",d)
        self.pen_to_floor = d
        if self.use_socket_server:
            command = "SET_PEN_TO_FLOOR D{d:d}".format(d=d)
            self.sendToSocketServer(command)

    # mostly used for simulation
    def setFlipXY(self,flip):
        f = 1 if flip else 0
        if (self.debug): print("Setting flip xy:",f)
        self.flip_xy = flip
        if self.use_socket_server:
            command = "FLIP_XY F{f:d}".format(f=f)
            self.sendToSocketServer(command)

    # mostly used for simulation
    def setZUpFromFloor(self,zup):
        z = 1 if zup else 0
        if (self.debug): print("Setting x_up_from_floor:",z)
        self.z_up_from_floor = zup
        # don't send it to socket server as 
        #if self.use_socket_server:
        #    command = "SET_Z_UP_FROM_FLOOR Z{z:d}".format(z=z)
        #    self.sendToSocketServer(command)

    # mostly used for simulation
    def addPaintLocation(self,x,y,zup,zdn,b,g,r):
        self.paintLocations.append({'up':[x,y,zup],'down':[x,y,zdn],'color':[b,g,r]})
        if self.use_socket_server:
            command = "ADD_PAINT_LOCATION X{x:.3f} Y{y:.3f} ZUP{zup:.3f} ZDN{zdn:.3f} B{b:d} G{g:d} R{r:d}".format(x=x, y=y, zup=zup, zdn=zdn, b=b, g=g, r=r)
            self.sendToSocketServer(command)
            
    def addPaintLocationByList(self,up, down, color):
        self.addPaintLocation(up[0],up[1],up[2],down[2],color[0],color[1],color[2])
            
    # paint = dictionary of paint location/color
    def getPaint(self,up, down, color, fast, slow):
        orig_speed = self.speed
        self.setSpeed(fast)
        self.go_to_z(up[2])
        self.go_to_xyz(up)
        self.setSpeed(slow)
        self.go_to_xyz(down)
        if (self.simDraw) : self.setPenColor(color)
        self.doDwell(500) # ms
        self.go_to_z(up[2])
        self.setSpeed(orig_speed)

    def penUp(self,z):
        self.go_to_z(z)
        if (self.simDraw):
           self.simulatePenUp()
           if self.debug: print("SIMULATE_PEN_UP")

    def penDown(self,z):
        self.go_to_z(z)
        if (self.simDraw):
            self.simulatePenDown()
            if self.debug: print("SIMULATE_PEN_DOWN")

    # mostly used for verifying the canvas
    def drawCanvasOutline(self):
        zup = 0
        orig_speed = self.speed
        self.setSpeed(self.maxSpeed)
        if (self.z_up_from_floor): zup = self.pen_to_floor
        self.go_to_z(zup)
        self.go_to_canvas_xy(0,0)
        self.go_to_z(self.canvasLocation[2])
        self.go_to_canvas_xy(0,self.canvasDimensions[1])
        self.go_to_canvas_xy(self.canvasDimensions[0],self.canvasDimensions[1])
        self.go_to_canvas_xy(self.canvasDimensions[0],0)
        self.go_to_canvas_xy(0,0)
        self.go_to_z(zup)
        self.setSpeed(orig_speed)
        
    def __init__(self):
        self.debug = False
        self.queue = False
        self.flip_xy = False # if true, then flip x/y axes when sending command to bot
        self.z_up_from_floor = False # if true, then z goes "up" from floor, else z goes "up" from 
        self.x_max = 900 # mm
        self.y_max = 600
        self.z_max = 50
        self.pen_to_floor = 20 # for simulator, how far is the pen/brush from tip to floor when in home position (mm)
        self.x = 0
        self.y = 0
        self.z = 0
        self.canvasLocation = [0,0,0]
        self.canvasDimensions = [300,200]
        self.canvasColor = [220,230,240] # bgr
        self.canvasLocation = [10,10,-10] # mm
        self.simulatePenColor = [0,0,0]
        self.simulatePenRadius = 10 # mm
        self.speed = 5000 # mm/s
        self.maxSpeed = 30000 # mm/s
        self.botDimensions = np.array([900,600,60])
        self.simDraw = False
        self.simBot = False
        self.simPenDown = False
        self.host = ''
        self.port = ''
        self.use_socket_server = False
        self.paintLocations = []
        self.grbl = None
