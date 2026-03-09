import base64
import json
import requests
import time
import os

BASE_URL = "http://localhost:8000/api/v2"

def load_file_as_b64(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def main():
    # 1. Fetch Workflows
    print("Fetching workflows...")
    wf_resp = requests.get(f"{BASE_URL}/studio/workflows")
    if wf_resp.status_code != 200:
        print(f"Failed to fetch workflows: {wf_resp.status_code}")
        return
        
    workflows = wf_resp.json()
    
    # 2. Select workflow_courtroom_30_fused_dual (or whichever we just seeded)
    workflow_id = None
    for item in workflows:
        w_id = item.get('id', '')
        if 'courtroom_30_fused_dual' in w_id:
            workflow_id = w_id
            break
            
    if not workflow_id:
        print("Required workflow courtroom_30 not found.")
        return
        
    print(f"Selected workflow: {workflow_id}")

    # Load authentic V1 PDF files
    base_dir = r"c:\src\quorum\data\files\548d78cd-d540-44a3-bc3e-965064803a40"
    
    path_history = os.path.join(base_dir, "keskusteluhistoria SITRA.pdf")
    path_product = os.path.join(base_dir, "lopputuote sitra.pdf")
    path_reflection = os.path.join(base_dir, "Reflektiodokumentti sitra.pdf")

    # Simulate Flutter app payload containing base64 files
    raw_inputs = {
        "history_text": {
            "filename": "keskusteluhistoria SITRA.pdf",
            "content_base64": load_file_as_b64(path_history)
        },
        "product_text": {
            "filename": "lopputuote sitra.pdf",
            "content_base64": load_file_as_b64(path_product)
        },
        "reflection_text": {
            "filename": "Reflektiodokumentti sitra.pdf",
            "content_base64": load_file_as_b64(path_reflection)
        },
        # We explicitly omit guided_reflection, as reflection_text serves as the alternative!
        "guided_reflection": None
    }
            
    # 3. Create Execution
    payload = {
        "workflow_id": workflow_id,
        "raw_inputs": raw_inputs
    }
    
    print("\nStarting execution with REAL PDF FILES encoded as Base64...")
    create_resp = requests.post(f"{BASE_URL}/executions/", json=payload)
    if create_resp.status_code != 202:
        print(f"Failed to create execution: {create_resp.status_code} - {create_resp.text}")
        return
        
    execution = create_resp.json()
    execution_id = execution['id']
    print(f"Execution started! ID: {execution_id}")
    
    # 4. Poll for completion
    print("Polling for status...")
    while True:
        status_resp = requests.get(f"{BASE_URL}/executions/{execution_id}")
        if status_resp.status_code != 200:
            print(f"Error fetching status: {status_resp.status_code}")
            break
            
        current_state = status_resp.json()
        status = current_state.get('status')
        print(f"Current status: {status}")
        
        if status in ['COMPLETED', 'FAILED']:
            if status == 'FAILED':
                print(f"Execution failed: {current_state.get('error')}")
            else:
                print("Execution completed successfully!")
                print("\n=== DEBUG PRINT: PROCESSED INPUTS BEFORE NEXT PHASE ===")
                results = current_state.get('results', {})
                input_step = results.get("step_input_processing", {})
                
                print(f"--- history_text snippet ({len(input_step.get('history_text', ''))} chars) ---")
                print(input_step.get("history_text", "")[:500] + "...\n")
                
                print(f"--- product_text snippet ({len(input_step.get('product_text', ''))} chars) ---")
                print(input_step.get("product_text", "")[:500] + "...\n")
                
                print(f"--- reflection_text snippet ({len(input_step.get('reflection_text', ''))} chars) ---")
                print(input_step.get("reflection_text", "")[:500] + "...\n")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    main()
