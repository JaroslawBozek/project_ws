#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import sensor_msgs.msg
import random
import numpy as np
from geometry_msgs.msg import Twist
from itertools import *
from operator import itemgetter




Lin_x = 0
PI = 3.141
Kp = 0.02
Ang_z = 0
Limit = 0.8
Ticks = 0
Timer = 300
Flag = 0
False_signal_counter = 0
False_turn_counter = 0


def Scan_Function_v2(data):
    laser_angles = np.arange(len(data.ranges))
    laser_ranges = np.array(data.ranges)
    laser_limited = (laser_ranges > Limit)
    laser_ranges = list(laser_angles[laser_limited])
    
    gap_limit = 25
    gap_list = []    
	
    for a, b in groupby(enumerate(laser_ranges), lambda (i,x):i-x):
        gap_list.append(map(itemgetter(1), b))
    gap_list.sort(key=len)
    largest_gap = gap_list[-1]

    min_angle, max_angle = largest_gap[0]*((data.angle_increment)*180/PI), largest_gap[-1]*((data.angle_increment)*180/PI)
    average_gap = (max_angle - min_angle)/2
	
    turn_angle = min_angle + average_gap

    global Lin_x
    global Ang_z
    global Ticks
    global Flag
    global Timer
    global False_signal_counter
    global False_turn_counter

    Flag = 0
    #Ignorowanie zaklocen
    for i in range (100, 620):
        if laser_limited[i] == 0:
            False_signal_counter = False_signal_counter + 1

            if False_signal_counter > 60:
               Flag = 1 
        else:
            False_singal_counter = 0

    if turn_angle > 97 or turn_angle < 83:
        False_turn_counter = False_turn_counter + 1    
    else:
        False_turn_counter = 0

    if average_gap < gap_limit:
        Lin_x = 0.0
        Ang_z = -0.2
        Timer = 300
    elif turn_angle > 97 and False_turn_counter > 5:
        Lin_x = 0.00
        Ang_z = 0.2
        Ticks = Ticks + 1
        Timer = 300
    elif turn_angle < 83 and False_turn_counter > 5:
        Lin_x = 0.0
        Ang_z = -0.2
        Ticks = Ticks - 1
        Timer = 300
    else:
        Ang_z = 0
        Lin_x = 0.1
    

    if Ticks < 0 and Flag == 0 and Timer == 0:
        Lin_x = 0.00
        Ang_z = 0.2
        Ticks = Ticks + 1
    if Ticks > 0 and Flag == 0 and Timer == 0:
        Lin_x = 0.00
        Ang_z = -0.2
        Ticks = Ticks - 1
    
    if Timer > 0:
        Timer = Timer - 1




def main():
    rospy.init_node('listener', anonymous=True)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber("/scan", sensor_msgs.msg.LaserScan , Scan_Function_v2)

    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        command = Twist()
	command.linear.x = Lin_x
        command.angular.z = Ang_z
	pub.publish(command)
        rate.sleep()

if __name__ == '__main__':
    main()
