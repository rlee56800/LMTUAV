""" Header
Calling:
plane --connect <connection_string>

connection_string: i.e. tcp:ip_address:port / udp:ip_address:port / comport,baudrate

You can also create the connection on a separate file with vehicle = connect(..) and then
initialize plane = Plane(vehicle), so that you can use the object in your own program


"""
# adjusting log files
# ******************good for flight testing*********************
# *****may want to avoid for set time for first flight test*****

from asyncio.windows_events import NULL
from ctypes.wintypes import WPARAM
from distutils.fancy_getopt import wrap_text
from operator import truediv
from this import d

from matplotlib.pyplot import switch_backend
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Battery, LocationGlobal, Attitude, LocationLocal
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
import serial

#setting up xbee communication

ser = serial.Serial(

    port='COM3',#7',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

shortDate = datetime.datetime.today().strftime('%Y_%m_%d')
outputFile = "log_output_" + shortDate + ".txt"
f = open(outputFile, "a")

class Plane():

    def __init__(self, connection_string=None, vehicle=None):
        """ Initialize the object
        Use either the provided vehicle object or the connections tring to connect to the autopilot

        Input:
            connection_string       - the mavproxy style connection string, like tcp:127.0.0.1:5760
                                      default is None
            vehicle                 - dronekit vehicle object, coming from another instance (default is None)


        """

        #---- Connecting with the vehicle, using either the provided vehicle or the connection string
        if not vehicle is None:
            self.vehicle    = vehicle
            print("Using the provided vehicle")
        elif not connection_string is None:

            print("Connecting with vehicle...")
            self._connect(connection_string)
        else:
            raise("ERROR: a valid dronekit vehicle or a connection string must be supplied")
            return

        self._setup_listeners()

        self.airspeed           = 0.0       #- [m/s]    airspeed
        self.groundspeed        = 0.0       #- [m/s]    ground speed
        #self.velocity           = []        #- [cm/s] [vx,vy,vz]
        self.vx                 = 0.0       #- [m/s]    vx speed (pos -> north, neg -> south)
        self.vy                 = 0.0       #- [m/s]    vy speed (pos -> east, neg -> west)
        self.vz                 = 0.0       #- [m/s]    vz speed (pos -> up, neg -> down)

        self.pos_lat            = 0.0       #- [deg]    latitude
        self.pos_lon            = 0.0       #- [deg]    longitude
        self.pos_alt_rel        = 0.0       #- [m]      altitude relative to takeoff
        self.pos_alt_abs        = 0.0       #- [m]      above mean sea level

        self.att_roll_deg       = 0.0       #- [deg]    roll
        self.att_pitch_deg      = 0.0       #- [deg]    pitch
        self.att_heading_deg    = 0.0       #- [deg]    magnetic heading

        self.wind_dir_to_deg    = 0.0       #- [deg]    wind direction (where it is going)
        self.wind_dir_from_deg  = 0.0       #- [deg]    wind coming from direction
        self.wind_speed         = 0.0       #- [m/s]    wind speed

        self.climb_rate         = 0.0       #- [m/s]    climb rate
        self.throttle           = 0.0       #- [ ]      throttle (0-100)

        self.ap_mode            = ''        #- []       Autopilot flight mode

        self.mission            = self.vehicle.commands #-- mission items

        self.location_home      = LocationGlobalRelative(0,0,0) #- LocationRelative type home
        self.location_current   = LocationGlobalRelative(0,0,0) #- LocationRelative type current position

        # Received information from partner XBee
        self.receive_msg = False
        self.receive_lattitude = 0.0        #- [deg]    latitude
        self.receive_longitude = 0.0        #- [deg]    longitude
        self.receive_altitude = 0.0         #- [m]      altitude
        self.receive_velocity = [0.0, 0.0, 0.0]
                                            #- [m/s]    velocity of craft; [vx (+ north, - south), vy (+ east, - west), vz (+ up, - down)]
        self.receive_airspeed = 0.0         #- [m/s]    airspeed

        # Collision avoidance variables
        self.all_clear = True               #- there is no crash predicted, proceed
        self.counter = 0                    #- counter*5 seconds for the plane to go toward avoidance point
        self.will_crash = False             #- collision is predicted (i.e. next 2 vars have values)
        self.crash_lat = 0.0                #- latitude of crash
        self.crash_lon = 0.0                #- longitude of crash
        self.avoiding = False               #- keeps track of when avoidance command is sent

        self.avoidwpX = 0
        self.avoidwpY = 0
        self.direction = "LEFT"             # avoid direction
        self.ahead = 0                      #- 0 = avoid bc close, 1 = avoid bc predicted in future

    def _connect(self, connection_string):      #-- (private) Connect to Vehicle
        """ (private) connect with the autopilot

        Input:
            connection_string   - connection string (mavproxy style)
        """
        self.vehicle = connect(connection_string, wait_ready=True, heartbeat_timeout=60)
        self._setup_listeners()

    def _setup_listeners(self):                 #-- (private) Set up listeners
        #----------------------------
        #--- CALLBACKS
        #----------------------------
        if True:
            #---- DEFINE CALLBACKS HERE!!!
            @self.vehicle.on_message('ATTITUDE')
            def listener(vehicle, name, message):          #--- Attitude
                self.att_roll_deg   = math.degrees(message.roll)
                self.att_pitch_deg  = math.degrees(message.pitch)
                self.att_heading_deg = math.degrees(message.yaw)%360

            @self.vehicle.on_message('GLOBAL_POSITION_INT')
            def listener(vehicle, name, message):          #--- Position / Velocity
                self.pos_lat        = message.lat*1e-7
                self.pos_lon        = message.lon*1e-7
                self.pos_alt_rel    = message.relative_alt*1e-3
                self.pos_alt_abs    = message.alt*1e-3
                self.location_current = LocationGlobalRelative(self.pos_lat, self.pos_lon, self.pos_alt_rel)
                self.vx             = message.vx*1e-3 # vx speed (pos -> north, neg -> south)
                self.vy             = message.vy*1e-3 # vy speed (pos -> east, neg -> west)
                self.vz             = message.vz*1e-3 # vz speed (pos -> up, neg -> down)



            @self.vehicle.on_message('VFR_HUD')
            def listener(vehicle, name, message):          #--- HUD
                self.airspeed       = message.airspeed
                self.groundspeed    = message.groundspeed
                self.throttle       = message.throttle
                self.climb_rate     = message.climb

            @self.vehicle.on_message('WIND')
            def listener(vehicle, name, message):          #--- WIND
                self.wind_speed         = message.speed
                self.wind_dir_from_deg  = message.direction % 360
                self.wind_dir_to_deg    = (self.wind_dir_from_deg + 180) % 360


        return (self.vehicle)
        print(">> Connection Established")

    def _get_location_metres(self, original_location, dNorth, dEast, is_global=False):
        """
        Returns a Location object containing the latitude/longitude `dNorth` and `dEast` metres from the
        specified `original_location`. The returned Location has the same `alt and `is_relative` values
        as `original_location`.

        The function is useful when you want to move the vehicle around specifying locations relative to
        the current vehicle position.
        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius=6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)

        if is_global:
            return LocationGlobal(newlat, newlon,original_location.alt)
        else:
            return LocationGlobalRelative(newlat, newlon,original_location.alt)

    def is_armed(self):                         #-- Check whether uav is armed
        """ Checks whether the UAV is armed

        """
        return(self.vehicle.armed)

    def arm(self):                              #-- arm the UAV
        """ Arm the UAV
        """
        self.vehicle.armed = True

    def disarm(self):                           #-- disarm UAV
        """ Disarm the UAV
        """
        self.vehicle.armed = False

    def set_airspeed(self, speed):              #--- Set target airspeed
        """ Set uav airspeed m/s
        """
        self.vehicle.airspeed = speed

    def set_ap_mode(self, mode):                #--- Set Autopilot mode
        """ Set Autopilot mode
        """
        time_0 = time.time()
        try:
            tgt_mode    = VehicleMode(mode)
        except:
            return(False)

        while (self.get_ap_mode() != tgt_mode):
            self.vehicle.mode  = tgt_mode
            time.sleep(0.2)
            if time.time() < time_0 + 5:
                return (False)

        return (True)

    def get_ap_mode(self):                      #--- Get the autopilot mode
        """ Get the autopilot mode
        """
        self._ap_mode  = self.vehicle.mode
        return(self.vehicle.mode)

    def clear_mission(self):                    #--- Clear the onboard mission
        """ Clear the current mission.

        """
        cmds = self.vehicle.commands
        self.vehicle.commands.clear()
        self.vehicle.flush()

        # After clearing the mission you MUST re-download the mission from the vehicle
        # before vehicle.commands can be used again
        # (see https://github.com/dronekit/dronekit-python/issues/230)
        self.mission = self.vehicle.commands
        self.mission.download()
        self.mission.wait_ready()

    def download_mission(self):                 #--- download the mission
        """ Download the current mission from the vehicle.

        """
        self.vehicle.commands.download()
        self.vehicle.commands.wait_ready() # wait until download is complete.
        self.mission = self.vehicle.commands

    def mission_add_takeoff(self, takeoff_altitude=50, takeoff_pitch=15, heading=None):
        """ Adds a takeoff item to the UAV mission, if it's not defined yet

        Input:
            takeoff_altitude    - [m]   altitude at which the takeoff is considered over
            takeoff_pitch       - [deg] pitch angle during takeoff
            heading             - [deg] heading angle during takeoff (default is the current)
        """
        if heading is None: heading = self.att_heading_deg

        self.download_mission()
        #-- save the mission: copy in the memory
        tmp_mission = list(self.mission)
        print(type(self.mission))

        print ("Mission Size: ", len(tmp_mission))
        is_mission  = False
        if len(tmp_mission) >= 1:
            is_mission = True
            print("Current mission:")
            for item in tmp_mission:
                print(item)
            #-- If takeoff already in the mission, do not do anything

        if is_mission and tmp_mission[0].command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
            print ("Takeoff already in the mission")
        else:
            print("Takeoff not in the mission: adding")
            self.clear_mission()
            takeoff_item = Command( 0, 0, 0, 3, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, takeoff_pitch,  0, 0, heading, 0,  0, takeoff_altitude)
            self.mission.add(takeoff_item)
            for item in tmp_mission:
                self.mission.add(item)
            self.vehicle.flush()
            print(">>>>>Done")

    def arm_and_takeoff(self, altitude=50, pitch_deg=12):
        """ Arms the UAV and takeoff
        Planes need a takeoff item in the mission and to be set into AUTO mode. The
        heading is kept constant

        Input:
            altitude    - altitude at which the takeoff is concluded
            pitch_deg   - pitch angle during takeoff
        """
        self.mission_add_takeoff(takeoff_altitude=1.5*altitude, takeoff_pitch=pitch_deg)
        print ("Takeoff mission ready")

        while not self.vehicle.is_armable:
            print("Wait to be armable...")
            time.sleep(1.0)


        #-- Save home
        while self.pos_lat == 0.0:
            time.sleep(0.5)
            print ("Waiting for good GPS...")
        self.location_home      = LocationGlobalRelative(self.pos_lat,self.pos_lon,altitude)

        print("Home is saved as "), self.location_home
        print ("Vehicle is Armable: try to arm")
        self.set_ap_mode("MANUAL")
        n_tries = 0
        while not self.vehicle.armed:
            print("Try to arm...")
            self.arm()
            n_tries += 1
            time.sleep(2.0)

            if n_tries > 5:
                print("!!! CANNOT ARM")
                break

        #--- Set to auto and check the ALTITUDE
        if self.vehicle.armed:
            print ("ARMED")
            self.set_ap_mode("AUTO")

            while self.pos_alt_rel <= altitude:# - 10.0:
                print ("Altitude = %.0f"%self.pos_alt_rel)
                time.sleep(0.5)

            #self.set_airspeed(50)

            #print("Altitude reached: set to GUIDED")
            #self.set_ap_mode("GUIDED")

            #time.sleep(5.0)

            #print("Set to AUTO")
            #self.set_ap_mode("AUTO")
        self.vehicle.airspeed = 50.0

        return True

    def current_WP_number(self):
        return self.vehicle.commands.next

    def insert_avoidWP(self,currentWP_index, avoidWP):
        """Annie's Code
            insert avoid wp into mission list and upload to vehicle
       """
        #CMD mission to list
        missionlist=list(self.mission)

        #create cmd wapoint
        newCMD=Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, avoidWP[0], avoidWP[1], avoidWP[2])

        #insert avoid wp to list
        missionlist.insert(currentWP_index,newCMD) # 1deal
        #missionlist.insert(currentWP_index-2,newCMD) # does not change anything
        #missionlist.insert(0,newCMD) # only works with 1 wp

        # Clear the current mission (command is sent when we call upload())
        self.mission.clear()
        self.vehicle.flush()

        #Write the modified mission and flush to the vehicle
        for cmd in missionlist:
            self.mission.add(cmd)
        self.mission.upload()

        # clearing the entire mission and leaving avoidance wp as the only wp -> goes straight home

    def get_target_from_bearing(self, original_location, ang, dist, altitude=None):
        """ Create a TGT request packet located at a bearing and distance from the original point

        Inputs:
            ang     - [rad] Angle respect to North (clockwise)
            dist    - [m]   Distance from the actual location
            altitude- [m]
        Returns:
            location - Dronekit compatible
        """

        if altitude is None: altitude = original_location.alt

        # print '---------------------- simulate_target_packet'
        dNorth  = dist*math.cos(ang)
        dEast   = dist*math.sin(ang)
        # print "Based on the actual heading of %.0f, the relative target's coordinates are %.1f m North, %.1f m East" % (math.degrees(ang), dNorth, dEast)

        #-- Get the Lat and Lon
        tgt     = self._get_location_metres(original_location, dNorth, dEast)

        tgt.alt = altitude
        # print "Obtained the following target", tgt.lat, tgt.lon, tgt.alt

        return tgt

    def ground_course_2_location(self, angle_deg, altitude=None):
        """ Creates a target to aim to in order to follow the ground course
        Input:
            angle_deg   - target ground course
            altitude    - target altitude (default the current)

        """
        tgt = self.get_target_from_bearing(original_location=self.location_current,
                                             ang=math.radians(angle_deg),
                                             dist=5000,
                                             altitude=altitude)
        return(tgt)

    def goto(self, location):
        """ Go to a location

        Input:
            location    - LocationGlobal or LocationGlobalRelative object

        """
        self.vehicle.simple_goto(location)

    def set_ground_course(self, angle_deg, altitude=None):
        """ Set a ground course

        Input:
            angle_deg   - [deg] target heading
            altitude    - [m]   target altitude (default the current)

        """

        #-- command the angles directly
        self.goto(self.ground_course_2_location(angle_deg, altitude))

    def get_rc_channel(self, rc_chan, dz=0, trim=1500):         #--- Read the RC values from the channel
        """
        Gets the RC channel values with a dead zone around trim

        Input:
            rc_channel  - input rc channel number
            dz          - dead zone, within which the output is set equal to trim
            trim        - value about which the dead zone is evaluated

        Returns:
            rc_value    - [us]
        """
        if (rc_chan > 16 or rc_chan < 1):
            return -1

        #- Find the index of the channel
        strInChan = '%1d' % rc_chan
        try:

            rcValue = int(self.vehicle.channels.get(strInChan))

            if dz > 0:
                if (math.fabs(rcValue - trim) < dz):
                    return trim

            return rcValue
        except:
            return 0

    def set_rc_channel(self, rc_chan, value_us=0):      #--- Overrides a rc channel (call with no value to reset)
        """
        Overrides the RC input setting the provided value. Call with no value to reset

        Input:
            rc_chan     - rc channel number
            value_us    - pwm value
        """
        strInChan = '%1d' % rc_chan
        self.vehicle.channels.overrides[strInChan] = int(value_us)

    def clear_all_rc_override(self):               #--- clears all the rc channel override
        self.vehicle.channels.overrides = {}

    def prediction(self):
        
        print("In Prediction funtion\n")
        
        #For Flight Test only
        '''
        tgt_mode    = VehicleMode("AUTO")
        while (self.get_ap_mode() != tgt_mode):    
            print("No in Auto Mode, No Predicting")
            time.sleep(5)
        '''
        #For Simulation only
        while not self.is_armed():
            print("Not Armed, No Predicting")
            time.sleep(10)


        #while self.is_armed():
        while True:
            print("predicting")

            while not self.receive_msg:
                #print("prediction: no message")
                time.sleep(1)
                # clear out old data so ownship doesn't avoid a ghost
                if not self.receive_lattitude:
                    self.receive_lattitude = 0.0        #- [deg]    latitude
                    self.receive_longitude = 0.0        #- [deg]    longitude
                    self.receive_altitude = 0.0         #- [m]      altitude
                    self.receive_velocity = [0.0, 0.0, 0.0]          #- [m/s]    velocity of craft
                    self.receive_airspeed = 0.0         #- [m/s]    airspeed
                pass

            XAvoidTolerance = 0.05  #10.0

            velX = float(self.vx) # vx speed (pos -> north, neg -> south)
            velY = float(self.vy) #- [m/s]  # vy speed (pos -> east, neg -> west) 
            velZ = float(self.vz) #- [m/s]  # vz speed (pos -> up, neg -> down)
            posX = self.pos_lon * 139  #lat/lon fix (this was good as is)
            posY = self.pos_lat * 111
            posZ = self.pos_alt_rel

            v2velX = self.receive_velocity[0] # vx speed (pos -> north, neg -> south)#- [m/s] 
            v2velY = self.receive_velocity[1] # vy speed (pos -> east, neg -> west) #- [m/s] 
            v2velZ = self.receive_velocity[2] # vz speed (pos -> up, neg -> down)
            v2posX = self.receive_longitude * 139
            v2posY = self.receive_lattitude * 111
            v2posZ = self.receive_altitude


            collisionPredicted = self.collisionPredictedCompare(XAvoidTolerance)
            print(collisionPredicted)
            if collisionPredicted:
                print("************************************************************")
                print("                  Predicted Collision")
                print("self position: [%f, %f]"%(posX, posY))  
                print("intruder position: [%f, %f]"%(v2posX, v2posY))
                print("collision predicted at (", self.crash_lon*139, self.crash_lat*111, ")")
                print("************************************************************\n\n")
                f = open(outputFile, "a")
                f.write("************************************************************\n")
                f.write("                  Predicted Collision\n")
                #f.write("self position: (" + str(posX) + ", " + str(posY) + ")\n")  
                #f.write("intruder position: (" + str(v2posX) + ", " + str(v2posY) + ")\n")
                f.write("collision predicted at (" + str(self.crash_lon*139) + ", " + str(self.crash_lat*111) + ")\n")
                f.write("************************************************************\n\n")
                f.close()
                self.will_crash = True
                collisionPredicted = self.collisionPredictedCompare(XAvoidTolerance)

                if self.all_clear: # all_clear True: plane is heading toward mission
                    # if plane WAS going toward mission, but detected a collision
                    #print('WEEEEEEEEEEEEE AREEEEEEEEEEEEEEEEEEEEEEEE COLLIDINGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')
                    self.all_clear = False
                    self.counter = 0 # randomly returns to mission; needs a concrete all-clear
                    # TODO: find new avoid point if another collision is predicted??

                    #print("~~~~~~Change to GUIDE Mode~~~~~~~~")
                    self.set_ap_mode("GUIDED")

                    # go away
                    # MAKE ANY CHANGES IN HERE
                    # self.avoiding = True
                    #while (abs(self.receive_lattitude-self.pos_lat) < XAvoidTolerance and abs(self.receive_longitude-self.pos_lon)):
                    self.goto(self.avoid(v2posX, posX, v2posY, posY, v2velX, v2velY)) # using avoid()
                    #print("prediction: avoiding for 5s")
                    self.avoiding = True
                    n = 0
                    f = open(outputFile, "a")
                    if self.ahead:
                        time.sleep(8)
                        print("avoiding for 10 sec")
                    else:
                        while ( abs(self.receive_lattitude-self.pos_lat)*111 < XAvoidTolerance and abs(self.receive_longitude-self.pos_lon)*139 < XAvoidTolerance):
                            time.sleep(1)
                            n+=1
                            print("called while", n, "times")
                            f.write("called while " + str(n) + " times\n")
                    f.write("\n")
                    f.close()
                    print("end sleep")
                    self.all_clear = True
                    self.avoiding = False
                    self.set_ap_mode("AUTO") # return to mission
                    print("start sleep 2")
                    time.sleep(2) #5
                    print("end sleep 2")


                    # # working version
                    # # just avoids for 10 sec
                    # self.goto(self.avoid(v2posX, posX, v2posY, posY, v2velX, v2velY)) # using avoid()
                    # print("prediction: avoiding for 5s")
                    # self.avoiding = True
                    # time.sleep(10)
                    # print("end sleep")
                    # self.all_clear = True
                    # self.avoiding = False
                    # self.set_ap_mode("AUTO") # return to mission
                    # print("start sleep 2")
                    # time.sleep(2) #5
                    # print("end sleep 2")

                    
                    # self.goto(LocationGlobalRelative(34.0384535, -117.81742575, 0)) # using fixed point (very bottom of farm)
                    
                #break
                    
            else: # TESTING ONLY; REMOVE LATER PLS
                # print("************************************************************")
                print("                 No Predicted Collision")
                # print("************************************************************\n\n")
                f = open(outputFile, "a")
                f.write("************************************************************\n")
                f.write("                 No Predicted Collision\n")
                f.write("************************************************************\n\n")
                f.close()
                self.will_crash = False
                
                if self.counter >= 2: # 2 iterations of predict(); 10 seconds; set 2 to whatever
                    self.counter = 0
                    self.all_clear = True
                    self.avoiding = False
                    self.set_ap_mode("AUTO") # return to mission

            # for item in self.mission:
            #     print(item)
            #if self.counter != -1:
            if not self.all_clear: # currently going toward AP
                self.counter = self.counter + 1
            #print('^^^COUNTER: %f' %self.counter)
            time.sleep(2) #5
            #print("end prediction function")

    def getFutureDistance(self, time, ownPosX, ownVelX, targPosX, targetVelX):
        futureTargPosX = targPosX + (targetVelX * time)
        futureOwnPosX = ownPosX + (ownVelX * time)
        return abs(futureOwnPosX - futureTargPosX)

    def getFuturePosition(self, PosX,VelX,time):
        futurePosX = PosX*1000 + VelX * time
        #futurePosY = PosY*1000 + VelY * time
        #futurePosZ = PosZ + VelZ * time
        return futurePosX

    #def collisionPredictedCompare(self, collisionPredicted, distX, distY, distZ, XAvoidTolerance, YAvoidTolerance, ZAvoidTolerance):
    """
    def collisionPredictedCompare(self, XAvoidTolerance):
        f = open(outputFile, "a")
        # vector math (make function later)
        ownX = self.pos_lon * 139
        ownY = self.pos_lat * 111
        print("own: (", ownX, ownY, ")")
        f.write("own position (x,y): (" + str(ownX) + ", " + str(ownY) + ")\n")

        intrX = self.receive_longitude * 139
        intrY = self.receive_lattitude * 111
        print("intr: (", intrX, intrY, ")")
        f.write("intr position (x,y): (" + str(intrX) + ", " + str(intrY) + ")\n")

        # put into if case 2 statement
        self.avoidwpX = intrX 
        self.avoidwpY = intrY

        if self.receive_velocity[0] > 0:
            self.avoidwpX -= XAvoidTolerance
        else:
            self.avoidwpX += XAvoidTolerance

        if self.receive_velocity[1] > 0:
            self.avoidwpY -= XAvoidTolerance
        else:
            self.avoidwpY += XAvoidTolerance
        # end if case 2

        # thank you stack overflow
        # https://stackoverflow.com/questions/2931573/determining-if-two-rays-intersect

        # lat/lon fix ? 
        dx = (self.receive_longitude - self.pos_lon) * 139 
        dy = (self.receive_lattitude - self.pos_lat) * 111 
        det = self.receive_velocity[0] * self.vy - self.receive_velocity[1] * self.vx

        print("Distance between own/intr x:", ownX - intrX)
        print("Distance between own/intr y:", ownY - intrY)
        f.write("distance between own and intruder: (" + str(ownX-intrX) + ", " + str(ownY-intrY) + ")\n")

        # stationary:
        # if abs(self.receive_velocity[0]) < 0.1 and abs(self.receive_velocity[1]) < 0.1 and abs(dx) < XAvoidTolerance and abs(dy) < XAvoidTolerance:
        # TODO: MAKE CRASH POSITION MIDPOINT SO ANGLE CALCULATIONS WORK
        if abs(dx) < XAvoidTolerance and abs(dy) < XAvoidTolerance:
            print("from distance")
            if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                print("STATIONARY OBJECT DETECTED")
                f.write("stationary object detected\n")
            print("velocity:", self.vx, self.vy)
            f.write("own velocity: (" + str(self.vx) + "m/s, " + str(self.vy) + "m/s)\n")
            f.write("intruder velocity: (" + str(self.receive_velocity[0]) + "m/s, " + str(self.receive_velocity[1]) + "m/s)\n")
            self.crash_lat = self.receive_lattitude
            self.crash_lon = self.receive_longitude
            dist_self = ( ((((self.crash_lat-self.pos_lat)*111)**2) + (((self.crash_lon-self.pos_lon)*139)**2))**(1/2) ) # distance collision is from self
            dist_intr = ( ((((self.crash_lat-self.receive_lattitude)*111)**2) + (((self.crash_lon-self.receive_longitude)*139)**2))**(1/2) ) # distance collision is from intruder
            print('crash distance from self / intruder')
            print(dist_self, dist_intr)
            print("--------------------------------")
            #print("angle between self and intruder vectors:\n", angle)
            print("--------------------------------")
            f.close()
            self.ahead = 0
            return True

        if det == 0:
            return False
        u = (dy * self.receive_velocity[0] - dx * self.receive_velocity[1]) / det
        v = (dy * self.vx - dx * self.vy) / det

        # intersection equations p = [self current position] + [self current velocity] * u
        #                        p = [intr current position] + [intr current velocity] * v
        # if u and v are positive, point of intersection is in front of both
        if u >= 0 and v >= 0:
            self.crash_lat = ((self.pos_lat * 111) + self.vy * u)/111 # no particular reason to use this over the v
            self.crash_lon = ((self.pos_lon * 139) + self.vx * u)/139

            # new code:
            crashX = self.crash_lon * 139
            crashY = self.crash_lat * 111

            # distance own to crash
            # final - initial 
            docX = crashX - ownX
            docY = crashY - ownY

            # distance own to crash
            # final - initial 
            dciX = crashX - intrX
            dciY = crashY - intrY

            dotprod = docX*dciX + docY*dciY
            det = docX*dciY - docY*dciX

            angle = math.degrees(math.atan2(det, dotprod))

            if 0 <= angle <= 90 or -180 <= angle <= -90:
                print("left")
                self.direction = "LEFT"
            else:
                print("right")
                self.direction = "RIGHT"
            # end new code

            # distance formula: sqrt( (x2-x1)^2 + (y2-y1)^2 )
            #                   ( (  ((x2-x1)**2) + ((y2-y1)**2)  )**(1/2) )
            dist_self = ( ((((self.crash_lat-self.pos_lat)*111)**2) + (((self.crash_lon-self.pos_lon)*139)**2))**(1/2) ) # distance collision is from self
            dist_intr = ( ((((self.crash_lat-self.receive_lattitude)*111)**2) + (((self.crash_lon-self.receive_longitude)*139)**2))**(1/2) ) # distance collision is from intruder

            print('crash distance from self / intruder')
            print(dist_self, dist_intr)
            print("--------------------------------")
            print("angle between self and intruder vectors:\n", angle)
            print("angle: " + str(angle) + "\n")
            print("--------------------------------")
            if min(dist_self, dist_intr) <= XAvoidTolerance:
            #if dist_self <= XAvoidTolerance:
                print(XAvoidTolerance)
                f.close()
                print("from velocity vectors")
                self.ahead = 1
                return True
        f.close()
        return False
    """

    def collisionPredictedCompare(self, XAvoidTolerance):
        f = open(outputFile, "a")
        ownX = self.pos_lon * 139
        ownY = self.pos_lat * 111
        vx = self.vx
        vy = self.vy
        print("own: (", ownX, ownY, ")")
        f.write("own position (x,y): (" + str(ownX) + ", " + str(ownY) + ")\n")

        intrX = self.receive_longitude * 139
        intrY = self.receive_lattitude * 111
        intrvx = self.receive_velocity[0]
        intrvy = self.receive_velocity[1]
        print("intr: (", intrX, intrY, ")")
        f.write("intr position (x,y): (" + str(intrX) + ", " + str(intrY) + ")\n")

        # thank you stack overflow
        # (this was previous algorithm)
        # https://stackoverflow.com/questions/2931573/determining-if-two-rays-inters

        print("Distance between own/intr x:", ownX - intrX)
        print("Distance between own/intr y:", ownY - intrY)
        f.write("distance between own and intruder: (" + str(ownX-intrX) + ", " + str(ownY-intrY) + ")\n")
        
        print("own velocity:", vx, vy)
        print("intr velocity:", intrvx, intrvy)
        f.write("own velocity: (" + str(vx) + "m/s, " + str(vy) + "m/s)\n")
        f.write("intruder velocity: (" + str(intrvx) + "m/s, " + str(intrvy) + "m/s)\n")
            
        dx = ownX - intrX
        dy = ownY - intrY

        foundX = False
        foundY = False

        if abs(dx) < XAvoidTolerance and abs(dy) < XAvoidTolerance:
            print("from distance")
            self.ahead = 0
            foundX = True
            foundY = True
            if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                print("STATIONARY OBJECT DETECTED")
                f.write("stationary object detected\n")
            self.crash_lat = (self.receive_lattitude+self.pos_lat)/2
            self.crash_lon = (self.receive_longitude+self.pos_lon)/2
            # print("--------------------------------")
            # #print("angle between self and intruder vectors:\n", angle)
            # print("--------------------------------")
            # f.close()
            # self.ahead = 0
            # return True

        # calculates future positions
        for i in range (1, 301):
            t = i/2000
            # WAS 100, 2000 PROBABLY BETTER

            newX = vx*t + ownX
            newY = vy*t + ownY

            newintrX = intrvx*t + intrX
            newintrY = intrvy*t + intrY

            if i % 30 == 0:
                print("new intr position: (", newintrX, ",", newintrY, ")")
                f.write("new intr pos: (" + str(newintrX) + ", " + str(newintrY) + ")\n")

            dx = newX-newintrX
            dy = newY-newintrY

            # if abs(dx) < XAvoidTolerance:
            #     foundX = True
            #     self.crash_lon = newX/139
            # if abs(dy) < XAvoidTolerance:
            #     foundY = True
            #     self.crash_lat = newY/111

            if abs(dx) < XAvoidTolerance and abs(dy) < XAvoidTolerance:
                foundX = True
                foundY = True
                self.crash_lon = newX/139
                self.crash_lat = newY/111
            
            if foundX and foundY:
                print("collision found!")
                break

        if foundX and foundY:
            print("from future calculations")
            self.ahead = 1
            # new code:
            crashX = self.crash_lon * 139
            crashY = self.crash_lat * 111

            # distance own to crash
            # final - initial 
            docX = crashX - ownX
            docY = crashY - ownY

            # distance own to crash
            # final - initial 
            dciX = crashX - intrX
            dciY = crashY - intrY

            dotprod = docX*dciX + docY*dciY
            det = docX*dciY - docY*dciX

            angle = math.degrees(math.atan2(det, dotprod))

            if 0 <= angle <= 90 or -180 <= angle <= -90:
                print("left")
                self.direction = "LEFT"
            else:
                print("right")
                self.direction = "RIGHT"
            # end new code

            dist_self = ( ((((self.crash_lat-self.pos_lat)*111)**2) + (((self.crash_lon-self.pos_lon)*139)**2))**(1/2) ) # distance collision is from self
            dist_intr = ( ((((self.crash_lat-self.receive_lattitude)*111)**2) + (((self.crash_lon-self.receive_longitude)*139)**2))**(1/2) ) # distance collision is from intruder
            print('crash distance from self / intruder')
            print(dist_self, dist_intr)
            print("--------------------------------")
            print("angle between self and intruder vectors:\n", angle)
            print("--------------------------------")
            f.close()
            return True

        f.close()
        return False


    def chooseY(self, ypos, yneg):
        y = ypos
        if abs(ypos) > abs(yneg):
            y = ypos
        else:
             y = yneg
        return y

    def avoid(self, intruderX, ownX, intruderY, ownY, intVx, intVy):
        print("avoid called")
        f = open(outputFile, "a")
        f.write("avoid called\n")

        # # case 2
        # lonAvoid = self.avoidwpX/139
        # latAvoid = self.avoidwpY/111

        # head on case
        if (self.vy > 0 and self.direction == "RIGHT") or (self.vy < 0 and self.direction == "LEFT"):
            print("adding to wp avoid")
            newX = ownX + 50 
        else:
            print("subtracting from wp avoid")
            newX = ownX - 50
        newY = ownY + 10

        # lat/lon fix
        # lonAvoid = self.pos_lon
        # latAvoid = self.pos_lat
        lonAvoid = newX/139
        latAvoid = newY/111

        zAvoid = self.pos_alt_rel

        wpAvoid = LocationGlobalRelative(latAvoid, lonAvoid, zAvoid)
        print("going to waypoint ", latAvoid, lonAvoid)
        f.write("going to waypoint (latitude, longitude): (" + str(latAvoid) + ", " + str(lonAvoid) + ")\n")
        f.write("going to waypoint (x, y): (" + str(newX) + ", " + str(newY) + ")\n")
        f.close()
        return wpAvoid
        #return [xAvoid, yAvoid, zAvoid] # note: insert_avoidWP requires a list of x, y, z values

    def save_to_file(self):
        f.write("\n\n\n\n\n________________________________________________________________\n")
        f.write("NEW MISSION: " + str(datetime.datetime.now()) + "\n")
        f.write("________________________________________________________________\n")
        for item in list(self.mission):
            f.write(str(item) + '\n')
        time.sleep(1.0)
        f.close()
        
    def send_ADSB_data(self):

        print("In send ADSB funtion")
        #msg = "In send ADSB funtion\n"
        #ser.write(msg.encode())
        while True:
            print("sending")

            msg = "ICAO: SKYLINE;"
            msg += "Lattitude: " + str(self.pos_lat) + ';'
            msg += "Longitude: " + str(self.pos_lon) + ';'
            msg += "Altitude: " + str(self.pos_alt_rel) + ';'
            msg += "Velocity: " + str(self.vehicle.velocity) + ';'
            msg += "Airspeed: " + str(self.airspeed) + ';'
            #msg += "#######################\n"

            # msg = "ICAO: SKYLINE;"
            # msg += "Lattitude: 34.0592904;"
            # msg += "Longitude: -117.8110313;"
            # msg += "Altitude: " + str(self.pos_alt_rel) + ';'
            # msg += "Velocity: [-15.35, -15.81, 0.0];"
            # msg += "Airspeed: 22.035;"
            # #msg += "#######################\n"

            #Send out ADSB data
            ser.write(msg.encode())
            time.sleep(2.0) #5
            #print("end send ADSB function")

    def receive_ADSB_data(self):
        """
        inactivityCounter = 0
        while True:
            print("In receive_ADSB_data function")
            msg = ser.readline().decode()
            print(msg)

            while not msg:
                inactivityCounter += 1 # if other vehicle disconnects, clear its old data
                if inactivityCounter > 5:
                    self.receive_msg = False

                print('waiting for xbee msg')
                time.sleep(1)
                msg = ser.readline().decode()
                print(msg)
            inactivityCounter = 0
            #print("msg!!!!!!!!!!!!\n")
            #print(msg)


            self.receive_msg = True
            # Variable Saving
            #lst_msg = msg.split("\n")
            lst_msg = msg.split(";")

            #print(lst_msg)
            #print(lst_msg[1].split(': '))

            self.receive_lattitude = float((lst_msg[1].split(': '))[-1])
            self.receive_longitude = float((lst_msg[2].split(': '))[-1])
            self.receive_altitude = float((lst_msg[3].split(': '))[-1])
            temp = (lst_msg[4].split(': '))[-1]
            self.receive_velocity = temp.strip('][').split(', ')
            for value in range(len(self.receive_velocity)):
                self.receive_velocity[value] = float(self.receive_velocity[value])
            self.receive_airspeed = float((lst_msg[5].split(': '))[-1])

            print(self.receive_lattitude)
            print(self.receive_longitude)
            print(self.receive_velocity)
            # Variable Saving end

            time.sleep(1)
            print("end send ADSB function")
            """
            

        while True:
            print("receiving")
            self.receive_msg = True
            # self.receive_lattitude = 34.0434543 #34.0434543
            # self.receive_longitude = -117.8128 # -117.8128
            self.receive_lattitude = 34.0431653 #34.0434854
            self.receive_longitude = -117.8125119 #-117.8131127
            self.receive_velocity = [-1.026, -2.097, self.vz]
            #self.receive_velocity = [2.097, -1.026, self.vz]
            #self.receive_velocity = [-self.vy, self.vx, self.vz]

            # print("intruder is at lat ",self.receive_lattitude)
            # print("intruder is at lon", self.receive_longitude)
            # print("intruder velocity is ",self.receive_velocity)
            # #Variable Saving end

            time.sleep(1)


    def run(self):
        #t1 = threading.Thread(target=self.save_to_file, daemon=True) # flight test: comment out daemon=true
        t2 = threading.Thread(target=self.send_ADSB_data, daemon=True)
        t3 = threading.Thread(target=self.receive_ADSB_data, daemon=True)
        t4 = threading.Thread(target=self.prediction, daemon=True)

        #t1.start()
        t2.start()
        t3.start()
        t4.start()