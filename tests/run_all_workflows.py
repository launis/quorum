
import requests
import os
import json
import time

BASE_URL = "http://localhost:8000"
EXEC_DIR = r"c:\Users\risto\OneDrive\quorum\backend\files\executions\0ab27be9-aaef-4446-87fa-749038c75dc2"

FILES_MAPPING = {
    "history_file": "keskusteluhistoria SITRA.pdf",
    "product_file": "lopputuote sitra.pdf",
    "reflection_file": "Reflektiodokumentti sitra.pdf"
}

WORKFLOWS_TO_RUN = [
    "sequential_audit_chain",
    "fused_audit_chain",
    "sequential_audit_chain_cognitive",
    "fused_audit_chain_cognitive",
    "sequential_audit_chain_dual",
    "fused_audit_chain_dual"
]

def get_db_workflows_map():
    try:
        r = requests.get(f"{BASE_URL}/db/workflows")
        r.raise_for_status()
        workflows = r.json()
        # Map ID to Name or just confirm ID exists
        return {w['id']: w for w in workflows}
    except Exception as e:
        print(f"Failed to fetch workflows: {e}")
        return {}

def trigger_workflow(workflow_id, file_paths):
    url = f"{BASE_URL}/executions"
    
    files = {}
    opened_files = []
    
    try:
        for key, filename in FILES_MAPPING.items():
            path = os.path.join(EXEC_DIR, filename)
            if os.path.exists(path):
                f = open(path, "rb")
                opened_files.append(f)
                files[key] = (filename, f, "application/pdf")
            else:
                print(f"Warning: File not found: {path}")

        data = {
            "workflow_id": workflow_id,
            "inputs": json.dumps({}) # Backend expects JSON string for inputs
        }

        print(f"Triggering workflow: {workflow_id}...")
        response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            res_json = response.json()
            print(f"SUCCESS: Started {workflow_id} -> ID: {res_json.get('execution_id')}")
            return res_json.get('execution_id')
        else:
            print(f"FAILED: {workflow_id} -> Status: {response.status_code}, Body: {response.text}")
            return None
            
    finally:
        for f in opened_files:
            f.close()

def main():
    print("--- Mass Workflow Runner ---")
    
    # 1. Check Backend Connectivity
    try:
        requests.get(f"{BASE_URL}/docs")
        print("Backend is reachable.")
    except:
        print("Backend is NOT reachable. Please ensure it is running.")
        return

    # 2. Validate Workflows
    available_workflows = get_db_workflows_map()
    print(f"Found {len(available_workflows)} available workflows in DB.")

    # 3. Run Loop
    for wf_id in WORKFLOWS_TO_RUN:
        if wf_id not in available_workflows:
            print(f"Skipping {wf_id} (Not found in DB?) - Check seed_data.json consistency.")
            continue
            
        execution_id = trigger_workflow(wf_id, FILES_MAPPING)
        
        # Optional: Wait a bit to avoid overwhelming if locally resource constrained? 
        # But Mock mode is fast.
        time.sleep(2) 

if __name__ == "__main__":
    main()
