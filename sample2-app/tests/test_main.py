import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data

def test_read_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_get_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["data"]) == 3
    assert data["data"][0]["name"] == "홍길동"

def test_get_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "sample2-app"
    assert data["features"]["monitoring"] == True

def test_simulate_error():
    response = client.get("/api/error")
    assert response.status_code in [200, 500]

def test_not_found():
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Not Found"