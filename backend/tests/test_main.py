import os
import sys
from unittest.mock import MagicMock
# Task 1: Fix Backend Path Resolution
# Ensure the backend root is in the Python path for CI test discovery
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Task 1: Fix Backend Test Collection Error
# Injecting system-level mocks before any other imports
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.generative_models'] = MagicMock()

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Mock env vars
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GOOGLE_CIVIC_API_KEY"] = "test-key"

from main import app

client = TestClient(app)

def test_read_root():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_endpoint():
    """
    Test the chat endpoint with mocked GenerativeModel.
    Bypasses real network calls by configuring the system-level mock.
    """
    from vertexai.generative_models import GenerativeModel
    
    # Task 1: Configure the Mock Return Value
    # Configure the nested mock structure: GenerativeModel().generate_content_async().text
    mock_response = MagicMock()
    mock_response.text = "This is a mocked AI response"
    
    # Vertex AI service uses generate_content_async
    GenerativeModel.return_value.generate_content_async = AsyncMock(return_value=mock_response)
    
    response = client.post("/api/chat", json={"message": "What are my civic duties?"})
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert response.json()["text"] == "This is a mocked AI response"

def test_rate_limiter():
    """Verify rate limiter triggers correctly using the mocked service."""
    from vertexai.generative_models import GenerativeModel
    mock_response = MagicMock(text="resp")
    GenerativeModel.return_value.generate_content_async = AsyncMock(return_value=mock_response)
    
    # Make 6 requests (limit is 5/minute)
    for _ in range(5):
        client.post("/api/chat", json={"message": "hi"})
    
    response = client.post("/api/chat", json={"message": "limited"})
    assert response.status_code == 429
