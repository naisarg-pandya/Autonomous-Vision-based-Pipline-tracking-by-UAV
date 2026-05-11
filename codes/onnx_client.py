#!/usr/bin/python3
import rospy
import math
from custom_msg_python.msg import custom
import socket
import pickle  
import numpy as np
import timeit

n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
n.connect(("localhost",1808))
print("got connected")

rospy.init_node('onxx_client_pub', anonymous=False)
pub=rospy.Publisher('parameter', custom, queue_size=1 )
angle_array =[0]*5
while not rospy.is_shutdown():
    data = n.recv(4096)
    N = pickle.loads(data)
    D = N[1]
    cx = D[0]
    cy = D[1]
    angle = D[2]
    angle_array.append(angle)
    
    if len(angle_array) >5:
        del angle_array[0]
    Derivative = angle_array[-1] - angle_array[-2]
    if Derivative > 20:
        print("=="*10)
        angle = angle_array[-2]
        
    
    msg = custom()
    msg.coordinate = [cx,cy,angle]
    pub.publish(msg)
    print(cx,cy,angle)
    

