
import json
import logging

from tinydb import Query, TinyDB

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "data/db.json"  # Correct path found via find_by_name
SEED_PATH = "backend/seed/seed_data.json"

def migrate():
    """Extracts steps from workflows and saves them to the 'steps' table."""
    logger.info("Starting migration...")

    # 1. Load Seed Data (Source of Truth for defaults) or DB
    # We'll read from SEED for safety to populate the Registry.
    try:
        with open(SEED_PATH, encoding="utf-8") as f:
            seed_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Seed file not found at {SEED_PATH}")
        return

    workflows = seed_data.get("workflows", [])
    logger.info(f"Found {len(workflows)} workflows to process.")

    # 2. Open Database
    db = TinyDB(DB_PATH)
    steps_table = db.table("steps")
    Step = Query()

    extracted_count = 0
    skipped_count = 0

    for wf in workflows:
        wf_steps = wf.get("steps", [])
        wf_id = wf.get("id")
        logger.info(f"Processing workflow '{wf_id}' ({len(wf_steps)} steps)...")

        for step in wf_steps:
            step_id = step.get("id")
            if not step_id:
                logger.warning(f"Skipping step without ID in workflow {wf_id}")
                continue

            # Check if exists
            if steps_table.contains(Step.id == step_id):
                logger.info(f"Step '{step_id}' already exists. Skipping.")
                skipped_count += 1
                continue

            # Prepare Step Record
            # We enforce the schema from backend/api/routes/config/steps.py
            step_record = {
                "id": step_id,
                "name": step.get("name") or step.get("id"), # Fallback name
                "description": step.get("description") or f"Imported from {wf_id}",
                "task_key": step.get("task_key", "analyst"),
                "config": step.get("config", {}),
                "inputs": step.get("inputs", {}) # Save inputs too for reference
            }

            # Insert
            steps_table.insert(step_record)
            extracted_count += 1
            logger.info(f"Imported step '{step_id}'.")

    logger.info("========================================")
    logger.info("Migration Complete.")
    logger.info(f"Extracted: {extracted_count}")
    logger.info(f"Skipped:   {skipped_count}")
    logger.info(f"Total Steps in Registry: {len(steps_table.all())}")
    logger.info("========================================")

if __name__ == "__main__":
    migrate()
