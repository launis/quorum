
import json
import os

SEED_PATH = r"backend/database/seed_data.json"

def fix_truncation():
    print(f"Reading {SEED_PATH}...")
    try:
        with open(SEED_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("UTF-8 read failed, trying UTF-16")
        with open(SEED_PATH, 'r', encoding='utf-16') as f:
            data = json.load(f)

    updates = 0
    
    # We explicitly suppress the echoing of large text fields
    # Use explicit instructions to override any previous schema hints
    overrides = {
        "TASK_GUARD": "\n\nCRITICAL OUTPUT RULE: Field 'safe_data' MUST be null/None. Do NOT output the sanitized text in the JSON.",
        "TASK_ANALYST": "\n\nCRITICAL OUTPUT RULE: Do NOT include full source documents. Use short citations only."
    }
    
    if "components" in data:
        for comp in data['components']:
            if comp.get('id') in overrides:
                msg = overrides[comp['id']]
                if msg.strip() not in comp.get('content', ''):
                    comp['content'] += msg
                    updates += 1
                    print(f"Updated {comp['id']}")

    if updates > 0:
        print("Saving seed_data.json (UTF-8)...")
        with open(SEED_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Fix applied.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    fix_truncation()
