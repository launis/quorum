import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def purge_strictness_block():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    TARGET_ID = "blk_b43b4976fc97467dad0a5187a817a9c2"

    blocks = data.get("prompt_blocks", [])
    original_block_count = len(blocks)

    # Remove from prompt_blocks
    data["prompt_blocks"] = [b for b in blocks if b.get("id") != TARGET_ID and b.get("slug") != "block_instruction_strictness"]

    removed_count = original_block_count - len(data["prompt_blocks"])
    if removed_count > 0:
        logging.info(f"Removed {removed_count} prompt block(s) matching the target ID or slug.")

    # Remove references from steps
    steps_updated = 0
    for step in data.get("steps", []):
        ids = step.get("prompt_blocks_ids", [])
        if TARGET_ID in ids:
            ids.remove(TARGET_ID)
            steps_updated += 1

    if steps_updated > 0:
        logging.info(f"Removed {TARGET_ID} from prompt_blocks_ids in {steps_updated} step(s).")

    # Remove from workflows (if they hold direct references)
    workflows_updated = 0
    for wf in data.get("workflows", []):
        g_ids = wf.get("global_prompt_blocks", [])
        if TARGET_ID in g_ids:
            g_ids.remove(TARGET_ID)
            workflows_updated += 1

    if workflows_updated > 0:
        logging.info(f"Removed {TARGET_ID} from global_prompt_blocks in {workflows_updated} workflow(s).")

    if removed_count > 0 or steps_updated > 0 or workflows_updated > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("Purge complete. Seed data updated.")
    else:
        logging.info("Target ID not found anywhere. No changes made.")

if __name__ == "__main__":
    purge_strictness_block()
