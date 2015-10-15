import os
from PIL import Image
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename, SharedDataMiddleware


UPLOAD_FOLDER = '/uploads/'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

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
    return render_template('upload.html')

# need to add a function to delete the image after the page is loaded. 
# they’re small thumbnails, but should get cleared out anyway.

@app.route('/show/<filename>')
def uploaded_file(filename):
        image = Image.open(UPLOAD_FOLDER + filename)
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

        inwidth = round(width / 300, 4)
        inheight = round(height / 300, 4)
        imgthumb = image.copy()
        imgthumb.thumbnail((200, 200))
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
                         bigstickmulti=bigstickmulti
                        )
  

app.run(host="0.0.0.0", port=8000)

