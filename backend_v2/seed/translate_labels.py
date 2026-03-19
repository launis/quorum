import json
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def fix_label(label: str) -> str:
    # Just format it as Title Case if it's all caps, or provide specific mappings
    if label == "TOULMIN ARGUMENTATION MODEL": return "Toulmin Argumentation Model"
    if label == "BLOOM'S TAXONOMY": return "Bloom's Taxonomy"
    if label == "SITRA'S MEGA-TREND ANALYSIS": return "Sitra's Megatrend Analysis"
    
    # Generic title casing for all caps (safeguard)
    if label.isupper():
        return label.title()
    return label

def run_label_translation():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    count = 0

    for block in prompt_blocks:
        en_label = block.get("label", {}).get("translations", {}).get("en")
        if en_label:
            fixed_label = fix_label(en_label)
            if fixed_label != en_label:
                logging.info(f"Fixed: {en_label} -> {fixed_label}")
                block["label"]["translations"]["en"] = fixed_label
                count += 1
                
        # Also clean up descriptions if they have weird (EN) suffixes left over from old formatting
        en_desc = block.get("description", {}).get("translations", {}).get("en")
        if en_desc and "(EN)" in en_desc:
             fixed_desc = en_desc.replace("(EN)", "").strip()
             block["description"]["translations"]["en"] = fixed_desc

    # Save mutated data back
    if count > 0:
        logging.info(f"Saving changes. Labels fixed: {count}")
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info("Label translation complete.")

if __name__ == "__main__":
    run_label_translation()
