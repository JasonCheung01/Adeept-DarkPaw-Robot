import os
import cv2	
import numpy as np  
import SpiderG	

SpiderG.move_init()   
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

# elliminates contour that is smaller than a certain size 
def contours_ellimination(list, area_size): 
	contours_update = []

	# Once it finds the contour, we will elliminate all contour that is smaller than a certain size 
	for i in list: 
		area = cv2.contourArea(i) 

		if (area > area_size): 
			contours_update.append(i)

	return contours_update


# Controls robot movement for line following 
def line_following(input, slope, alignment_error, val1, val2):  
	if (abs(slope) < val1 or abs(alignment_error) > val2):
		if (m > 0):
			if (alignment_error > 0):
				cv2.putText(input,('Walking forward 1'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				SpiderG.walk('forward')
			else:
				cv2.putText(input,('Turning Left'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				SpiderG.walk('turnleft')

		else:
			if (alignment_error > 0):
				cv2.putText(input,('Turning Right'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				SpiderG.walk('turnright')

			else:
				cv2.putText(input,('Walking Forward 2'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
				SpiderG.walk('forward')

	else:
		cv2.putText(input,('Walking Forward 3'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)
		SpiderG.walk('forward') 

# calculates midpoint
def midpoint(val1, val2):
        midpoint = (val1 + val2) // 2

        return midpoint 

#---------------------------------------# 
# Main Program: 
#---------------------------------------# 

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

# Variable Initialization
count_backward = 0 

# Video Recording Initialization 
#video_capture = cv2.VideoWriter('adeept_line_following.avi', -1 , 30, (640,480))

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read()     
	
	# Adjust brightness of video frame	
	bright_img = cv2.convertScaleAbs(frame, alpha = 1 / (brightness_adjustment(frame, 150)), beta = 0) 
	
	# Convert to grayscale	  
	frame_gray = cv2.cvtColor(bright_img, cv2.COLOR_BGR2GRAY)   

	# Gaussian Blur (reduce image noise (brightness or color information) and details)	 
	frame_blur = cv2.GaussianBlur(frame_gray,(3,3),0)  

	# Color Thresholding 
	ret, thresh = cv2.threshold(frame_blur, 55, 255, cv2.THRESH_BINARY_INV)   
	
	try:  
		# Finds our contour
		contours,hierarchy = cv2.findContours(thresh.copy(),1, cv2.CHAIN_APPROX_NONE)
		C = None   
	  
		# Elliminate contours smaller than a certain size 
		contours_update = contours_ellimination(contours,500) 

		# Finds the biggest existing contour
		if len(contours_update) > 0: 
			C = max(contours_update, key = cv2.contourArea)   
			x, y, w, h = cv2.boundingRect(C)  	 

			# Draws bounding rectangle box on biggest contour
			frame = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) 
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1) 
			cv2.drawContours(frame, contours_update, -1, (0, 255, 0), 1)

			# Draws our two horizontal line on the bounding rectangle box 
			cv2.line(frame, (x, y + h // 3), (x + w, y + h // 3), (255,0,0), 1)  
			cv2.line(frame, (x, y + h // 3 * 2), (x + w, y + h // 3 * 2), (255,0,0), 1)	
	  
			contour = C 

			# Draws the intersection point between our first horizontal line and the contour
			y1_points = contour[contour[:,:,1] == (y + h // 3)] 
			cv2.circle(frame, (y1_points[0][0], y1_points[0][1]), 3, (0,0,255), 3) 
			cv2.circle(frame, (y1_points[1][0], y1_points[1][1]), 3, (0,0,255), 3) 

                        # Draws the intersection point between our second horizontal line and the contour
			y2_points = contour[contour[:,:,1] == (y + h // 3 * 2)]
			cv2.circle(frame, (y2_points[0][0], y2_points[0][1]), 3, (0,0,255), 3)
			cv2.circle(frame, (y2_points[1][0], y2_points[1][1]), 3, (0,0,255), 3) 
		
			# Calculate and draw the midpoint of the intersection point between our first horizontal line and the contour 
			y1_x_mp = midpoint(y1_points[0][0], y1_points[1][0])
			y1_y_mp = midpoint(y1_points[0][1], y1_points[1][1]) 
			cv2.circle(frame, (y1_x_mp, y1_y_mp), 3, (127,0,63), 3)  

			# Calculate and draw the midpoint of the intersection point between our second horizontal line and the contour 
			y2_x_mp = midpoint(y2_points[0][0], y2_points[1][0]) 
			y2_y_mp = midpoint(y2_points[0][1], y2_points[1][1]) 
			cv2.circle(frame, (y2_x_mp, y2_y_mp), 3, (127,0,63), 3) 

			# Calculate and draw the slope of the two midpoint  
			m = (y2_y_mp - y1_y_mp) / (y2_x_mp - y1_x_mp) 
			cv2.line(frame, (y1_x_mp, y1_y_mp), (y2_x_mp, y2_y_mp), (127,0,63), 3) 

			# Calculate and draw the center x and y coordinate of the two midpoint
			center_mp_x = midpoint(y1_x_mp, y2_x_mp)
			center_mp_y = midpoint(y1_y_mp, y2_y_mp) 
			cv2.circle(frame, (center_mp_x, center_mp_y), 3, (252,186,3), 3) 

			# Calculate how far off the center y coordinate is from center of OpenCV window frame (Xm - 1/2 * width) 
			alignment_error = center_mp_x - (0.5 * frame.shape[1]) 

			# Display slope of the midpoint and alignment error on screen 
			cv2.putText(frame,('Slope: ' + str(m)), (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)   
			cv2.putText(frame,('Alignment Error: ' + str(alignment_error)), (30,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA)  

			# Controls line Following Movements
			line_following(frame,m,alignment_error,2,160)	 

			count_backward = 0 

		# else if there is no contour, stop the robot 	
		else:
			if (count_backward < 100): 
				count_backward += 1
				cv2.putText(frame,('Walking Backward (count: '+str(count_backward)+')'), (30,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128), 1, cv2.LINE_AA) 
				SpiderG.walk('backward')
			else:
				SpiderG.move_init()
				SpiderG.servoStop()  	
	except: 	   
		pass 		
 
	# Display the resulting frame on screen  
	cv2.imshow('display', frame) 

	#video_capture.write(frame)    

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break 

# After the loop release the capture object
vid.release() 

#video_capture.release()

# Destroy all the windows
cv2.destroyAllWindows()


