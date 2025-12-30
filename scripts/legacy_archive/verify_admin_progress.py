from fastapi.testclient import TestClient
from backend.main import app
import time
import sys
import os

client = TestClient(app)

def test_export_progress():
    print("\n[TEST] Testing Export Seed Data Progress...")
    # 1. Start Task
    res = client.post("/admin/export/seed-data")
    if res.status_code != 200:
        print(f"FAIL: Start failed: {res.text}")
        return
    
    data = res.json()
    job_id = data.get("job_id")
    print(f"Job Started: {job_id}")
    
    # 2. Poll Status
    status = "starting"
    while status not in ["completed", "failed"]:
        res = client.get(f"/admin/status/{job_id}")
        if res.status_code != 200:
             print(f"FAIL: Poll failed: {res.text}")
             break
        
        state = res.json()
        status = state['status']
        stage = state.get('stage', 'Unknown')
        percent = state.get('percent', 0)
        
        print(f"Progress: [{status.upper()}] {stage} ({percent}%)")
        
        if status in ["completed", "failed"]:
            print(f"Final Result: {state.get('result') or state.get('error')}")
            break
            
        time.sleep(0.5)

def main():
    try:
        test_export_progress()
        print("\n[SUCCESS] Verification Complete.")
    except Exception as e:
        print(f"\n[ERROR] Verification Failed: {e}")

if __name__ == "__main__":
    main()
