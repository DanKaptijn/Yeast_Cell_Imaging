from PIL import Image
import numpy as np

img = Image.open("C:/Users/danka/Documents/Internships/Yeast Cell Tracking/Movies/mask-RCNN_input/ser20_0001.tif")

out = "C:/Users/danka/Documents/Internships/Yeast Cell Tracking/Movies/files/image.txt"

output = open(out, 'w')
counter = 0
for i in np.array(img):
    print(max(i))
    output.write("[")
    for j in i:
        if counter%10 ==0:
            output.write(str(j))
            output.write(" ")
        counter += 1
    output.write("]")
    output.write("\n")

output.close()

print (np.array(img))
