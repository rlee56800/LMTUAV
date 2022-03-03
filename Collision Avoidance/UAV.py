import matplotlib.pyplot as plt
<<<<<<< HEAD

########## CHANGE FILE NAME HERE ########## 
name = 'Log Outputs 2021_12_24/log_output_2021_12_24 (1).txt'
title = 'Flight Graph: 12/24/21 Simulation 1'

longitude = []
lattitude = []

with open(name) as file:
    for line in file:

        if 'Current lattitude' in line:
            i = line.split()
            i = float(i[6])
            lattitude.append(i)
        elif 'Current longitude' in line:
            i = line.split()
            i = float(i[6])
            longitude.append(i)


print("{}\n\n{} ".format(longitude, lattitude))


plt.scatter(lattitude, longitude)
plt.plot(lattitude, longitude)

plt.title(title)
plt.xlabel('Latitude')
plt.ylabel('Longitude')

plt.show()
=======

########## CHANGE FILE NAME HERE ########## 
title_of_graph = 'Flight Graph: 12/24/21 Simulation 3'
name_of_file = 'Log Outputs 2021_12_24/log_output_2021_12_24 (3).txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
show_predicted = [0, 10, 20, 30] # index/indices of value to show predicted values


def main(graph_name: str, file_name: str, predicted_indices = []):
    ########## Graphing ########## 
    longitude = []
    lattitude = []
    future_pos_x = []
    future_pos_y = []
    x = []
    y = []

    with open(file_name) as file:
        for line in file:
            if 'Current lattitude' in line:
                i = line.split()
                i = i[6]
                lattitude.append(float(i))
            elif 'Current longitude' in line:
                i = line.split()
                i = i[6]
                longitude.append(float(i))
            elif '~~~~~~~~~~New Point~~~~~~~~~~~~' in line:
                # future_pos are lists of future positions from each point
                future_pos_x.append(x)
                future_pos_y.append(y)
                x = []
                y = []
            elif 'futurePosX' in line:
                i = line.split()
                i = i[5]
                x.append(float(i))
            elif 'futurePosY' in line:
                i = line.split()
                i = i[5]
                y.append(float(i))
    future_pos_x.append(x)
    future_pos_y.append(y)

    future_pos_x.pop(0) # 0th element is empty
    future_pos_y.pop(0) # 0th element is empty

    plt.figure(figsize=(10, 7)) # Window size

    if predicted_indices:
        for i in predicted_indices: # predictive paths; comment out for less hairy graph
            #plt.scatter(future_pos_x[i], future_pos_y[i]) # scatter plot dots
            plt.plot(future_pos_x[i], future_pos_y[i]) # line

    plt.scatter(lattitude, longitude, color='black') # Creates scatter plot (dots)
    plt.plot(lattitude, longitude, color='black') # Creates line

    plt.ticklabel_format(useOffset=False) # Display axes correctly

    plt.title(graph_name)
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')

    plt.show()


if __name__ == '__main__':
    main(title_of_graph, name_of_file, show_predicted)
>>>>>>> f828a5da47abe12dc64dc129d48eb3ac06f25287
