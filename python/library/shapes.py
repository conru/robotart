import numpy as np
from math import cos, sin, acos

class Shape:

    def setID(self, i):
        self.id = i

    def getID(self, i = -1):
        if i >= 0: 
            self.id = 0

        return self.id

    def setPenColor(self, r, g, b):
        self.pen_color = (b, g, r)  # yah, in this order

    def setThickness(self, t = 1):
        self.thickness = t

    def getPenColor(self):
        return self.pen_color

#    std2.string getColorXML():
#            std2.string line
#            line.append(paint_util2.string_format("<color r=\"%i\" g=\"%i\" b=\"%i\"></color>", sef.pen_color[2], sef.pen_color[1], sef.pen_color[0]))
#            return line
#    }
#
#    virtual std2.string getXML():
#            std2.string line = getColorXML()
#            return line
#    }
#
#    virtual std2.string getText(){
#            std2.string line = ""
#            return line
#    }
#
#
#    def toggleBreakPoint(bool toggle):
#            isBreakPo= toggle
#    }
#
#    def draw(DrawWindow *W) { 
#            printf("hey, you should know how to draw yourself (%i x %i)\n",W.width,W.height); 
#    }
#
#    virtual PolyLine* toPolyline(){
#            printf("if you are seeing this message, this class cannot convert to polyline\n")
#            return NULL
#    }
#
#    virtual PixelRegion* toPixelRegion(){
#            printf("if you are seeing this message, this class cannot convert to pixelregion\n")
#            return NULL
#    }
#
    def __init__(self):
        self.id = -1
        self.type = 'shape'
        self.isBreakPoint = False
        self.fill = False
        self.hasPainted = False
        self.hasSimulated = False

class PolyLine(Shape):

    def addPoint(self, pt):
        self.points.append(pt)
#
#	def getXML():
#		std2.string line
#		line.append(paint_util2.string_format("<shape type=\"polyline\" id=\"%i\" breakpoint=\"%i\" thickness=\"%i\">", getID(), self.isBreakPoint, thickness))
#		line.append(Shape2.getColorXML())
#		line.append("<points>")
#		for (i = 0; i < (int)self.points.size(); i++):
#			line.append(paint_util2.string_format("<p x=\"%i\" y=\"%i\"></p>", self.points[i].x, self.points[i].y))
#		}
#		line.append("</points>")
#		line.append("</shape>")
#		return line
#	}
#
#	#create ABB text file for polyline
#	def string getText(){
#		.string line
#		line.append("blue,")
#		for (i = 0; i < (int)self.points.size(); i++){
#			line.append(paint_util2.string_format("%i,%i,", self.points[i].x, self.points[i].y))
#		}
#		line.append(";,")
#		return line
#	}
#
    def draw(self, W):
        color = self.getPenColor()
        W.setPenColor(color)
        W.setLineThickness(self.thickness)

        for i in range(len(self.points) - 1):
            W.drawLine(self.points[i], self.points[i + 1])

#	def PolyLine* toPolyline(){
#            return this

    def getPoints(self):
        return self.points

    def __init__(self):
        Shape.__init__(self)
        self.type = "polyline"
        self.points = []
        self.thickness = 1
        self.fill = False



# bunch of pixels
class PixelRegion(Shape):
#	self._style; # 1=square, 2=circle
#	std2.vector<cv2.Point> points
#
    def addPoint(self,pt, dup_check = False):
        if dup_check:
            if (pt in self.points):
                self.points.append(pt)

#	void addPoint(i, j, dup_check=0: # add poif it doesn't exist yet
#		if (dup_check):
#			found = 0
#			for (n = 0; n < (int)points.size(); n++):
#				if (points[n].x == i && points[n].y == j):
#					found = 1
#					n = (int)points.size()
#				}
#			}
#			if (!found) addPoint(cv2.Point(i, j))
#		}
#		else:
#			addPoint(cv2.Point(i, j))
#		}
#	}
#
    def setStyle(self, s = 1):
        self.style = s
