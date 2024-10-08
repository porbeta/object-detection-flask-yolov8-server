from flask import Flask, render_template 
from flask_socketio import SocketIO, emit
from pathlib import Path
from ultralytics import YOLO
import supervision as sv
import os
import numpy as np
import base64
import io
import PIL.Image as Image
import socketio as sio

socket_to_observer = sio.Client()

model_path = Path(__file__).parents[3]

app = Flask(__name__)
model = YOLO(os.path.join(model_path, "yolov8n.pt"))

box_annotator = sv.BoxAnnotator(
    thickness=1,
    text_thickness=1,
    text_scale=1
)

MAX_BUFFER_SIZE = 50 * 1000 * 1000
socketio = SocketIO(app, max_http_buffer_size=MAX_BUFFER_SIZE, cors_allowed_origins="*")

connected = False
observer_endpoint = os.environ.get('OBSERVER_ENDPOINT')

if observer_endpoint:
    print("OBSERVER SET TO: ", observer_endpoint)

    try:
        socket_to_observer.connect(observer_endpoint, namespaces=['/observer'])
    except sio.exceptions.ConnectionError as err:
        print("ConnectionError: ", err)
    else:
        print("Connected!")
        connected = True
else:
    print("OBSERVER NOT SET: Continuing with default mode")

def process_frame(frame, model, box_annotator):
    result = model(frame, agnostic_nms=True)[0]
    detections = sv.Detections.from_yolov8(result)
    labels = [
        f"{model.model.names[class_id]} {confidence:0.2f}"
        for _, confidence, class_id, _
        in detections
    ]
    annotated_frame = box_annotator.annotate(
        scene=frame,
        detections=detections,
        labels=labels
    )
    return annotated_frame

@app.route('/ping')
def hello():
    return "{\"status\": \"SUCCESS\"}"

@app.route('/')
def show_client():
    return render_template('client.html') 

@socketio.on('receive-image', namespace='/image-processing')
def handle_receive_image(images_bytes):
    b = bytearray()
    b.extend(map(ord, images_bytes))

    image = Image.open(io.BytesIO(b))
    image_array = np.array(image)

    annotated_frame = process_frame(image_array, model, box_annotator)

    returned_image = Image.fromarray(annotated_frame)
    returned_buffer = io.BytesIO()
    returned_image.save(returned_buffer, format="JPEG")

    base64string = base64.b64encode(returned_buffer.getvalue()).decode("utf-8")
    data_url = 'data:image/jpeg;base64,' + base64string

    emit('stream-image', data_url)

    if connected:
        print("IMAGE SENT TO OBSERVER")
        socket_to_observer.emit('observer-image', data_url, namespace="/observer")
