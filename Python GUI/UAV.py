import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ##########
# This is placeholder data/allows program to be run without GUI
title_of_graph = 'Flight Graph: 12/24/21 Simulation 3'
name_of_file = 'Python GUI/Log Outputs 2021_12_24/log_output_2022_03_08.txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
show_predicted = [] # index/indices of value to show predicted values
show_intruder = 0

def splitter(input_str: str, index: int):
    i = input_str.split()
    i = i[index].replace(',','')
    return float(i)

def main(graph_name: str, file_name: str, map_intruder: int, predicted_indices = [], plotted_point = [], predicted_collision_point = []):
    ########## Graphing ##########
    waypoint = []
    longitude = []
    lattitude = []
    future_pos_x = []
    future_pos_y = []
    x = []
    y = []

    intruder_longitude = []
    intruder_lattitude = []

    waypoint_latitude = []
    waypoint_longitude = []

    with open(file_name) as file:
        for line in file:
            if 'MISSION_ITEM' in line:
                cur_lat = splitter(line, 36)
                cur_lon = splitter(line, 39)
                if cur_lat != 0.0 and cur_lon != 0.0:
                    waypoint_latitude.append(cur_lat)
                    waypoint_longitude.append(cur_lon)
            elif 'Current lattitude' in line:
                cur = splitter(line, 6)
                if cur != 0:
                    lattitude.append(cur)
            elif 'Current longitude' in line:
                cur = splitter(line, 6)
                if cur != 0:
                    longitude.append(cur)
            elif map_intruder and 'Intruder lattitude' in line:
                cur = splitter(line, 6)
                if cur != 0:
                    intruder_lattitude.append(cur)
            elif map_intruder and 'Intruder longitude' in line:
                cur = splitter(line, 6)
                if cur != 0:
                    intruder_longitude.append(cur)
            elif '~~~~~~~~~~New Point~~~~~~~~~~~~' in line:
                # future_pos are lists of future positions from each point
                # New Point means all 10 futurePos points have been printed
                future_pos_x.append(x)
                future_pos_y.append(y)
                x = []
                y = []
            elif 'futurePosX' in line:
                x.append(splitter(line, 5))
            elif 'futurePosY' in line:
                y.append(splitter(line, 5))
    future_pos_x.append(x)
    future_pos_y.append(y)

    future_pos_x.pop(0) # 0th element is empty
    future_pos_y.pop(0) # 0th element is empty

    plt.figure(figsize=(10, 7)) # Window size


    # for current vehicle
    #plt.scatter(lattitude[1:], longitude[1:], color='black') # Creates scatter plot (dots)
    plt.plot(longitude[1:], lattitude[1:], color='black', zorder=1) # Creates line

    # for intruder vehicle
    if map_intruder:
        #print(len(intruder_lattitude), len(intruder_longitude))
        #plt.scatter(intruder_lattitude, intruder_longitude, color='red') # Creates scatter plot (dots)
        plt.plot(intruder_longitude, intruder_lattitude, color='red', zorder=1) # Creates line
        # throw error if either are empty

    for i in range(len(waypoint_latitude)):
        plt.scatter(waypoint_longitude[i], waypoint_latitude[i], marker='*', zorder=2)

    # TESTING SPACE
    # plt.scatter(-117.whatever, 34.whatever, color = 'green')
    # plt.scatter(-117.793221, 34.045700, color = 'blue')
    #plt.scatter(117.851720786, 34.0116185925, color = 'orange')
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


    if predicted_indices:
        for i in predicted_indices: # predictive paths; comment out for less hairy graph
            #plt.scatter(future_pos_x[i], future_pos_y[i]) # scatter plot dots
            plt.plot(future_pos_y[i], future_pos_x[i]) # line
            
    if plotted_point:
        for point in plotted_point:
            plt.scatter(float(point[0]), float(point[1]), c=point[2], zorder=2)

    counter = 0
    set_id = 0
    marker_lst = ['o', 'X']
    color_lst = ['#f44336', '#8fce00', '#2986cc', '#8300ff']

    if predicted_collision_point:
        for point in predicted_collision_point:
            lst = point.split()
            point_id = 0
            for i in range(len(lst)):
                counter += 1
                if counter == 2 and point_id != 2:
                    point_id += 1
                    plt.scatter(float(lst[i].replace('{','').replace('}','')),
                                float(lst[i-1].replace('{','').replace('}','')),
                                marker=marker_lst[0], c=color_lst[set_id], zorder=2)
                    counter = 0
                elif counter == 2 and point_id == 2:
                    plt.scatter(float(lst[i].replace('{', '').replace('}', '')),
                                float(lst[i - 1].replace('{', '').replace('}', '')),
                                marker=marker_lst[1], c=color_lst[set_id], zorder=2)
                    counter = 0
            set_id += 1

    plt.ticklabel_format(useOffset=False) # Display axes correctly

    plt.title(graph_name)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')

    plt.show()

def predicted_collision_points_dropdown(file_name: str):
    predicted_collision_points = []

    with open(file_name) as file:
        file_content = file.readlines()
        for i in range(len(file_content)):
            if 'Predicted crash lattitude' in file_content[i]:
                predicted_collision_points.append([
                    [(file_content[i - 6].split())[6], (file_content[i - 5].split())[6]],
                    [(file_content[i - 2].split())[6], (file_content[i - 1].split())[6]],
                    [(file_content[i].split())[6], (file_content[i + 1].split())[6]]
                ])

    return predicted_collision_points


if __name__ == '__main__':
    main(title_of_graph, name_of_file, show_intruder, show_predicted)