#
#	virtual std2.string getXML():
#		std2.string line
#		line.append(paint_util2.string_format("<shape type=\"pixelregion\" id=\"%i\" breakpoint=\"%i\" thickness=\"%i\" style=\"%i\">", getID(), self.isBreakPoint, thickness, style))
#		line.append(Shape2.getColorXML())
#		line.append("<points>")
#		for (i = 0; i < (int)points.size(); i++):
#			line.append(paint_util2.string_format("<p x=\"%i\" y=\"%i\"></p>", points[i].x, points[i].y))
#		}
#		line.append("</points>")
#		line.append("</shape>")
#		return line
#	}
#
#	#create ABB text file for pixel region
#	virtual std2.string getText(){
#		std2.string line
#		line.append("blue,")
#		for (i = 0; i < (int)points.size(); i++):
#			line.append(paint_util2.string_format("%i,%i,", points[i].x, points[i].y))
#		}
#		line.append(";,")
#		return line
#	}
#
    def draw(self, W):
        color = self.getPenColor()
        W.setPenColor(color)
        W.setLineThickness(1)

        for i in range(len(self.points) -1):
            if self.thickness == 1:
                    W.drawPixel(self.points[i])
            
            else:
                if self.style == 1: # square
                    delx = self.thickness / 2
                    dely = self.thickness / 2

                    W.drawRectangle(self.points[i].x - delx, self.points[i].y - dely,
                                    self.points[i].x + (self.thickness - delx), self.points[i].y + (self.thickness - dely), 1)
                    print("R %i,%i,%i,%i\n", self.points[i].x - delx, self.points[i].y - dely, self.points[i].x + (self.thickness - delx), self.points[i].y + (self.thickness - dely))
 
                else:
                    W.drawEllipse(self.points[i].x, self.points[i].y, self.thickness / 2, self.thickness / 2, 0, 1)
                    print("E %i,%i,%i,%i\n", self.points[i].x, self.points[i].y, self.thickness / 2, self.thickness / 2)
               
            
        
    
#
#	virtual PixelRegion* toPixelRegion(){
#		return this
#	}
#
#	std2.vector<cv2.Point> getPoints(){
#		return this.points
#	}
#
    def __init__(self):
        Shape.__init__(self)

        self.type = "pixelregion"
        self.style = 1
        self.thickness = 1
        self.fill = True
        self.points = []



# filled in region bounded by points
class PolyPoints(Shape):

    def addPoint(self, pt):
        self.points.append(pt)

