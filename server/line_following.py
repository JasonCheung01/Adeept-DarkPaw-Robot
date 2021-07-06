# Psuedocode: 
# 1) Start the Camera 
# 2) Filter an image by color (considering using RGB) 
# 3) Pick a threshold for the image to have a binary image 
# 4) Detect the line  
# 5) Robot moves while simultaneously trying to keep track of the line 
# 6) Robot stops when it reaches the end of the line

import os
import cv2 
from base_camera import BaseCamera 
from camera_opencv import CVThread
from camera_opencv import Camera  

vid = cv2.VideoCapture(Camera.video_source)
  
while(True):
      
	# Capture the video frame by frame
	ret, frame = vid.read() 

	if frame is None: 
		break
	
	# convert the video frame from BGR to RBG 
	# CV2 uses BRG by default
	frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	thresh = cv2.threshold(frame, 105, 255, cv2.THRESH_BINARY) 	

	# Display the resulting frame
	cv2.imshow('frame', frame) 

	# the 'q' button is set as the
	# quitting button you may use any
	# desired button of your choice
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# After the loop release the cap object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()


