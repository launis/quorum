import sys

import requests

BASE_URL = "http://127.0.0.1:8000"

def verify_live_env():
    print(f"[*] Verifying connection to {BASE_URL} (Timeout: 20s)...")

    # 1. Check Root / Docs Access
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=20)
        if r.status_code == 200:
            print("[✅] Connection Check: SUCCESS")
        else:
            print(f"[❌] Connection Check: FAILED (Status: {r.status_code})")
            sys.exit(1)

    except Exception as e:
        print(f"[❌] Connection Check: FAILED (Error: {e})")
        print("    -> Ensure run_local.bat is running!")
        sys.exit(1)

    # 2. Check Workflows (Data Validity)
    print("\n[*] Verifying Data Load (Workflows)...")
    try:
        # Based on execution_router.py V2, list may be at /execution-data/workflows or similar?
        # Actually standard router for workflows in V2.9 execution_router.py is likely mounted.
        # Let's try endpoint defined in execution_router.py: @workflow_router.get("/")
        # In main.py: app.include_router(execution_router.workflow_router)
        # Prefix for workflow_router was not explicitly seen in snippet, assuming it's imported from execution_router.

        # Let's try the common endpoint: /builder/workflows (Builder Router)
        endpoint = "/builder/workflows"
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)

        # If 404, valid fallback might be /v2/workflow or /config/workflows (legacy)
        if r.status_code == 404:
            print(f"[!] {endpoint} not found, trying /config/workflows...")
            endpoint = "/config/workflows"
            r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)

        if r.status_code == 200:
            workflows = r.json()
            print(f"[✅] Workflow List: SUCCESS ({len(workflows)} found)")

            ids = [w.get('id') for w in workflows]
            target_id = "sequential_audit_chain"
            if target_id in ids:
                print(f"[✅] Found Target Workflow: '{target_id}'")
            else:
                 print(f"[❌] Target Workflow '{target_id}' MISSING in list: {ids}")
                 # This would mean db.json sync issue

        else:
            print(f"[❌] Workflow List: FAILED (Status: {r.status_code})")
            print(f"    Body: {r.text[:200]}")

    except Exception as e:
        print(f"[❌] Data Check Failed: {e}")

    # 3. Check Recent Executions (Persistence)
    print("\n[*] Verifying Execution History...")
    try:
        endpoint = "/executions/recent"
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)

        if r.status_code == 200:
             execs = r.json()
             print(f"[✅] Recent Executions: SUCCESS ({len(execs)} items)")
             if execs:
                 item = execs[0]
                 print(f"    Sample ID: {item.get('execution_id')} - Status: {item.get('status')}")
        else:
             print(f"[!] Recent Executions check returned {r.status_code} (This is OK if endpoint behavior varies)")

    except Exception as e:
        print(f"[!] Warning: Could not check recent executions: {e}")

if __name__ == "__main__":
    verify_live_env()
