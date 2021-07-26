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
	frame_blur = cv2.GaussianBlur(frame_gray,(5,5),0) 

	# Color Thresholding 
	ret, thresh = cv2.threshold(frame_blur, 60, 255, cv2.THRESH_BINARY_INV) 

	# Assuming there is only one contour conts[0] 
	contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE) 
	x, y, w, h = cv2.boundingRect(contours[0])  

	# Draws a rectangle around the first contour of the frame 
	frame = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR) 
	cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)  
	cv2.drawContours(frame, contours, -1, (0, 255, 0), 1)

	# Draws our two line on the rectangle 
	cv2.line(frame, (x, y + h // 3), (x + w, y + h // 3), (255,0,0), 1)  
	cv2.line(frame, (x, y + h // 3 * 2), (x + w, y+ h // 3 * 2), (255,0,0), 1)	
 
	points = []  
	y1 = y + h // 3 
	y2 = y + h // 3 * 2   
	contour = contours[0] 

	# appends the intersection point between lines and contours to a list  
	for y in (y1,y2):  
		points.append(contour[contour[:,:,1] == y])  
		test = contour[contour[:,:,1] == y]  
	
	# draws the intersection point between lines and contours from the list 
	for x in points:   
		# coordinates = tuple(x)
		cv2.circle(frame, (x[0][0],x[0][1]), 3, (0,0,255), 3) 
		cv2.circle(frame, (x[1][0],x[1][1]), 3, (0,0,255), 3)
				
 
	# Display the resulting frame on screen 
	cv2.imshow('display', frame)  

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

# After the loop release the capture object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()

