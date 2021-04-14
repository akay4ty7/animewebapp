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

# This definition uses detectron2 to identify humans and replaces them with anime characters.
def humanReplacement(filename):
    cfg: CfgNode = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml")
    predictor: DefaultPredictor = DefaultPredictor(cfg)

    # Directory for taking and putting the image
    directory = './static/client/img'
    img: np.ndarray = cv2.imread('./static/client/origin_img.jpg')
    changedImg: np.ndarray = cv2.imread(os.path.join(directory, filename))
    x, y = img.shape[0:2]
    changedImg = cv2.resize(changedImg, (y, x))
    output: Instances = predictor(img)["instances"]

    add_anime_characters(output, changedImg, filename)

    v = Visualizer(img[:, :, ::-1],
                   MetadataCatalog.get(cfg.DATASETS.TRAIN[0]),
                   scale=1.0)
    result: VisImage = v.draw_instance_predictions(output.to("cpu"))
    result_image: np.ndarray = result.get_image()[:, :, ::-1]

    cv2.imwrite('./static/client/mask_img.jpg', result_image)

# This definition adds the anime characters according tot he human positions and size.
def add_anime_characters(output_instance, img, filename):
    # Original image size-> x,y
    x, y = img.shape[0:2]
    ones = np.ones((img.shape[0], img.shape[1])) * 255
    img = np.dstack([img, ones])

    print("x,y: ",x, y)
    file_path = './static/anime_images/'
    anime_images = os.listdir(file_path)
    random.shuffle(anime_images)

    animeMaskArray = []
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
            animeMaskArray.append([i,row_end-row_start])
    print("animeMaskArray:", animeMaskArray)
    sortedAnimeMaskArray = sorted(animeMaskArray, key=lambda x:x[1], reverse=False)
    print("sortedAnimeMaskArray:", sortedAnimeMaskArray)

    for i in sortedAnimeMaskArray:
        mask = output_instance.pred_masks.cpu().numpy()[i[0]]
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
        anime = cv2.imread(os.path.join(file_path, anime_images[i[0] % (len(anime_images))]), cv2.IMREAD_UNCHANGED)
        print("row_end, row_start, col_end, col_start: ", row_end, row_start, col_end, col_start)
        print(os.path.join(file_path, anime_images[i[0] % (len(anime_images))]))
        print("img.shape: ", img.shape)

        print(filename)
        x1, y1 = anime.shape[0:2]

        anime = cv2.resize(anime, (int(y1 * ((row_end - row_start) / x1)), row_end - row_start))
        img = cleanBackGround(img, anime, row_start, row_end, col_start,
                                col_start + int(y1 * ((row_end - row_start) / x1)))

        cv2.imwrite('./static/client/img/' + filename, img)

# This defintion makes sure that the anime character images have transparentyy backgrounds.
def cleanBackGround(img,anime,row_start,row_end,col_start,col_end):
    backgroundImg = img
    characterImg = anime
    alpha_characterImg = characterImg[:, :, 3] / 255.0

    alpha_image = 1 - alpha_characterImg

    for c in range(0, 3):
        backgroundImg[row_start:row_end, col_start:col_end, c] = ((alpha_image * backgroundImg[row_start:row_end, col_start:col_end, c]) + (alpha_characterImg * characterImg[:, :, c]))

    print("background: ",backgroundImg)

    return backgroundImg

