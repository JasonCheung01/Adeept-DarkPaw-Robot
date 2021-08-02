import os
import cv2	
import numpy as np 
import move		
import Kalman_filter  
import SpiderG	 
import math 
import time

SpiderG.move_init()   
from skimage.draw import line 
from base_camera import BaseCamera 
from camera_opencv import CVThread
from camera_opencv import Camera

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

# Initialization of variables  
queue = []  
queue_size = 10

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read()   

	# Binarization, filter out noise
	#frame = np.where(frame < 100, 0, 255).astype(np.uint8) 
	
	# Adjust brightness of video frame	
	cols, rows = frame.shape[-2:] 
	brightness = np.sum(frame) / (255 * cols * rows)
	 
	minimum_brightness = 150 
	ratio = brightness / minimum_brightness 
	
	bright_img = cv2.convertScaleAbs(frame, alpha = 1 / ratio, beta = 0)
	#bright_img = cv2.convertScaleAbs(frame, alpha = 1, beta = 255 * (minimum_brightness - brightness))

	# Convert to grayscale	 
	frame_gray = cv2.cvtColor(bright_img, cv2.COLOR_BGR2GRAY) 

	# Gaussian Blur (reduce image noise (brightness or color information) and details)	 
	frame_blur = cv2.GaussianBlur(frame_gray,(3,3),0) 

	# Color Thresholding 
	ret, thresh = cv2.threshold(frame_blur, 50, 255, cv2.THRESH_BINARY_INV)  
	
	# Erode image
	#frame_findline = cv2.erode(thresh, None, iterations=6)  
	
	try:  
		# Assuming there is only one contour conts[0]
		contours,hierarchy = cv2.findContours(thresh.copy(),1, cv2.CHAIN_APPROX_NONE)
		C = None 

		if len(contours) > 0: 
			C = max(contours, key = cv2.contourArea)   
			x, y, w, h = cv2.boundingRect(C)  	 

			frame = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) 
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1) 
			cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

			# Draws our two line on the rectangle 
			cv2.line(frame, (x, y + h // 3), (x + w, y + h // 3), (255,0,0), 1)  
			cv2.line(frame, (x, y + h // 3 * 2), (x + w, y + h // 3 * 2), (255,0,0), 1)	
	  
			y1 = y + h // 3 
			y2 = y + h // 3 * 2   
			contour = C 

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
		    
			#if (abs(m) < 2):  
				# Add slope into our queue 
				#queue.append(m)

				# Do not execute the rest of the code below until queue size is full 
				#if (len(queue) <= queue_size): 
					#continue
 
				# After that, we’re going to use the oldest slope of the queue to make our decision
				#m = queue.pop(0) 
  
				#if m > 0:  
					#SpiderG.walk('turnleft') 
 
				#if m < 0:   
					#SpiderG.walk('turnright')  

			#else: 
				#SpiderG.walk('forward')  

		# else if there is no contour, stop the robot 	
		else:    
			SpiderG.move_init()
			SpiderG.servoStop()  	
	except: 	   
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

