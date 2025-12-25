import requests
import os
import json
import time

BASE_URL = "http://localhost:8000"

# Files from the execution mentioned: 0ab27be9-aaef-4446-87fa-749038c75dc2
# Path: backend/files/executions/0ab27be9-aaef-4446-87fa-749038c75dc2/
# Filenames: Reflektiodokumentti sitra.pdf, keskusteluhistoria SITRA.pdf, lopputuote sitra.pdf

EXECUTION_ID = "0ab27be9-aaef-4446-87fa-749038c75dc2"
FILES_DIR = os.path.join("backend", "files", "executions", EXECUTION_ID)

FILE_MAP = {
    "keskusteluhistoria": "keskusteluhistoria SITRA.pdf",
    "lopputuote": "lopputuote sitra.pdf",
    "reflektiodokumentti": "Reflektiodokumentti sitra.pdf"
}

def run_execution_test(use_fusion=False):
    print(f"\n🚀 Starting E2E{' FUSION' if use_fusion else ''} Execution Test...")

    # 1. Get Base Workflow
    r = requests.get(f"{BASE_URL}/builder/workflows")
    r.raise_for_status()
    wfs = r.json()
    seed_wf = next((w for w in wfs if w['id'] == 'sequential_audit_chain'), None)
    
    if not seed_wf:
        print("❌ Seed workflow not found")
        return
        
    wf_id = seed_wf['id']

    # 2. If Fusion requested, create a fused workflow
    if use_fusion:
        print("🔹 Creating Fused Workflow...")
        # Copy
        r = requests.post(f"{BASE_URL}/builder/workflows/{seed_wf['id']}/copy", json={"new_name": "E2E Fusion Test"})
        if r.status_code != 200:
            print(f"❌ Copy failed: {r.text}")
            return
        
        new_wf = r.json()
        wf_id = new_wf['id']
        
        # Compile
        payload = {
            "workflow_id": wf_id,
            "steps": ["step_logician", "step_falsifier", "step_causal", "step_detector", "step_overseer"]
        }
        r = requests.post(f"{BASE_URL}/builder/compile", json=payload)
        if r.status_code != 200:
             print(f"❌ Compilation failed: {r.text}")
             return
        print(f"✅ Fused Workflow Created: {wf_id}")

    # 3. Prepare Files
    files_payload = []
    
    # Verify files exist
    for key, fname in FILE_MAP.items():
        fpath = os.path.join(FILES_DIR, fname)
        if not os.path.exists(fpath):
            print(f"❌ File missing: {fpath}")
            return
        # Tuples for requests: (field_name, (filename, file_handle, content_type))
        # API expects: files list of ('files', (filename, open(path, 'rb'), 'application/pdf'))
        # AND Inputs mapped correctly.
        
    # 4. Create Execution
    print(f"🔹 Submitting Execution for {wf_id}...")
    
    # We need to open files. Using Context Manager stack is tricky here, so we do it manually and verify close.
    open_files = []
    
    try:
        multipart_files = []
        for key, fname in FILE_MAP.items():
            fpath = os.path.join(FILES_DIR, fname)
            f = open(fpath, 'rb')
            open_files.append(f)
            # The API expects key to match the input name if we used simple form fields, 
            # BUT our endpoint usually takes 'files' as a list and maps them via logic.
            # Let's check execution_router endpoint signature.
            # If it uses UploadFile, key matters.
            # Usually: key='files' for all, or specific keys.
            # In validation step we saw: 'Multipart/Form-Data source'.
            # I will assume key name matches the input variable name for auto-mapping?
            # Or generic 'files'.
            # Let's use key name.
            multipart_files.append((key, (fname, f, 'application/pdf')))

        # Inputs JSON
        # If sending files, we usually send inputs as form fields OR query params.
        # execution_router.py likely handles this.
        # Let's try sending basic inputs as data.
        data = {
            "workflow_id": wf_id,
            "inputs": json.dumps({"test_run": "true"}) # Inputs needs to be JSON string if multipart
        }
        
        # We need to find the correct endpoint. 
        # Usually POST /executions
        
        r = requests.post(f"{BASE_URL}/executions", files=multipart_files, data=data) 
        
        if r.status_code == 200:
            exec_res = r.json()
            exec_id = exec_res['execution_id']
            print(f"✅ Execution ID: {exec_id}")
            
            # 5. Monitor
            print("🔹 Monitoring status (Polling)...")
            status = "pending"
            start_time = time.time()
            
            while status in ["pending", "running"]:
                time.sleep(2)
                r_status = requests.get(f"{BASE_URL}/executions/{exec_id}")
                if r_status.status_code != 200:
                    print("❌ Status check failed")
                    break
                
                info = r_status.json()
                status = info['status']
                print(f"   Status: {status}...")
                
                if time.time() - start_time > 600: # 10 min timeout for production
                    print("⏰ Timeout!")
                    break
            
            print(f"🏁 Final Status: {status}")
            if status == "completed":
                print("✅ RESULT OK.")
                # print(json.dumps(info.get('result', {}), indent=2))
            else:
                print(f"❌ Execution failed: {info.get('error')}")

        else:
            print(f"❌ Submission Failed: {r.text}")

    finally:
        for f in open_files:
            f.close()

if __name__ == "__main__":
    print("=== MOCK ENVIRONMENT TEST ===")
    
    # Test 1: Standard
    # print("\n[TEST 1] Standard Sequential Chain")
    # run_execution_test(use_fusion=False)
    
    # Test 2: Fused
    print("\n[TEST 2] Fused Panel Chain")
    run_execution_test(use_fusion=True)
