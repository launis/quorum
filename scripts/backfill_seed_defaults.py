
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
    logger.info(f"✅ Saved updated seed data to {SEED_FILE}")

def backfill_workflow_defaults(workflows: List[Dict[str, Any]]):
    count = 0
    for wf in workflows:
        # Default status: draft
        if "status" not in wf:
            wf["status"] = "draft"
            count += 1
        
        # Default version: 1
        if "version" not in wf:
            wf["version"] = 1
            count += 1
            
        # Default scoring_logic: []
        if "scoring_logic" not in wf:
            wf["scoring_logic"] = []
            count += 1

        # Default ui_schema: {}
        if "ui_schema" not in wf:
             wf["ui_schema"] = {}
             count += 1
             
        # Normalize steps
        for step in wf.get("steps", []):
            if "hoist_keys" not in step:
                step["hoist_keys"] = []
                count += 1
            if "metadata" not in step:
                 step["metadata"] = {}
                 count += 1
            if "config" not in step:
                 step["config"] = {}
                 count += 1
            if "inputs" not in step:
                 step["inputs"] = {}
                 count += 1

    logger.info(f"Backfilled defaults for {len(workflows)} workflows (touched {count} fields).")

def backfill_step_defaults(steps: List[Dict[str, Any]]):
    count = 0
    for step in steps:
        if "inputs" not in step:
            step["inputs"] = {}
            count += 1
        if "config" not in step:
            step["config"] = {}
            count += 1
        if "hoist_keys" not in step:
            step["hoist_keys"] = []
            count += 1
        if "metadata" not in step:
            step["metadata"] = {}
            count += 1
    logger.info(f"Backfilled defaults for {len(steps)} steps.")

def backfill_system_config_defaults(sys_config: List[Dict[str, Any]]):
    # For strict parity with ConfigComponentResponse defaults
    for item in sys_config:
        if item.get("type") == "knowledge_base":
             # ConfigComponentResponse defaults
             defaults = {
                 "name": None, "description": None, "citation": None, 
                 "citation_full": None, "module": None, 
                 "component_class": None, "class_name": None, 
                 "registered_at": None
             }
             for k, v in defaults.items():
                 if k not in item:
                     item[k] = v


def main():
    if not SEED_FILE.exists():
        logger.error(f"Seed file not found: {SEED_FILE}")
        return

    data = load_seed()
    
    if "workflows" in data:
        backfill_workflow_defaults(data["workflows"])
        
    if "steps" in data:
        backfill_step_defaults(data["steps"])
        
    if "system_config" in data:
        backfill_system_config_defaults(data["system_config"])
    # Those are None defaults. My verifier handles None vs missing as Soft.
    # But checking verifier_report.txt:
    # ❌ MISMATCH [knowledge_base]: Value mismatch at root ...
    # Wait, knowledge_base in system_config is complicated.
    # It has 'content': [] vs 'content': [] (match)
    # But DB has 'name': None, 'description': None...
    # Seed has missing name/description.
    # This should be SOFT mismatch.
    # In verifier_v2.py I implemented soft check.
    # Why did it fail?
    # Because `deepdiff` reported `values_changed`? No.
    # It failed because `deepdiff` output structure was interpreted by my code as Hard.
    # I'll re-check verifier logic later. For now, focus on Hard mismatches (missing dicts/lists).
    
    save_seed(data)

if __name__ == "__main__":
    main()
