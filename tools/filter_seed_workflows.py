import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

SEED_FILE = r"C:\src\quorum\backend\seed\seed_data.json"

def filter_workflows():
    if not os.path.exists(SEED_FILE):
        logging.error(f"Seed file not found at {SEED_FILE}")
        return

    try:
        logging.info(f"Reading {SEED_FILE}...")
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        workflows = data.get("workflows", [])
        initial_count = len(workflows)
        
        # Filter Logic: Starts with "COURTROOM" (case-insensitive)
        filtered_workflows = [
            wf for wf in workflows 
            if wf.get("name", "").strip().upper().startswith("COURTROOM")
        ]
        
        final_count = len(filtered_workflows)
        logging.info(f"Filtered workflows from {initial_count} to {final_count}.")

        # Update data
        data["workflows"] = filtered_workflows

        logging.info(f"Writing back to {SEED_FILE}...")
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logging.info("Done.")
        
        # Print remaining workflow names for verification
        print("\nRemaining Workflows:")
        for wf in filtered_workflows:
            print(f"- {wf.get('name')}")

    except Exception as e:
        logging.error(f"Failed to filter workflows: {e}")

if __name__ == "__main__":
    filter_workflows()
