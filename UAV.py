import matplotlib.pyplot as plt

########## CHANGE FILE NAME HERE ########## 
name = 'Log Outputs 2021_12_24/log_output_2021_12_24 (1).txt'

longitude = []
lattitude = []

index = 0

with open(name) as file:
    for line in file:
        index += 1

        if 'Current lattitude' in line:
            i = line.split()
            i = i[6]
            lattitude.append(i)
        elif 'Current longitude' in line:
            i = line.split()
            i = i[6]
            longitude.append(i)

plt.plot(lattitude, longitude)
plt.show()