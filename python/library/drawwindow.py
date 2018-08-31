import numpy as np
import cv2
import random

# Packages simple drawing commands for the simulator display window
class DrawWindow:

    def setCanvasColor(self, b, g, r):
        self.canvas_color = np.array([b, g, r])

    def clearWindow(self, b=None, g=None, r=None, full=True): 
        if all([b, g, r]):
            self.setCanvasColor(b, g, r)
        if (full == True):
            self.grid[:, :] = self.canvas_color
        else: # only do border
            self.grid[self.border:self.border + self.height, self.border:self.border + self.width] = self.canvas_color

    def copy(self, W):
        self.grid = W.grid.clone()

	# copies pixels of W that are NOT r,g,b
    def overlay(self, W, outline = False, r = 0, g = 0, b = 0):
        min_width = min(W.width, self.width)
        min_height = min(W.height, self.height)

        for i in range(min_width):
            for j in range(min_height):
                color = W.getColor(i, j)

                if color[0] != b or color[1] != g or color[2] != r: # ABC: need to check color order
                    if outline:
                        # check for neighbors to see if it has 1+ pixels that are r,g,b
                        is_boundary = False
                        left = max(i - 1, 0)
                        right = min(i + 1, self.width - 1)
                        top = max(j - 1, 0)
                        bottom = min(j + 1, self.height - 1)

                        for n in range(left, right + 1):
                            for m in range(top, bottom + 1):
                                neighbor_color = W.getColor(n, m)
                                if neighbor_color[0] == b and neighbor_color[1] == g and neighbor_color[2] == r:
                                    is_boundary = True
                            
                        if is_boundary:
                            self.grid[i + self.border][ j + self.border] = color
                        

                    else:
                       self.grid[i + self.border][j + self.border] = color

    def setLineType(self, type):
        if type == 'solid':
            self.line_type = 8 # 8 for solid antialiased line 

    def setLineThickness(self, thickness = 1):
        self.pen_thickness = thickness
 
    def setPenColor(self, bgr):
        self.pen_color = bgr 

    def setPenColorRandom(self): 
        self.setPenColor((random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
        print('Setting pen to {} {} {}'.format(random.randint(100,200),
                                                    random.randint(100,200),
                                                    random.randint(100,200)))

    def drawLine(self, pt1, pt2):
        pt1 = (int(pt1[0] + self.border), int(pt1[1] + self.border))
        pt2 = (int(pt2[0] + self.border), int(pt2[1] + self.border))
        cv2.line(self.grid, pt1, pt2, self.pen_color, self.pen_thickness, self.line_type)

    def drawLine2(self, x1, y1, x2, y2):
        self.drawLine([x1,y1], [x2,y2])

    def drawRectangle(self, pt1, pt2, fill = False):
        thickness = self.pen_thickness
        if fill:
            thickness = -1
        x1 = int(pt1[0] + self.border)
        y1 = int(pt1[1] + self.border)
        x2 = int(pt2[0] + self.border)
        y2 = int(pt2[1] + self.border)
        cv2.rectangle(self.grid, (x1, y1), (x2, y2), self.pen_color, thickness)

    def drawRectangle2(self, x1, y1, x2, y2, fill = False):
        self.drawRectangle([x1, y1], [x2, y2], fill)

    def drawCircle(self, pt, r, fill = False):
        x = int(pt[0] + self.border)
        y = int(pt[1] + self.border)

        thickness = self.pen_thickness

        if fill:
            thickness = -1
            cv2.circle(self.grid, (x, y), r, self.pen_color, thickness, self.line_type)
  
    def drawCircle2(self, x, y, r, fill = False):
        self.drawCircle([x, y], r, fill)

    def drawEllipse(self, pt, axes, angle, fill = False):
        thickness = self.pen_thickness
        if fill:
            thickness = -1

        x = int(pt[0] + self.border)
        y = int(pt[1] + self.border)

        print((x, y), axes, angle, 0., 360., self.pen_color, thickness, self.line_type)
        cv2.ellipse(self.grid, (x, y), axes, angle, 0., 360., self.pen_color, thickness, self.line_type)
  

    def drawEllipse2(self, x, y, major_axis, minor_axis, angle, fill = False):
        self.drawEllipse([x, y], [major_axis / 2, minor_axis / 2], angle, fill)

    def drawText(self, pt, text):
        x = int(pt[0] + self.border)
        y = int(pt[1] + self.border)
        cv2.putText(self.grid, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 0.3, self.pen_color, 1, cv2.LINE_AA)


    def drawText2(self, x1, y1, text):
        self.drawText([x1, y1], text)

    def startPolyPoints(self):
        while len(self.poly_points):
            self.poly_points.pop()

    def addPolyPoint(self, x, y):
        self.poly_points.append((x + self.border, y + self.border))

    def drawPolyPoints(self):
        pts = np.array([self.poly_points], np.int32)
        cv2.fillPoly(self.grid, pts, self.pen_color, self.line_type)

    def inRange(self, pt):
        if (pt.x >= border and pt.y >= border and pt.x < self.grid.cols - border and pt.y < self.grid.rows - border):
           return 1
        else:
           return 0

    def drawPixel(self, pt):
        x = pt[0] + self.border
        y = pt[1] + self.border

        if x >= 0 and y >= 0 and x < self.grid.shape[1] and y < self.grid.shape[0]:
            self.grid[y, x] = self.pen_color

    def getPixel(self, pt):
        x = int(pt[0] + self.border)
        y = int(pt[1] + self.border)

        if x >= 0 and y >= 0 and x < self.grid.shape[1] and y < self.grid.shape[0]:
            return self.grid[y, x]
        else:
            return self.getPixel((0, 0)) # yah silly 
         
    def getPixel2(self, x, y):
        return self.getPixel([x, y])

    def getColor(self, x, y):
        return self.getPixel((x, y))

    def getGrid(self):
        return self.grid[self.border:self.border + self.height, self.border:self.border + self.width]

  # returns true if x,y color is rgb
    def testPixel(self, pt, bgr):
        pix = self.getPixel(pt)

        if pix == bgr:
            return True
        else:
            return False;	


    def drawRegion(self, pixels): # could be changed to pass reference but I've not figured out how to access vector
        for (x, y) in pixels:
            x += self.border
            y += self.border

            self.grid[y, x] = self.pen_color
 
  # blur the window
    def blur(self, size = 3):
        cv2.blur(self.grid, (size, size))

  # put random specks all over the window 
    def speckle(self, fraction = 0.1):
        n = fraction * self.grid.shape[1] * self.grid.shape[0]
        for i in range(n):
            self.setPenColor(0, random.randint(0, 255), random.randint(0, 255))
            self.drawPixel((random.randint(0, self.width), random.randint(0, self.height)))

    def defineMouseCallback(self, onMouse):
        cv2.setMouseCallback(self.window_name, onMouse)

    def moveWindow(self, x,  y):
        cv2.moveWindow(self.window_name, x, y)
        self.winx = x
        self.winy = y

    def moveWindowDelta(self, dx, dy):
        self.winx += dx
        self.winy += dy
        cv2.moveWindow(self.window_name, self.winx, self.winy)

    def hideWindow(self):
        cv2.moveWindow(self.window_name, 5000, 5000)

    def showWindow(self):
        cv2.moveWindow(self.window_name, self.winx, self.winy)  

  # creates the window
    def popWindow(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        self.window_created = True

    def show(self):
        if not(self.window_created):
            self.popWindow()

        cv2.imshow(self.window_name, self.grid)

  # overrides self.grid with mat
    def setMat(self, mat):
        self.grid = mat

  # draw a rectangle around the border
    def drawBorder(self, indent = 4, set_thickness=True):
        orig_thickness = self.pen_thickness
        self.setLineThickness(set_thickness)

        if indent > self.border:
            indent = self.border

        self.drawRectangle((-indent, -indent), (self.width + indent, self.height + indent), False) # draw outline of canvas
        self.setLineThickness(orig_thickness)
  

    def __init__(self, w, h, name, border_width = 0, hide_window = False, blackwhite = False): # constructor
        self.width = w
        self.height = h

        self.window_name = name
        self.border = border_width
        self.window_created = False

        if not(hide_window):
            self.popWindow()

        self.winx = 0
        self.winy = 0

        if blackwhite:  #
            self.grid = np.zeros((h + 2 * self.border, w + 2 * self.border), dtype=np.uint8)
        else:
            self.grid = np.zeros((h + 2 * self.border, w + 2 * self.border, 3), dtype=np.uint8)

        self.poly_points = []

        self.setLineType('solid')
        self.setLineThickness(2)
        self.setPenColor([0, 0, 0])
        self.setCanvasColor(255, 255, 255)
        self.clearWindow()

    def __del__(self):
        cv2.destroyWindow(self.window_name)
