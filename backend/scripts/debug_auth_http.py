
import requests


def debug_auth_http():
    base_url = "http://localhost:8000"

    # 1. Check Health
    try:
        resp = requests.get(f"{base_url}/docs", timeout=2)
        print(f"[HTTP] Backend is reachable (Status: {resp.status_code})")
    except Exception as e:
        print(f"[HTTP] CRITICAL: Cannot reach backend at {base_url}. Is it running? Error: {e}")
        return

    # 2. Simulate Mock Login (Verify Token)
    # The client sends: Authorization: Bearer mock-token:root_master
    # To endpoint: /api/v1/auth/verify (or similar - let's check auth_router.py)

    # Actually, the client uses `signInWithMockToken` which might just set the token and call `verify`.
    # Let's check `auth_router.py` to see the exact endpoint for verification.
    # It is likely `GET /auth/verify` or `POST /auth/verify`.

    # Based on previous file reads, it was `c:\src\quorum\backend\api\auth_router.py`.
    # Let's assume GET /auth/verify for now with the header.

    # 3. Correct Endpoint: POST /auth/verify
    url = f"{base_url}/auth/verify"
    payload = {"token": "mock-token:root_master"}

    print(f"[HTTP] POST {url} with payload {payload}")
    try:
        resp = requests.post(url, json=payload, timeout=5)

        if resp.status_code == 200:
            print(f"[SUCCESS] Login Successful! User: {resp.json().get('user', {}).get('uid')}")
        else:
            print(f"[FAILURE] Status: {resp.status_code}, Body: {resp.text}")

    except Exception as e:
        print(f"[HTTP] Request failed: {e}")

if __name__ == "__main__":
    debug_auth_http()
