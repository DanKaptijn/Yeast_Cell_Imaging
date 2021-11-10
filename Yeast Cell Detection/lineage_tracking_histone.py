'''
Author: Daniel Kaptijn
Date: 22/09/2021
PyVersion: 3.8.8

Aim: Using histone channel to predict a daughter yeast cells' mother cell
'''

import pandas as pd
from math import sqrt
from numpy import std
import statistics
import matplotlib.pyplot as plt

df = pd.read_excel("cell detections.xlsx")

DISTANCE = 30
HISTONE_INTENSITY = 1000 # the minimum pixel intensity value when a cell has a histone

print("Creating dictionaries for data..")
mother_dict = {}

list_of_cells = df.drop_duplicates(subset=['cell'])

print("Calculating possible mother cells..")
possible_mothers = {}
for cell in list_of_cells["cell"]:
    cell_data = df[df["cell"]==cell]
    cell_data.index = [i for i in range(len(cell_data["frame"]))]
    if cell_data["histone pixel intensity"][0] > HISTONE_INTENSITY:
        mother_dict[str(cell)] = "None"
        print(f"cell {cell} is a mother cell")
    else:
        possible_mothers[str(cell)] = []
        mothers_found = 0
        for histone, frame in zip(cell_data["histone pixel intensity"], cell_data["frame"]):
            if len(cell_data[cell_data["frame"]==frame-1]["histone pixel intensity"].values) ==0:
                continue
            if (histone > 5*cell_data[cell_data["frame"]==frame-1]["histone pixel intensity"].values[0] or histone > HISTONE_INTENSITY)  and mothers_found == 0:
            # if histone > 5*cell_data[cell_data["frame"]==frame-1]["histone pixel intensity"].values[0]  and mother_found == 0:
                temp_df = df[df["frame"]==frame]
                for i in temp_df["cell"]:
                    new_cell = temp_df[temp_df["cell"]==cell] # this is the cell we want to determine the mother of
                    new_cell.index = [i for i in range(len(new_cell["cell"]))]
                    other_cell = temp_df[temp_df["cell"]==i] # this is another cell in the same frame that could be the mother cell
                    other_cell.index = [i for i in range(len(other_cell["cell"]))]
                    if other_cell["area"][0] < 200 or other_cell["cell"].values[0] == new_cell["cell"].values[0]: # Ensure small cells not considered for mother cells, also cell can't consider itself as a mother cell
                        continue
                    if ( sqrt( (other_cell["x"][0]-new_cell["x"][0])**2 + (other_cell["y"][0]-new_cell["y"][0])**2 ) ) < DISTANCE:
                        possible_mothers[str(cell)].append(other_cell["cell"][0])
                for mother in possible_mothers[str(cell)]:
                    histone_value = 0
                    for i in range(frame-1, frame+2):
                        temp_df = df[df["frame"]==i]
                        temp_df = temp_df[temp_df["cell"]==mother]
                        if len(temp_df["histone pixel intensity"].values) == 0: # skip empty values
                            continue
                        if temp_df["histone pixel intensity"].values[0] < 0.7*histone_value:
                            mothers_found += 1
                            found_mother = mother
                            break
                        if histone_value == 0:
                            histone_value = temp_df["histone pixel intensity"].values[0]
                if mothers_found == 0:
                    mother_dict[str(cell)] = "Unknown"
                    print(f"cell: {cell} Unknown mother, no candidates.")
                if mothers_found == 1:
                    mother_dict[str(cell)] = found_mother
                    print(f"cell: {cell}, mother: {found_mother}")
                if mothers_found > 1:
                    mother_dict[str(cell)] = "Unknown"
                    print(f"cell: {cell} Unknown mother, more than 1 candidate. {mothers_found}")
                break
        if mothers_found == 0:
            mother_dict[str(cell)] = "Unknown"

# exit()
# print(mother_dict)
"""Creating dictionary for generations in order to create a column showing how many generations have reproduced"""
print("Creating data for excel..")
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
            if generation > 10: # in cases where 2 cells have each other as a mother cell creating an infinite loop
                generation_found = True
                generations_dict[key] = "Unknown"
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
print("Creating excel spreadsheet..")
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
