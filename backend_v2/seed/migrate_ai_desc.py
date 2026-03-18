import json
import os

SEED_FILE = r'c:\src\quorum\backend_v2\seed\seed_data.json'

def migrate_ai_description():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    workflows = data.get("workflows", [])
    count = 0
    for wf in workflows:
        expected_inputs = wf.get("expected_inputs", [])
        for inp in expected_inputs:
            ai_desc = inp.get("ai_description")
            if isinstance(ai_desc, dict):
                # Try to extract English translation
                translations = ai_desc.get("translations", {})
                en_text = translations.get("en", "")
                
                # If no english, fallback to fi
                if not en_text:
                    en_text = translations.get("fi", "")
                
                inp["ai_description"] = en_text
                count += 1
                
    if count > 0:
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully migrated {count} ai_description fields.")
    else:
        print("No ai_description fields needed migration.")

if __name__ == "__main__":
    migrate_ai_description()
