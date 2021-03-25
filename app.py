import os, cv2
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, send_file, safe_join
from PIL import Image, ImageFont, ImageDraw, ImageFile
from uuid import uuid4
import numpy as np
from werkzeug.utils import secure_filename
from test import runTest
from testDet2 import det2run
from run_inference import mainfunction
from mainremoval import main

ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)
global fileName
full_filename = ""

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
    return render_template('home.html', user_image=full_filename)
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
    return send_from_directory(app.config['CLIENT_IMAGES'], filename=changeName, as_attachment=True)

@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        fileName = "img.jpg"
        global changeName
        changeName = make_unique(fileName)
        if fileName != ' ':
            if allow_image(fileName):
                pngtojpg(fileName)
                deleteAllFile()
                fileName = secure_filename(fileName)
                #the place to store image
                print(fileName)
                photo.save(os.path.join('./static/client/img', fileName))
                old = os.path.join('static/client/img/', fileName)
                new = os.path.join('static/client/img/', changeName)
                os.rename(old, new)
                global originRatio
                originRatio = imagesize()
                global text
                text = mainfunction(changeName)
                global squareImage
                squareImage = main(mode=2)
                imageResize()
                #det2run(filename)
                runTest()
                #textinput(changeName)
                global full_filename
                full_filename = os.path.join(app.config['CLIENT_IMAGES'], changeName)
                return redirect(url_for('home'))

def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"

def deleteAllFile():
    for allFile in os.listdir('./static/client/img'):
        file_path = os.path.join('./static/client/img', allFile)
        os.remove((file_path))

def pngtojpg(originalImageName):
    """

    originalImageName.load()  # required for png.split()
    newRGB = Image.new("RGB", originalImageName.size, (255, 255, 255))
    newRGB.paste(originalImageName, mask=originalImageName.split()[3])  # 3 is the alpha channel
    newRGB.save('foo.jpg', 'JPEG', quality=100)

    """
    print(originalImageName)
    root_ext = originalImageName.rsplit(".", 1)[0] + ".jpg"
    print(root_ext)
    return root_ext

def imagesize():
    fileNameSize = Image.open("static/client/img/" + changeName)
    return fileNameSize

def imageResize():
    squareImage = Image.open("static/client/img/" + changeName)
    print(squareImage.size)
    print(originRatio.size)
    size = originRatio.size
    print(size)
    squareImage = squareImage.resize(size)
    print(squareImage.size)
    basewidth = 1250
    wpercent = (basewidth / float(squareImage.size[0]))
    hsize = int((float(squareImage.size[1]) * float(wpercent)))
    squareImage = squareImage.resize((basewidth, hsize), Image.ANTIALIAS)

    imagedraw = ImageDraw.Draw(squareImage)
    fontsize = 1
    img_fraction = 0.50
    title_font = ImageFont.truetype('JPFONT.ttf', fontsize)

    while title_font.getsize(text)[0] < img_fraction * squareImage.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    fontsize -= 1
    title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    imagedraw.text((10, 25), text, (252, 190, 17), font=title_font)

    squareImage.save(os.path.join('static/client/img/', changeName))

if __name__ == '__main__':
    app.run(debug=True)
