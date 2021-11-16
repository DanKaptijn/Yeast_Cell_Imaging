'''
Author: Daniel Kaptijn
Date: 12/08/2021
PyVersion: 3.8.8

Aim: Make 3 graphs of a cell from mask-RCNN: std dev of SFP1 channel, cell size over time, fluorescence of histone channel.
'''

import os
import pandas as pd
from math import sqrt
import numpy as np
from numpy import std
import statistics
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.signal import savgol_coeffs
from scipy.interpolate import interp1d

""" Functions """
# Remove data points if cell size decreases by unlikely amount
def CorrectForCellArea(yhat_cell, y_cell, y_histone, ysfp, x, xv):
    no_of_deletions = 0
    index_to_remove = []
    too_noisy = False # if there are too many points being deleted, the entire cell will be discarded
    for value in range(0, len(yhat_cell)):
        if y_cell[value] < 0.9 * yhat_cell[value]:
            index_to_remove.append(value)
            no_of_deletions += 1
            change = True
        if y_cell[value] > 1.1 * yhat_cell[value]:
            index_to_remove.append(value)
            no_of_deletions += 1
            change = True
    # print('deletions', no_of_deletions)
    if no_of_deletions >= 0.1*len(yhat_cell):
        too_noisy = True
    index_to_remove.reverse()
    for index in index_to_remove:
        yhat_cell = np.delete(yhat_cell, index)
        y_cell = y_cell.drop(index, axis=0, inplace=False)
        y_histone = y_histone.drop(index, axis=0, inplace=False)
        ysfp = ysfp.drop(index, axis=0, inplace=False)
        x = x.drop(index, axis=0, inplace=False)
        del xv[index]

    return yhat_cell, y_cell, y_histone, ysfp, x, xv, too_noisy



""" Code to run """
##########################################
##########################################
""" Edit this variable to match the name of the protein in your excel spreadsheet e.g. for 'stdev of SFP1 pixel intensity' it should be SFP1 """
protein = 'SFP1'
##########################################
##########################################


no_of_cc = 0
cc_interp = [] # list of cell cycles with interpolated points so every cell cycle is the same size

