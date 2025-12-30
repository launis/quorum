
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def rebuild_db():
    print("Triggering Database Rebuild...")
    try:
        response = requests.post(f"{BASE_URL}/admin/database/rebuild")
        if response.status_code == 200:
            job_id = response.json().get("job_id")
            print(f"Rebuild started. Job ID: {job_id}")
            
            while True:
                status_response = requests.get(f"{BASE_URL}/admin/status/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    state = status_data.get("status")
                    progress = status_data.get("progress", [])
                    print(f"Status: {state}, Progress: {progress[-1] if progress else 'Starting...'}")
                    
                    if state in ["COMPLETED", "FAILED"]:
                        print(f"Final State: {state}")
                        if state == "FAILED":
                             print(f"Error: {status_data.get('error')}")
                             sys.exit(1)
                        break
                else:
                    print(f"Error checking status: {status_response.status_code}")
                time.sleep(1)
        else:
            print(f"Failed to trigger rebuild: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rebuild_db()
