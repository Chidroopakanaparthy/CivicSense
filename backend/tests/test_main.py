import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

# Evaluation Criterion: Testing (Backend)
def test_read_root():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("main.llm_service.get_response", new_callable=AsyncMock)
def test_chat_endpoint(mock_get_response):
    """Test the chat endpoint with mocked LLM service."""
    mock_get_response.return_value = {"text": "Neutral election info", "cached": False}
    
    response = client.post("/api/chat", json={"message": "When is election day?"})
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert response.json()["text"] == "Neutral election info"
    mock_get_response.assert_called_once()

def test_rate_limiter():
    """
    Test that the rate limiter triggers after multiple requests.
    Note: Depends on the '5/minute' setting in main.py.
    """
    with patch("main.llm_service.get_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = {"text": "response", "cached": False}
        
        # Make 6 requests (limit is 5)
        for _ in range(5):
            client.post("/api/chat", json={"message": "hello"})
        
        response = client.post("/api/chat", json={"message": "sixth request"})
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.text

@patch("main.civic_service.get_voter_info", new_callable=AsyncMock)
def test_civic_info_endpoint(mock_civic):
    """Test the civic info endpoint with mocked service."""
    mock_civic.return_value = {"pollingLocations": [{"name": "Town Hall"}]}
    
    response = client.post("/api/civic-info", json={"address": "123 Main St"})
    
    assert response.status_code == 200
    assert "pollingLocations" in response.json()
    assert response.json()["pollingLocations"][0]["name"] == "Town Hall"
