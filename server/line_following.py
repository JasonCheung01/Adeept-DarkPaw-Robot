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

count = -1

while(True): 
	# Capture the video frame by frame
	ret, frame = vid.read() 

	count+=1 
	print(count)  

	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)     
	frame_blur = cv2.GaussianBlur(frame_gray,(5,5),0)	# reduce image noise (brightness or color information)  and details 
	ret, thresh = cv2.threshold(frame_blur, 60, 255, cv2.THRESH_BINARY_INV) 
	contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE) 

	if len(contours) > 0: 
		c = max(contours, key=cv2.contourArea) 
		M = cv2.moments(c) 
	
		try:
			cx = int(M['m10']/M['m00']) 
			cy = int(M['m01']/M['m00']) 
			cv2.putText(frame,('Something Detected'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA) 
		except: 
			cv2.putText(frame,('Nothing Detected'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA) 

		cv2.line(frame,(cx,0),(cx,720),(255,0,0),1) 
		cv2.line(frame,(0,cy),(1280,cy),(255,0,0),1)	 

		cv2.drawContours(frame, contours, -1, (0,255,0), 1) 
		
		print(cx) 

		if cx >= 630: 
			SpiderG.walk('turnleft')  
			cv2.putText(frame,('Turning Left'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)  

		if cx < 630 and cx > 250: 
			SpiderG.walk('forward') 
			cv2.putText(frame,('Going Forward'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)  

		if cx <= 250:  
			SpiderG.walk('turnright') 
			cv2.putText(frame,('Turning Right'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA) 

		else:
			cv2.putText(frame,('No Line Detected'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)    
			SpiderG.move_init() 
			SpiderG.servoStop() 

	# Display the resulting frame on screen 
	cv2.imshow('display', frame)  

	# Closes CV2 display by pressing the 'q' button (you may use any desired button of your choice)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# After the loop release the capture object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()

