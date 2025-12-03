import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.main import engine

client = TestClient(app)

def test_banned_phrases_crud():
    # 1. Create
    payload = {"phrase": "test_ban_phrase", "language": "en"}
    response = client.post("/admin/banned-phrases", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    doc_id = data["id"]
    
    # 2. Read
    response = client.get("/admin/banned-phrases")
    assert response.status_code == 200
    phrases = response.json()
    assert any(p["phrase"] == "test_ban_phrase" for p in phrases)
    
    # 3. Delete
    response = client.delete(f"/admin/banned-phrases/{doc_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get("/admin/banned-phrases")
    phrases = response.json()
    assert not any(p["phrase"] == "test_ban_phrase" for p in phrases)

def test_duplicate_phrase():
    payload = {"phrase": "duplicate_test", "language": "en"}
    client.post("/admin/banned-phrases", json=payload)
    
    # Try adding again
    response = client.post("/admin/banned-phrases", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "exists"
    
    # Cleanup
    # (In a real test env, we'd reset DB, but here we just leave it or manually find and delete)
    # For now, relying on unique test names.