#	# returns a polyline representation of a PolyPoints (note: just returns the perimeter)
#	virtual PolyLine* toPolyline(: # note: only perimeter
#		PolyLine* PL = PolyLine()
#		for (i = 0; i < (int)self.points.size() - 1; i++) { PL.addPoint(self.points[i]); }
#		PL.addPoint(self.points[0])
#		return PL
#	}
#
#	# returns a pixelregion representation of a rectangle
#	virtual PixelRegion* toPixelRegion():
#		# plan is to draw a temp graphic then convert it to pixels (yah ugly... )
#		minx = 9999999
#		miny = 9999999
#		maxx = 0
#		maxy = 0
#		for (i = 0; i < (int)self.points.size() - 1; i++):
#			if (self.points[i].x > maxx) { maxx = self.points[i].x; }
#			if (self.points[i].x < minx) { minx = self.points[i].x; }
#			if (self.points[i].y > maxy) { maxy = self.points[i].y; }
#			if (self.points[i].y < miny) { miny = self.points[i].y; }
#		}
#
#		unsigned n = self.points.size()
#		npt[] = { n }
#
#		cv2.Po**pself.points = cv2.Point*[1]
#		pself.points[0] = cv2.Point[n]
#		for (size_t i = 0; i < n; i++):
#			pself.points[0][i] = cv2.Point(self.points[i].y - miny, self.points[i].x - minx); # dunno why y,x but seems to work
#		}
#		const cv2.Point* ppt[1] = { pself.points[0] }
#
#		w = maxx - minx + 1
#		h = maxy - miny + 1
#		cv2.Mat grid = cv2.Mat(w, h, CV_8UC3); # 3 channel color
#		grid.setTo(cv2.Scalar(255, 255, 255))
#		fillPoly(grid, ppt, npt, 1, cv2.Scalar(0, 0, 0), 8)
#
#		PixelRegion* PR = PixelRegion()
#		for (i = 0; i < w; i++):
#			for (j = 0; j < h; j++):
#				if (grid.at<cv2.Vec3b>(i, j)[0] == 0: # i,j is in the region
#					PR.addPoint(i + minx, j + miny)
#				}
#			}
#		}
#
#		delete[] pself.points[0]
#		delete[] pself.points
#		return PR
#	}
#
#	virtual std2.string getXML():
#		std2.string line
#		line.append(paint_util2.string_format("<shape type=\"polyself.points\" id=\"%i\" breakpoint=\"%i\" thickness=\"%i\">", getID(), self.isBreakPoint, thickness))
#		line.append(Shape2.getColorXML())
#		line.append("<self.points>")
#		for (i = 0; i < (int)self.points.size(); i++):
#			line.append(paint_util2.string_format("<p x=\"%i\" y=\"%i\"></p>", self.points[i].x, self.points[i].y))
#		}
#		line.append("</self.points>")
#		line.append("</shape>")
#		return line
#	}
#
#	#create ABB text file for polyself._points
#	virtual std2.string getText(){
#		std2.string line
#		line.append("blue,")
#		for (i = 0; i < (int)self._points.size(); i++):
#			line.append(paint_util2.string_format("%i,%i,", self._points[i].x, self._points[i].y))
#		}
#		line.append(";,")
#		return line
#	}
#
    def draw(self, W):
        color = self.getPenColor()
        W.setPenColor(color)
        W.setLineThickness(self.thickness)
        #W.startPolyPoints()
        for point in self.points:
                W.addPolyPoint(point[0], point[1])

        W.drawPolyPoints()
	
#   
    def __init__(self):
        Shape.__init__(self)

        self.type = 'polyline'
        self.thickness = 1
        self.fill = True
        self.points = []

#
#
class RectangleShape(Shape):

    def setCorners(self, x1, y1, x2, y2):
        self.pt1 = (int(x1), int(y1))
        self.pt2 = (int(x2), int(y2))
	

    # returns a polyline representation of a rectangle
    def toPolyline(self): # note: only perimeter
        PL = PolyLine()
        PL.addPoint(self.pt1)
        PL.addPoint((self.pt2[0], self.pt1[1]))
        PL.addPoint(self.pt2)
        PL.addPoint((self.pt1[0], self.pt2[1]))
        PL.addPoint(self.pt1)
        return PL
	
#
#	# returns a pixelregion representation of a rectangle
#	virtual PixelRegion* toPixelRegion():
#		PixelRegion* PR = PixelRegion()
#		for (i = std2.min(self.pt1.x, self.pt2.x); i <= std2.max(self.pt1.x, self.pt2.x); i++):
#			for (j = std2.min(self.pt1.y, self.pt2.y); j <= std2.max(self.pt2.y, self.pt1.y); j++):
#				if (self.fill == 1 || (i == self.pt1.x || i == self.pt2.x || j == self.pt1.y || j == self.pt2.y)):
#					PR.addPoint(i, j)
#				}
#			}
#		}
#		return PR
#	}
#
    def setFill(self, f = 1):
        self.fill = f
