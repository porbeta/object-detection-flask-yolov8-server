import pytest
from src.app.flaskapp import main

@pytest.fixture()
def app():
    yield main.app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_hello(client):
    response = client.get("/ping")
    assert b"{\"status\": \"SUCCESS\"}" in response.data