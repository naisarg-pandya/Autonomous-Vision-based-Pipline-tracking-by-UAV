#!/usr/bin/python3
import rospy
import cv2
import numpy as np
import message_filters
from custom_msg_python.msg import custom
from sensor_msgs.msg import Image
from sensor_msgs.msg import Joy
import math
from geometry_msgs.msg import QuaternionStamped
import tf


def sub():
    print("data_recived")
    attitude = message_filters.Subscriber("/dji_sdk/attitude", QuaternionStamped)
    b_vel = message_filters.Subscriber('body_frame_vel',  custom)

    
    merge = message_filters.ApproximateTimeSynchronizer([attitude,b_vel],10,0.1,allow_headerless=True)
    merge.registerCallback(callback)
    rospy.spin()
    
def callback(q,data):
   
    pub = rospy.Publisher('/dji_sdk/flight_control_setpoint_ENUvelocity_yawrate', Joy, queue_size = 2)
    pub_d = rospy.Publisher('depth_info', custom, queue_size = 2)
    V_D = data.coordinate
    #print('data_received')
    error_y = data.x
    v_x = V_D[0]
    v_y = V_D[1]
   
    yaw_rate = V_D[2]
    
    
    quat = q.quaternion
    quat_list = [quat.x, quat.y, quat.z, quat.w]
    (phi, theta, psi) = tf.transformations.euler_from_quaternion(quat_list)

    V_x = math.cos(psi)*v_x - math.sin(psi)*v_y
    V_y = math.sin(psi)*v_x + math.cos(psi)*v_y

    if yaw_rate > 0.1:
        yaw_rate = 0.1
    if yaw_rate<-0.1:
        yaw_rate = -0.1

    msg = Joy()
    msg.axes = [V_x,V_y,0,yaw_rate]
    pub.publish(msg)
    print(V_x,V_y,0,yaw_rate)
    
    rospy.sleep(0)
    
if __name__=='__main__':
   rospy.init_node('obj_cordi', anonymous = True)
   try:
      sub()
   except rospy.ROSInterruptException:
      pass
      
'''    

'''   

