'''
Author: Daniel Kaptijn
Date: 05/05/2021
PyVersion: 3.7.6

Aim: Using available data predict a yeast cells mother cell
'''

import pandas as pd
from math import sqrt
from numpy import std
import statistics
import matplotlib.pyplot as plt

df = pd.read_excel("cell detections.xlsx")


"""sample contains two cells that appear after frame 0, one is a FP"""
sample = df.loc[0:101,:]

"""The distance a cell can be in order to be considered the mother cell"""
DISTANCE = 30
NO_FRAMES = 10

"""Create first entries in a dictionary called mother_dict with the cells from frame 0 above a cut-off size"""
"""cells not present in frame 0 are added to a list called cells_to_check along with the frame they first appear in and their mother cell will be determined"""
mother_dict = {}
cells_to_check = []
cell_sizes_dict = {}
# appear_frame = df.groupby("cell")['frame'].min()
# cell_area = df.groupby("cell")['area'].min()
first_frame_area = df.drop_duplicates(subset=['cell'])
first_frame_area = first_frame_area.filter(items=["cell","frame","area"])
first_frame_area = first_frame_area.sort_values(["cell","frame"])
first_frame_area.index = [i for i in range(len(first_frame_area))]
for i in range(len(first_frame_area)):
    if first_frame_area["frame"][i] == 0 and first_frame_area["area"][i] >= 150:
        mother_dict[str(i)] = "None"
        cell_sizes_dict[str(i)] = first_frame_area["area"][i]
    else:
        cells_to_check.append([i,first_frame_area["frame"][i]])
        cell_sizes_dict[str(i)] = first_frame_area["area"][i]


"""possible_mothers is a dictionary showing the cells likely to be a cells mother: key=cell, value=possible mother(s)"""
possible_mothers = {}
for cell in cells_to_check:
    possible_mothers[str(cell[0])] = [] # Creates a new key in the possible_mothers dictionary
    temp = df[df["frame"]==cell[1]] # a subset of the initial dataframe containing all the data from the frame the cell appeared in
    temp = temp.sort_values("cell") # put them in numerical order (e.g. cell 0 will be first)
    temp.index = [i for i in range(len(temp["cell"]))] # A new index needs to be set
    for i in temp["cell"]:
        new_cell = temp[temp["cell"]==cell[0]] # this is the cell we want to determine the mother of
        new_cell.index = [i for i in range(len(new_cell["cell"]))]
        other_cell = temp[temp["cell"]==i] # this is another cell in the same frame that could be the mother cell
        other_cell.index = [i for i in range(len(other_cell["cell"]))]
        if other_cell["area"][0] < 200 or other_cell["cell"].values[0] == new_cell["cell"].values[0]: # Ensure small cells not considered for mother cells, also cell can't consider itself as a mother cell
            continue
        if ( sqrt( (other_cell["x"][0]-new_cell["x"][0])**2 + (other_cell["y"][0]-new_cell["y"][0])**2 ) ) < DISTANCE:
            possible_mothers[str(cell[0])].append(other_cell["cell"][0])


"""For cells with more than one possible mother cell further analysis is done on the distance over time"""
distances_dict = {}
for key in possible_mothers:
    if len(possible_mothers[key]) < 1: # These are cells that had no identified nearby adult cells
        if (key) not in mother_dict:
            mother_dict[key] = "Unknown"
    if len(possible_mothers[key]) >= 1:
        for i in cells_to_check:
            if str(i[0]) == key:
                frames = [j for j in range(i[1],i[1]+NO_FRAMES)]
                cells = [int(key)] + possible_mothers[key]
                df_slice = df[df["frame"].isin(frames)]
                df_slice = df_slice[df_slice["cell"].isin(cells)]
                for frame in frames:
                    df_frame = df_slice[df_slice["frame"]==frame]
                    for cell in cells:
                        if cell != cells[0]:
                            if str(cells[0]) not in distances_dict: # Create dictionary within dictionary with daughter cell as the key for outer dictionary
                                distances_dict[str(cells[0])] = {}
                            if str(cell) not in distances_dict[str(cells[0])]: # each candidate mother cell is a key for the inner dictionary with the value being the distances between the daughter and candidate cell
                                distances_dict[str(cells[0])][str(cell)] = []
                            try: # If the cell isn't detected in a frame no distance can be calculated
                                x_dist = (df_frame[df_frame["cell"]==cell]["x"].array[0]-df_frame[df_frame["cell"]==cells[0]]["x"].array[0])**2
                                y_dist = (df_frame[df_frame["cell"]==cell]["y"].array[0]-df_frame[df_frame["cell"]==cells[0]]["y"].array[0])**2
                                dist = sqrt(x_dist + y_dist)
                                distances_dict[str(cells[0])][str(cell)].append(dist)
                            except:
                                continue


