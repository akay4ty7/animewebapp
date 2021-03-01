#coding:utf-8
import os
from PIL import Image
import numpy as np

def resize(imgPath,savePath):
 files = os.listdir(imgPath)
 files.sort()
 print('****************')
 print('input :',imgPath)
 print('start...')
 for file in files:
     fileType = os.path.splitext(file)
     if fileType[1] == '.png':
        new_png = Image.open(imgPath+'/'+file) #打开图片
        #new_png = new_png.resize((1000, 1000),Image.ANTIALIAS) #改变图片大小
        new_png = new_png.convert('L') # convert image to black and white
        new_png.save(savePath+'/'+file) #保存图片
        print('down!')
        print('****************')

if __name__ == '__main__':
 # undone image path
 dataPath = 'C:\\Users\LU\Desktop\\RND-s2\Animewebapp-main\\Python'
 # save image path
 savePath = 'C:\\Users\\LU\\Desktop\\RND-s2\\Animewebapp-main\\Python'
 resize(dataPath,savePath)
