longitude = []
lattitude = []

result = {}

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

file.close()

for longi in longitude:
    for lat in lattitude:
        result[longi] = lat
        lattitude.remove(lat)
        break
    
print(result)