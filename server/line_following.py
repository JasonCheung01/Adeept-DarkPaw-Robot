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

#---------------------------------------# 
# List of our Functions: 
#---------------------------------------#

# adjust brightness of video frame
def brightness_adjustment(input, min_brightness): 
	cols, rows = input.shape[-2:]

	brightness = np.sum(input) / (255 * cols * rows)
	ratio = brightness / min_brightness

	return ratio
          
#---------------------------------------# 
# Main Program: 
#---------------------------------------# 

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

# Variable Initialization
count_backward = 0

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read()   
	
	# Adjust brightness of video frame	
	ratio = brightness_adjustment(frame, 150)	
	bright_img = cv2.convertScaleAbs(frame, alpha = 1 / ratio, beta = 0)

	# Convert to grayscale	 
	frame_gray = cv2.cvtColor(bright_img, cv2.COLOR_BGR2GRAY) 

	# Gaussian Blur (reduce image noise (brightness or color information) and details)	 
	frame_blur = cv2.GaussianBlur(frame_gray,(3,3),0) 

	# Color Thresholding 
	ret, thresh = cv2.threshold(frame_blur, 50, 255, cv2.THRESH_BINARY_INV)   
	
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

			count_backward = 0

			# Draws the intersection point between our first horizontal line and the contour
			y1_points = contour[contour[:,:,1] == y1] 
			cv2.circle(frame, (y1_points[0][0], y1_points[0][1]), 3, (0,0,255), 3) 
			cv2.circle(frame, (y1_points[1][0], y1_points[1][1]), 3, (0,0,255), 3) 
		
			# Calculate and draw the midpoint of the intersection point between our first horizontal line and the contour 
			y1_x_mp = (y1_points[0][0] + y1_points[1][0]) // 2 
			y1_y_mp = (y1_points[0][1] + y1_points[1][1]) // 2 
			cv2.circle(frame, (y1_x_mp, y1_y_mp), 3, (127,0,63), 3)  

			# Draws the intersection point between our second horizontal line and the contour
			y2_points = contour[contour[:,:,1] == y2] 
			cv2.circle(frame, (y2_points[0][0], y2_points[0][1]), 3, (0,0,255), 3) 
			cv2.circle(frame, (y2_points[1][0], y2_points[1][1]), 3, (0,0,255), 3)  

			# Calculate and draw the midpoint of the intersection point between our second horizontal line and the contour 
			y2_x_mp = (y2_points[0][0] + y2_points[1][0]) // 2 
			y2_y_mp = (y2_points[0][1] + y2_points[1][1]) // 2 
			cv2.circle(frame, (y2_x_mp, y2_y_mp), 3, (127,0,63), 3) 

			# Calculate and draw the slope of the midpoint  
			m = (y2_y_mp - y1_y_mp) / (y2_x_mp - y1_x_mp) 
			cv2.line(frame, (y1_x_mp, y1_y_mp), (y2_x_mp, y2_y_mp), (127,0,63), 3) 

			# Display slope of the midpoint on screen 
			cv2.putText(frame,('Slope: ' + str(m)), (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)   

                        # Calculate and draw the center x and y coordinate of the two midpoint 
			center_mp_y = (y1_y_mp + y2_y_mp) // 2  
			center_mp_x = (y1_x_mp + y2_x_mp) // 2 
			cv2.circle(frame, (center_mp_x, center_mp_y), 3, (252,186,3), 3)   

			# Calculate how far off the center y coordinate is from center of OpenCV window frame (Xm - 1/2 * width) 
			alignment_error = center_mp_x - (0.5 * frame.shape[1])    

			# Display alignment error on screen  
			cv2.putText(frame,('Alignment Error: ' + str(alignment_error)), (30,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA) 

			if (abs(m) < 2 or abs(alignment_error) > 160): 
				if (m > 0): 
					if (alignment_error > 0):  
						cv2.putText(frame,('Walking forward 1'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
						#SpiderG.walk('forward') 
					else: 
						cv2.putText(frame,('Turning Left'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)  
						#SpiderG.walk('turnleft')  
	
				else:  
					if (alignment_error > 0): 
						cv2.putText(frame,('Turning Right'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA) 
						#SpiderG.walk('turnright') 

					else: 
						cv2.putText(frame,('Walking Forward 2'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA) 
						#SpiderG.walk('forward')  

			else:  
				cv2.putText(frame,('Walking Forward 3'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				#SpiderG.walk('forward') 

		# else if there is no contour, stop the robot 	
		else:
			if (count_backward < 100):
				count_backward = count_backward+1
				cv2.putText(frame,('Walking Backward (count: '+str(count_backward)+')'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				#SpiderG.walk('backward')
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


