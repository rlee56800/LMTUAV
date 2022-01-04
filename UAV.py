
import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ########## 
name = 'Log Outputs 2021_12_24/log_output_2021_12_24 (3).txt'
title = 'Flight Graph: 12/24/21 Simulation 3'



longitude = []
lattitude = []

with open(name) as file:
    for line in file:
      
        if 'Current lattitude' in line:
            i = line.split()
            i = i[6]
            lattitude.append(float(i))
        elif 'Current longitude' in line:
            i = line.split()
            i = i[6]
            longitude.append(float(i))


plt.figure(figsize=(10, 7))
plt.scatter(lattitude, longitude)
plt.plot(lattitude, longitude)

plt.ticklabel_format(useOffset=False)

plt.title(title)
plt.xlabel('Latitude')
plt.ylabel('Longitude')

plt.show()
