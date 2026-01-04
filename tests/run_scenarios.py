import os
import requests
import time
import json

BACKEND_URL = "http://localhost:8000"
SCENARIOS_DIR = "tests/scenarios"
WORKFLOW_ID = "HOLISTINEN_MESTARUUS_3"

def run_scenario(category, filename):
    filepath = os.path.join(SCENARIOS_DIR, category, filename)
    print(f"\n--- Running Scenario: {category}/{filename} ---")
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # For simplicity, we use the same file for all 3 inputs to test the specific content
    # In a real test, we might mix and match.
    files = {
        "history_file": (filename, open(filepath, "rb"), "text/plain"),
        "product_file": (filename, open(filepath, "rb"), "text/plain"),
        "reflection_file": (filename, open(filepath, "rb"), "text/plain")
    }

    try:
        # Start Job
        response = requests.post(
            f"{BACKEND_URL}/orchestrator/run",
            params={"workflow_id": WORKFLOW_ID},
            files=files
        )
        
        if response.status_code != 200:
            print(f"Failed to start job: {response.status_code} - {response.text}")
            return

        job_id = response.json()['job_id']
        print(f"Job Started: {job_id}")

        # Poll for completion
        while True:
            status_res = requests.get(f"{BACKEND_URL}/orchestrator/status/{job_id}")
            if status_res.status_code == 200:
                status_data = status_res.json()
                status = status_data.get('status')
                
                if status in ["COMPLETED", "FAILED"]:
                    print(f"Job Finished with status: {status}")
                    if status == "FAILED":
                        print(f"Error: {status_data.get('error')}")
                    else:
                        # Check for specific outcomes based on scenario
                        result = status_data.get('result', {})
                        xai = result.get('xai_report')
                        
                        # Simple assertion logic
                        if category == "rule_violations":
                            if "prompt_injection" in filename:
                                # We expect the GuardAgent to have caught this or the model to refuse
                                print("Verifying Prompt Injection handling...")
                                # In a real test, we'd check the GuardAgent logs or specific flags
                                # For now, just printing the result summary is enough for manual verification
                            elif "pii_leak" in filename:
                                print("Verifying PII handling...")
                        
                        print("Result snippet:")
                        print(str(result)[:500] + "...")
                    break
                else:
                    time.sleep(1)
            else:
                print("Failed to poll status")
                break

    except Exception as e:
        print(f"Exception: {e}")
    finally:
        # Close file handles
        for f in files.values():
            f[1].close()

def main():
    # List all scenarios
    categories = ["rule_violations", "error_models"]
    
    for category in categories:
        cat_path = os.path.join(SCENARIOS_DIR, category)
        if os.path.exists(cat_path):
            for filename in os.listdir(cat_path):
                run_scenario(category, filename)

if __name__ == "__main__":
    main()