"""Calculating The Mother Cell"""
for cell in possible_mothers:
    for key in distances_dict:
        if cell == key:
            temp_list = []
            for candidate in distances_dict[key]:
                unknown = False
                variance = 0 # A defined variance cut-off will remove unsuitable cells
                change = 0 # A defined distance change metric will remove unsuitable cells
                mean = statistics.mean(distances_dict[key][candidate])
                first = distances_dict[key][candidate][0]
                prev = first
                for value in distances_dict[key][candidate]:
                    variance += (value-mean)**2
                    change += (value-prev)
                    prev = value
                variance = variance/len(distances_dict[key][candidate])

                if variance < 10 and change > 0 and change < 10:
                    temp_list.append(candidate)

                if len(temp_list) == 0:
                    unknown = True
            # temp_list = [(i-1)**2 for i in temp_list]
            if unknown == False:
                mother_dict[cell] = temp_list[0]
            else:
                mother_dict[cell] = 'Unknown'


"""Creating dictionary for generations in order to create a column showing how many generations have reproduced"""
def Generations(key):
    new_key = str(mother_dict[key])
    return new_key

generations_dict = {}
for key in mother_dict: #go through every cell in the movie
    generation_found = False #boolian to allow for later loop that can calculate generations indefinitely
    if mother_dict[key] == "None": #"None" are the original cells in the movie (generation 0)
        generation_found = True
        generations_dict[key] = 0
    elif mother_dict[key] == "Unknown": #If mother was unknoen it is impossible to find a generation (likely FP)
        generation_found = True
        generations_dict[key] = "Unknown"
    else:
        next_key = key #as each value is a mother cell we can use this value to find the mother of the mother cell until we get to "None"
        generation = 0
        while generation_found==False:
            generation += 1
            try:
                next_key = Generations(next_key)
                if mother_dict[next_key] == "None":
                    generation_found = True
                    generations_dict[key] = generation
            except:
                generation_found = True
                generations_dict[key] = "Unknown"

"""
List of Outputs:
-mother_dict = The dictionary containing the cell ID and the ID of its mother (None means the cell existed in frame 0, unknown usually means cell was a FP)
-possible_mothers = The dictionary containing cells which had multiple mothers as options, contains each option as well
-distances_dict = The dictionary with the distance between a cell and each candidate mother cell
-generations_dict = The dictionary showing how many generations of cells have managed to produce a daughter cell
-cell_sizes_dict = The dictionary of the size of each cell when it was first detected
"""

"""Adding lineage to excel spreadsheet"""
cell = []
mother = []
for key in range(len(mother_dict)):
    cell.append(key)
    mother.append(mother_dict[str(key)])

new_col = {"cell":cell, "mother":mother}
new_col = pd.DataFrame(new_col)
df_merged = pd.merge(df, new_col)
df_merged = df_merged.sort_values(["frame","mask"])

"""Adding generations to excel spreadsheet"""
cell = []
generation = []
for key in range(len(generations_dict)):
    cell.append(key)
    generation.append(generations_dict[str(key)])

