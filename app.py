import os, cv2
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, send_file, safe_join
from PIL import Image, ImageFont, ImageDraw, ImageFile
from uuid import uuid4
import PIL.Image
from werkzeug.utils import secure_filename
from animeFilter import animeFilter
from det2HumanReplace import humanReplacement
from im2txt import im2txt
from humanRemoval import humanRemoval
from googletrans import Translator
import pykakasi

ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)
global fileName
full_filename = ""
textD = ""
japanese = ""
displayText = ""
stringfuri = ""
furi = ""
englishKanji = ""
japaneseKanji = ""
explanationKanji = ""
englishFuri = ""
japaneseFuri = ""
explanationFuri = ""

@app.route('/privacypolicy/')
def privacypolicy():
    return render_template('privacypolicy.html')

@app.route('/sample/')
def sample():
    return render_template('sample.html')

@app.route('/sampleJ/')
def sampleJ():
    return render_template('sampleJ.html')

@app.route('/ack/')
def ack():
    return render_template('ack.html')

@app.route('/homeJ/')
def homeJ():
    return render_template('homeJ.html', user_image=full_filename, renderText=textD, renderText2=japanese, renderText3=furi, renderTextE=englishKanji, renderTextJ=japaneseKanji, renderTextEX=explanationKanji,  renderTextEF=englishFuri, renderTextJF=japaneseFuri, renderTextEXF=explanationFuri)

@app.route('/privacypolicyJ/')
def privacypolicyJ():
    return render_template('privacypolicyJ.html')

@app.route('/ackJ/')
def ackJ():
    return render_template('ackJ.html')

@app.route("/")
def home():
    return render_template('home.html', user_image=full_filename, renderText=textD, renderText2=japanese, renderText3=furi)

# Only allow certain image style to be upload.
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]

# Constant path used throughout code specifically for english version.
app.config['CLIENT_IMAGES'] = './static/client/img'

# Constant path used throughout code specifically for japanese version.
app.config['CLIENT_IMAGESJ'] = '../static/client/img'

@app.route("/get-refresh", methods=['post'])
def get_refresh():
    deleteAllFile()
    if request.referrer == "https://cvapp.aut.ac.nz/homeJ/":
       return redirect(url_for('homeJ'))
    else:
       return redirect(url_for('home'))

# Function for downloading the image from the web-app.
@app.route("/get-image", methods=['post'])
def get_image():
    return send_from_directory(app.config['CLIENT_IMAGES'], filename=changeName, as_attachment=True)

