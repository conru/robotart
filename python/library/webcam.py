import cv2
import numpy as np

# Packages simple drawing commands for the simulator display window
class Webcam:
#  cv2.Point2f self.webcamQuad[4] # four corners of webcam input
#  cv2.Point2f self.zoomQuad[4] # four corners of which region of the webcam is desired
#  cv2.Point2f self.canvasQuad[4] # four corners of desired mapped output

    # reset the map used to map webcam to another matrix/frame
    def resetMapping(self):
        # The 4 points where the mapping is to be done , from top-left in clockwise order
        self.canvasQuad[0] = [0, 0]
        self.canvasQuad[1] = [self.map_width, 0]
        self.canvasQuad[2] = [self.map_width, self.map_height]
        self.canvasQuad[3] = [0, self.map_height]

        frame = self.getFrame() # get a new frame from camera
        self.zoomQuad[0] = [0, 0]
        self.zoomQuad[1] = [frame.shape[1], 0]
        self.zoomQuad[2] = [frame.shape[1], frame.shape[0]]
        self.zoomQuad[3] = [0, frame.shape[0]]
  

    #sets up zoom on webcam
    def setWebcamZoom(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.zoomQuad[0] = [x1, y1]
        self.zoomQuad[1] = [x2, y2]
        self.zoomQuad[2] = [x3, y3]
        self.zoomQuad[3] = [x4, y4]


  #recieves current zoom on webcam.
    def getWebcamZoom(self):
        return self.zoomQuad.reshape((-1))

  # used by calibrateWebcam to have user click on the 4 corners of webcam's desired region
    def zoomMouseCallBackFunc(self, event, x, y, flags, userdata):
        if event == cv2.EVENT_LBUTTONDOWN:
          print('Setting zoom corner {} to {}, {}'.format(self.webcam_corner + 1, x, y))
          self.zoomQuad[self.webcam_corner][0] = x * 2
          self.zoomQuad[self.webcam_corner][1] = y * 2

  # sets the desired region of the webcam 
    def calibrateWebcam(self, skip_reset = False):
        #cv2.Mat webcam
        #cv2.Mat mapped_webcam # this is the webcam mapped to the same dimensions as the final canvas pixels
        #    cv2.Mat canvas # this is the "canvas"
        mapped_name = "Mapped Webcam"
        webcam_name = "Calibration Window"

        # QMessageBox instruct
        # instruct.show()
        # instruct.setText('Use Keys 1-4, 'x' or 'esc' to quit')
        # instruct.setInformativeText(''); 

        cv2.namedWindow(webcam_name, 1)
        cv2.moveWindow(webcam_name, 20, 20)
        cv2.setMouseCallback(webcam_name, self.zoomMouseCallBackFunc)

        cv2.namedWindow(mapped_name, 1)

        if not(skip_reset):
            self.resetMapping()

        #cv2.Mat scaledWebcam
        self.webcam_corner = 0
        #HWND hwnd1 = (HWND)cvGetWindowHandle('Mapped Webcam')
        #HWND hwnd2 = (HWND)cvGetWindowHandle('Calibration Window')
        while True: #   IsWindowVisible(hwnd1)  IsWindowVisible(hwnd2)):
            webcam = self.getFrame(3) # get a new frame from camera (blend 3 frames for better clarity)

            scaledWebcam = cv2.resize(webcam, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow(webcam_name, scaledWebcam)
            cv2.moveWindow(mapped_name, 40 + scaledWebcam.shape[1], 20)

            mapped_webcam = self.getMappedFrame()
            cv2.imshow(mapped_name, mapped_webcam)

            k = cv2.waitKey(33)
            if k == 27 or k == ord('x'): # Esc key to stop
                break
            
            elif k == ord('1'):
              self.webcam_corner = 0
              print("Click on the desired region's upper left corner")
            
            elif k == ord('2'):
              self.webcam_corner = 1
              print("Click on the desired region's upper right corner")
            
            elif k == ord('3'):
              self.webcam_corner = 2
              print("Click on the desired region's lower right corner")
            
            elif k == ord('4'):
              self.webcam_corner = 3
              print("Click on the desired region's lower left corner")
        
        #instruct.close()
        print('Webcam calibration matrix defined')
        cv2.destroyWindow(mapped_name)
        cv2.destroyWindow(webcam_name)


    # returns a 2x4 array which is the mapping of a frame to the canvas mapping
    def getMapLambda(self, frame):
        # Get the Perspective Transform Matrix i.e. lambda
        frame_lambda = cv2.getPerspectiveTransform(np.float32(self.webcamQuad), np.float32(self.canvasQuad))

        return frame_lambda


  # sets frame to a mapping of the webcam 
    def getMappedFrame(self, loops = 0, blackwhite = False):
        webcam = self.getFrame(loops, blackwhite) # get a new frame from camera

        # Get the Perspective Transform Matrix i.e. lambda
        zoom_lambda = cv2.getPerspectiveTransform(np.float32(self.zoomQuad), np.float32(self.webcamQuad))

        # Apply the Perspective Transform just found to the src image
        webcam = cv2.warpPerspective(webcam, zoom_lambda, (webcam.shape[1], webcam.shape[0]))

        webcam_lambda = self.getMapLambda(webcam)

        # Apply the Perspective Transform just found to the src image
        return cv2.warpPerspective(webcam, webcam_lambda, (self.map_width, self.map_height))
      

    #set the size of the webcam (in pixels)
    def setMapSize(self, w, h): # this is the projection of the webcam to an arbitrary size
        self.map_height = h
        self.map_width = w
        self.resetMapping()
    
    #set whether the webcam looks like a camera pointed at you, or a mirror.
    def setFlip(self, flip): # set 1 to flip over the webcam
        self.flip_webcam = flip
  
    #returns an integer to do with the frame.
    def getFrame(self, loops = 0, blackwhite = False):
        if self.cam_id == 0:

            if self.cam0.isOpened():  # check if we succeeded
                retval, frame = self.cam0.read()

                if self.flip_webcam:
                    frame = cv2.flip(frame, -1) # horizontal and vertically

                if blackwhite:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                if loops > 0:
                    for i in range(loops):
                        #print('get frame loop %i\n',i)
                        temp_webcam = self.getFrame() # get a new frame from camera
                        frame = cv2.addWeighted(temp_webcam, 0.1, frame, 0.9, 0)

                # The 4 points that select quadilateral on the input , from top-left in clockwise order
                # These four pts are the sides of the rect box used as input (used for mapping to another frame/matrix)
                self.webcamQuad[0] = [0, 0]
                self.webcamQuad[1] = [frame.shape[1], 0]
                self.webcamQuad[2] = [frame.shape[1], frame.shape[0]]
                self.webcamQuad[3] = [0, frame.shape[0]]

                return frame
          
            else:
                print("Cam 0 didn't open")
              
        return None
  

    #shows the webcam
    def showWebcam(self):
        if not(self.cam0.isOpened()):
            print('your webcam is not attatched correctly.')
            return
    
        mapped_name = 'Mapped Webcam'
        cv2.namedWindow(mapped_name, 1)

        #HWND hwnd = (HWND)cvGetWindowHandle('Mapped Webcam')
        while True: #   IsWindowVisible(hwnd)):
            mapped_webcam = self.getMappedFrame()
            cv2.imshow(mapped_name, mapped_webcam)
            k = cv2.waitKey(33) #stall
            if k == 27 or k == ord('x'):
                break

            cv2.destroyWindow(mapped_name)
  

#  #takes a picture via webcam.
#  cv2.Mat getWebcamSnap(cv2.Mat grid):
#    if !self.cam0.isOpened()):
#      print('your webcam is not attatched correctly.\n')
#      return cv2.Mat(1, 1, 1)
#    }
#    print('Press any key to take a picture \n')
#    cv2.Mat mapped_webcam
#
#    char mapped_name[] = 'Mapped Webcam'
#    cv2.namedWindow(mapped_name, 1)
#
#    done = 0
#    frozen = 0
#
#    #If any key is pressed, frames stop updating.
#    #HWND hwnd = (HWND)cvGetWindowHandle('Mapped Webcam')
#    while (!done): #   IsWindowVisible(hwnd)):
#      if !frozen):
#	getMappedFrame(mapped_webcam)
#	cv2.imshow(mapped_name, mapped_webcam)
#      }
#
#      k = cv2.waitKey(27) #stall
#      if k != -1):
#	frozen = 1
#	getMappedFrame(mapped_webcam)
#	grid = mapped_webcam
#	cv2.imshow(mapped_name, mapped_webcam)
#	done = 1
#      }
#      if k == 27){
#	frozen = 0
#	done = 1
#      }
#    }
#    if frozen == 0):
#      print('No picture saved\n')
#      cv2.destroyWindow(mapped_name)
#      return cv2.Mat(1, 1, 1)
#    }
#    else:
#      print('picture saved\n')
#      cv2.destroyWindow(mapped_name)
#      return grid
#    }
#
#  }
#
#  #changes the current webcam.
#  def switchWebcam():
#    self.currentCamera++
#    self.cam1 = new cv2.VideoCapture(self.currentCamera)
#    if self.cam1.isOpened()) self.cam0 = self.cam1
#    else:
#      self.cam0 = new cv2.VideoCapture(0)
#      self.currentCamera = 0
#    }
#  }
#
#  #determines how similar two colors are.
#  colorCloseness(cv2.Vec3b c1, cv2.Vec3b c2):
#    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])
#  }
#
#  #used to determine if the painting looks correct.
#  def judge(cv2.Mat ideal):
#    width, height, done
#    #r, b
#    cv2.Vec3b pen_color_vec
#
#    width = ideal.size().width
#    height = ideal.size().height
#    done = 0
#
#    cv2.Mat toGovernate = cv2.Mat()
#    char mapped_name[] = 'Mapped Webcam'
#    cv2.namedWindow(mapped_name, 1)
#
#    done = 0
#    # HWND hwnd = (HWND)cvGetWindowHandle('Mapped Webcam')
#    while (!done): #   IsWindowVisible(hwnd)):
#      getMappedFrame(toGovernate)
#
#      right = 0
#      wrong = 0
#
#      for (i = 0; i < width; i++): #loop.shape[0]
#	for (j = 0; j < height; j++): #loop columns
#	  cv2.Vec3b desired_color = ideal.at<cv2.Vec3b>(i, j) #what we're aiming for
#
#	  #don't paover canvas we didn't put art on
#	  if desired_color[0] != 255  desired_color[1] != 255  desired_color[2] != 255):
#	    cv2.Vec3b desired_color = ideal.at<cv2.Vec3b>(i, j) #what we're aiming for
#	    cv2.Vec3b webcam_color = toGovernate.at<cv2.Vec3b>(i, j) #what the webcam sees
#
#	    closeness = colorCloseness(desired_color, webcam_color)
#	    cdiff = desired_color[0] - webcam_color[0] + desired_color[1] - webcam_color[1] + desired_color[2] - webcam_color[2]
#
#	    if cdiff > 255): cdiff = 255; }  #too far off?  just set to pure blue
#	    if cdiff < -255): cdiff = -255; } #too far off?  just set to pure red
#
#	    if cdiff >= 0):
#	      pen_color_vec[0] = cdiff #blue
#	      pen_color_vec[1] = 0 #green
#	      pen_color_vec[2] = 0 #red
#	    }
#	    else:
#	      pen_color_vec[0] = 0 #blue
#	      pen_color_vec[1] = 0 #greeen
#	      pen_color_vec[2] = -cdiff #red
#	    }
#
#	    toGovernate.at<cv2.Vec3b>(cv2.Point(j, i)) = pen_color_vec
#
#	    if closeness < 50): right++; }
#	    else : wrong++; }
#
#	  }
#	}
#      }
#
#      #status text in top left corner.
#      cv2.rectangle(toGovernate, cv2.Point(0, 0), cv2.Point(200, 12), cv2.Scalar(200, 200, 200), -1)
#      char text[50]
#      sprint(text, '%.0f%%  OK:%i TODO:%i', (double)100.*right / (right + wrong), right, wrong)
#      cv2.putText(toGovernate, text, cv2.Point(10, 10), cv2.FONT_HERSHEY_DUPLEX, 0.3, cv2.Scalar(0, 0, 0), 1, CV_AA)
#      cv2.imshow(mapped_name, toGovernate)
#
#      k = cv2.waitKey(33)
#      if k == 27 or k == int('m')): done = 1; }
#

    def setCameraId(self, id):
        self.currentCamera = id

    def __init__(self, width = 600, height = 600):  # constructor

        self.cam_id = 0
        self.map_width = width
        self.map_height = height
        self.flip_webcam = False
        self.webcam_corner = 0
        self.currentCamera = 0 #-1
        self.canvasQuad = np.empty((4, 2))
        self.zoomQuad = np.empty((4, 2))
        self.webcamQuad = np.empty((4, 2))

        self.cam0 = cv2.VideoCapture(self.currentCamera) # open the default camera
        if self.cam0.isOpened(): 
            self.resetMapping()