#
#	virtual std2.string getXML():
#		std2.string line
#		line.append(paint_util2.string_format("<shape type=\"rectangle\" id=\"%i\" fill=\"%i\" breakpoint=\"%i\">", getID(), fill, self.isBreakPoint))
#		line.append(getColorXML())
#		line.append(paint_util2.string_format("<corners self.pt1x=\"%i\" pt1y=\"%i\" pt2x=\"%i\" pt2y=\"%i\"></corners>",
#			self.pt1.x, self.pt1.y, self.pt2.x, self.pt2.y))
#		line.append("</shape>")
#		return line
#	}
#
#	#create ABB text file for rectangle
#	virtual std2.string getText(){
#		std2.string line
#		line.append("blue,")
#		line.append(paint_util2.string_format("%i,%i,%i,%i,", self.pt1.x, self.pt1.y, self.pt2.x, self.pt2.y))
#		line.append(";,")
#		return line
#	}
#
    def draw(self, W):
        color = self.getPenColor()
        W.setPenColor(color)
        W.drawRectangle(self.pt1, self.pt2, self.fill)
	

    def __init__(self):
        Shape.__init__(self)
        self.type = "rectangle"
        self.fill = False


class EllipseShape(Shape):

#    def setData(self, x, y, r): # circle
#        self.pt = cv2.Point(x, y)
#        self.axes = cv2.Size(r, r)
    

    def setData(self, x, y, width, height = None): # ellipse
        if not(height):
            height = width

        self.pt = (x, y)
        self.axes = (int(width), int(height))
	
#
	# returns a polyline representation of a circle [don't worry about doing a real ellipse for now]
    def toPolyline(self): # note: only perimeter
        PL = PolyLine()
        radius = (self.axes[0] + self.axes[1]) / 4. + .4; # .25 to help anti-aliasing
        #printf("xy=%i,%i r=%f\n",self.pt.x,self.pt.y,radius)
        n = radius * 2
        pi = 3.14159265358979323846; # yah, should find the math var
        for i in range(int(n)):
            rad = 2.*pi*(i / n)
            x = self.pt[0] + radius*cos(rad)
            y = self.pt[1] + radius*sin(rad)
            #printf("%i,%i at %f\n",x,y,rad)
            PL.addPoint((int(x), int(y)))

        PL.addPoint((int(self.pt[0] + radius), int(self.pt[1])))
        return PL
    

	# returns a pixelregion representation of a circle  [don't worry about doing a real ellipse for now]
    def toPixelRegion(self):
        PR = PixelRegion()
        radius = (self.axes[0] + self.axes[1]) / 4. + .4; # .4 to help anti-aliasing

        for dx in range(int(radius) + 1):
            rad = acos(dx / radius)
            dy = sin(rad) * radius
            #printf("dx dy %i %i\n",dx,dy)

            for i in range(int(-dx), int(dx) + 1):
                for j in range(int(-dy), int(dy) + 1):
                    if i == -dx or i == dx or j == -dy or j == dy: # just the rectangle
                        if self.fill or abs(i*j) == dx*dy: # if !self.fill, then just 4 corners
                            PR.addPoint((self.pt[0] + i, self.pt[1] + j), True)
                            #printf(" i,j = %i,%i\n",i,j)
                        
                    
                
            
        
        return PR
    

    def setFill(self, f = True):
        self.fill = f
#
#	virtual std2.string getXML():
#		std2.string line
#		line.append(paint_util2.string_format("<shape type=\"ellipse\" id=\"%i\" fill=\"%i\" x=\"%i\" y=\"%i\" w=\"%d\" h=\"%d\" breakPoint=\"%i\">",
#			getID(), self.fill, self.pt.x, self.pt.y, self.axes.width, self.axes.height, self.isBreakPoint))
#		line.append(getColorXML())
#		line.append("</shape>")
#		return line
#	}
#
#
#	#create ABB text file for an elipse
#	virtual std2.string getText(){
#		std2.string line
#		line.append("blue,")
#		#line.append(paint_util2.string_format("\"%i\",\"%i\",\"%i\",\"%i\",", self.pt1.x, self.pt1.y, self.pt2.x, self.pt2.y))
#		#please no
#		line.append(";,")
#		return line
#	}
#
    def draw(self, W):
        color = self.getPenColor()
        W.setPenColor(color)
        W.drawEllipse(self.pt, self.axes, 0, self.fill)
	

    def __init__(self):
        Shape.__init__(self)
        self.type = "ellipse"
        self.fill = False