# This definition holds all functions for image processing. For example rgbatoRGB.
@app.route("/handleUpload", methods=['post'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        fileName = "img.jpg"
        global changeName
        changeName = make_unique(fileName)
        if fileName != ' ':
            if allow_image(fileName):
                deleteAllFile()
                fileName = secure_filename(fileName)
                photo.save(os.path.join('./static/client/img', fileName))
                old = os.path.join('static/client/img/', fileName)
                new = os.path.join('static/client/img/', changeName)
                os.rename(old, new)
                rgbatoRGB(changeName)
                origin_img = cv2.imread(os.path.join('static/client/img/', changeName))
                cv2.imwrite(r'./static/client/origin_img.jpg', origin_img)
                global originRatio
                originRatio = imagesize()
                global text
                text = im2txt(changeName)
                global squareImage
                squareImage = humanRemoval(mode=2)
                imageResize()
                humanReplacement(changeName)
                animeFilter()
                textDrawJ()
                furigana()
                global full_filename
                global textD
                global japanese
                global furi
                global englishKanji
                global japaneseKanji
                global explanationKanji
                global englishFuri
                global japaneseFuri
                global explanationFuri
                print("request.referrer: ", request.referrer)
                if request.referrer == "https://cvapp.aut.ac.nz/homeJ/":
                    englishKanji = u"英語: "
                    englishFuri = u"えいご"
                    textD = (im2txt(changeName)).capitalize()
                    japaneseKanji = u"日本語: "
                    japaneseFuri = u"にほんご"
                    japanese = u"" + displayText
                    explanationKanji = u"説明: "
                    explanationFuri = u"せつめい"
                    furi = u"" + stringfuri
                    full_filename = os.path.join(app.config['CLIENT_IMAGESJ'], changeName)
                    return redirect(url_for('homeJ'))
                else:
                    textD = "English: " + (im2txt(changeName)).capitalize()
                    japanese = "Japanese: " + u"" + displayText
                    furi = "Explanations: " + u"" + stringfuri
                    full_filename = os.path.join(app.config['CLIENT_IMAGES'], changeName)
                    return redirect(url_for('home'))

# This definition checks the image extension upon upload.
def allow_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

# This definition creates a unique code for the image name.
# This will prevent chrome caching.
def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"

# This definition deletes all images after processing.
def deleteAllFile():
    for allFile in os.listdir('./static/client/img'):
        file_path = os.path.join('./static/client/img', allFile)
        os.remove((file_path))

# This definition Converts RGBA images to RGB so that any image can be uploaded.
def rgbatoRGB(changeName):
    rgba_image = PIL.Image.open("static/client/img/" + changeName)
    rgb_image = rgba_image.convert('RGB')
    rgb_image.save("static/client/img/" + changeName)

# This definition gets the original image size to be used later for resizing.
def imagesize():
    fileNameSize = Image.open("static/client/img/" + changeName)
    return fileNameSize

# This definition resizes the image.
def imageResize():
    squareImage = Image.open("static/client/img/" + changeName)
    size = originRatio.size
    squareImage = squareImage.resize(size)
    basewidth = 1250
    wpercent = (basewidth / float(squareImage.size[0]))
    hsize = int((float(squareImage.size[1]) * float(wpercent)))
    squareImage = squareImage.resize((basewidth, hsize), Image.ANTIALIAS)

    squareImage.save(os.path.join('static/client/img/', changeName))

def converttostr(input_seq, seperator):
   # Join all the strings in list
   final_str = seperator.join(input_seq)
   return final_str

# This definition draws the Japanese text onto the screen.
def furigana():
    print(text)
    translator = Translator()
    result = translator.translate(text, src='en', dest='ja')
    global displayText
    displayText = result.text

    kks = pykakasi.kakasi()
    furiganaText = kks.convert(displayText)

    global stringfuri
    stringfurii = []

    for item in furiganaText:
        elements = ("{}[{}][{}] ".format(item['orig'], item['hira'].capitalize(), item['hepburn'].capitalize()))
        stringfurii.append(elements)
        print(stringfurii)
    seperation = ' '
    stringfuri = converttostr(stringfurii, seperation)

def textDrawJ():
    print(text)
    translator = Translator()
    resultE = translator.translate(text, src='en', dest='en')
    result = translator.translate(text, src='en', dest='ja')
    displayTextE = resultE.text
    displayText = result.text
    squareImage = Image.open("static/client/img/" + changeName)
    width, height = squareImage.size

    imagedraw = ImageDraw.Draw(squareImage)
    fontsize = 1
    img_fraction = 0.60
    title_font = ImageFont.truetype('JPFONT.ttf', fontsize)

    while title_font.getsize(displayTextE)[0] < img_fraction * squareImage.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    fontsize -= 1
    title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    w, h = title_font.getsize(displayTextE)
    imagedraw.text(((width - w)/2, height - h - 10), displayTextE.capitalize(), (252, 190, 17), font=title_font, stroke_width=2, stroke_fill='black')

    while title_font.getsize(displayText)[0] < img_fraction * squareImage.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    fontsize -= 1
    title_font = ImageFont.truetype("JPFONT.ttf", fontsize)
    wj, hj = title_font.getsize(displayText)
    imagedraw.text(((width - wj)/2, height - hj - h - 20), displayText, (255, 255, 255), font=title_font, stroke_width=2, stroke_fill='black')

    squareImage.save(os.path.join('static/client/img/', changeName))




if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0", debug=False)
