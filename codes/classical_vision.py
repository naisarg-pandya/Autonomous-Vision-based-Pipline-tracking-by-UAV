#!/usr/bin/python3
import rospy
import cv2
import numpy as np
import imutils
from custom_msg_python.msg import custom

cap = cv2.VideoCapture(0)
frame_width =640
frame_height = 480
cap.set(3,frame_width)
cap.set(4,frame_height)

rospy.init_node('pipe_tracking', anonymous=False)
pub=rospy.Publisher('discrete_points', custom, queue_size=2 )
rate=rospy.Rate(10)
msg = custom()

while not rospy.is_shutdown():
    ret, image = cap.read()
    if not ret:
        break
    img_r = np.array(image[:,:,0])
    res2 = cv2.blur(img_r ,(3,3))
    ret_hsv, HSV_thers = cv2.threshold(res2,145,255,cv2.THRESH_BINARY)
    kernel_e = np.ones((12,12),np.uint8)
    cv2.erode(HSV_thers,kernel_e,iterations = 20)
    cnts_hsv, her_hsv = cv2.findContours(HSV_thers , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #lower = np.array([5,1,1])
    #upper = np.array([166,253,255])
    #thers1 = cv2.inRange(imgHSV,lower,upper)
    conts_hsv = sorted(cnts_hsv, key=cv2.contourArea, reverse=True)[:10] 
    
    image_binary = np.zeros((240,320),np.uint8)
    if len(conts_hsv)>0:
        cv2.drawContours(image_binary,[max(conts_hsv, key=cv2.contourArea)],-1,(255,255,255),-1)
        
    cnts, her = cv2.findContours(HSV_thers , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10] 
    
    
    if len(conts) >0:
    
        cnt = conts[0]
        area = cv2.contourArea(cnt)
        
        if area>15000 and area<150000:
    
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
        
            centre = rect[0]
            rect_angle = rect[2]
            print(rect_angle)
            d1 = np.sqrt((box[2][0] - box[3][0])**2)
            d2 = np.sqrt((box[1][0] - box[2][0])**2)
            rows,cols =image.shape[:2]
            [vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0,0.01,0.01)
            left = int((-x*vy/vx)+y)
            right = int(((cols-x)*vy/vx)+y)
            #print((cols-1,right),(0,left))

            angle = np.degrees(np.arctan((right-left)/((cols-1)-0)))
            if left>right:
                angle = -rect_angle
                #angle = -(90+rect_angle)
                cp_x = box[1][0]+(box[0][0] - box[1][0])/2
                cp_y = box[1][1]+(box[0][1] - box[1][1])/2            
            elif right>left:
                #angle = -rect_angle
                angle = 90-rect_angle
            if angle == -90 or angle == 90:
               angle =0
            #print(angle)
            cv2.line(image,(cols-1,right),(0,left),(255,0,0),2)
            print(centre, "angle",angle)
            cv2.drawContours(image, [box], 0, (0,255,0),3)

            msg.coordinate = [centre[0],centre[1], angle]
            
            pub.publish(msg)
    #cv2.imshow('HSV_thers', image)
    #cv2.imshow('c_img', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if rospy.is_shutdown():
        capture.release()
        
