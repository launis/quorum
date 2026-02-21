import json
from fastapi.testclient import TestClient
from backend.main import app

# Create a test client
client = TestClient(app)

# Use the root master user's token directly, or just bypass auth for the test
# Wait, quorum uses Authorization: Bearer mock-token-root-master for tests
headers = {"Authorization": "Bearer mock-token-root-master"}

response = client.get("/builder/workflows", headers=headers)
if response.status_code == 200:
    with open("api_dump.json", "w", encoding="utf-8") as f:
        json.dump(response.json(), f, indent=2)
    print("Dumped response to api_dump.json")
else:
    print("Error:", response.status_code, response.text)
