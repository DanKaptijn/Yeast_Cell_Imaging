import os
import numpy
import detectron2
import umsgpack

new_path = 'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/yeastcells-detection-maskrcnn/'
if new_path not in sys.path:
    sys.path.append(new_path)

from train import create_model, train

if __name__ == "__main__":
    data_path = f'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/synthetic-yeast-cells-data'

    version = 'v1'
    run = 1
    model_path = f'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/model-{version}'

    #load model
    config = create_model(
        model_path,
        device='cuda:0',
        data_workers=2,
        batch_size=2,
        learning_rate=0.00025,
        max_iter=20000,
        pretrained="COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
        tensorboard=f'C:/Users/DanKap/Documents/Personal Projects/Yeast Cell Detection/tensorboard/yeast-cells-mask-rcnn-run-{run}'
    )

    trainer = train(
        config,
        data_path
    )
