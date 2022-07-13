'''
New functions to graph
plots created from the
new output functions
'''

import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ##########
# This is placeholder data/allows program to be run without GUI
title_of_graph = 'Flight Graph: 7/08.1 Flight Test'
name_of_file = '../Python GUI/Log Outputs/flightTest_log_output_2022_07_08.1.txt'
#name_of_file = 'Python GUI/Log Outputs/flightTest_log_output_2022_07_07.txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
show_predicted = [] # index/indices of value to show predicted values
show_intruder = 1

def splitter(input_str: str, isX: bool):
    i = input_str.split()
    
    # i = ["text", "text", "text", "(-1234,", "5678)"]
    #                                  x         y
    if isX:
        return float(i[3][1:-1])
    else:
        return float(i[4][:-1])

def main(graph_name: str, file_name: str, map_intruder: int, predicted_indices = [], plotted_point = [], predicted_collision_point = []):
    ########## Graphing ##########
    # waypoint = []
    # longitude = []
    # lattitude = []
    # future_pos_x = []
    # future_pos_y = []
    # x = []
    # # y = []

    # intruder_longitude = []
    # intruder_lattitude = []

    # waypoint_latitude = []
    # waypoint_longitude = []

    own_x = []
    own_y = []
    intr_x = []
    intr_y = []
    avoid_x = []
    avoid_y = []
    save_next = False

    with open(file_name) as file:
        for line in file:
            if 'own position' in line:
                print("own found")
                own_x.append(splitter(line, True)/139)
                own_y.append(splitter(line, False)/111)
                if save_next:
                    avoid_x.append(own_x[-1])
                    avoid_y.append(own_y[-1])
                    save_next = False
            elif 'intr position' in line:
                print("intruder found")
                intr_x.append(splitter(line, True)/139)
                intr_y.append(splitter(line, False)/111)
            if 'avoid' in line:
                print("avoid called")
                save_next = True
                avoid_x.append(own_x[-1])
                avoid_y.append(own_y[-1])

    plt.figure(figsize=(10, 7)) # Window size


    # for current vehicle
    #plt.scatter(lattitude[1:], longitude[1:], color='black') # Creates scatter plot (dots)
    print(len(own_x))
    cutoff_end = 15
    cutoff_beg = 30
    own_x = own_x[cutoff_beg:len(own_x)-cutoff_end]
    own_y = own_y[cutoff_beg:len(own_y)-cutoff_end]
    plt.plot(own_x, own_y, color='black', zorder=1) # Creates line
    plt.plot(own_x[0], own_y[0], color = 'green', marker = 'X', markersize = '10', zorder = 1)
    plt.plot(own_x[len(own_x)-1], own_y[len(own_y)-1], color = 'red', marker = 'X', markersize = '10', zorder = 1)

    #mylistx = [0,0]
    #mylisty = [0,0]
    for i in range (0, len(avoid_x), 2):
        #print("connect these paths:", mylist[i], mylist[i+1])
        mylistx = [avoid_x[i], avoid_x[i+1]]
        mylisty = [avoid_y[i], avoid_y[i+1]]
        plt.plot(mylistx, mylisty, color = 'blue', zorder = 1)
        #plt.plot(avoid_x[i], avoid_y[i], color = 'blue', marker = '*', markersize = 10, zorder = 1)
        #plt.plot(avoid_x[i+1], avoid_y[i+1], color = 'blue', marker = '*', markersize = 10, zorder = 1)
    #print(intr_x)

    # TESTING SPACE
    # plt.scatter(-117.whatever, 34.whatever, color = 'green')
    # plt.scatter(-117.793221, 34.045700, color = 'blue')
    plt.scatter(intr_x[1], intr_y[1], color = 'orange')
    # plt.scatter(-117.812176, 34.044746, color = 'orange')
    # plt.scatter(-117.817139, 34.044439, color = 'green')
    # plt.scatter(-117.811862, 34.038192, color = 'green')
    # plt.scatter(-117.781062, 34.089111, color = 'purple')
    '''

2022-04-28 16:20:48.593403 : Current lattitude : 
2022-04-28 16:20:48.593403 : Current longitude : 
2022-04-28 16:20:48.593403 : Intruder X Velocity : -4.14
2022-04-28 16:20:48.593403 : Intruder Y Velocity : -21.76
2022-04-28 16:20:48.593403 : Intruder lattitude : 34.0389766
2022-04-28 16:20:48.593403 : Intruder longitude : -117.80709119999999
2022-04-28 16:20:48.593403: Predicted crash lattitude : 34.038433512448414
2022-04-28 16:20:48.593403: Predicted crash longitude : -117.80937068414933
2022-04-28 16:20:48.593403: Crash location :  '''

    plt.ticklabel_format(useOffset=False) # Display axes correctly

    plt.title(graph_name)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')

    plt.show()

if __name__ == '__main__':
    main(title_of_graph, name_of_file, show_intruder, show_predicted)
