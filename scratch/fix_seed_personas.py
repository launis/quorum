import json

path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

prompt_blocks = db.get("prompt_blocks", [])
updated = 0

for block in prompt_blocks:
    category = block.get("category_id", "")
    block_id = block.get("id", "")
    
    # Reset all to DETERMINISTIC_PARSER by default to fix the coaching bug
    if "execution_persona" in block:
        block["execution_persona"] = "DETERMINISTIC_PARSER"
    
    label_dict = block.get("label", {})
    translations = label_dict.get("translations", {}) if isinstance(label_dict, dict) else {}
    label_str = json.dumps(translations).lower()
    
    if "reporter" in label_str or "xai" in label_str:
        block["execution_persona"] = "XAI_REPORTER"
        print(f"Set XAI_REPORTER for {block_id}: {label_str}")
        updated += 1
    elif "coach" in label_str:
        block["execution_persona"] = "COACH"
        print(f"Set COACH for {block_id}: {label_str}")
        updated += 1
    elif category != "matrix":
        # If it's not a matrix, let's see if it's an instruction block that should be GENERATIVE_ASSISTANT
        if "instruction" in category:
            block["execution_persona"] = "GENERATIVE_ASSISTANT"
            print(f"Set GENERATIVE_ASSISTANT for {block_id}: {label_str}")
            updated += 1

if updated >= 0:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Saved seed_data.json. Fixed Personas.")
