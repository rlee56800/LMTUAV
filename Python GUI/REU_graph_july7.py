'''
New functions to graph
plots created from the
new output functions
'''

import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ##########
# This is placeholder data/allows program to be run without GUI
title_of_graph = 'Flight Graph: 7/07 Flight Test'
name_of_file = '../Python GUI/Log Outputs/flightTest_log_output_2022_07_07.txt'
#name_of_file = 'Python GUI/Log Outputs/flightTest_log_output_2022_07_07.txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)

def splitter(input_str: str, isX: bool):
    # takes floats out of given String
    # i = ["text", "position", "(x,y):", "(-1234,", "5678)"]
    #                                  x         y

    i = input_str.split()
    
    if isX: # procedure for X slightly different
        return float(i[3][1:-1]) / 139
    else: # is y
        return float(i[4][:-1]) / 111

def main(graph_name: str, file_name: str):
    ########## Graphing ##########
    own_x = [] # lon of ownship
    own_y = [] # lat of ownship
    intr_x = [] # lon of intruder
    intr_y = [] # lat of intruder
    avoid_x = [] # temp storage for lon of points in 1 avoid maneuver
    avoid_y = [] # temp storage for lat of points in 1 avoid maneuver
    all_avoid_x = [] # collection of avoid_x values (array of arrays)
    all_avoid_y = [] # collection of avoid_y values (array of arrays)
    save_next = False

    start = 0
    end = 30

    with open(file_name) as file:
        for line in file:
            if 'own position' in line:
                own_x.append(splitter(line, True))
                own_y.append(splitter(line, False))
                if save_next: # after avoid() is called
                    avoid_x.append(own_x[-1])
                    avoid_y.append(own_y[-1])
                    save_next = False
            elif 'intr position' in line:
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

    plt.figure(figsize=(10, 7)) # Window size


    # for current vehicle
    #plt.scatter(lattitude[1:], longitude[1:], color='black') # Creates scatter plot (dots)
    plt.plot(own_x[start:end], own_y[start:end], color='black', zorder=1) # Creates line for ownship

    plt.plot(intr_x[start:end], intr_y[start:end], color='orange', zorder=1) # Creates line for intruder

    for i in range(len(all_avoid_x)):
        plt.plot(all_avoid_x[i], all_avoid_y[i], color = 'blue', zorder = 1) # creates line for each avoid maneuver
    

    plt.plot(own_x[0], own_y[0], color = 'green', marker = 'X', markersize = '10', zorder = 1) # Creates starting point for ownship
    plt.plot(own_x[end-1], own_y[end-1], color = 'red', marker = 'X', markersize = '10', zorder = 1) # Creates ending point for ownship

    
    plt.plot(intr_x[0], intr_y[0], color = 'green', marker = 'X', markersize = '10', zorder = 1) # Creates starting point for intruder
    plt.plot(intr_x[end-1], intr_y[end-1], color = 'red', marker = 'X', markersize = '10', zorder = 1) # Creates ending point for intruder

    # num = 150
    # plt.scatter(own_x[num], own_y[num], color = 'magenta')

    plt.ticklabel_format(useOffset=False) # Display axes correctly

    plt.title(graph_name)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')

    plt.show()

if __name__ == '__main__':
    main(title_of_graph, name_of_file)
