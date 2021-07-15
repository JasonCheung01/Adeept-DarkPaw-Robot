# Psuedocode: 
# 1) Start the Camera (done) 
# 2) Filter an image by color (done) 
# 3) Pick a threshold for the image to have a binary image (done) 
# 3a) Reason why we go from RGB to binary is b/c it allows us to select pixels of interest according to where they lie in colour space (explanation)  
# 4) Detect the line (done) 
# 5) Robot moves while simultaneously trying to keep track of the line 
# 6) Robot stops when it reaches the end of the line

import os
import cv2 
import time 
import numpy as np  
import move 
import SpiderG
SpiderG.move_init()  
from base_camera import BaseCamera 
from camera_opencv import CVThread
from camera_opencv import Camera  
 
CVRun = 1
linePos_1 = 440
linePos_2 = 380
lineColorSet = 0		# 255 for white line and 0 for black line 
frameRender = 1
findLineError = 20		# How far off it is from the center coordinate when tracking for a line		
setCenter = 320			# Set center coordinate when tracking for a line 

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)
 
# Motor Speed for Robot Movements (from thread reading it seems like it is control by wsb) 


# Initialize Steady Camera Mode for Robot 
SpiderG.move_init()
SpiderG.steadyModeOn()

while(True):
     	
	# Capture the video frame by frame
	ret, frame = vid.read()  

	# if we are viewing a video and did not grab a frame, we have reached the end 
	if frame is None: 
		break    
		
	# Convert to gray scale
	frame_findline = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
	
	# Thresholding
	retval, thresh = cv2.threshold(frame_findline, 0, 250, cv2.THRESH_OTSU) 
	
	# Eroding the image (computes a local minimum over the area of given kernel)
	frame_findline = cv2.erode(thresh, None, iterations=6)   

	colorPos_1 = frame_findline[linePos_1] 
	colorPos_2 = frame_findline[linePos_2] 

	# Line detection algorithm
	try:  
		# sums of array elements over a given axis (for a white line)
		lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet) 
		lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

		# return elements chosen from x or y depending on condition (also for a white line)
		lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
		lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet) 

		if lineColorCount_Pos1 == 0:
			lineColorCount_Pos1 = 1
		if lineColorCount_Pos2 == 0:
			lineColorCount_Pos2 = 1 
	  	
		left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1-1]
		right_Pos1 = lineIndex_Pos1[0][0]
		center_Pos1 = int((left_Pos1 + right_Pos1) / 2)

		left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2-1]
		right_Pos2 = lineIndex_Pos2[0][0]
		center_Pos2 = int((left_Pos2 + right_Pos2) / 2)

		center = int((center_Pos1 + center_Pos2) / 2)   
	
		# Code below tracks the line 

		# Syntax: cv2.line(image, start_point, end_point, color, thickness)
		# Forms a white cross that goes through bottom part of the retangular box	
		cv2.line(frame,(left_Pos1,(linePos_1+30)),(left_Pos1,(linePos_1-30)),(255,128,64),1)
		cv2.line(frame,(right_Pos1,(linePos_1+30)),(right_Pos1,(linePos_1-30)),(64,128,255),)
		cv2.line(frame,(0,linePos_1),(640,linePos_1),(255,255,64),1)

		# Forms a white cross that goes through the top part of the rectangular box
		cv2.line(frame,(left_Pos2,(linePos_2+30)),(left_Pos2,(linePos_2-30)),(255,128,64),1)
		cv2.line(frame,(right_Pos2,(linePos_2+30)),(right_Pos2,(linePos_2-30)),(64,128,255),1)
		cv2.line(frame,(0,linePos_2),(640,linePos_2),(255,255,64),1)
		
		# Forms a black cross that goes through the middle of the rectangular box 
		cv2.line(frame,((center-20),int((linePos_1+linePos_2)/2)),((center+20),int((linePos_1+linePos_2)/2)),(0,0,0),1)
		cv2.line(frame,((center),int((linePos_1+linePos_2)/2+20)),((center),int((linePos_1+linePos_2)/2-20)),(0,0,0),1) 
		
		if center > (setCenter + findLineError):  
			SpiderG.walk('turnright')  

		elif center < (setCenter - findLineError): 	 
			SpiderG.walk('turnleft') 
		
		else: 
			SpiderG.walk('forward')  
	
	# if an exception occur during the try clause, go here
	except:   
		center = None  
		SpiderG.move_init() 
		SpiderG.servoStop()
		pass 

	# Display the resulting frame 
	# Syntax: cv2.imshow('window_name', image) 
	cv2.imshow('display', frame)  

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Release Steady Camera Mode 
SpiderG.steadyModeOff() 

# After the loop release the capture object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()

