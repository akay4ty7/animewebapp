# -*- coding: utf-8 -*-
"""
@Time ： 2021/2/21 13:07
@Auth ： Yvon～早安阳光
@File ：dongmanlvj
"""
# 导入OpenCV-Python模块、导入文件与系统模块
import cv2,os
import numpy as np

def filter(filein,picture_name):
    imgI_filename = os.path.join(filein,picture_name) # 源文件路径
    imgO_filename = os.path.join(r'C:\Users\LU\Documents\GitHub\animewebapp\ImageProcessing\testImage', picture_name) # 目标文件路径
    img_rgb = cv2.imread(imgI_filename) # 读取图片
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY) # 转换为灰度
    img_blur = cv2.medianBlur(img_gray, 5) # 增加模糊效果。值越大越模糊（取奇数）
    # 检测到边缘并且增强其效果
    img_edge = cv2.adaptiveThreshold(img_blur, 128,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,blockSize=9,C=8)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)  # 彩色图像转为灰度图像
    img_cartoon = cv2.bitwise_and(img_rgb, img_edge)  # 灰度图像转为彩色图像
    res = np.uint8(np.clip((2.0 * img_cartoon + 16), 0, 255))  # 调整亮度和对比度
    cv2.imwrite(imgO_filename, res)  # 保存转换后的图片

if __name__ == '__main__':
    imagelist = [] # 创建空列表
    # 循环读取指定路径下的文件名
    for filename in os.listdir(r'‪C:\Users\LU\Documents\GitHub\animewebapp\ImageProcessing\3.jpg'):
        imagelist.append(filename) # 将文件名添加到imagelist
        print(filename)
        filter(r'‪C:\Users\LU\Documents\GitHub\animewebapp\ImageProcessing\3.jpg',filename) # 为图片应用卡通动漫滤镜
