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
    print("Triggering dart E2E simulation to push inputs via REST API...")
    os.chdir(r"c:\src\quorum\client_app_v2")
    # We use flutter test to run the client simulation without needing a GUI driver
    res = subprocess.run(["flutter", "test", "test/e2e_client_test.dart"], capture_output=True, text=True, shell=True)
    os.chdir(r"c:\src\quorum")
    print(res.stdout)
    if res.returncode != 0:
        print("Dart test failed!")
        print(res.stderr)
        sys.exit(1)

for i in range(2):
    print(f"\n=== RUN {i+1} ===")
    print("Cleaning up old services...")
    subprocess.run([r"c:\src\quorum\kill_services.bat"], capture_output=True, shell=True)

    print("Starting run_local.bat...")
    # creationflags=subprocess.CREATE_NEW_CONSOLE allows it to spawn detached windows just like a user double-clicking it
    p = subprocess.Popen([r"c:\src\quorum\run_local.bat"], creationflags=subprocess.CREATE_NEW_CONSOLE)

    print("Waiting for backend to become responsive...")
    if not check_backend():
        print("Backend failed to start!")
        sys.exit(1)

    # Wait extra time for the worker to fully boot up and connect to Redis
    time.sleep(10)

    trigger_execution()

    print("Polling database for execution completion (max 15 mins)...")
    db_path = r"c:\src\quorum\data\db_v2.json"
    timeout = 900
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
subprocess.run([r"c:\src\quorum\kill_services.bat"], capture_output=True, shell=True)

print("\n=== RUNNING DIFF EXECUTIONS ===")
res = subprocess.run(["uv", "run", "python", r"c:\src\quorum\scratch\diff_executions.py"], capture_output=True, text=True, shell=True)
print(res.stdout)
if res.stderr:
    print("STDERR:")
    print(res.stderr)
