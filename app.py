from funs import StepperMotor, create_options, capture_and_save_image, save_Video
from flask import Flask, render_template, request, redirect, url_for, session
from flask import send_from_directory
from pathlib import Path
import os
#initial code to for motor
GPIO_PIN_LIST = [5,6,13,19]
Motor = StepperMotor(GPIO_PIN_LIST)
#Motor.rotate(direction=True, degrees=-180)
#Initialize Flask App
app= Flask(__name__)
app.secret_key = "abc" 
#Folder for storage
IMG_FOLDER = os.path.join('static', 'IMG')
app.config['UPLOAD_FOLDER'] = IMG_FOLDER
capturedFolder = os.path.join('static','StoredData')
CurrentDir = capturedFolder
index= 0
currentFile = 'snap'+str(index)+'.jpeg'

selected_folder =""


@app.route("/")
@app.route("/home",  methods =["GET", "POST"])
def home():
    FolderName = session.get('selectedFolder')
    options = create_options(app,capturedFolder)
    if request.method == "POST":
       # getting input with name = fname in HTML form
       FolderName = request.form.get("FolderName")
       return "Your name is "+ FolderName 
    
    return render_template("start.html", FolderN = FolderName, options= options)

@app.route('/create_folder', methods=["GET", "POST"])
def create_folder():
    # Get the selected option from the form
    global selected_folder
    selected_option = request.form.get('folder')
    print("New folder ", selected_option)
    # Check if the "create new folder" option was selected
    if selected_option == 'Create new folder':
        # Get the name of the new folder from the form
        folder_name = request.form['folder_name']
        # Get the path to the static folder
        static_folder = app.static_folder
        # Get the path to the subfolder within the static folder
        subfolder_path = os.path.join(static_folder, 'StoredData')
        # Create the new folder in the subfolder
        new_folder_path = os.path.join(subfolder_path, folder_name)
        os.makedirs(new_folder_path)
        print("New folder created")
        session['selectedFolder'] = folder_name
    else:
        session['selectedFolder']  = selected_option
    # Redirect to the index page
    return redirect(url_for('home'))


@app.route('/start_Photos', methods=["GET", "POST"])
def start_Photos():
    FolderName = session.get('selectedFolder')
    capture_and_save_image(FolderName)
    return redirect(url_for('home'))

@app.route('/browse')
def browse_folder():
    folder = 'static/StoredData'
    files = os.listdir(folder)
    return render_template('browse.html', files=files)

@app.route('/browse/<path:filename>')
def serve_file(filename):
    return send_from_directory("static/StoredData", filename)

@app.route('/take_video', methods=["GET", "POST"])
def take_Video():
    FolderName = session.get('selectedFolder')
    save_Video(FolderName)
    capture_and_save_image(FolderName)
    return redirect(url_for('home'))



if __name__ =="__main__":\
    app.run(debug=True)