#!/usr/bin/python3

import sys
sys.path.append('../library')

import cv2

from drawwindow import DrawWindow
from shapes import Shapes, PolyLine, PolyPoints, PixelRegion, RectangleShape, EllipseShape
import random
#
#debug=0
##cv2.RNG random(12345)
#
#
## add some lines
w=400
h=500
##PolyLine *PL
S = Shapes()

for i in range(5):
    PL = PolyLine()
    PL.setPenColor(random.randint(50,250),random.randint(50,250),random.randint(50,250))
    for i in range(10):
        PL.addPoint((random.randint(100,w-100),random.randint(100,h-100)))
    S.addShape(PL)
    

# add a poly poregion
PP = PolyPoints()

ww=100
delx=20
dely=200

PP.setPenColor(255,255,0)
PP.addPoint((ww/4.0 + delx, 7*ww/8.0 + dely))
PP.addPoint((3*ww/4.0 + delx, 7*ww/8.0 + dely))
PP.addPoint((3*ww/4.0 + delx, 13*ww/16.0 + dely))
PP.addPoint((11*ww/16.0 + delx, 13*ww/16.0 + dely))
PP.addPoint((19*ww/32.0 + delx, 3*ww/8.0 + dely))
PP.addPoint((3*ww/4.0 + delx, 3*ww/8.0 + dely))
PP.addPoint((3*ww/4.0 + delx, ww/8.0 + dely))
PP.addPoint((26*ww/40.0 + delx, ww/8.0 + dely))
PP.addPoint((26*ww/40.0 + delx, ww/4.0 + dely))
PP.addPoint((22*ww/40.0 + delx, ww/4.0 + dely))
PP.addPoint((22*ww/40.0 + delx, ww/8.0 + dely))
PP.addPoint((18*ww/40.0 + delx, ww/8.0 + dely))
PP.addPoint((18*ww/40.0 + delx, ww/4.0 + dely))
PP.addPoint((14*ww/40.0 + delx, ww/4.0 + dely))
PP.addPoint((14*ww/40.0 + delx, ww/8.0 + dely))
PP.addPoint((ww/4.0 + delx, ww/8.0 + dely))
PP.addPoint((ww/4.0 + delx, 3*ww/8.0 + dely))
PP.addPoint((13*ww/32.0 + delx, 3*ww/8.0 + dely))
PP.addPoint((5*ww/16.0 + delx, 13*ww/16.0 + dely))
PP.addPoint((ww/4.0 + delx, 13*ww/16.0 + dely))
S.addShape(PP)

## test overwriting with pixel region
#PPtoPR = PP.toPixelRegion()
#PPtoPR.setPenColor(0,255,255)
##S.addShape(&PPtoPR)

# add pixel region
PR = PixelRegion()
PR.setPenColor(0,0,random.randint(0,244))
for i in range(100):
    PR.addPoint((random.randint(0,w),random.randint(h-100,h)))

S.addShape(PR)

## add rectangle
R = RectangleShape()
R.setCorners(20,20,50,60)
R.setPenColor(200,0,0)
S.addShape(R)
R = RectangleShape()
R.setCorners(20,120,50,160)
R.setPenColor(0,0,200)
S.addShape(R)

R = RectangleShape()
R.setCorners(w-100,20,w-50,260)
R.setPenColor(200,0,220)
R.setFill(1)
S.addShape(R)

RtoPL = R.toPolyline()
RtoPL.setPenColor(0,255,0)
S.addShape(RtoPL)

## test overwriting with pixel region
#RtoPR = R.toPixelRegion()
#RtoPR.setPenColor(0,255,255)
##  S.addShape(&RtoPR)
#
# add circle
E = EllipseShape()
E.setFill(1)
E.setPenColor(200,0,0)
E.setData(30,200,20.0) # circle
S.addShape(E)

EtoPL = E.toPolyline()
EtoPL.setPenColor(0,255,0)
S.addShape(EtoPL)

EtoPR = E.toPixelRegion()
EtoPR.setPenColor(255,255,0)
S.addShape(EtoPR)

E = EllipseShape()
E.setPenColor(200,0,0)
E.setData(130,200,20.0,40.)
S.addShape(E)

## draw the shapes
W = DrawWindow(w,h,"Generated Shapes",hide_window=False)
W.clearWindow(230,230,230) # default background is white
S.drawAll(W)
W.show()

### save to XML
##xml = "<?xml version=\"1.0\"?>\n"
##xml.append(S.getXML())
##myfile.open ("shapes.xml")
##myfile << xml
##myfile.close()
##if debug:
##    std2.cout << xml
##
### load up a drawing from XML
##
##pugi2.xml_document doc
##pugi2.xml_parse_result result = doc.load_file("shapes.xml")
##
##if (debug) std2.cout << "Load result: " << result.description() << std2.endl
##
##pugi2.xml_node shapes = doc.child("shapes")
##Shapes SS
##SS.parseXML(&shapes)
##
##xml = "<?xml version=\"1.0\"?>\n"
##xml.append(SS.getXML())
##if debug:
##    std2.cout << xml
#
#W2 = DrawWindow(w,h,"Shapes Loaded via XML") # w,h
#W2.clearWindow(230,230,230) # default background is white
#SS.drawAll(W2)
#W2.show()

## remove some shapes by ID
#for i in range(4, 7):
#    SS.removeShape(i)

#W3 = DrawWindow(w, h, "removed shapes") # w,h
#W3.clearWindow(230,230,230) # default background is white
#SS.drawAll(W3)
#W3.show()

while True:
    k = cv2.waitKey(33)
    #if (k>0) { printf("key = %d\n",k); 
    if k==27:
        break  # Esc key to stop

    if k == 'n':
        pass 
