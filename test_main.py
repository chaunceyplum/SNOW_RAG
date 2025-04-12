from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app  # Ensure your FastAPI app is named 'app' in main.py

client = TestClient(app)

@patch("main.sendQuery")
def test_question_endpoint(mock_sendQuery):
    # Mock the response of sendQuery
    mock_sendQuery.return_value = "This is a mocked response from the LLM."

    # Define the test payload
    payload = {"query": "What is Snowflake?"}

    # Make the request
    response = client.post("/question", json=payload)

    # Assertions
    # assert response.status_code == 200
    # assert response.json() == "This is a mocked response from the LLM."

def test_question_invalid_payload():
    # Test when no query parameter is sent
    response = client.post("/question", json={})

    assert response.status_code == 422  # Unprocessable Entity due to missing required field
