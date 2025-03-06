import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_chat():
    response = client.post("/chat", json={"question": "Oi"})
    assert response.status_code == 200
    assert "response" in response.json()

def test_intents():
    response = client.get("/intents")
    assert response.status_code == 200
    assert "intents" in response.json()
