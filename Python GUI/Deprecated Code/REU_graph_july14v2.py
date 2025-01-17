'''
New functions to graph 
plots created from the
new output functions
'''

from turtle import color
import matplotlib.pyplot as plt

from matplotlib.animation import PillowWriter # for gif
from matplotlib.animation import FFMpegWriter # for mp4
f = open("Python GUI/ffmpeg_path.txt", "r")
plt.rcParams['animation.ffmpeg_path'] = f.read()
f.close()
# download ffmpeg from here https://www.ffmpeg.org/download.html#releases
# Windows https://github.com/BtbN/FFmpeg-Builds/releases

########## CHANGE FILE NAME HERE ##########
# This is placeholder data/allows program to be run without GUI
title_of_graph = 'Flight Graph: 7/08 Flight Test 2'
name_of_file = 'Python GUI/Log Outputs/flightTest_log_output_2022_07_08.2.txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
start = 120
end = 180

def splitter(input_str: str, isX: bool):
    # takes floats out of given String
    # i = ["text", "position", "(x,y):", "(-1234,", "5678)"]
    #                                  x         y

    i = input_str.split()
    
    if isX: # procedure for X slightly different
        return float(i[3][1:-1]) / 139
    else: # is y
        return float(i[4][:-1]) / 111

def splitter2(input_str: str, index: int):
    i = input_str.split()
    i = i[index].replace(',','')
    return float(i)

