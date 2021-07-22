import os
import cv2	
import numpy as np 
import move		
import Kalman_filter  
import SpiderG	

SpiderG.move_init()   
from base_camera import BaseCamera 
from camera_opencv import CVThread
from camera_opencv import Camera

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read()   

	# Convert to grayscale	
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 

	# Gaussian Blur (reduce image noise (brightness or color information) and details)	 
	frame_blur = cv2.GaussianBlur(frame_gray,(5,5),0) 
	
	# Color Thresholding
	ret, thresh = cv2.threshold(frame_blur, 60, 255, cv2.THRESH_BINARY_INV)  

	# Finds all the contours of the frame and take the first contour
	contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)  
	cnt = contours [0]   
 
	# Draw a rectangle around the first contour of the frame
	x,y,w,h = cv2.boundingRect(cnt)
	cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),1) 

	# Display the resulting frame on screen 
	cv2.imshow('display', frame)  

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

# After the loop release the capture object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()