new_col = {"cell":cell, "generation":generation}
new_col = pd.DataFrame(new_col)
df_merged = pd.merge(df_merged, new_col)
df_merged = df_merged.sort_values(["frame","mask"])

saving = input("Do you want to save the output?: ")
if saving.lower() == "yes" or saving.lower() == "y":
    print("saving file as lineage detections.xlsx")
    df_merged.to_excel(r'lineage detections.xlsx', index = False)
if saving.lower() != "yes" and saving.lower() != "y":
    print("file not saved")

print(mother_dict)
exit()
""" Making Plots of Pairwise Distance """
plt.style.use('seaborn-whitegrid')
fig = plt.figure()
ax = plt.axes()
# plt.plot(test, linestyle = "solid")
cell_count = 0
labelled_TP = False
labelled_FP = False
title = ""
# list_mother_cells = [10,4,5,3,0,1,7,9,10,13,6,0,13,4,3,5,2,2,8,16,19,1,7,9,10,3,13,12,6,25,4,15,12,16,17,32,5,28]
list_mother_cells = [9,7,3,5,1,8,2,8,9,0,10,3]
# list_daugh_cells_ID = [16,17,18,19,20,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,40,41,42,43,44,46,47,48,50,51,52,53,54,55,57,59,60]
list_daugh_cells_ID = [11,15,16,17,18,19,20,21,22,23,25,26]
for key in distances_dict:
    # if count == 88:
    #     print(key)
    #     plt.plot(distances_dict[key], linestyle = "solid", color = "blue")
    if int(key) in list_daugh_cells_ID:
        for candidate in distances_dict[key]:
            if candidate == str(list_mother_cells[cell_count]):
                first = distances_dict[key][str(list_mother_cells[cell_count])][0]
                mean = statistics.mean(distances_dict[key][candidate])
                median = statistics.median(distances_dict[key][candidate])
                variance = 0
                change = 0
                prev = first
                for i in distances_dict[key][candidate]:
                    variance += (i-mean)**2
                    change += (i-prev)
                    prev = i
                variance = variance/len(distances_dict[key][candidate])
                sd = sqrt(variance)
                # last = distances_dict[key][str(list_mother_cells[cell_count])][len(distances_dict[key][str(list_mother_cells[cell_count])]  )-1]
                # y = (last-first)/len(distances_dict[key][str(list_mother_cells[cell_count])])
                y = variance
                x = key
                # x = cell_sizes_dict[key]
                if labelled_TP == False:
                    plt.scatter(x, y, color="lime", label='Mother cell')
                    labelled_TP = True
                else:
                    plt.scatter(x, y, color = "lime")
                plt.text(x, y, candidate)
            else:
                first = distances_dict[key][candidate][0]
                mean = statistics.mean(distances_dict[key][candidate])
                median = statistics.median(distances_dict[key][candidate])
                variance = 0
                change = 0
                prev = first
                for i in distances_dict[key][candidate]:
                    variance += (i-mean)**2
                    change += (i-prev)
                    prev = i
                variance = variance/len(distances_dict[key][candidate])
                sd = sqrt(variance)
                # last = distances_dict[key][candidate][len(distances_dict[key][candidate]  )-1]
                # y = (last-first)/len(distances_dict[key][candidate])
                y = variance
                x = key
                # x = cell_sizes_dict[key]
                if labelled_FP == False:
                    plt.scatter(x, y, color="blue", label='Other cell')
                    labelled_FP = True
                else:
                    plt.scatter(x, y, color = "blue")
                plt.text(x, y, candidate)
        cell_count += 1
y = [10]*len(list_daugh_cells_ID)
plt.plot(y, "r--", color = "red", label="Chosen cut-off")
# y = [0]*len(list_daugh_cells_ID)
# plt.plot(y, "r--", color = "red")
title = "Variance of distance over 10 frames"
plt.title(title)
# plt.xlabel("Frame")
# plt.ylabel("Distance")
plt.xlabel("Daughter Cell")
plt.ylabel("Variance")
leg=ax.legend()
plt.show()
