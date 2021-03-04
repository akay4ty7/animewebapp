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
        new_png = Image.open(imgPath+'/'+file) #openImage
        #new_png = new_png.resize((1000, 1000),Image.ANTIALIAS) #ResizeImage
        new_png = new_png.convert('L') # convert image to black and white
        new_png.save(savePath+'/'+file) #saveImage
        print('down!')
        print('****************')

if __name__ == '__main__':
 # undone image path
 dataPath = 'D://new main folider//test photo sonvert'
 # save image path
 savePath = 'D://new main folider//test photo sonvert'
 resize(dataPath,savePath)
