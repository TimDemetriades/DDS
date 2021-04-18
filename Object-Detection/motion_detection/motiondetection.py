# Python program to detect motion using OpenCV

# import OpenCV, time, and Pandas
import cv2
import time
import pandas
#import datetime class from datetime
from datetime import datetime

# Assign static background to None (null)
static_back = None

# List when any motion is detected
motion_list = [None, None]

# Time of movement
time = []

# Initializing DataFrame, first column is start time, second is end time
df = pandas.DataFrame(columns = ['Start', 'End'])

# Capturing video
video = cv2.VideoCapture(0)
#video = cv2.VideoCapture('assets/drone_vid3.mp4')

buffer_count = 0
# Infinite while loop to treat stack of images as video
while True:
    status, frame = video.read()    # returns capture status and frame (numpy array)
    
    # Initialize motion
    motion = 0    # (0 means no motion)
    
    # Convert color image to gray scale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Convert gray scale image to Gaussian Blue (reduce noise and detail to better detect motion)
    gaussian_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    
    if buffer_count > 150:
        static_back = None
        buffer_count = 0
    
    buffer_count += 1
    # In first iteration assign value of static_back to first frame of video
    if static_back is None:
        static_back = gaussian_frame
        continue
    
    # Difference between static background and current frame
    diff_frame = cv2.absdiff(static_back, gaussian_frame)
    
    # If difference is greater than 30 it will show white color (255)
    # Params: source (should be grayscale image), threshold value, value to give if pixel value > threshold, threshold style
    threshold_frame = cv2.threshold(diff_frame, 40, 255, cv2.THRESH_BINARY)[1]
    threshold_frame = cv2.dilate(threshold_frame, None, iterations = 2)
    
    # Find contour/outline of moving image
    # Params: source, contour retrieval mode, contour approximation method
    contours, hierarchy = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < 500:    # smaller number means it will detect smaller objects and make more rectangles
            continue    # do not set motion = 1
        motion = 1
        
        (x, y, w, h) = cv2.boundingRect(contour)
        # Make green rectangle around the moving object
        # Params: what to draw on, top left postion, bottom right position, color, thickness (-1 to fill)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
    # Append status of motion
    motion_list.append(motion)
    
    motion_list = motion_list[-2:]   # remove last 2 values?
    
    # Append start time of motion
    if motion_list[-1] == 1 and motion_list[-2] == 0:    # last value is 1 and second to last is 0 (start of motion)
        time.append(datetime.now())
        
    # Append end time of motion
    if motion_list [-1] == 0 and motion_list[-2] == 1:    # last value is 0 and second to last is 1 (end of motion)
        time.append(datetime.now())
        
    # Display image in gray scale
    # cv2.imshow('Gray Scale Frame', gray_frame)
    
    # Display difference in current frame and static frame (first frame)
    # cv2.imshow('Difference Frame', diff_frame)
    
    # Display black and white image in which if intensity difference > 30 it will appear white
    cv2.imshow('Threshold Frame', threshold_frame)
    
    # Display color frame with green rectangles around moving objects
    cv2.imshow('Color frame', frame)
    
    if cv2.waitKey(1) == ord('q'):    # checks to see if q key is pressed
        if motion == 1:
            time.append(datetime.now())    # append end time of movement if something is moving when stopped
        break
    
# Append time of motion to DataFrame
for i in range(0, len(time), 2):
    df = df.append({'Start':time[i], 'End':time[i + 1]}, ignore_index = True)

# Create csv of time of movements
df.to_csv('time_of_movements.csv')

video.release()    # release camera
cv2.destroyAllWindows()    # destroy all windows















