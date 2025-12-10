import requests
import json
import sys

API_URL = "http://localhost:8000"
STEP_ID = "STEP_1_GUARD"

def run_verification():
    print(f"--- 1. Fetching current configuration for {STEP_ID} ---")
    try:
        res = requests.get(f"{API_URL}/config/steps")
        if res.status_code != 200:
            print(f"Error fetching steps: {res.text}")
            return
        
        steps = res.json()
        target_step = next((s for s in steps if s['id'] == STEP_ID), None)
        
        if not target_step:
            print(f"Step {STEP_ID} not found!")
            return

        original_desc = target_step.get('description', '')
        print(f"Original Description: '{original_desc}'")
        
        # 2. Modify Description
        print(f"\n--- 2. Modifying Description ---")
        new_desc = original_desc + " [TESTI-VERIFICATION]"
        target_step['description'] = new_desc
        
        # We need to send the full step object for update
        res = requests.put(f"{API_URL}/config/steps/{STEP_ID}", json=target_step)
        if res.status_code == 200:
            print("Update successful!")
        else:
            print(f"Update failed: {res.text}")
            return

        # 3. Verify Update
        print(f"\n--- 3. Verifying Update from Backend ---")
        res = requests.get(f"{API_URL}/config/steps")
        steps = res.json()
        updated_step = next((s for s in steps if s['id'] == STEP_ID), None)
        
        current_desc = updated_step.get('description', '')
        print(f"Current Description: '{current_desc}'")
        
        if "[TESTI-VERIFICATION]" in current_desc:
            print("✅ SUCCESS: The backend returned the modified description.")
        else:
            print("❌ FAILURE: The backend did not return the modified description.")

        # 4. Revert Change
        print(f"\n--- 4. Reverting Change ---")
        target_step['description'] = original_desc
        res = requests.put(f"{API_URL}/config/steps/{STEP_ID}", json=target_step)
        
        if res.status_code == 200:
            print("Revert successful!")
        else:
            print(f"Revert failed: {res.text}")

        # Final Check
        res = requests.get(f"{API_URL}/config/steps")
        steps = res.json()
        final_step = next((s for s in steps if s['id'] == STEP_ID), None)
        print(f"Final Description: '{final_step.get('description', '')}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_verification()