def main(graph_name: str, file_name: str, start: int, end: int):
    # FOR GRAPHING
    global own_x, own_y, intr_x, intr_y, avoid_x, avoid_y, all_avoid_x, all_avoid_y, save_next
    own_x = [] # lon of ownship
    own_y = [] # lat of ownship
    intr_x = [] # lon of intruder
    intr_y = [] # lat of intruder
    avoid_x = [] # temp storage for lon of points in 1 avoid maneuver
    avoid_y = [] # temp storage for lat of points in 1 avoid maneuver
    all_avoid_x = [] # collection of avoid_x values (array of arrays)
    all_avoid_y = [] # collection of avoid_y values (array of arrays)
    save_next = False # save value after predict

    # waypoint_latitude = []
    # waypoint_longitude = []    

    with open(file_name) as file:
        for line in file:
            #print(line)
            # if 'MISSION_ITEM' in line:
            #     cur_lat = splitter2(line, 36)
            #     cur_lon = splitter2(line, 39)
            #     if cur_lat != 0.0 and cur_lon != 0.0:
            #         waypoint_latitude.append(cur_lat)
            #         waypoint_longitude.append(cur_lon)
            if 'own position (x,y):' in line:
                own_x.append(splitter(line, True))
                own_y.append(splitter(line, False))
                if save_next: # after avoid() is called
                    avoid_x.append(own_x[-1])
                    avoid_y.append(own_y[-1])
                    save_next = False
            elif 'intr position (x,y)' in line:
                intr_x.append(splitter(line, True))
                intr_y.append(splitter(line, False))
            if 'avoid' in line:
                save_next = True

                if avoid_x and (avoid_x[-1] != own_x[-1] and avoid_y[-1] != own_y[-1]):
                    # if the last avoid_x value and own_x value aren't the same,
                    # then the plane finished avoiding
                    # (i.e. start a new array)
                    all_avoid_x.append(avoid_x)
                    all_avoid_y.append(avoid_y)
                    avoid_x = []
                    avoid_y = []

                avoid_x.append(own_x[-1])
                avoid_y.append(own_y[-1])

    if avoid_x:
        all_avoid_x.append(avoid_x)
        all_avoid_y.append(avoid_y)
    

    # ## GENERATE GRAPH IMAGE ###
    # plt.figure(figsize=(10, 7)) # Window size

    # # for current vehicle
    # #plt.scatter(lattitude[1:], longitude[1:], color='black') # Creates scatter plot (dots)
    # plt.plot(own_x[start:end], own_y[start:end], color='black', zorder=1) # Creates line for ownship

    # plt.plot(intr_x[start:end], intr_y[start:end], color='orange', zorder=1) # Creates line for intruder

    # for i in range(len(all_avoid_x)):
    #     plt.plot(all_avoid_x[i], all_avoid_y[i], color = 'blue', zorder = 1) # creates line for each avoid maneuver


    ### GENERATE GIF ANIMATION FILE ###
    # using https://www.youtube.com/watch?v=bNbN9yoEOdU
    fig = plt.figure(figsize=(10, 7))
    own_line, = plt.plot([], [], 'k-') # line for the ownship
    intr_line, = plt.plot([], [], color='orange') # line for the intruder
    # for avoid points
    cur_avoid = 0 # current avoid maneuver (first, second, etc)
    cur_point = 0 # current point within the avoid maneuver
    avoidance = {} # plt.plot lines stored in a dictionary, using cur_avoid as keys
    
    plt.xlim(min(own_x[start:end])-0.0005, max(own_x[start:end])+0.0005)
    plt.ylim(min(own_y[start:end])-0.0005, max(own_y[start:end])+0.0005)
    ### gif code continued below (this order matters :P )
    
    
    plt.plot(own_x[start], own_y[start], color = 'green', marker = 'X', markersize = '10', zorder = 1) # Creates starting point for ownship
    plt.plot(own_x[end-1], own_y[end-1], color = 'red', marker = 'X', markersize = '10', zorder = 1) # Creates ending point for ownship
    
    # for i in range(len(waypoint_latitude)):
    #     plt.scatter(waypoint_longitude[i], waypoint_latitude[i], marker='*', c="purple", zorder=2)
    
    if (min(intr_x) == max(intr_x)) and (min(intr_y) == max(intr_y)):
        # if intruder position never changes
        plt.scatter(intr_x[0], intr_y[0], color = 'orange')
    else:
        # intruder moves and start/end points are added
        plt.plot(intr_x[start], intr_y[start], color = 'green', marker = 'X', markersize = '10', zorder = 1) # Creates starting point for intruder
        plt.plot(intr_x[end], intr_y[end], color = 'red', marker = 'X', markersize = '10', zorder = 1) # Creates ending point for intruder
    
    plt.ticklabel_format(useOffset=False) # Display axes correctly

    plt.title(graph_name)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    

    ### gif continued
    metadata = dict(title = 'Movie', artist = 'Orange Joe')
    #writer = PillowWriter(fps = 10, metadata=metadata) # for gif
    writer = FFMpegWriter(fps = 10, metadata=metadata) # for mp4

    with writer.saving(fig, "Flight Graphs/7-08.2_flight_test_mp4.mp4", 100):
        for i in range(start, end+1):
            
            # draw own line
            own_line.set_data(own_x[start:i], own_y[start:i])
            
            # draw intruder line
            intr_line.set_data(intr_x[start:i], intr_y[start:i])

            # draw avoidance lines
            if (cur_avoid < len(all_avoid_x)):
                if (cur_point < len(all_avoid_x[cur_avoid]) and 
                ((own_x[i] == all_avoid_x[cur_avoid][cur_point]) and (own_y[i] == all_avoid_y[cur_avoid][cur_point]))):
                    # if cur_point is within the range of the avoid values
                    # and the current x value equals the current avoid value
                    
                    try:
                        # checks if avoidance[cur_avoid] exists

                        if avoidance[cur_avoid]:
                            # if so, do nothing
                            pass

                    except:
                        # if not, create it
                        avoidance[cur_avoid], = plt.plot([], [], color='blue')
                    
                    avoidance[cur_avoid].set_data(all_avoid_x[cur_avoid][0:cur_point+1], all_avoid_y[cur_avoid][0:cur_point+1])
                    #print(all_avoid_x[cur_avoid][0:cur_point+1], all_avoid_y[cur_avoid][0:cur_point+1])

                    cur_point += 1
                    #print(cur_avoid, cur_point)
                elif cur_point == len(all_avoid_x[cur_avoid]):
                    # else cur_point no longer points to an avoid value

                    cur_avoid += 1 # move to next maneuver
                    cur_point = 0 # reset cur_point
            
            writer.grab_frame()

    #plt.show() # graph image

if __name__ == '__main__':
    main(title_of_graph, name_of_file, start, end)