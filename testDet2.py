import argparse

import cv2
import numpy as np
import re
import os

import random

from detectron2 import model_zoo
from detectron2.config import get_cfg, CfgNode
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor
from detectron2.structures import Instances
from detectron2.utils.visualizer import Visualizer, VisImage


def _get_parsed_args() -> argparse.Namespace:
    """
    Create an argument parser and parse arguments.

    :return: parsed arguments as a Namespace object
    """

    parser = argparse.ArgumentParser(description="Detectron2 demo")

    # default model is the one with the 2nd highest mask AP
    # (Average Precision) and very high speed from Detectron2 model zoo
    parser.add_argument(
        "--base_model",
        default="COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml",
        help="Base model to be used for training. This is most often "
             "appropriate link to Detectron2 model zoo."
    )

    parser.add_argument(
        "--images",
        nargs="+",
        help="A list of space separated image files that will be processed. "
             "Results will be saved next to the original images with "
             "'_processed_' appended to file name."
    )

    return parser.parse_args()


def det2run(filename):
    args: argparse.Namespace = _get_parsed_args()

    cfg: CfgNode = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(args.base_model))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(args.base_model)
    predictor: DefaultPredictor = DefaultPredictor(cfg)

    directory = './static/client/img' # Directory for taking and putting the image
    img: np.ndarray = cv2.imread(os.path.join(directory, filename))

    output: Instances = predictor(img)["instances"]
    #########add
    add_anime_characters(output, img)
    ########
    v = Visualizer(img[:, :, ::-1],
                   MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
                   scale=1.0)
    result: VisImage = v.draw_instance_predictions(output.to("cpu"))
    result_image: np.ndarray = result.get_image()[:, :, ::-1]

    cv2.imwrite(os.path.join(directory, filename), result_image)


def add_anime_characters(output_instance, img):
    x, y = img.shape[0:2]
    print(x, y)
    file_path = './static/anime_images/'
    anime_images = os.listdir(file_path)
    random.shuffle(anime_images)
    for i in range(output_instance.pred_classes.shape[0]):
        if output_instance.pred_classes[i] == 0:
            mask = output_instance.pred_masks.cpu().numpy()[i]
            row_start = y
            col_start = x
            row_end = -1
            col_end = -1
            for j in range(0, x - 1):
                for k in range(0, y - 1):
                    if mask[j][k]:
                        if j < row_start:
                            row_start = j
                        if j > row_end:
                            row_end = j
                        if k < col_start:
                            col_start = k
                        if k > col_end:
                            col_end = k
            anime = cv2.imread(os.path.join(file_path, anime_images[i % (len(anime_images))]))
            print(row_end, row_start, col_end, col_start)
            print(os.path.join(file_path, anime_images[i % (len(anime_images))]))
            print(img.shape)
            anime = cv2.resize(anime, (col_end - col_start, row_end - row_start))
            #print(img[col_start:col_end, row_start:row_end, :].shape)
            #img[row_start:row_end, col_start:col_end, :] = anime
            img = delet_background(anime, img, row_start, row_end, col_start, col_end)
    # print(anime_images)
    # print(img)
    cv2.imwrite(r'./static/client/anime_img.jpg', img)


def delet_background(anime_img, img_back, row_start, row_end, col_start, col_end):

    hsv = cv2.cvtColor(anime_img, cv2.COLOR_BGR2HSV)
    lower = np.array([0,0,250])
    upper = np.array([0,0,256])
    mask = cv2.inRange(hsv, lower, upper)

    erode = cv2.erode(mask, None, iterations=1)
    dilate = cv2.dilate(erode, None, iterations=1)
    for i in range(0, row_end-row_start):
        for j in range(0, col_end-col_start):
            if dilate[i, j] == 0:
                img_back[row_start + i, col_start + j] = anime_img[i, j]  # 此处替换颜色，为BGR通道
    return img_back
