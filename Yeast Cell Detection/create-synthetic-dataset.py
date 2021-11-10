import numpy
import sys

new_path = 'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/syntheticyeastcells/'
if new_path not in sys.path:
    sys.path.append(new_path)

from detectron22 import create_dataset
import umsgpack


if __name__ == "__main__":
    version = 'v1'
    synthetic_data_path = f'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/synthetic-yeast-cells-{version}/'

    labels = create_dataset(synthetic_data_path,\
    sets={'test': 0, 'val': 0, 'train': 1},\
    n_cells_per_image=100,\
    size=(512, 512),\
    min_distance_boundary=50,\
    # r0_range=(2, 14),
    r0_range=(7, 12),\
    # r1_factor_range=(0.7, 1.3),
    r1_factor_range=(0.8, 1.3),\
    # spatial_blur_std=1.5,
    spatial_blur_std=2,\
    # background_intensity=0.4,
    background_intensity=0.4,\
    # background_contrast=0.00188,
    background_contrast=0.1,\
    # core_contrast=0.0752,
    core_contrast=0.1,\
    # p_white_outside=0.5,
    p_white_outside=1,\
    # k=1,
    k=1,\
    x0=0,\
    # x0=0.5,

    # measure of how close cells are allowed to be, acceptable input: none, low, normal, high
    strictness = 'high', # if none, bud cells can not be created
\
    # whether to include bud cells (1 for yes, 0 for no)
    bud_cells = 1,\
    cell_bud_ratio = 5, # The higher this value is the fewer buds are created per image
\
    # number of processes to run in parallel, number of samples created in one batch
    njobs=40, batch_size=10,

    # show a progressbar
    progressbar=True)


    with open(f'{synthetic_data_path}/labels.umsgpack', 'wb') as f:
      umsgpack.pack(labels, f, encoding = "utf-8")
