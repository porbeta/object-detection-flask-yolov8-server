# Object Detection with yolov8 on a Python Flask server

<p>This is a simplified example of object detection running on a Flask app.</p>

## Installation
<p>It is recommended to run this application in a virtual environment:</p>

```
python3 -m venv .venv
source .venv/bin/activate
```

<p>To instal the application and its dependencies, run:</p>

```
pip3 install -r requirements.txt
```


## Running the application

<p>To run the Flask application in development mode, use the following command:</p>

```
flask --app src.app.flaskapp.main run
```

<p>To run the application using Gunicorn, use the following command:</p>

```
gunicorn "wsgi" --bind=0.0.0.0:8080 --access-logfile=- --config ""
```

## Containerization

<p>From the top directory, run the following to create an image:</p>

```
podman build -t object-detection-server:latest -f ./docker/Dockerfile .
```

<p>You can also create a new image using s2i-light using the following command:</p>

```
podman build -t object-detection-sever-base:latest -f ./docker/Dockerfile.s2i .
s2i build . object-detection-sever-base:latest object-detection-sever
```

<p>To create a container, run:</p>

```
podman run -p 8081:8081 object-detection-server
```

## Building and packaging

<p>To generate a distribution package of the application, run:<p>

```
python3 -m build
```

## Running Tests
<p>To install the dependencies needed for executing tests, run:</p>

```
pip3 install -e '.[test]'
```

<p>To run the tests, use the following command from the top directory:</p>

```
pytest
```