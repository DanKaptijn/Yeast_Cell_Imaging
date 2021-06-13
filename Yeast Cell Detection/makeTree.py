'''
Author: Daniel Kaptijn
Date: 03/06/2021
PyVersion: 3.7.6

Aim: Make a simple phylogenetic tree using graphviz
p.s. To use graphviz on Windows with anaconda: conda install python-graphviz

user guide: https://graphviz.readthedocs.io/en/stable/manual.html
node shapes: https://graphviz.org/doc/info/shapes.html
more examples: https://graphviz.readthedocs.io/en/stable/examples.html
more examples: https://stackoverflow.com/questions/49480361/how-to-keep-nodes-on-the-same-rank-using-python-and-graphviz
'''

import pandas as pd
from graphviz import Graph
file_location = 'tree_images/tree.gv'


''' Import spreadsheet and extract required information '''
df = pd.read_excel("lineage detections.xlsx")

df_all_cells = df.drop_duplicates(subset=['cell'])
df_all_cells = df_all_cells.filter(items=["cell","mother"])
df_all_cells = df_all_cells.sort_values(["cell"])
df_all_cells.index = [i for i in range(len(df_all_cells))]

a_dict = {} # dictionary used in loop to create neat connections in phylogenetic tree
list_edges = [] # edges create the connections in the tree, this list is created in the loop before being added to the tree
dot = Graph(comment='Yeast Lineage')

for cell in df_all_cells["cell"]:
    if df_all_cells["mother"][cell] == "None": # these are the original cells which do not have an assigned mother cell
        dot.node(f'cell {cell}', shape='box', fillcolor='deepskyblue', style='filled') # this command draws a box with the cell number inside
    elif df_all_cells["mother"][cell] == "Unknown": # we do not want these cells in the tree
        continue
    else: # these are all daughter cells and need edges drawn between them and their respective mother cell
        fill = 'lime'
        # wrong_list = [16,37,47,50,52]
        # if cell in wrong_list:
        #     fill = 'red'
        dot.node(f'cell {cell}', shape='box', fillcolor=fill, style='filled')
        if f'{df_all_cells["mother"][cell]}' not in a_dict: # this is done to make sure there is only one line coming from the mother cell
            dot.node(f'cell {df_all_cells["mother"][cell]}A', shape='point') # creates a dot between mother and daughter(s)
            list_edges.append((f'cell {df_all_cells["mother"][cell]}', f'cell {df_all_cells["mother"][cell]}A')) # draws line between mother and dot
            a_dict[f'{df_all_cells["mother"][cell]}'] = 1 # the value here does not matter, only that there is a value
        list_edges.append((f'cell {df_all_cells["mother"][cell]}A', f'cell {cell}')) # draws line between daughter and dot

dot.edges(list_edges)

'''Choose your preferred file format'''
dot.format = 'svg'
# dot.format = 'jpg'
# dot.format = 'png'

dot.graph_attr['rankdir'] = 'LR'
dot.graph_attr['splines'] = 'polyline'
# dot.graph_attr['splines'] = 'ortho'
# dot.graph_attr['splines'] = 'line'

# print(dot.source)
dot.render(file_location, view=True)
