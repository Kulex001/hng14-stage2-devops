import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("main.r") as mock:
        mock.ping = MagicMock(return_value=True)
        mock.lpush = MagicMock(return_value=1)
        mock.hset = MagicMock(return_value=1)
        mock.hget = MagicMock(return_value=None)
        yield mock


def test_health_endpoint(mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_job_returns_id(mock_redis):
    response = client.post("/jobs")
    assert response.status_code == 200
    assert "job_id" in response.json()


def test_get_nonexistent_job(mock_redis):
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404


def test_get_existing_job(mock_redis):
    mock_redis.hget.return_value = "queued"
    response = client.get("/jobs/some-job-id")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_create_job_pushes_to_queue(mock_redis):
    client.post("/jobs")
    assert mock_redis.lpush.called
