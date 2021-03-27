import os, cv2
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, send_file, safe_join
from PIL import Image, ImageOps, ImageFilter
from uuid import uuid4
import numpy as np
from werkzeug.utils import secure_filename
from test import runTest
#from testDet2 import det2run
from removal.remove import remove
from im2txt.run_inference import im2txt

app = Flask(__name__)
currentImageName = ""
full_filename = ""
description = ""
ja_description = ""
removal_img = ""

@app.route('/privacypolicy/')
def privacypolicy():
    return render_template('privacypolicy.html')

@app.route('/ack/')
def ack():
    return render_template('ack.html')

@app.route('/homeJ/')
def homeJ():
    return render_template('homeJ.html')

@app.route('/privacypolicyJ/')
def privacypolicyJ():
    return render_template('privacypolicyJ.html')

@app.route('/ackJ/')
def ackJ():
    return render_template('ackJ.html')

@app.route("/")
def home():
    return render_template('home.html', user_image = full_filename,description = description,
                           ja_description = ja_description,removal_img=removal_img)
#only allow certain image style to be upload

app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF"]
app.config['CLIENT_IMAGES'] = './static/client/img'

def allow_image(filename):
    #check if the file upload include "." eg: abc.PNG
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/get-image", methods=['post'])
def get_image():
    return send_from_directory(app.config['CLIENT_IMAGES'], filename=currentImageName, as_attachment=True)

@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        global PictureName
        PictureName = make_unique(photo.filename)
        if PictureName != ' ' :
            if allow_image(PictureName):
                deleteAllFile()
                filename = secure_filename(PictureName)
                global currentImageName
                currentImageName = PictureName
                #the place to store image
                print(os.path.join('./static/client/img', filename))
                photo.save(os.path.join('./static/client/img', filename))
                det2run(filename)
                remove()
                global full_filename, description, ja_description,removal_img
                removal_img = "./static/client/removal_img.jpg"
                description, ja_description = im2txt(os.path.join('./static/client/img', filename))
                runTest()
                full_filename = os.path.join(app.config['CLIENT_IMAGES'], currentImageName)

                return redirect(url_for('home'))

def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"

def deleteAllFile():
    cur_path = 'F:/animewebapp'
    static_path = os.path.join(cur_path, './static/client/img')
    print(static_path)
    all_dir = os.listdir(static_path)
    print(all_dir)
    for allFile in all_dir:
        file_path = os.path.join(static_path, allFile)
        print(file_path)
        os.remove((file_path))

def GreyTone(imgPath,savePath,imageName):
    new_png = Image.open(imgPath+'/'+imageName) #openImage
    #new_png = new_png.resize((1000, 1000),Image.ANTIALIAS) #ResizeImage
    new_png = new_png.convert('L') # convert image to black and white
    new_png.save(savePath+'/'+imageName) #saveImage

def filter1(filein,picture_name):
    imgI_filename = os.path.join(filein,picture_name) # æºæ–‡ä»¶è·¯å¾„
    imgO_filename = os.path.join('./static/client/img', picture_name) # ç›®æ ‡æ–‡ä»¶è·¯å¾„
    img_rgb = cv2.imread(imgI_filename) # è¯»å–å›¾ç‰‡
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY) # è½¬æ¢ä¸ºç°åº¦
    img_blur = cv2.medianBlur(img_gray, 5) # å¢žåŠ æ¨¡ç³Šæ•ˆæžœã€‚å€¼è¶Šå¤§è¶Šæ¨¡ç³Šï¼ˆå–å¥‡æ•°ï¼‰
    # æ£€æµ‹åˆ°è¾¹ç¼˜å¹¶ä¸”å¢žå¼ºå…¶æ•ˆæžœ
    img_edge = cv2.adaptiveThreshold(img_blur, 128,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,blockSize=9,C=8)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)  # å½©è‰²å›¾åƒè½¬ä¸ºç°åº¦å›¾åƒ
    img_cartoon = cv2.bitwise_and(img_rgb, img_edge)  # ç°åº¦å›¾åƒè½¬ä¸ºå½©è‰²å›¾åƒ
    res = np.uint8(np.clip((2.0 * img_cartoon + 16), 0, 255))  # è°ƒæ•´äº®åº¦å’Œå¯¹æ¯”åº¦
    cv2.imwrite(imgO_filename, res)  # ä¿å­˜è½¬æ¢åŽçš„å›¾ç‰‡

