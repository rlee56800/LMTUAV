import matplotlib.pyplot as plt

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