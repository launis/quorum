import json
import os
import subprocess
import sys
import time

import requests


def check_backend():
    for _ in range(45):
        try:
            r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

def trigger_execution():
    print("Triggering E2E execution natively via Python requests...")
    import requests
    
    # 1. Read Inputs
    inputs_file = os.environ.get("TEST_INPUTS_FILE", "")
    if not inputs_file:
        inputs_file = r"c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json"
    
    with open(inputs_file, "r", encoding="utf-8") as f:
        raw_inputs = json.load(f)
        
    # 2. Setup requests session
    headers = {"Authorization": "Bearer mock-token:usr_18a0d5f6151349a5"}
    base_url = "http://127.0.0.1:8000/api/v2"
    
    # 3. Get Workflow ID
    w_res = requests.get(f"{base_url}/studio/workflows/", headers=headers, timeout=10)
    w_res.raise_for_status()
    workflows = w_res.json()
    workflow_id = workflows[0]["id"] if workflows else "wf_9d68c573802341db"
    
    # 4. Trigger Execution
    print(f"Sending POST to {base_url}/execution/executions/ using workflow {workflow_id}")
    resp = requests.post(
        f"{base_url}/execution/executions/",
        headers=headers,
        json={
            "workflow_id": workflow_id,
            "profile_id": "prf_5d6e7f8091a2b3c4",
            "raw_inputs": {"dynamic_inputs": raw_inputs},
            "target_locale": "fi"
        },
        timeout=300
    )
    if not resp.ok:
        print(f"HTTP ERROR {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    
    # 5. Save Trace
    out_trace = r"c:\src\quorum\backend_v2\tests\test_data\e2e_new_trace.json"
    trace_data = resp.json().get("execution_trace")
    if trace_data is not None:
        with open(out_trace, "w", encoding="utf-8") as f:
            json.dump(trace_data, f)
        print("Saved trace successfully.")
    else:
        print("Error: execution_trace missing from response!")
        sys.exit(1)

for i in range(2):
    print(f"\n=== RUN {i+1} ===")
    print("Cleaning up old services...")
    subprocess.run([r"c:\src\quorum\kill_services.bat"], input="\n", text=True, capture_output=True, shell=True)

    print("Starting run_local.bat...")
    # creationflags=subprocess.CREATE_NEW_CONSOLE allows it to spawn detached windows just like a user double-clicking it
    p = subprocess.Popen([r"c:\src\quorum\run_local.bat"], creationflags=subprocess.CREATE_NEW_CONSOLE)

    print("Waiting for backend to become responsive...")
    if not check_backend():
        print("Backend failed to start!")
        sys.exit(1)

    # Wait extra time for the worker to fully boot up and connect to Redis
    time.sleep(10)

    # Inject noise for Run 2 to test the normalizer
    if i == 1:
        print("Injecting noise into inputs for Run 2 (to test normalizer)...")
        input_path = r"c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json"
        noisy_path = r"c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs_NOISY.json"
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Add a zero-width space, some trailing spaces, and change a regular space to multiple spaces in product_text
        if "product_text" in data and isinstance(data["product_text"], str):
            original_text = data["product_text"]
            # Inject a micro-perturbation (Butterfly effect test)
            # A single typo (one extra letter) early in the text that BYPASSES normalization.py
            noisy_text = original_text.replace(" a ", " aa ", 1)
            data["product_text"] = noisy_text
        
        with open(noisy_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        # Tell the dart test to use the noisy file
        os.environ["TEST_INPUTS_FILE"] = noisy_path
    else:
        # Run 1 uses default
        os.environ["TEST_INPUTS_FILE"] = ""

    trigger_execution()

    print("Polling database for execution completion (max 60 mins)...")
    db_path = r"c:\src\quorum\data\db_v2.json"
    timeout = 3600
    start = time.time()
    done = False

    while time.time() - start < timeout:
        time.sleep(5)
        try:
            with open(db_path, encoding="utf-8") as f:
                db_data = json.load(f)
            execs = list(db_data.get("executions", {}).values())
            if execs:
                latest = sorted(execs, key=lambda x: x.get("created_at", ""), reverse=True)[0]
                status = str(latest.get("status")).upper()
                if status in ["COMPLETED", "FAILED"]:
                    print(f"Execution {latest.get('id')} finished with status: {status}")
                    done = True
                    break
        except Exception:
            pass

    if not done:
        print("Timeout waiting for execution!")
        sys.exit(1)

print("\n=== FINAL CLEANUP ===")
subprocess.run([r"c:\src\quorum\kill_services.bat"], input="\n", text=True, capture_output=True, shell=True)

print("\n=== RUNNING DIFF EXECUTIONS ===")
res = subprocess.run(["uv", "run", "python", r"c:\src\quorum\scripts\diff_executions.py"], capture_output=True, text=True, shell=True)
print(res.stdout)
if res.stderr:
    print("STDERR:")
    print(res.stderr)
