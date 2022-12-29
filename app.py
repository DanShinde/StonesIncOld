from time import sleep
from funs import StepperMotor, create_options, capture_and_save_image, save_Video
from flask import Flask, render_template, request, redirect, url_for, session, Response
from PIL import Image
import os, cv2
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
streaming = True
global img_array
streaming = True
recording = False
global out

img_array = []


@app.route("/")
@app.route("/home",  methods =["GET", "POST"])
def home():
    global cap
    cap = cv2.VideoCapture(0)
    cap.release()
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
    global streaming
    streaming = False
    FolderName = session.get('selectedFolder')
    capture_and_save_image(FolderName)
    return redirect(url_for('home'))

@app.route('/browser')
def browse_folder():
    folder = 'static/StoredData'
    files = os.listdir(folder)
    return render_template('browse.html', files=files)

@app.route('/StoredData/<path:path>')
def view_media(path):
    directory = '/static/StoredData'
    imgfiles = os.listdir(f"static/StoredData/{path}")
    imgfiles.sort()
    return render_template('view_media.html', files=imgfiles, path=path)


@app.route('/take_video', methods=["GET", "POST"])
def take_Video():
    FolderName = session.get('selectedFolder')
    save_Video(FolderName)
    return redirect(url_for('home'))

def gen(rec):
    # Open the video stream
    global cap
    cap = cv2.VideoCapture(0)
    # Initialize the video writer
    with app.test_request_context():
        folder_name = session.get('selectedFolder')

    while True:
        # Check the status of the streaming
        if not streaming:
            cap.release()
            print("Not streaming")
            break

        # Read a frame from the video stream
        success, frame = cap.read()
        if not success:
            print("Error reading video stream")
            break
        frame = cv2.flip(frame, -1)

        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if jpeg is None:
            print("Error encoding frame as JPEG")
            break
        rec = recording
        # If the recording is on, add the frame to the video
        if rec:
            img_array.append(frame)
            #out.write(frame)
            print(f"Recording {streaming} {len(img_array)}")
        #print(streaming, recording, rec)
        # Yield the JPEG frame
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(recording), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_stream', methods=['POST'])
def start_stream():
  global streaming
  streaming = True
  print("Streaming started")
  return 'Stream started'

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
  global streaming
  streaming = False
  print("Streaming Stopped")
  return 'Stream stopped'

@app.route('/rec_on', methods=['POST'])
def rec_on():
  global recording
  recording = True
  print("Recording Started")
  Motor.rotate(degrees=360, delay=0.01)
  # Set the timer for 5 seconds
  sleep(5)
  recording = False
  # Redirect to the rec_stop route to stop the recording
  return redirect(url_for('rec_off'))

@app.route('/rec_off', methods=["GET",'POST'])
def rec_off():
  global recording
  recording = False
  FolderName = session.get('selectedFolder')
  out = cv2.VideoWriter(f"static/StoredData/{FolderName}/exam1.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 24, (640, 480))
  
  for i, img in enumerate(img_array):
    out.write(img)
    # Construct the file name
#     file_name = f"image_{i}.jpg"
#     # Construct the file path
#     file_path = os.path.join(f"static/StoredData/{FolderName}", file_name)
#     # Save the image to the file
#     cv2.imwrite(file_path, img)
#   image_folder = f"static/StoredData/{FolderName}"
#   images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or
#              img.endswith(".jpeg") or img.endswith("png")]
#   for image in images:
#         out.write(cv2.imread(os.path.join(image_folder,image)))
        #os.remove(os.path.join(image_folder,image))
  out.release()
  print(len(img_array))
  img_array.clear()
  print("Recording Stopped")
  return 'Recording stopped'


if __name__ =="__main__":
    app.run(debug=True)



