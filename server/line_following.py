import os
import cv2	
import numpy as np 
import move		
import Kalman_filter  
import SpiderG	

SpiderG.move_init()   
from skimage.draw import line 
from base_camera import BaseCamera 
from camera_opencv import CVThread
from camera_opencv import Camera

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read()   

	# Binarization, filter out noise
	#frame = np.where(frame < 100, 0, 255).astype(np.uint8) 

	# Convert to grayscale	 
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  

	# Gaussian Blur (reduce image noise (brightness or color information) and details)	 
	frame_blur = cv2.GaussianBlur(frame_gray,(3,3),0) 

	# Color Thresholding 
	ret, thresh = cv2.threshold(frame_blur, 60, 255, cv2.THRESH_BINARY_INV)  
	
	# Erode image
	#frame_findline = cv2.erode(thresh, None, iterations=6)  

	try:
		# Assuming there is only one contour conts[0] 
		contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE) 
		x, y, w, h = cv2.boundingRect(contours[0])  

		# Draws a rectangle around the first contour of the frame 
		frame = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) 
		cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)  
		cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

		# Draws our two line on the rectangle 
		cv2.line(frame, (x, y + h // 3), (x + w, y + h // 3), (255,0,0), 1)  
		cv2.line(frame, (x, y + h // 3 * 2), (x + w, y + h // 3 * 2), (255,0,0), 1)	
 
		#points = []  
		y1 = y + h // 3 
		y2 = y + h // 3 * 2   
		contour = contours[0] 

		#----------------------------------------------------------------#
		# Initial Method for interestction of line and contour: 
		#----------------------------------------------------------------#

		# appends the intersection point between lines and contours to a list  
		# for y in (y1,y2):  
			#points.append(contour[contour[:,:,1] == y])  
			#test = contour[contour[:,:,1] == y]  
			#print(test) 

		#y1_x1 = points[0][0][0]
                #y1_x2 = points[0][1][0]
                #y2_x1 = points[1][0][0]
                #y2_x2 = points[1][1][0]

                #x1 = (y1_x1 + y1_x2)/2
                #x2 = (y2_x1 + y2_x2)/2

                #m = (y2-y1)/(x2-x1)

                #cv2.line(img, (x1,y1), (x2,y2), (255, 255, 0), 1)

                #draws the intersection point between lines and contours from the list
                #for x in points:   
                        #coordinates = tuple(x) 
                        #print(x[0][0])
                        #print("hello") 
                        #print(x[0][1]) 
                        #print(x)
                        #print("-----------")
                        #cv2.circle(frame, (x[0][0], x[0][1]), 3, (0,0,255), 3) # draws the two circle on the left
                        #cv2.circle(frame, (x[1][0], x[1][1]), 3, (0,0,255), 3) # draws the two circle on the right
                        #cv2.line(frame, (x[0][0], x[1][1]),(x[0][1], x[1][0]), (0,0,255), 2)
                        #cv2.line(frame, (x[1][0]), (x[1][1]), (0,0,255), 2)
 
		#----------------------------------------------------------------#  

		# Draws the intersection point between our first horizontal line and the contour
		y1_points = contour[contour[:,:,1] == y1] 
		cv2.circle(frame, (y1_points[0][0], y1_points[0][1]), 3, (0,0,255), 3) 
		cv2.circle(frame, (y1_points[1][0], y1_points[1][1]), 3, (0,0,255), 3) 
		
		# Calculate and draw the midpoint of the intersection point between our first horizontal line and the contour 
		y1_x_mp = (y1_points[0][0] + y1_points[1][0]) // 2 
		y1_y_mp = (y1_points[0][1] + y1_points[1][1]) // 2 
		#cv2.circle(frame, (y1_x_mp, y1_y_mp), 3, (127,0,63), 3)  

		# Draws the intersection point between our second horizontal line and the contour
		y2_points = contour[contour[:,:,1] == y2] 
		cv2.circle(frame, (y2_points[0][0], y2_points[0][1]), 3, (0,0,255), 3) 
		cv2.circle(frame, (y2_points[1][0], y2_points[1][1]), 3, (0,0,255), 3)  

		# Calculate and draw the midpoint of the intersection point between our second horizontal line and the contour 
		y2_x_mp = (y2_points[0][0] + y2_points[1][0]) // 2 
		y2_y_mp = (y2_points[0][1] + y2_points[1][1]) // 2 
		#cv2.circle(frame, (y2_x_mp, y2_y_mp), 3, (127,0,63), 3) 

		# Calculate and draw the slope of the midpoint  
		m = (y2_y_mp - y1_y_mp) / (y2_x_mp - y1_x_mp) 
		cv2.line(frame, (y1_x_mp, y1_y_mp), (y2_x_mp, y2_y_mp), (127,0,63), 3) 

		# Display slope of the midpoint on screen 
		cv2.putText(frame,('Slope: ' + str(m)), (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)   
	
		if (m > -50 and m < 50): 
			SpiderG.walk('forward') 
		#elif (m <= 5): 
			#SpiderG.walk('turnleft') 
		#else: 
			#SpiderG.walk('turnright') 	
	except: 
		#m = 0	
		SpiderG.move_init() 
		SpiderG.servoStop()   
		pass 		
 
	# Display the resulting frame on screen 
	cv2.imshow('display', frame)  

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

# After the loop release the capture object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()

