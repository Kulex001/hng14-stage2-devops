import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Mock Redis so tests don't need a real Redis connection
@pytest.fixture(autouse=True)
def mock_redis():
    with patch("main.redis_client") as mock:
        mock.lpush = MagicMock(return_value=1)
        mock.lrange = MagicMock(return_value=[])
        mock.hgetall = MagicMock(return_value={})
        yield mock

def test_root_returns_running():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_job_returns_id():
    response = client.post("/jobs", json={"type": "test-job"})
    assert response.status_code == 200
    assert "id" in response.json()

def test_invalid_job_returns_error():
    response = client.post("/jobs", json={})
    assert response.status_code == 422

def test_get_nonexistent_job():
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
