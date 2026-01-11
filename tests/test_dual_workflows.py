"""Dual Workflows Integration Tests."""

import json
import os
import sys
import time

import requests

# --- CONFIG ---
BASE_URL = "http://localhost:8000"
EXEC_DIR = r"c:\Users\risto\OneDrive\quorum\backend\files\executions\0ab27be9-aaef-4446-87fa-749038c75dc2"

FILES_MAPPING = {
    "history_file": "keskusteluhistoria SITRA.pdf",
    "product_file": "lopputuote sitra.pdf",
    "reflection_file": "Reflektiodokumentti sitra.pdf",
}

WORKFLOWS_TO_TEST = [
    "sequential_audit_chain",
    "fused_audit_chain",
    "sequential_audit_chain_cognitive",
    "fused_audit_chain_cognitive",
    "sequential_audit_chain_dual",
    "fused_audit_chain_dual",
]

# --- HELPERS ---


def trigger_workflow(workflow_id):
    """Trigger a workflow execution via API."""
    url = f"{BASE_URL}/executions"
    files = {}
    opened = []
    try:
        for key, filename in FILES_MAPPING.items():
            path = os.path.join(EXEC_DIR, filename)
            if os.path.exists(path):
                f = open(path, "rb")
                opened.append(f)
                files[key] = (filename, f, "application/pdf")

        data = {"workflow_id": workflow_id, "inputs": json.dumps({})}
        r = requests.post(url, data=data, files=files)
        if r.status_code == 200:
            return r.json()["execution_id"]
        else:
            print(f"❌ Failed to start {workflow_id}: {r.text}")
            return None
    finally:
        for f in opened:
            f.close()


def wait_for_completion(execution_id, timeout=60):
    """Poll API for execution completion."""
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{BASE_URL}/executions/{execution_id}")
        if r.status_code == 200:
            status = r.json()["status"]
            if status in ["completed", "failed", "rejected"]:
                return r.json()
        time.sleep(1)
    return None


def verify_result(wf_id, data):
    """Verify execution result structure."""
    issues = []

    # Check Status
    if data["status"] != "completed":
        issues.append(f"Status is {data['status']} (Expected: completed)")
        return issues

    res = data.get("result", {})
    raw = res.get("Raw_Steps", {})

    # 1. Check System Status Meta (New Feature)
    sys_stat = res.get("System_Status", {})
    if sys_stat.get("workflow_id") != wf_id:
        issues.append(f"System_Status missing correct workflow_id. Found: {sys_stat.get('workflow_id')}")
    if not sys_stat.get("workflow_name"):
        issues.append("System_Status missing workflow_name")

    # 2. Check Judge Data Availability
    is_cognitive = "cognitive" in wf_id
    is_dual = "dual" in wf_id

    has_cog = "step_judge_cognitive" in raw

    if (is_cognitive or is_dual) and not has_cog:
        issues.append(
            f"Missing 'step_judge_cognitive' in Raw_Steps for cognitive/dual workflow. Found keys: {list(raw.keys())}"
        )

    if (not is_cognitive and not is_dual) and has_cog:
        issues.append("Unexpected 'step_judge_cognitive' in standard workflow")

    # 3. Check Scores
    scores = res.get("Report", {}).get("scores", {})
    if not scores:
        issues.append("Missing scores in Report")

    return issues


# --- MAIN ---


def main():
    """Run integration tests."""
    sys.stdout.reconfigure(encoding="utf-8")
    print("🚀 STARTING INTEGRATION TEST: Dual & Cognitive Workflows")
    print(f"Backend: {BASE_URL}")
    print("-" * 60)

    results = {}
    all_passed = True

    for wf_id in WORKFLOWS_TO_TEST:
        print(f"Testing {wf_id}...", end=" ", flush=True)

        exec_id = trigger_workflow(wf_id)
        if not exec_id:
            print("FAILED TO START")
            results[wf_id] = ["Start failure"]
            all_passed = False
            continue

        final_data = wait_for_completion(exec_id)
        if not final_data:
            print("TIMEOUT")
            results[wf_id] = ["Timeout"]
            all_passed = False
            continue

        issues = verify_result(wf_id, final_data)

        if not issues:
            print("PASS ✅")
            results[wf_id] = []
        else:
            print("FAIL ❌")
            for i in issues:
                print(f"  - {i}")
            results[wf_id] = issues
            all_passed = False

    print("-" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
