
import asyncio
import sys

import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_safety():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n--- Testing Model Registry Safety Rules ---\n")

        # Health Check
        try:
            await client.get(f"{BASE_URL.replace('/api/v1', '')}/docs")
            print("Server is up.")
        except Exception:
            print("Server seems down or slow.")

        # 1. Test System Integrity (Cannot delete default)
        # Assuming 'fast' is default. If checking settings via API is possible, we could do that.
        # But 'fast' is fairly standard.
        print("[1] Attempting to delete default strategy 'fast'...")
        resp = await client.delete(f"{BASE_URL}/config/models/fast")
        if resp.status_code == 403:
            print("✅ PASS: Blocked with 403 Forbidden.")
        else:
            print(f"❌ FAIL: Expected 403, got {resp.status_code} {resp.text}")

        # 2. Setup: Create Temp Strategy
        temp_strat = "safety_test_strat"
        print(f"\n[2] Creating temp strategy '{temp_strat}'...")
        config = {
            "provider": "vertex_ai",
            "model_name": "gemini-pro",
            "id": temp_strat
        }
        resp = await client.put(f"{BASE_URL}/config/models/{temp_strat}", json=config)
        assert resp.status_code in (200, 201), f"Setup failed: {resp.text}"

        # 3. Setup: Create Step using Strategy
        step_id = "safety_test_step"
        print(f"[3] Creating step '{step_id}' using '{temp_strat}'...")
        step_payload = {
            "id": step_id,
            "name": "Safety Test Step",
            "task_key": "analyst",
            "config": {
                "model_strategy": temp_strat
            }
        }
        # Try to delete step first just in case
        await client.delete(f"{BASE_URL}/config/steps/{step_id}")

        resp = await client.post(f"{BASE_URL}/config/steps", json=step_payload)
        if resp.status_code not in (200, 201):
             print(f"⚠️ Setup warning: Step creation failed {resp.status_code} {resp.text}. Trying PUT...")
             resp = await client.put(f"{BASE_URL}/config/steps/{step_id}", json=step_payload)
             assert resp.status_code in (200, 201), f"Setup failed: {resp.text}"

        # 4. Test Reference Integrity (Cannot delete used strategy)
        print(f"[4] Attempting to delete strategy '{temp_strat}' (in use)...")
        resp = await client.delete(f"{BASE_URL}/config/models/{temp_strat}")
        if resp.status_code == 409:
            print("✅ PASS: Blocked with 409 Conflict.")
        else:
             print(f"❌ FAIL: Expected 409, got {resp.status_code} {resp.text}")

        # 5. Cleanup: Remove Usage (Delete Step)
        print(f"\n[5] Deleting step '{step_id}' to remove usage...")
        resp = await client.delete(f"{BASE_URL}/config/steps/{step_id}")
        assert resp.status_code == 200, f"Cleanup failed: {resp.text}"

        # 6. Test Success (Can delete unused strategy)
        print(f"[6] Attempting to delete strategy '{temp_strat}' (unused)...")
        resp = await client.delete(f"{BASE_URL}/config/models/{temp_strat}")
        if resp.status_code == 204:
            print("✅ PASS: Deleted successfully (204).")
        else:
            print(f"❌ FAIL: Expected 204, got {resp.status_code} {resp.text}")

if __name__ == "__main__":
    try:
        asyncio.run(test_safety())
    except Exception as e:
        print(f"Script Error: {e}")
        sys.exit(1)
