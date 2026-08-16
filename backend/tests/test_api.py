from fastapi.testclient import TestClient
from app.main import app

# Create a test client using our FastAPI app instance
client = TestClient(app)

def test_health_check():
    # Act: Send a simulated GET request to the health endpoint
    response = client.get("/api/health")
    
    # Assert: Verify the status code and JSON payload
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ForumSearch API" in data["message"]