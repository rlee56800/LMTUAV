from planeClass_SIM import *
from dronekit import connect, VehicleMode, LocationGlobalRelative,  Battery, LocationGlobal, Attitude
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
    
    #Connection to Mission Planner Simulation
    connection_string = args.connect   
    
    #Establishing Connection With PIXHAWK
    #THIS IS TELEMETRY - DO NOT CHANGE
    #connection_string = '/dev/ttyACM0'	  #Linux: use 'dmesg | grep tty" to find the correct port
    #connection_string = 'COM10'#'COM5'     #Windows: check Device manager for the correct port 
    
    #-- Create the object
    plane = Plane(connection_string)

    
    #Simulation only -- Arm and takeoff for
    if not plane.is_armed(): plane.arm_and_takeoff(altitude=10)

    plane.save_to_file()
    
    plane.run()
    
    while plane.is_armed(): 
        time.sleep(1)

    plane.mission.clear()
    
















