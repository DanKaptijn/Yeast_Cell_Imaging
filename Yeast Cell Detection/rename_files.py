'''
Author: Daniel Kaptijn
Date: 23/04/2021
PyVersion: 3.7.6

Aim: Automate the renaming and separation of brightfield and flourescent images of yeast cells
'''

""" NOTE: run FaxTool before running this code """

import os
import shutil

FILENAME = "ser11" #To edit this edit for loop below (currently set to be first 5 characters of a filename)
EXT = ".tif"
CHANNELS = int(input("How many channels are in the movie?: "))
BRIGHT = int(input("Which channel is the brightfield channel?: "))-1
FLUORESCENT = int(input("Which channel is the fluorescent channel?: "))-2

""" In case the first channel is the fluorescent channel, need to set to 0 """
if FLUORESCENT == -1:
    FLUORESCENT = 0

path = "C:/Users/danka/Documents/Internships/Yeast Cell Tracking/Movies/mask-RCNN_input/"

for filename in os.listdir(path):
    FILENAME = filename[0:5] # This needs to be editted to change the filename
    break

number_of_files = len(os.listdir(path))

""" Loop which adds leading zeroes so that the images will be in the correct order """
num = 0
for i in range(0, number_of_files):
    num += 1
    no_zeroes = len(str(number_of_files)) - len(str(num))
    for filename in os.listdir(path):
        if "_"+str(num)+EXT in filename:
            new_filename = FILENAME + "_" + "0"*no_zeroes + str(num) + EXT
            os.rename(os.path.join(path, filename), os.path.join(path, new_filename))

""" Loop which separates a brightfield and a fluorescent channel from the rest """
new_path_1 = "C:/Users/danka/Documents/Internships/Yeast Cell Tracking/Movies/br channel/"
new_path_2 = "C:/Users/danka/Documents/Internships/Yeast Cell Tracking/Movies/fl channel/"
num = 0 - BRIGHT
if len(os.listdir(new_path_1)) > 1:
    print(f"\nNot moving files as brightfield folder is not empty:\n{new_path_1}")

if len(os.listdir(new_path_2)) > 1:
    print(f"\nNot moving files as fluorescence folder is not empty:\n{new_path_2}")

if len(os.listdir(new_path_1)) <= 1 and len(os.listdir(new_path_2)) <= 1:
    print(f"\nBright field and first fluorescent channel moved to: \n{new_path_1} \n{new_path_2}")
    for filename in os.listdir(path):
        if num % CHANNELS == 0:
            shutil.move(f"{path}{filename}", f"{new_path_1}{filename}")
        num += 1
    CHANNELS -= 1
    num = 0 - FLUORESCENT
    for filename in os.listdir(path):
        if num % CHANNELS == 0:
            shutil.move(f"{path}{filename}", f"{new_path_2}{filename}")
        num += 1
