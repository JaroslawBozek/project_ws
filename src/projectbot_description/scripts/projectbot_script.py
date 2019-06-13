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
Limit = 0.6


def Scan_Function(data):
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

    if average_gap < gap_limit:
        Lin_x = 0.0
        Ang_z = -0.2
    else:
        Lin_x = 0.1
        Ang_z = Kp*(-1)*(90 - turn_angle)


def main():
    rospy.init_node('listener', anonymous=True)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber("/scan", sensor_msgs.msg.LaserScan , Scan_Function)

    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        command = Twist()
	command.linear.x = Lin_x
        command.angular.z = Ang_z
	pub.publish(command)
        rate.sleep()

if __name__ == '__main__':
    main()