##*******  SHAPES ********
#
class Shapes:

    def addShape(self, shape):
        id = shape.getID()
        if (id < 0):
            self.max_id += 1
            shape.setID(self.max_id)

        if id > self.max_id:
            self.max_id = id
        self.shapes.append(shape)
	

##	std2.string getXML():
##		std2.string line = "<shapes>\n"
##		for (i = 0; i < (int)shapes.size(); i++):
##			line.append(shapes[i].getXML())
##			line.append("\n")
##		}
##		line.append("</shapes>\n")
##		return line
##	}
##
##	std2.string getText(){
##		std2.string line = ""
##		for (i = 0; i < (int)self.shapes.size(); i++){
##			line.append(self.shapes[i].getText())
##		}
##		return line
##	}
##
##	void parseXML(pugi2.xml_node *shapes):
##		debug = 0
##
##		for (pugi2.xml_node shape = self.shapes.first_child(); shape; shape = shape.next_sibling()):
##			std2.string type = shape.attribute("type").value()
##			id = shape.attribute("id").as_int()
##			r = shape.child("color").attribute("r").as_int()
##			g = shape.child("color").attribute("g").as_int()
##			b = shape.child("color").attribute("b").as_int()
##			breakPo= shape.attribute("breakPoint").as_int()
##			if (debug) std2.cout << type
##			if (debug) printf(" shape ID:%i\n", id)
##			if (debug) printf(" RGB %d %d %d\n", r, g, b)
##
##			if (type.compare("polyline") == 0):
##				PolyLine *PL = PolyLine()
##				PL.setPenColor(r, g, b)
##				PL.setID(id)
##				thickness = shape.attribute("thickness").as_int()
##				if (breakPo== 1) PL.toggleBreakPoint(true)
##				PL.setThickness(thickness)
##
##				pugi2.xml_node points = shape.child("points")
##				for (pugi2.xml_node po= points.first_child(); point; po= point.next_sibling()):
##					x = point.attribute("x").as_int()
##					y = point.attribute("y").as_int()
##					if (debug) printf(" - po%i %i\n", x, y)
##					PL.addPoint(x, y)
##				}
##				addShape(PL)
##			}
##
##			if (type.compare("polypoints") == 0):
##				PolyPoints *PP = PolyPoints()
##				thickness = shape.attribute("thickness").as_int()
##				PP.setPenColor(r, g, b)
##				PP.setID(id)
##				PP.setThickness(thickness)
##				if (breakPo== 1) PP.toggleBreakPoint(true)
##
##
##				pugi2.xml_node points = shape.child("points")
##				for (pugi2.xml_node po= points.first_child(); point; po= point.next_sibling()):
##					x = point.attribute("x").as_int()
##					y = point.attribute("y").as_int()
##					if (debug) printf(" - po%i %i\n", x, y)
##					PP.addPoint(x, y)
##				}
##				addShape(PP)
##			}
##
##			if (type.compare("pixelregion") == 0):
##				PixelRegion *PR = PixelRegion()
##				PR.setPenColor(r, g, b)
##				PR.setID(id)
##				if (breakPo== 1) PR.toggleBreakPoint(true)
##				style = shape.attribute("style").as_int()
##				thickness = shape.attribute("thickness").as_int()
##				PR.setStyle(style)
##				PR.setThickness(thickness)
##
##				pugi2.xml_node points = shape.child("points")
##				for (pugi2.xml_node po= points.first_child(); point; po= point.next_sibling()):
##					x = point.attribute("x").as_int()
##					y = point.attribute("y").as_int()
##					if (debug) printf(" - po%i %i\n", x, y)
##					PR.addPoint(x, y)
##				}
##				addShape(PR)
##			}
##
##			if (type.compare("rectangle") == 0):
##				RectangleShape *R = RectangleShape()
##				R.setPenColor(r, g, b)
##				R.setID(id)
##				if (breakPo== 1) R.toggleBreakPoint(true)
##
##
##				pugi2.xml_node corners = shape.child("corners")
##				pt1x = corners.attribute("pt1x").as_int()
##				pt1y = corners.attribute("pt1y").as_int()
##				pt2x = corners.attribute("pt2x").as_int()
##				pt2y = corners.attribute("pt2y").as_int()
##				if (debug) printf(" - corners %i %i %i %i\n", pt1x, pt1y, pt2x, pt2y)
##				R.setCorners(pt1x, pt1y, pt2x, pt2y)
##				self.fill = shape.attribute("fill").as_int()
##				R.setFill(self.fill)
##				addShape(R)
##			}
##
##			if (type.compare("ellipse") == 0):
##				EllipseShape *E = EllipseShape()
##				E.setPenColor(r, g, b)
##				if (breakPo== 1) E.toggleBreakPoint(true)
##				E.setID(id)
##
##				x = shape.attribute("x").as_int()
##				y = shape.attribute("y").as_int()
##				w = shape.attribute("w").as_int()
##				h = shape.attribute("h").as_int()
##				if (debug) printf(" - corners %i %i %d %d\n", x, y, w, h)
##				E.setData(x, y, w, h)
##				self.fill = shape.attribute("fill").as_int()
##				E.setFill(self.fill)
##				addShape(E)
##			}
##		}
##	}
##
    def drawAll(self, W):
        for shape in self.shapes:
            shape.draw(W)
     	
     

