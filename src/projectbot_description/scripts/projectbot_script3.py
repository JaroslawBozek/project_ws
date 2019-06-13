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
Dist_from_path = 0
Timer2 = 600
Mimic_ticks = 0
coming_high = 0
coming_low = 0
lock = 0
lock_from_high = 0
lock_from_low = 0

def Scan_Function_v3(data):
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
    global Dist_from_path
    global Timer2
    global Mimic_ticks
    global coming_high
    global coming_low
    global lock
    global lock_from_high
    global lock_from_low

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
        Timer2 = 600
    elif turn_angle > 97 and False_turn_counter > 5 and lock == 0:
        Lin_x = 0.00
        Ang_z = 0.2
        Ticks = Ticks + 1
        Timer = 300
        Timer2 = 600
    elif turn_angle < 83 and False_turn_counter > 5 and lock == 0:
        Lin_x = 0.0
        Ang_z = -0.2
        Ticks = Ticks - 1
        Timer = 300
        Timer2 = 600
    else:
        Ang_z = 0
        Lin_x = 0.1
    



    if Ticks < 0 and Flag == 0 and Timer == 0 and lock == 0:
        Lin_x = 0.00
        Ang_z = 0.2
        Ticks = Ticks + 1
    if Ticks > 0 and Flag == 0 and Timer == 0 and lock == 0:
        Lin_x = 0.00
        Ang_z = -0.2
        Ticks = Ticks - 1
    
    if Timer > 0 and lock == 0:
        Timer = Timer - 1

    if Ticks == 0 and Timer == 0 and Timer2 > 0 and lock == 0:
        Timer2 = Timer2 - 1
    



    Dist_from_path = Dist_from_path + Lin_x*Ticks




    if Timer2 == 0 and Dist_from_path > 0 and lock == 0:
        if Mimic_ticks < 150:
            Ang_z = -0.2
            Lin_x = 0.0
            Mimic_ticks = Mimic_ticks + 1
            coming_low = 1
            lock_from_low = 1
        else:
            Lin_x = 0.1
            Dist_from_path = Dist_from_path + (-Mimic_ticks*Lin_x)

    if Timer2 == 0 and Dist_from_path < 0 and lock == 0:
        if Mimic_ticks < 150:
            Ang_z = 0.2
            Lin_x = 0.0
            Mimic_ticks = Mimic_ticks + 1
            coming_high = 1
            lock_from_high = 1
        else:
            Lin_x = 0.1
            Dist_from_path = Dist_from_path + (Mimic_ticks*Lin_x)




    if coming_high == 1 and Dist_from_path > -40 and Mimic_ticks > 0:
        lock = 1
        Dist_from_path = 0
        Lin_x = 0.0
        Ang_z = -0.2
        Mimic_ticks = Mimic_ticks - 1
    else:
        if lock == 1 and lock_from_low == 0:
            coming_low = 0
            coming_high = 0
            Dist_from_path = 0
            lock_from_high = 0
            lock = 0

    if coming_low == 1 and Dist_from_path < 40 and Mimic_ticks > 0:
        lock = 1
        Dist_from_path = 0
        Lin_x = 0.0
        Ang_z = 0.2
        Mimic_ticks = Mimic_ticks - 1
    else:
        if lock == 1 and lock_from_high == 0:
            coming_low = 0
            coming_high = 0
            Dist_from_path = 0
            lock_from_low = 0
            lock = 0
       




def main():
    rospy.init_node('listener', anonymous=True)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber("/scan", sensor_msgs.msg.LaserScan , Scan_Function_v3)

    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        command = Twist()
	command.linear.x = Lin_x
        command.angular.z = Ang_z
	pub.publish(command)
        rate.sleep()

if __name__ == '__main__':
    main()
