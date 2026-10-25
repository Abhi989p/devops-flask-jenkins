import pytest
from app import app, APP_VERSION


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_status(client):
    """Homepage should return HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_home_contains_version(client):
    """Homepage should display the current version number."""
    response = client.get("/")
    assert APP_VERSION.encode() in response.data


def test_home_contains_title(client):
    """Homepage should contain the app title."""
    response = client.get("/")
    assert b"Flask DevOps Demo" in response.data


def test_health_status(client):
    """Health endpoint should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_json_status(client):
    """Health endpoint should return JSON with status=healthy."""
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "healthy"


def test_health_json_version(client):
    """Health endpoint should return the current version."""
    response = client.get("/health")
    data = response.get_json()
    assert data["version"] == APP_VERSION
