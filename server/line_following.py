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
 
linePos_1 = 440
linePos_2 = 380
lineColorSet = 0	# 255 for white line and 0 for black line 
findLineError = 40 
setCenter = 320		

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

# Video capture initialization
vid = cv2.VideoCapture(Camera.video_source)

while(True):
     	
	# Capture the video frame by frame
	ret, frame = vid.read()      
		
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
	retval, thresh = cv2.threshold(frame_gray, 0, 250, cv2.THRESH_OTSU) 
	frame_findline = cv2.erode(thresh, None, iterations=6)  

	colorPos_1 = frame_findline[linePos_1] 
	colorPos_2 = frame_findline[linePos_2] 

	try:  
		# sums of array elements over a given axis 
		lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet) 
		lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

		# return elements chosen from x or y depending on condition (also for a white line)
		lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
		lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet) 

		#-------------------------------------------------------#
		# Line Detection Algorithm Below:  
		#-------------------------------------------------------#

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

		#-------------------------------------------------------#
		# Displays current line color that robot is tracking:  
		#-------------------------------------------------------#

		#if lineColorSet == 255:  
			#cv2.putText(frame,('Following White Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA) 
		#elif lineColorSet == 0: 
			#cv2.putText(frame,('Following Black Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)		 
		#else: 
			#cv2.putText(frame,('No Line Detected'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)

		#------------------------------------------------------------------------------------------#
		# Track line by analyzing two pixels in parallel and utilizes the information it detects  
		#------------------------------------------------------------------------------------------# 

		# Forms a cross that goes through bottom part of the retangular box	
		cv2.line(frame,(left_Pos1,(linePos_1+30)),(left_Pos1,(linePos_1-30)),(255,128,64),1)		# vertical line of cross (orange)
		cv2.line(frame,(right_Pos1,(linePos_1+30)),(right_Pos1,(linePos_1-30)),(64,128,255),)		# vertical line of cross (blue)
		cv2.line(frame,(0,linePos_1),(640,linePos_1),(255,255,64),1)					# horizontal line of rectangular box (turquoise)

		# Forms a cross that goes through the top part of the rectangular box
		cv2.line(frame,(left_Pos2,(linePos_2+30)),(left_Pos2,(linePos_2-30)),(255,128,64),1)
		cv2.line(frame,(right_Pos2,(linePos_2+30)),(right_Pos2,(linePos_2-30)),(64,128,255),1)
		cv2.line(frame,(0,linePos_2),(640,linePos_2),(255,255,64),1)
		
		# Forms a slope that connects the center coordinate for both the orange and blue vertical line
		cv2.line(frame,(left_Pos1,linePos_1),(left_Pos2, linePos_2),(198,52,235),1) 			# orange vertical line	 
		cv2.line(frame,(right_Pos1,linePos_1),(right_Pos2, linePos_2),(198,52,235),1) 			# blue vertical line

		# Forms a black cross that goes through the middle of the rectangular box 
		cv2.line(frame,((center-20),int((linePos_1+linePos_2)/2)),((center+20),int((linePos_1+linePos_2)/2)),(0,0,0),1)
		cv2.line(frame,((center),int((linePos_1+linePos_2)/2+20)),((center),int((linePos_1+linePos_2)/2-20)),(0,0,0),1) 
		
		#---------------------------------------------------------#
		# Line Following Algorithm: 
		#---------------------------------------------------------#  
	
		print (center) 

		if center > (setCenter + findLineError): #(320 + 5)  
			SpiderG.walk('turnleft') 
			#move.dove_move_tripod(2, 5, 'right')  
		elif center < (setCenter - findLineError): # (320 -5)
			SpiderG.walk('turnright')    
			#move.dove_move_tripod(2, 5, 'left')	   
		else:   
			SpiderG.walk('forward')  
			#move.dove_move_tripod(2, 5, 'forward')  

	except:   
		center = None
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

