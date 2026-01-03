import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "mock-token:root_master"
WF_ID = "fused_audit_chain"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Get current state
print("--- Fetching current state ---")
res = requests.get(f"{BASE_URL}/builder/workflows/{WF_ID}", headers=headers)
if res.status_code != 200:
    print(f"Failed to fetch: {res.text}")
    exit(1)
    
curr = res.json()
print(f"Current Public: {curr.get('is_public')}")

# 2. Update to True
print("\n--- Updating to True ---")
payload = {
    "is_public": True
}
res = requests.put(f"{BASE_URL}/builder/workflows/{WF_ID}", json=payload, headers=headers)
if res.status_code != 200:
    print(f"Update failed: {res.text}")
    exit(1)
    
updated = res.json()
print(f"Response Public: {updated.get('is_public')}")

# 3. Verify Persistence
print("\n--- Verifying Persistence ---")
res = requests.get(f"{BASE_URL}/builder/workflows/{WF_ID}", headers=headers)
final = res.json()
print(f"Final Public: {final.get('is_public')}")
