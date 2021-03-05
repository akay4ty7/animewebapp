import os
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, send_file, safe_join
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

currentImageName = ""

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
    return render_template('home.html')
#only allow certain image style to be upload
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF"]

def allow_image(filename):
    #check if the file upload include "." eg: abc.PNG
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

app.config['CLIENT_IMAGES'] = './static/client/img'

@app.route("/get-image", methods=['post'])
def get_image():
    return send_from_directory(app.config['CLIENT_IMAGES'], filename=currentImageName, as_attachment=True)

@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != ' ' :
            if allow_image(photo.filename):
                filename = secure_filename(photo.filename)
                global currentImageName
                currentImageName = photo.filename
                #the place to store image
                photo.save(os.path.join('./static/client/img', filename))
                # undone image path
                dataPath = 'D:\\new main folider\\Github clones\\animewebapp\\static\\client\\img'
                # save image path
                savePath = 'D:\\new main folider\\Github clones\\animewebapp\\static\\client\\img'
                resize(dataPath,savePath)
    return redirect(url_for('home'))

def resize(imgPath,savePath):
 files = os.listdir(imgPath)
 files.sort()
 for file in files:
        new_png = Image.open(imgPath+'/'+file) #openImage
        #new_png = new_png.resize((1000, 1000),Image.ANTIALIAS) #ResizeImage
        new_png = new_png.convert('L') # convert image to black and white
        new_png.save(savePath+'/'+file) #saveImage

if __name__ == '__main__':
    app.run(debug=True)
