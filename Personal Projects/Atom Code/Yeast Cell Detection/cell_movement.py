'''
Author: Daniel Kaptijn
Date: 05/05/2021
PyVersion: 3.7.6

Aim: Remove False Positives by checking how much they have moved
'''

import pandas as pd
from math import sqrt

df = pd.read_excel("cell detections.xlsx")

cells = df[df["frame"]==0]
cells = cells["cell"]

first_frame = df[df["frame"]==df["frame"].min()]
final_frame = df[df["frame"]==df["frame"].max()]

for i in cells:
    check = 0
    if i in first_frame["cell"].values:
        x1 = first_frame[first_frame["cell"]==i]
        x1 = x1["x"].values[0]
        y1 = first_frame[first_frame["cell"]==i]
        y1 = y1["y"].values[0]
    if i in final_frame["cell"].values:
        check = 1
        x2 = final_frame[final_frame["cell"]==i]
        x2 = x2["x"].values[0]
        y2 = final_frame[final_frame["cell"]==i]
        y2 = y2["y"].values[0]
    if check == 1:
        print("cell ", i)
        print(sqrt((x2 - x1)**2 + (y2 - y1)**2))
        print("\n")
