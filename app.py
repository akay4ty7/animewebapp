import os
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, send_file, safe_join
from werkzeug.utils import secure_filename

app = Flask(__name__)

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

app.config["CLIENT_IMAGES"] = "D:/new main folider/Github clones/animewebapp/static/client/img"

@app.route("/get-image", methods=['post'])
def get_image():
    return send_from_directory(app.config["CLIENT_IMAGES"], filename='a.png', as_attachment=True)


@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != ' ' :
            if allow_image(photo.filename):
                filename = secure_filename(photo.filename)
                #the place to store image
                photo.save(os.path.join('D:/new main folider/Github clones/animewebapp/static/client/img', filename))
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
