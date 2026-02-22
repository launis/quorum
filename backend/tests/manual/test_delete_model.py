import asyncio

import httpx
import pytest

pytestmark = pytest.mark.skip(reason="Manual API test requiring live server")

BASE_URL = "http://127.0.0.1:8000/api/v1/config/models"


async def test_delete_api():
    print("--- Testing DELETE API Endpoint ---")

    # 1. Create Dummy Strategy via PUT
    provider_id = "mock/temp_delete_me"
    payload = {"id": "temp_delete_me", "provider": "mock", "model_name": "mock-delete-test", "additional_params": {}}

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Creating {provider_id}...")
        resp = await client.put(f"{BASE_URL}/{provider_id}", json=payload)
        if resp.status_code != 200:
            print(f"FAIL: Create failed. {resp.status_code} - {resp.text}")
            return
        print("Created successfully.")

        # 2. Verify Existence
        resp = await client.get(BASE_URL)
        models = resp.json()
        found = any(m["id"] == provider_id for m in models)
        if found:
            print("VERIFIED: Strategy exists in list.")
        else:
            print("FAIL: Strategy not found in list.")
            return

        # 3. DELETE
        print(f"Deleting {provider_id}...")
        resp = await client.delete(f"{BASE_URL}/{provider_id}")
        if resp.status_code == 204:
            print("SUCCESS: Delete returned 204.")
        else:
            print(f"FAIL: Delete returned {resp.status_code} - {resp.text}")
            return

        # 4. Verify Absence
        resp = await client.get(BASE_URL)
        models = resp.json()
        found = any(m["id"] == provider_id for m in models)
        if not found:
            print("VERIFIED: Strategy is GONE from list.")
        else:
            print("FAIL: Strategy still exists in list.")


if __name__ == "__main__":
    asyncio.run(test_delete_api())
