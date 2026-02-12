
import asyncio
import os
import sys
import httpx
from pathlib import Path

# Setup Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

async def main():
    print("--- DEBUG AUTH HTTP ---")
    url = "http://localhost:8000/auth/verify"
    payload = {"token": "mock-token:admin_1"}

    print(f"POST {url}")
    print(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ HTTP Auth Success!")
            else:
                print("❌ HTTP Auth Failed!")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Is the backend running? (run_local.bat)")

if __name__ == "__main__":
    asyncio.run(main())