directory_in_str = 'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/excel-data'
directory = os.fsencode(directory_in_str)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".xlsx"):

        df = pd.read_excel(f"{directory_in_str}/{filename}")
        print(filename)
        save_loc_area = "C:/Users/DanKap/Pictures/cell area"
        save_loc_histone = "C:/Users/DanKap/Pictures/histone intensity graphs"
        save_loc_differential = "C:/Users/DanKap/Pictures/histone differential graphs"

        cells = df.drop_duplicates(subset=["cell"])
        cells = [i for i in cells["cell"]]

        for cell in cells:
            ''' Select a cell '''
            chosen_cell = cell
            # print(chosen_cell)

            df_chosen_cell = df[df['cell']==chosen_cell]


            ''' data for std dev of Protein of interest '''
            plt.style.use('bmh')
            fig = plt.figure()
            ax = plt.axes()

            x = df_chosen_cell['frame']
            ysfp = df_chosen_cell[f'stdev of {protein} pixel intensity']
            ysfp.index = [i for i in range(len(ysfp))]
            xv = [1] * len(ysfp)
            y_cell = df_chosen_cell['area']
            y_histone = df_chosen_cell['histone pixel intensity']
            x.index = [num for num in range(len(x))]
            y_cell.index = [num for num in range(len(y_cell))]
            y_histone.index = [num for num in range(len(y_histone))]

            if len(ysfp) > 40:
                yhatsfp = savgol_filter(ysfp, 7, 3) # window size 7, polynomial order 3

            if len(ysfp) < 40:
                plt.close()
                continue


            ''' data for size of cell '''
            if len(y_cell) > 40:
                yhat_cell = savgol_filter(y_cell, 21, 2) # window size 7, polynomial order 2

                yhat_cell, y_cell, y_histone, ysfp, x, xv, too_noisy = CorrectForCellArea(yhat_cell, y_cell, y_histone, ysfp, x, xv)
                if too_noisy: # this will reduce the number of timepoints to try and get a clean signale
                    x = df_chosen_cell['frame']
                    ysfp = df_chosen_cell[f'stdev of {protein} pixel intensity']
                    y_cell = df_chosen_cell['area']
                    y_histone = df_chosen_cell['histone pixel intensity']

                    x.index = [num for num in range(len(x))]
                    ysfp.index = [i for i in range(len(ysfp))]
                    y_cell.index = [num for num in range(len(y_cell))]
                    y_histone.index = [num for num in range(len(y_histone))]

                    x = x.truncate(after = round(len(x)*0.8))
                    ysfp = ysfp.truncate(after = round(len(ysfp)*0.8))
                    y_cell = y_cell.truncate(after = round(len(y_cell)*0.8))
                    y_histone = y_histone.truncate(after = round(len(y_histone)*0.8))
                    xv = [1] * len(ysfp)
                    yhat_cell = savgol_filter(y_cell, 21, 2) # window size 7, polynomial order 2

                    yhat_cell, y_cell, y_histone, ysfp, x, xv, too_noisy = CorrectForCellArea(yhat_cell, y_cell, y_histone, ysfp, x, xv)

                if too_noisy: # this reduces the timepoints even more to try and get a clean signal
                    x = df_chosen_cell['frame']
                    ysfp = df_chosen_cell[f'stdev of {protein} pixel intensity']
                    y_cell = df_chosen_cell['area']
                    y_histone = df_chosen_cell['histone pixel intensity']

                    x.index = [num for num in range(len(x))]
                    ysfp.index = [i for i in range(len(ysfp))]
                    y_cell.index = [num for num in range(len(y_cell))]
                    y_histone.index = [num for num in range(len(y_histone))]

                    x = x.truncate(after = round(len(x)*0.6))
                    ysfp = ysfp.truncate(after = round(len(ysfp)*0.6))
                    y_cell = y_cell.truncate(after = round(len(y_cell)*0.6))
                    y_histone = y_histone.truncate(after = round(len(y_histone)*0.6))
                    xv = [1] * len(ysfp)
                    yhat_cell = savgol_filter(y_cell, 21, 2) # window size 7, polynomial order 2

                    yhat_cell, y_cell, y_histone, ysfp, x, xv, too_noisy = CorrectForCellArea(yhat_cell, y_cell, y_histone, ysfp, x, xv)

                if too_noisy: # finally the rest are deemed too noisy and not used to find cell cycles
                    plt.close()
                    continue
                x.index = [num for num in range(len(x))]
                y_cell.index = [num for num in range(len(y_cell))]
                y_histone.index = [num for num in range(len(y_histone))]
                ysfp.index = [num for num in range(len(ysfp))]

                yhat_cell = savgol_filter(y_cell, 21, 2)


            ''' data from histone channel '''
            if len(y_histone) > 40:
                yhat_histone = savgol_filter(y_histone, 7, 3) # window size 7, polynomial order 3
                grad = savgol_filter(yhat_histone,7,3,deriv=1)
                grad_std = -1.3 * statistics.stdev(grad)

                cctp = [] # list for cell cycle timepoints
                break_point = False # used to locate minimum value during cell division
                grad_value_min = 0
                for diff in range(len(grad)):
                    if grad[diff] <= grad_std and diff != 0:
                        grad_value = grad[diff]
                        if grad_value < grad_value_min: # we want to find the point at which the slope is at the minimum
                            grad_value_min = grad_value
                        break_point = True
                    if grad[diff] > grad_std and break_point == True:
                        break_point = True # this is to stop multiple timepoints happening in a row
                        diff_value = x[diff]
                        cctp.append(diff_value)
                        grad_value_min = 0
                        break_point = False

                if len(cctp) < 10 and len(cctp) > 1: # too many cell cycles is a sign of too much noise
                    list_of_cc = []
                    temp_list = []
                    for num in range(len(yhat_histone)): # collect all SFP1 data for cell cycles calculated above
                        if num in cctp:
                            list_of_cc.append(temp_list)
                            temp_list = []
                        temp_list.append(ysfp[num])
                    # list_of_cc.append(temp_list)

                    skip_first_cc = True # we skip the first cell cycle as it is likely incomplete or the growth stage of a bud
                    for cell_cycle in list_of_cc:
                        cc_mean = statistics.mean(cell_cycle)
                        cell_cycle = [x/cc_mean for x in cell_cycle]
                        if skip_first_cc == False and len(cell_cycle) > 10:
                            xcc = [j for j in range(len(cell_cycle))]
                            f = interp1d(xcc, cell_cycle) # interpolate points so that every cell cycle consists of 60 data points
                            # f2 = interp1d(x, i, kind="cubic")
                            xnew = np.linspace(0, len(cell_cycle)-1, num=60, endpoint=True)
                            cc_interp.append(f(xnew))
                            no_of_cc += 1
                            # plt.plot(xcc, cell_cycle)
                            plt.plot(xnew, f(xnew))
                            # plt.show()
                            plt.close()
                        skip_first_cc = False


                xv = [[x] * len(ysfp) for x in cctp]


                """ Making Graphs """
        ##########################################

                if len(y_cell > 40):

                    """ Plotting cell size across frames for a cell """
                    plt.plot(x, y_cell)
                    plt.plot(x, yhat_cell)
                    title = f"Size of cell {chosen_cell} over time"
                    plt.title(title)
                    plt.xlabel("Frame")
                    plt.ylabel("Cell Area")
                    # plt.show()
                    # plt.savefig(f"{save_loc_area}/Size of cell {chosen_cell}")
                    plt.close()
        ##########################################

                    """ Plotting the Pixel Intensity for the histone channel for a cell """
                    plt.plot(x, y_histone)
                    plt.plot(x, yhat_histone, color="firebrick")
                    for thing in xv:
                        plt.plot(thing, yhat_histone, color='black')
                    title = f"Pixel intensity for histone over time for cell {chosen_cell}"
                    plt.title(title)
                    plt.xlabel("Frame")
                    plt.ylabel("Pixel intensity of histone")
                    # plt.show()
                    # plt.savefig(f"{save_loc_histone}/Histone pixel intensity for cell {chosen_cell}")
                    plt.close()
        ##########################################

                    """ Plotting differentail with stdev threshold """
                    plt.plot(x, grad)
                    plt.plot(x, [grad_std]*len(x))
                    title = f"Differentiation of timepoint for cell {chosen_cell}"
                    plt.title(title)
                    plt.xlabel("Frame")
                    plt.ylabel(f"Differential")
                    # plt.show()
                    # plt.savefig(f"{save_loc_differential}/Differentiation of timepoint for cell {chosen_cell}")
                    plt.close()
        ##########################################

                    """ Plotting protein stdev with cell cycle timepoints """
                    plt.plot(x, ysfp)
                    for thing in xv:
                        plt.plot(thing, ysfp, color='black')
                    yhatsfp = savgol_filter(ysfp, 7, 3) # window size 7, polynomial order 3
                    plt.plot(x, yhatsfp, color="firebrick")
                    title = f"{protein} standard deviation over time for cell {cell}"
                    plt.title(title)
                    plt.xlabel("Frame")
                    plt.ylabel(f"Std dev {protein}")
                    # plt.show()
                    plt.close()
        ##########################################

    print(f"Total cell cycles so far: {no_of_cc}")

plt.close()
# print(no_of_cc)
xnew = np.linspace(0, 1, num=60, endpoint=True)
a = np.array(cc_interp)
res = np.average(a, axis=0)
se = (2*(std(a, axis=0))) / sqrt(no_of_cc)
resplus = res+se
resminus = res-se
plt.plot(xnew,resplus, color='dodgerblue', alpha=0.2)
plt.plot(xnew,resminus, color = 'dodgerblue', alpha=0.2)
plt.fill_between(xnew, resplus, resminus, color='dodgerblue', alpha=0.2)
plt.plot(xnew,res, color='blue')
title = f"Standard deviation of {protein} over all cell cycles (n={no_of_cc})"
plt.title(title)
plt.xlabel("proportion along cell cycle")
plt.ylabel(f"Stdev of {protein} pixel intensity")
plt.show()
plt.close()
