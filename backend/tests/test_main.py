import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Task 1: Fix Backend Tests (Mocking Vertex AI)
# We set dummy environment variables BEFORE importing 'main' to avoid initialization errors
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GOOGLE_CIVIC_API_KEY"] = "test-key"

# We mock vertexai.init and GenerativeModel to avoid real API calls during import/init
with patch("vertexai.init"), patch("vertexai.generative_models.GenerativeModel"):
    from main import app

from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("main.llm_service.get_response", new_callable=AsyncMock)
def test_chat_endpoint(mock_get_response):
    """
    Test the chat endpoint with mocked LLM service.
    Verifies that the route returns 200 and a mocked response.
    """
    mock_get_response.return_value = MagicMock()
    mock_get_response.return_value.text = "Neutral election info"
    mock_get_response.return_value.cached = False
    
    response = client.post("/api/chat", json={"message": "When is election day?"})
    
    assert response.status_code == 200
    # The actual service returns a ChatResponse object which is serialized to JSON
    # If the mock return value has a .text attribute, we need to ensure the response matches
    assert "text" in response.json()
    assert response.json()["text"] == "Neutral election info"
    mock_get_response.assert_called_once()

def test_rate_limiter():
    """Test that the rate limiter triggers after multiple requests."""
    with patch("main.llm_service.get_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = MagicMock(text="response", cached=False)
        
        # Make 6 requests (limit is 5/minute)
        for _ in range(5):
            client.post("/api/chat", json={"message": "hello"})
        
        response = client.post("/api/chat", json={"message": "sixth request"})
        assert response.status_code == 429

@patch("main.civic_service.get_voter_info", new_callable=AsyncMock)
def test_civic_info_endpoint(mock_civic):
    """Test the civic info endpoint with mocked service."""
    mock_civic.return_value = {"pollingLocations": [{"name": "Town Hall"}]}
    
    response = client.post("/api/civic-info", json={"address": "123 Main St"})
    
    assert response.status_code == 200
    assert "pollingLocations" in response.json()
