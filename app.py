import os
from PIL import Image
from flask import Flask, request, redirect, url_for,
                  send_from_directory, render_template
from werkzeug import secure_filename, SharedDataMiddleware


UPLOAD_FOLDER = '/Users/Treehouse/GitHub/imagevalidator/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
VERSION = '0.19'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        upfile = request.files['file']
        if upfile and allowed_file(upfile.filename):
            filename = secure_filename(upfile.filename)
            upfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

    return render_template('upload.html',
                           version=VERSION)

@app.route('/show/<filename>')
def uploaded_file(filename):
        image = Image.open(app.config['UPLOAD_FOLDER'] + filename)
        height = image.size[0]
        width = image.size[1]
        area = width * height

# At Treehouse Stickers (http://treehousestickers.com), we price 
# stickers by square inches. This will tell you the biggest size  
# price category in which the image can fit.
#
# If the image is larger than 6x6, it will display a multiplier
# used to get a price based on the 6 inch category.

        sticksize = 1
        bigstickmulti = 0
        area = round(area / 90000, 4)
        if area > 36:
          sticksize = 7
          bigstickmulti = round(area / 36, 4)
        if area <= 36:
          sticksize = 6
        if area <= 25:
          sticksize = 5
        if area <= 16:
          sticksize = 4
        if area <= 9:
          sticksize = 3
        if area <= 4:
          sticksize = 2
        if area <= 1:
          sticksize = 1
# displays the image mode for the file. PIL images are all RBG, so
# this doesn’t work yet.
#
#        mode = image.mode
        imgthumb = image.copy()
#
#       update 10-18-15 (1/2): adjusted the thumnail to display proportionately.
#
        imgthumb.thumbnail((int(round(width / sticksize)), int(round(height / sticksize))))
        inwidth = round(width / 300, 4)
        inheight = round(height / 300, 4)
 
        imgthumb.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

  
        return render_template('index.html',

                         area=area,
                         filename=filename,
                         height=height, 
                         width=width,
                         inheight=inheight,
                         inwidth=inwidth,
 #                        mode=mode,
                         sticksize=sticksize,
                         bigstickmulti=bigstickmulti,
                         version=VERSION
                        )
#
# update 10-18-15 (2/2) - created this fuction that will delete individual
# files by name. opted to go with a '/clear' option that will delete all
# uploaded thumbnails. Also returns a new html file that tells you how many
# files are deleted, and how big the files are, in b, kb, or mb depending
# on how much data was removed.
#
#@app.route('/delete/<filename>')
#def delete_file(filename):
#        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#        return render_template('done.html', delaction="Deleted!")

@app.route('/clear/')
def clear_data():
    listcount = 0
    datasaved = 0
    for filename in os.listdir(UPLOAD_FOLDER):
        datasaved = datasaved + os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        listcount += 1
    if datasaved <= 1024:
        datasave = str(datasaved) + ' Bytes'
    elif datasaved <= 1048576:
        datasave = str(round(datasaved/1024, 2)) + ' Kilobytes'
    else:
        datasave = str(round(datasaved/1048576, 2)) + ' Megabytes'
        
    return render_template('done.html',
                           delaction="Cleared!",
                           itemsdeleted=listcount,
                           datasave=datasave,
                           version=VERSION
                           )


app.run(host="0.0.0.0", port=8000, debug=True)
