import os
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF"]

def allow_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != ' ' :
            if allow_image(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join('D:/new main folider/testSerUpload', filename))
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
