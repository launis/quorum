import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def categorize_blocks():
    logging.info(f"Loading data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for block in data.get("prompt_blocks", []):
        slug = block.get("slug", "")

        # 1. MATRICES
        if slug.startswith("matrix_") or "scales" in block:
            block["category_id"] = "matrix"
            block["type"] = "float"
            block["allow_decimals"] = True
            block["require_justification"] = True

        # 2. AGENT ROLES
        elif slug.startswith("block_role_"):
            block["category_id"] = "agent_role"
            block["type"] = "instruction"
            block["allow_decimals"] = False
            block["require_justification"] = False

        # 3. TASK DEFINITIONS
        elif slug.startswith("block_task"):
            block["category_id"] = "task_definition"
            block["type"] = "string"
            block["allow_decimals"] = False
            block["require_justification"] = False

        # 4. PROTOCOLS
        elif slug.startswith("block_protocol_") or slug.startswith("block_instruction_"):
            block["category_id"] = "protocol"
            block["type"] = "instruction"
            block["allow_decimals"] = False
            block["require_justification"] = False

        # 5. SYSTEM RULES (Catch-all for heuristics, mandates, headers, oprules, rules)
        else:
            block["category_id"] = "system_rule"
            block["type"] = "instruction"
            block["allow_decimals"] = False
            block["require_justification"] = False

        count += 1

    if count > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Successfully re-categorized all {count} blocks.")
    else:
        logging.info("No blocks found.")

if __name__ == "__main__":
    categorize_blocks()
