
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SEED_PATH = "backend/seed/seed_data.json"

def clean_seed():
    """Removes embedded step configs to enforce SSOT."""
    logger.info("Starting Seed Cleanup for SSOT...")
    
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            seed_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Seed file not found at {SEED_PATH}")
        return

    workflows = seed_data.get("workflows", [])
    
    cleaned_count = 0
    
    for wf in workflows:
        steps = wf.get("steps", [])
        new_steps = []
        for step in steps:
            # Keep only Essential Binding References
            # ID is mandatory
            step_id = step.get("id")
            if not step_id:
                new_steps.append(step) # Skip invalid
                continue
                
            # Create Minimal Reference
            ref = {
                "id": step_id
            }
            
            # Keep bindings
            if "inputs" in step:
                ref["inputs"] = step["inputs"]
            
            if "hoist_keys" in step:
                ref["hoist_keys"] = step["hoist_keys"]

            # Note: We remove 'config', 'task_key', 'name', 'description'
            # creating a pure reference.
            
            new_steps.append(ref)
            cleaned_count += 1
            
        wf["steps"] = new_steps
        logger.info(f"Cleaned workflow '{wf.get('id')}': {len(steps)} steps converted to references.")

    # Save
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=4)
        
    logger.info("========================================")
    logger.info(f"Cleanup Complete. {cleaned_count} steps converted.")
    logger.info("========================================")

if __name__ == "__main__":
    clean_seed()
