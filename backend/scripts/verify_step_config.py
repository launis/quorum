import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_step_config():
    db_path = "data/db.json"
    if not os.path.exists(db_path):
        logger.error(f"DB file not found at {db_path}")
        return

    try:
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read DB: {e}")
        return

    # Inspect structure
    workflows = data.get("workflows", {}) # Seeder likely puts definitions here?
    # Or in 'workflow_definitions'?
    # Let's check common keys.

    # Actually, the 'steps' are inside the workflow definition.
    # Where are workflow definitions stored?
    # Usually in a table called 'workflows' or 'workflow_definitions'.

    # Let's search recursively for "step_analyst"

    found = False

    def search_recursive(obj, path=""):
        nonlocal found
        if isinstance(obj, dict):
            if obj.get("id") == "step_analyst":
                logger.info(f"FOUND step_analyst at {path}")
                config = obj.get("config", {})
                pre_hooks = config.get("pre_hooks", [])
                logger.info(f"  Pre-Hooks: {pre_hooks}")
                found = True

            for k, v in obj.items():
                search_recursive(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_recursive(item, f"{path}[{i}]")

    search_recursive(data)

    if not found:
        logger.warning("step_analyst NOT FOUND in db.json")

if __name__ == "__main__":
    check_step_config()
