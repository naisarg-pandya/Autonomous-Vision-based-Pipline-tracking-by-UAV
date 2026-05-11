#!/usr/bin/python3
import rospy
import cv2
import numpy as np
from custom_msg_python.msg import custom
from sensor_msgs.msg import Image
from sensor_msgs.msg import Joy
import math
from geometry_msgs.msg import TwistStamped


def callback(data):

    
    A = data.coordinate
    
    D_1 = np.array([320,240])
    angle = A[2]
    theta = -angle
    cx = A[0]
    

    error = (cx - 320)/320
    e_l.append(error)
   
    if  len(e_l) > 10:
        del e_l[0]
    error_int = (1/3)*((e_l[-10]+e_l[-1])+(4*(e_l[-2]+e_l[-4]+e_l[-6]+e_l[-8]))+(2*(e_l[-3]+e_l[-5]+e_l[-7]+e_l[-9])))
    #print(error_int)
    c = 7.2
    d = 0.04
    e = 0.18
    n = 0
    S = c*error +d*(error_int)
    V_y =-(e/c)*math.tanh(S) - (1/c)*(error) -n*((e_l[-1]-e_l[-2])/0.1)
    
    #print(V_y, 'derivative', (e_l[-1]-e_l[-2])/0.1)
    
    theta = theta/90
    e_yaw.append(theta)
    
    if  len(e_yaw) > 10:
        del e_yaw[0]
            
    error_y_int = (1/3)*((e_yaw[-10]+e_yaw[-1])+(4*(e_yaw[-2]+e_yaw[-4]+e_yaw[-6]+e_yaw[-8]))+(2*(e_yaw[-3]+e_yaw[-5]+e_yaw[-7]+e_yaw[-9])))    
    
    c_y = 6.1
    d_y = 0.01
    e_y = 0.04
    n_y = 0
    S_yaw = c_y*theta + d_y*error_y_int
    
    
    yaw_rate = -(e_y/c_y)*math.tanh(S_yaw) - (1/c_y)*(theta) -n_y*((e_yaw[-1]-e_yaw[-2])/0.1)
    
    
    
    # lateral_velocity
    threshold = 0.2
    
    
  
    
        
    if V_y >threshold:
        V_y = threshold
    if V_y<-threshold:
        V_y =-threshold
    
    #V_x = 0.4/((0.0355*abs(theta) +0.1263*abs(error)+1.5))
    #yaw_rate = 0
    theta = theta*90
    error = error*320    
    
    V_x = 0.8/((0.1078*abs(theta) +0.098*abs(error)+1.8))
   # V_x = 0.1
    if abs(theta) >30:
        V_x = 0.04
    thershold = 0.2
    if V_x >threshold:
        V_x = threshold
    if V_x<-threshold:
        V_x =-threshold     



            
    print(V_x, V_y, yaw_rate)

    msg = TwistStamped()
    msg.twist.linear.x = V_x
    msg.twist.linear.y = V_y
    msg.twist.linear.z = V_z 
    pub.publish(msg)    
    

    
if  __name__ == "__main__":
    rospy.init_node("tracking_vel")
    global e_yaw, e_l,name
    e_l = [0]*10
    e_yaw = [0]*10
    
    
    sub = rospy.Subscriber("homographic_transformed_parameter",custom,callback)
    #pub = rospy.Publisher("body_frame_vel", custom, queue_size=2)
    pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=2)
    rate = rospy.Rate(30)
    rospy.spin()
    
'''    
    file1 = open("/home/xavier/custom_ws/src/custom_msg_python/recorded_data/sliding_onnx_"+name+".txt", "a")
    data = [str(error),',',str(theta),',',str(V_x),',',str(V_y) , ',', str(yaw_rate)] 
    file1.writelines(data)
    file1.writelines(["\n"])
    file1.close()    
'''    
