import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

SEED_PATH = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
BACKUP_DIR = Path("c:/src/quorum/backend_v2/seed/backups")

def main():
    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"seed_data_{timestamp}.json.bak"
    shutil.copy2(SEED_PATH, backup_path)
    print(f"Backup created at: {backup_path}")

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    mod_count = 0

    def process_tda(tda: dict):
        nonlocal mod_count
        desc = tda.get("concept_description", "")
        if not desc or "STEP 1:" not in desc:
            return

        # Preamble is anything before "STEP 1:"
        preamble_match = re.match(r"^(.*?)(?=STEP 1:)", desc, re.DOTALL | re.IGNORECASE)
        preamble = preamble_match.group(1).strip() if preamble_match else ""

        # STEP 1 to STEP 2
        step1_match = re.search(r"STEP 1:(.*?)(?=STEP 2|\Z)", desc, re.DOTALL | re.IGNORECASE)
        anchor_target = step1_match.group(1).strip() if step1_match else ""

        # STEP 2 to EXTRACTION CONDITION
        step2_match = re.search(r"STEP 2\s*\(Bounding Box\):(.*?)(?=EXTRACTION CONDITION:|\Z)", desc, re.DOTALL | re.IGNORECASE)
        bounding_box_raw = step2_match.group(1).strip() if step2_match else ""

        # EXTRACTION CONDITION
        extraction_match = re.search(r"EXTRACTION CONDITION:(.*)", desc, re.DOTALL | re.IGNORECASE)
        extraction_rule = extraction_match.group(1).strip() if extraction_match else ""

        bounding_box_scope = "paragraph"
        if "sentence" in bounding_box_raw.lower():
            bounding_box_scope = "sentence"
        elif "document" in bounding_box_raw.lower():
            bounding_box_scope = "document"

        tda["concept_description"] = preamble
        tda["anchor_target"] = anchor_target
        tda["bounding_box_scope"] = bounding_box_scope
        tda["extraction_rule"] = extraction_rule
        mod_count += 1

    if "prompt_blocks" in data:
        for block in data["prompt_blocks"]:
            scales = block.get("scales", [])
            if scales:
                for scale in scales:
                    claims = scale.get("claims", [])
                    for claim in claims:
                        tdas = claim.get("tda_assertions", [])
                        for tda in tdas:
                            process_tda(tda)

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

    print(f"Migration complete. Modified {mod_count} TDA assertions.")

if __name__ == "__main__":
    main()
