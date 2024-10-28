from flask import Flask, render_template, request 
from flask_socketio import SocketIO, emit
from pathlib import Path
from ultralytics import YOLO
import supervision as sv
import os.path as path
import numpy as np
import base64
import io
import PIL.Image as Image
import redis

redis_client = None
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    print("Connected to Redis")
except redis.exceptions.ConnectionError as e:
    print("Connection attempt failed")
    redis_client = None

model_path = Path(__file__).parents[3]

app = Flask(__name__)
model = YOLO(path.join(model_path, "yolov8n.pt"))

box_annotator = sv.BoxAnnotator(
    thickness=1,
    text_thickness=1,
    text_scale=1
)

MAX_BUFFER_SIZE = 50 * 1000 * 1000
socketio = SocketIO(app, max_http_buffer_size=MAX_BUFFER_SIZE, cors_allowed_origins="*")

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

@app.route('/recorder')
def show_recorder():
    return render_template('recorder.html')

@app.route('/')
def show_observer():
    return render_template('observer.html')

@socketio.on('connect', namespace='/image-processing')
def handle_connect():
    sid = request.sid
    if redis_client is not None:        
        active_client = redis_client.get('active_client')

        if active_client is None:
            redis_client.set('active_client', sid)
            print("active_client set to " + sid)

    print('Client connected with SID:', sid)

@socketio.on('disconnect', namespace='/image-processing')
def handle_disconnect():
    if redis_client is not None:        
        active_client = redis_client.get('active_client')

        if active_client is not None:
            redis_client.delete('active_client')
            print("active_client deleted")

    print('Client disconnected')

@socketio.on('receive-image', namespace='/image-processing')
def handle_receive_image(images_bytes):
    sid = request.sid
    active_client = None

    print("socket id: " + sid)

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

    if redis_client is not None:        
        active_client = redis_client.get('active_client')

        if active_client is not None:
            active_client_str = active_client.decode("utf-8")
            print("active_client: " + active_client_str)

            if active_client_str == sid:
                emit('broadcasted-image', data_url, broadcast=True)
                print('sent to observer')
        else:
            redis_client.set('active_client', sid)
            print("active_client set to " + sid)