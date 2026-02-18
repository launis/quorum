
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

# Setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = PROJECT_ROOT / "backend" / "seed" / "seed_data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_seed() -> Dict[str, Any]:
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_seed(data: Dict[str, Any]):
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"✅ Saved minimized seed data to {SEED_FILE}")

def minimize_workflow_steps(workflows: List[Dict[str, Any]]):
    count = 0
    # Fields to KEEP in workflow step references
    ALLOWED_FIELDS = {
        "id", 
        "name", 
        "description", 
        "task_key", 
        "inputs", 
        "hoist_keys", 
        "metadata"
    }
    
    for wf in workflows:
        for i, step in enumerate(wf.get("steps", [])):
            # If step has 'config', remove it unless it's a specific override?
            # User guideline: "components ... related to steps not directly to workflows"
            # Assuming strictly reference model.
            
            keys_to_remove = []
            for k in step.keys():
                if k not in ALLOWED_FIELDS:
                    keys_to_remove.append(k)
            
            if keys_to_remove:
                for k in keys_to_remove:
                    del step[k]
                count += 1
                
    logger.info(f"Minimized {len(workflows)} workflows (cleaned {count} steps).")

def main():
    if not SEED_FILE.exists():
        logger.error(f"Seed file not found: {SEED_FILE}")
        return

    data = load_seed()
    
    if "workflows" in data:
        minimize_workflow_steps(data["workflows"])
        
    save_seed(data)

if __name__ == "__main__":
    main()
