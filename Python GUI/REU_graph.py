'''
New functions to graph
plots created from the
new output functions
'''

import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ##########
# This is placeholder data/allows program to be run without GUI
title_of_graph = 'Flight Graph: 7/07 Flight Test'
name_of_file = 'Python GUI/Log Outputs/flightTest_log_output_2022_07_08.txt'
#name_of_file = 'Python GUI/Log Outputs/flightTest_log_output_2022_07_07.txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
show_predicted = [] # index/indices of value to show predicted values
show_intruder = 1

def splitter(input_str: str, isX: bool):
    i = input_str.split()
    
    # i = ["text", "text", "text", "(-1234,", "5678)"]
    #                                  x         y
    if isX:
        return float(i[2][:-1])
    else:
        return float(i[3])

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

    with open(file_name) as file:
        for line in file:
            if 'own position:' in line:
                print("own found")
                own_x.append(splitter(line, True))
                own_y.append(splitter(line, False))
            elif 'intr position:' in line:
                print("intruder found")
                intr_x.append(splitter(line, True))
                intr_y.append(splitter(line, False))

    plt.figure(figsize=(10, 7)) # Window size


    # for current vehicle
    #plt.scatter(lattitude[1:], longitude[1:], color='black') # Creates scatter plot (dots)
    plt.plot(own_x, own_y, color='black', zorder=1) # Creates line
    print(intr_x)

    # for intruder vehicle
    if True:
        #print(len(intruder_lattitude), len(intruder_longitude))
        #plt.scatter(intruder_lattitude, intruder_longitude, color='red') # Creates scatter plot (dots)
        plt.plot(intr_x, intr_y, color='red', zorder=1) # Creates line
        # throw error if either are empty


    # TESTING SPACE
    # plt.scatter(-117.whatever, 34.whatever, color = 'green')
    # plt.scatter(-117.793221, 34.045700, color = 'blue')
    #plt.scatter(intr_x[1], intr_y[1], color = 'red')
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
