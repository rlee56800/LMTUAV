import matplotlib.pyplot as plt
#import tkinter

########## CHANGE FILE NAME HERE ########## 
title_of_graph = 'Flight Graph: 12/24/21 Simulation 3'
name_of_file = 'Log Outputs 2021_12_24/log_output_2021_12_24 (3).txt'
## NOTE: check if file has completed time stamps (i.e. has both future x AND y pos)
show_predicted = [0, 10, 20, 30] # index/indices of value to show predicted values


########## GUI ########## 
#master = tkinter.Tk(className="Graph Options")
#tkinter

########## Graphing ########## 
longitude = []
lattitude = []
future_pos_x = []
future_pos_y = []
x = []
y = []

with open(name_of_file) as file:
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

if show_predicted:
    for i in show_predicted: # predictive paths; comment out for less hairy graph
        #plt.scatter(future_pos_x[i], future_pos_y[i]) # scatter plot dots
        plt.plot(future_pos_x[i], future_pos_y[i]) # line

#plt.scatter(lattitude, longitude, color='black') # Creates scatter plot (dots)
plt.plot(lattitude, longitude, color='black') # Creates line

plt.ticklabel_format(useOffset=False) # Display axes correctly

plt.title(title_of_graph)
plt.xlabel('Latitude')
plt.ylabel('Longitude')

plt.show()

#master.mainloop()