# è½¬æ¢æˆæ¼«ç”»é£Žæ ¼
def filter2_toCarttonStyle(picturePath):
 # å±žæ€§è®¾ç½®
 num_down = 2 # ç¼©å‡åƒç´ é‡‡æ ·çš„æ•°ç›®
 num_bilateral = 7 # å®šä¹‰åŒè¾¹æ»¤æ³¢çš„æ•°ç›®
 # è¯»å–å›¾ç‰‡
 img_rgb = cv2.imread(os.path.join('./static/client/img',picturePath))
 # ç”¨é«˜æ–¯é‡‘å­—å¡”é™ä½Žå–æ ·
 img_color = img_rgb
 for _ in range(num_down):
     img_color = cv2.pyrDown(img_color)
 # é‡å¤ä½¿ç”¨å°çš„åŒè¾¹æ»¤æ³¢ä»£æ›¿ä¸€ä¸ªå¤§çš„æ»¤æ³¢
 for _ in range(num_bilateral):
     img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)
 # å‡é‡‡æ ·å›¾ç‰‡åˆ°åŽŸå§‹å¤§å°
 for _ in range(num_down):
     img_color = cv2.pyrUp(img_color)
 # è½¬æ¢ä¸ºç°åº¦å¹¶ä¸”ä½¿å…¶äº§ç”Ÿä¸­ç­‰çš„æ¨¡ç³Š
 img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
 img_blur = cv2.medianBlur(img_gray, 7)
 # æ£€æµ‹åˆ°è¾¹ç¼˜å¹¶ä¸”å¢žå¼ºå…¶æ•ˆæžœ
 img_edge = cv2.adaptiveThreshold(img_blur, 255,
     cv2.ADAPTIVE_THRESH_MEAN_C,
     cv2.THRESH_BINARY,
     blockSize=9,
     C=2)
 # ç®—æ³•å¤„ç†åŽï¼Œç…§ç‰‡çš„å°ºå¯¸å¯èƒ½ä¼šä¸ç»Ÿä¸€
 # æŠŠç…§ç‰‡çš„å°ºå¯¸ç»Ÿä¸€åŒ–
 height=img_rgb.shape[0]
 width = img_rgb.shape[1]
 img_color=cv2.resize(img_color,(width,height))
 # è½¬æ¢å›žå½©è‰²å›¾åƒ
 img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
 img_cartoon = cv2.bitwise_and(img_color, img_edge)
 # ä¿å­˜è½¬æ¢åŽçš„å›¾ç‰‡
 cv2.imwrite(os.path.join('./static/client/img', picturePath), img_cartoon)

 # é€æ˜Žåº¦è½¬æ¢ ç´ æè½¬æ¢çš„ä¸€éƒ¨åˆ†
def filter2_dodge(a, b, alpha):
  # alphaä¸ºå›¾ç‰‡é€æ˜Žåº¦
  return min(int(a * 255 / (256 - b * alpha)), 255)

  # å›¾ç‰‡è½¬æ¢ä¸ºç´ æ
def filter2_toSketchStyle(picturePath, blur=25, alpha=1.0):
   # è½¬åŒ–æˆimaå¯¹è±¡
   img = Image.open(os.path.join('./static/client/img', picturePath))
   # å°†æ–‡ä»¶è½¬æˆç°è‰²
   img1 = img.convert('L')
   img2 = img1.copy()
   img2 = ImageOps.invert(img2)
   # æ¨¡ç³Šåº¦
   for i in range(blur):
       img2 = img2.filter(ImageFilter.BLUR)
   width, height = img1.size
   for x in range(width):
       for y in range(height):
           a = img1.getpixel((x, y))
           b = img2.getpixel((x, y))
           img1.putpixel((x, y), filter2_dodge(a, b, alpha))

   # ä¿å­˜è½¬æ¢åŽæ–‡ä»¶
   img1.save(os.path.join('./static/client/img', picturePath))

if __name__ == '__main__':
    app.run(debug=True)
