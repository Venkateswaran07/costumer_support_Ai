from fastapi.testclient import TestClient
from main import app
from schemas import ChatRequest
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_static_files_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ElectionGuide" in response.text

def test_chat_endpoint_validation_error():
    # Missing required fields
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 422 # Unprocessable Entity

def test_chat_endpoint_success(mocker):
    # Mock the generate_response to avoid calling real API during tests
    mock_generate = mocker.patch("main.generate_response", return_value="Here is how you register to vote.")
    mock_get_memory = mocker.patch("main.get_memory", return_value=[])
    mock_add_memory = mocker.patch("main.add_memory")

    request_data = {"user_id": "test_user_123", "message": "How do I register?"}
    response = client.post("/chat", json=request_data)

    assert response.status_code == 200
    assert response.json() == {"response": "Here is how you register to vote."}
    
    mock_get_memory.assert_called_once_with("test_user_123", "How do I register?")
    mock_generate.assert_called_once_with("How do I register?", [])
    mock_add_memory.assert_called_once_with("test_user_123", "How do I register?", "Here is how you register to vote.")