##	# draw only one command by its shape id
##	# optional ugly hack to specify an override color [b/c can't figure out how to SS.at(id).setColor(r,g,b)]
##	void drawOne(DrawWindow *W, id = 0, r = -1, g = -1, b = -1):
##		for (i = 0; i < (int)self.shapes.size(); i++):
##			cv2.Scalar color
##			if (self.shapes[i].getID() == id):
##				if (r > -1 && g > -1 && b > -1): # save and set color
##					color = self.shapes[i].getPenColor()
##					self.shapes[i].setPenColor(b, g, r)
##				}
##				self.shapes[i].draw(W)
##				if (r > -1 && g > -1 && b > -1): # put back color
##					self.shapes[i].setPenColor(color[2], color[1], color[0])
##				}
##			}
##		}
##	}
##
##	void removeShape(id):
##		for (i = 0; i < (int)self.shapes.size(); i++):
##			if (self.shapes[i].getID() == id):
##				self.shapes.erase(self.shapes.begin() + i)
##				i = (int)self.shapes.size() + 1
##			}
##		}
##	}
##
##	void removeShapeAt(index):
##		self.shapes.erase(self.shapes.begin() + index)
##	}
##
##	Shape* at(position):
##		return self.shapes.at(position)
##	}
##
##	Shape* getById(id):
##		for (size_t i = 0; i < self.shapes.size(); i++):
##			if (self.shapes[i].getID() == id):
##				return self.shapes.at(i)
##			}
##		}
##		return NULL
##	}
##
##	# ABC: should be renamed to something like getNumShapes as length is ambiguous
##	length() { return self.shapes.size(); }
##
##	void clear():
##		self.shapes.clear()
##		self.max_id = 0
##	}
##
##	void swap(pos1, pos2):
##		std2.iter_swap(self.shapes.begin() + pos1, self.shapes.begin() + pos2)
##	}
##
    def __init__(self):
        self.max_id = 0
        self.shapes = []
