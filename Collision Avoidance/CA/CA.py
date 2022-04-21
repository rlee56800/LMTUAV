from planeClass_CA import *
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Battery, LocationGlobal, Attitude
from pymavlink import mavutil

import time
import math
import numpy as np 
import psutil
import argparse
import copy
import datetime
import threading
from  threading import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
    args = parser.parse_args()
    
    #connection_string = args.connect   #Connection to Mission Planner Simulation
    #connection_string = '/dev/ttyACM0'	#Establishing Connection With PIXHAWK  Linux
    connection_string = 'COM9'#'COM5'  #Establishing Connection With PIXHAWK  Windows
    #-- Create the object
    plane = Plane(connection_string)

    
    #-- Arm and takeoff for Simulation only
    #if not plane.is_armed(): plane.arm_and_takeoff(altitude=10)

    avoidWP = [34.0458323, -117.7980, 0]
    plane.run()
    
    #tgt_mode    = VehicleMode("AUTO")
    #while (plane.get_ap_mode() != tgt_mode):    
        #print("No in Auto Mode, No Predicting")
    #    time.sleep(5)

    #
    while True: #plane.is_armed():
    #     if(plane.current_WP_number() == 3):
    #         plane.insert_avoidWP(plane.current_WP_number(), avoidWP)
    #         #print("current_WP_number: ", plane.current_WP_number())
    #         time.sleep(1)
    #     #print("current_WP_number: ", plane.current_WP_number())   
        time.sleep(1) # just so the main thread doesn't end and printouts keep printing out :)
    
    plane.mission.clear()
    
















