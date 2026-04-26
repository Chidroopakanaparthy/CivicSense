import sys
from unittest.mock import MagicMock
# Task 1: Fix Backend Test Collection Error
# Injecting system-level mocks before any other imports
sys.modules['vertexai'] = MagicMock()
sys.modules['vertexai.generative_models'] = MagicMock()

import os
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

@patch("main.llm_service.get_response", new_callable=AsyncMock)
def test_chat_endpoint(mock_get_response):
    """
    Test the chat endpoint with mocked LLM service.
    Bypasses real network calls for CI.
    """
    mock_get_response.return_value = MagicMock()
    mock_get_response.return_value.text = "Mocked AI Response"
    mock_get_response.return_value.cached = False
    
    response = client.post("/api/chat", json={"message": "What are my civic duties?"})
    
    assert response.status_code == 200
    assert "text" in response.json()

def test_rate_limiter():
    """Verify rate limiter unblocks CI without real backend activity."""
    with patch("main.llm_service.get_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = MagicMock(text="resp", cached=False)
        for _ in range(5):
            client.post("/api/chat", json={"message": "hi"})
        
        response = client.post("/api/chat", json={"message": "limited"})
        assert response.status_code == 429
