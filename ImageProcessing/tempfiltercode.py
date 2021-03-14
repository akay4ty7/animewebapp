"""
def filter1(filein,picture_name):
    imgI_filename = os.path.join(filein,picture_name) # 源文件路径
    imgO_filename = os.path.join('./static/client/img', picture_name) # 目标文件路径
    img_rgb = cv2.imread(imgI_filename) # 读取图片
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY) # 转换为灰度
    img_blur = cv2.medianBlur(img_gray, 5) # 增加模糊效果。值越大越模糊（取奇数）
    # 检测到边缘并且增强其效果
    img_edge = cv2.adaptiveThreshold(img_blur, 128,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,blockSize=9,C=8)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)  # 彩色图像转为灰度图像
    img_cartoon = cv2.bitwise_and(img_rgb, img_edge)  # 灰度图像转为彩色图像
    res = np.uint8(np.clip((2.0 * img_cartoon + 16), 0, 255))  # 调整亮度和对比度
    cv2.imwrite(imgO_filename, res)  # 保存转换后的图片

# 转换成漫画风格
def filter2_toCarttonStyle(picturePath):
 # 属性设置
 num_down = 2 # 缩减像素采样的数目
 num_bilateral = 7 # 定义双边滤波的数目
 # 读取图片
 img_rgb = cv2.imread(os.path.join('./static/client/img',picturePath))
 # 用高斯金字塔降低取样
 img_color = img_rgb
 for _ in range(num_down):
     img_color = cv2.pyrDown(img_color)
 # 重复使用小的双边滤波代替一个大的滤波
 for _ in range(num_bilateral):
     img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)
 # 升采样图片到原始大小
 for _ in range(num_down):
     img_color = cv2.pyrUp(img_color)
 # 转换为灰度并且使其产生中等的模糊
 img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
 img_blur = cv2.medianBlur(img_gray, 7)
 # 检测到边缘并且增强其效果
 img_edge = cv2.adaptiveThreshold(img_blur, 255,
     cv2.ADAPTIVE_THRESH_MEAN_C,
     cv2.THRESH_BINARY,
     blockSize=9,
     C=2)
 # 算法处理后，照片的尺寸可能会不统一
 # 把照片的尺寸统一化
 height=img_rgb.shape[0]
 width = img_rgb.shape[1]
 img_color=cv2.resize(img_color,(width,height))
 # 转换回彩色图像
 img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
 img_cartoon = cv2.bitwise_and(img_color, img_edge)
 # 保存转换后的图片
 cv2.imwrite(os.path.join('./static/client/img', picturePath), img_cartoon)

 # 透明度转换 素描转换的一部分
def filter2_dodge(a, b, alpha):
  # alpha为图片透明度
  return min(int(a * 255 / (256 - b * alpha)), 255)

  # 图片转换为素描
def filter2_toSketchStyle(picturePath, blur=25, alpha=1.0):
   # 转化成ima对象
  # img = Image.open(os.path.join('./static/client/img', picturePath))
   # 将文件转成灰色
   img1 = img.convert('L')
   img2 = img1.copy()
   img2 = ImageOps.invert(img2)
   # 模糊度
   for i in range(blur):
       img2 = img2.filter(ImageFilter.BLUR)
   width, height = img1.size
   for x in range(width):
       for y in range(height):
           a = img1.getpixel((x, y))
           b = img2.getpixel((x, y))
           img1.putpixel((x, y), filter2_dodge(a, b, alpha))

   # 保存转换后文件
   #img1.save(os.path.join('./static/client/img', picturePath))
