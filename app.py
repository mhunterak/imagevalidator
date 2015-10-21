import os
from PIL import Image
from flask import (Flask, flash, request, redirect,
                   url_for, send_from_directory, render_template)
from werkzeug import secure_filename, SharedDataMiddleware
from daemonize import Daemonize
import time
import datetime
# development projects, future development:
# Dropbox integration
#import dropbox - get files from dropbox?
#import logging - save log file to dropbox directory?

### v0.21 10-21-15

UPLOAD_FOLDER = '/Users/Treehouse/GitHub/imagevalidator/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
VERSION = '0.21'
#dbx = dropbox.Dropbox('')
#dbx.users_get_current_account()

app = Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['SECRET_KEY']='unique key'           
pid = "/tmp/test.pid"

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
        else:
            flash("Only file types png, jpg, jpeg, and gif are currently supported.")
    return render_template('index.html',
                           version=VERSION)
# added flash message if the upload fails due to a bad filetype.

#@app.route('/dropbox/<filename>')
#def dropbox(filename):
#    filelist = []
#    for entry in dbx.files_list_folder(filename).entries:
#        filelist.append(entry.name)
#    return render_template('dropbox.html',
#                           version=VERSION,
#                           filelist=filelist)

@app.route('/show/<filename>')
def uploaded_file(filename):
        try:
            image = Image.open(app.config['UPLOAD_FOLDER'] + filename)
            height = image.size[0]
            width = image.size[1]
            area = width * height
        except FileNotFoundError:
            flash("Error loading image. Please upload a new file.")
            return redirect(url_for('upload_file'))        
#
# At Treehouse Stickers (http://treehousestickers.com), we price 
# stickers by square inches. This will tell you the biggest size  
# price category in which the image can fit.
#
# If the image is larger than 6x6, it will display a multiplier
# used to get a price based on the 6 inch category.
#
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

#
# displays the image mode for the file. PIL images are all RBG, so
# this doesn’t work yet.
#
#        mode = image.mode
#
        imgthumb = image.copy()
        imgthumb.thumbnail((int(round(width / sticksize)),
                            int(round(height / sticksize))))
        inwidth = round(width / 300, 4)
        inheight = round(height / 300, 4)
        imgthumb.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template('show.html',
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
# changed this funtion to try to delete the selected file, then
# redirects to the upload page. Currently using it for the primary
# redirect back to the upload page.
#
@app.route('/delete/<filename>')
def delete_file(filename):
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except FileNotFoundError:
            # continues if the file was already deleted
            flash("Error deleting image.")
            pass
        return redirect(url_for('upload_file'))

#
# set up a daemon to clear all data in the upload folder (cache) every morning
# at 2am every morning. I'm leaving this function intact to add to an 'admin options'
# page once I get a login figured out.
#
@app.route('/admin-clear/')
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

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/admin-shutdown/')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

#
# This is the daemon that clears out the files every morning.
#
def sweeper():
    with daemon.DaemonContext():
        for i in xrange(0,365):
            t = datetime.datetime.today()
            future = datetime.datetime(t.year,t.month,t.day,2,0)
            if t.hour >= 2:
                future += datetime.timedelta(days=1)
            time.sleep((future-t).seconds)
            for filename in os.listdir(UPLOAD_FOLDER):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

app.run(host="0.0.0.0", port=8000, debug=True)
daemon = Daemonize(app="test_app", pid=pid, action=sweeper)
daemon.start()
