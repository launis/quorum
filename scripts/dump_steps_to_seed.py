
import json
import logging

from tinydb import TinyDB

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "data/db.json"  # Assuming Standard Local DB
SEED_PATH = "backend/seed/seed_data.json"

def dump_steps_to_seed():
    """Reads steps from DB and injects them into seed_data.json."""
    logger.info(f"Reading Steps from DB: {DB_PATH}")

    try:
        with TinyDB(DB_PATH, encoding="utf-8") as db:
            steps_table = db.table("steps")
            all_steps = steps_table.all()
    except FileNotFoundError:
        logger.error(f"Database not found at {DB_PATH}. Cannot dump steps.")
        return

    logger.info(f"Found {len(all_steps)} steps in Registry.")

    # Read Seed
    try:
        with open(SEED_PATH, encoding="utf-8") as f:
            seed_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Seed file not found at {SEED_PATH}")
        return

    # Injections
    # Remove 'doc_id' if present (TinyDB internal)
    cleaned_steps = []
    for s in all_steps:
        # Shallow copy to avoid mutating cache if any
        s_clean = s.copy()
        if "doc_id" in s_clean: # TinyDB usually doesn't put doc_id in dict unless explicitly there
             pass
        # But TinyDB .all() returns dicts.
        # Check if internal id leaked? Usually no.
        cleaned_steps.append(s_clean)

    # Sort for deterministic seed
    cleaned_steps.sort(key=lambda x: x.get("id", ""))

    seed_data["steps"] = cleaned_steps

    logger.info(f"Injecting {len(cleaned_steps)} steps into seed_data.json...")

    # Save
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=4)

    logger.info("Success. Seed data now contains top-level steps.")

if __name__ == "__main__":
    dump_steps_to_seed()
