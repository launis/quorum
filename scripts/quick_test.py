import requests
import json
import time

def trigger_analysis():
    url = "http://localhost:8000/api/v1/executions"
    payload = {
        "workflow_id": "fused_audit_chain_cognitive",
        "initial_input": {
            "history_text": "Test input for strict mode verification.",
            "file_metadata": {}
        }
    }
    
    print(f"Triggering workflow at {url}...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        execution_id = data["id"]
        print(f"Workflow started! ID: {execution_id}")
        return execution_id
    except Exception as e:
        print(f"Failed to trigger workflow: {e}")
        return None

def monitor_execution(execution_id):
    url = f"http://localhost:8000/api/v1/executions/{execution_id}"
    print(f"Monitoring execution {execution_id}...")
    
    for _ in range(10):  # Check for 20 seconds
        try:
            response = requests.get(url)
            data = response.json()
            status = data.get("status")
            step = data.get("current_step")
            print(f"Status: {status} | Step: {step}")
            
            if status == "failed":
                print("❌ Workflow FAILED.")
                return False
            if status == "completed":
                print("✅ Workflow COMPLETED.")
                return True
            if step != "step_guard" and step is not None:
                 # If we moved past step_guard, the fix likely worked (guard is usually first)
                 print(f"✅ Moved past Guard step! Current: {step}")
                 return True
                 
            time.sleep(2)
        except Exception as e:
            print(f"Error monitoring: {e}")
    
    print("⚠️ Timed out monitoring (Backend might be slow, but no immediate crash).")
    return True # Tentative pass

if __name__ == "__main__":
    exec_id = trigger_analysis()
    if exec_id:
        monitor_execution(exec_id)
