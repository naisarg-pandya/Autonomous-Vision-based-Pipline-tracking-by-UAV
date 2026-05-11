#!/usr/bin/python3
import rospy
import cv2
import numpy as np
from custom_msg_python.msg import custom
from sensor_msgs.msg import Image
from sensor_msgs.msg import Joy
import math


def callback(data):

    
    A = data.coordinate
    
    D_1 = np.array([320,240])
    
    angle = A[2]
    theta = -angle
    #theta = -25
    cx = A[0]
    yaw_rate = -0.08*(math.tanh(0.04*theta))
    
    error = (cx- 320)/320
    
    V_y = -0.26*math.tanh(1*(error)) - 0.003*error
    threshold = 0.2

    
  
    error = error*320
        
    if V_y >threshold:
        V_y = threshold
    if V_y<-threshold:
        V_y =-threshold
        
    V_x = 0.78/((0.1078*abs(theta) +0.098*abs(error)+1.8))
    thershold = 0.18
    if V_x >threshold:
        V_x = threshold
    if V_x<-threshold:
        V_x =-threshold     
        
    #V_x = 0
    file1 = open("/home/xavier/custom_ws/src/custom_msg_python/recorded_data/classical_vision.txt", "a")
    data = [str(error),',',str(theta),',',str(V_x),',',str(V_y) , ',', str(yaw_rate)] 
    file1.writelines(data)
    file1.writelines(["\n"])
    file1.close()
    
    
    print(V_x, V_y, yaw_rate)
    msg = custom()
    msg.x = error
    msg.coordinate = [V_x, V_y, yaw_rate]
    pub.publish(msg)
    

    
if  __name__ == "__main__":
    rospy.init_node("tracking_vel")
    sub = rospy.Subscriber("homographic_transformed_parameter",custom,callback)
    pub = rospy.Publisher("body_frame_vel", custom, queue_size=2) 
    rate = rospy.Rate(30)
    rospy.spin()
'''    
    if error<20 and error>-20 and yaw_rate < 0.04:
        V_x = 0.2
    elif error<50 and error>-50 and yaw_rate<0.04:
        V_x = 0.07
    else:
        V_x = 0
    
'''   
    
