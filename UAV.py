import matplotlib.pyplot as plt

longitude = []
lattitude = []

map = {}

file = open(r"C:\\Users\\justi\Desktop\\logData.txt", "r+")

index = 0

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

file.close()