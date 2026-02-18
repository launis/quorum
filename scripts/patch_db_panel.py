import json
import os
import sys

DB_PATH = r"c:\src\quorum\data\db.json"

def patch_db():
    print(f"Reading {DB_PATH}...")
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading DB: {e}")
        sys.exit(1)

    if "components" not in data:
        print("Error: 'components' key not found in db.json")
        # Initialize if missing?
        data["components"] = {} if isinstance(data.get("knowledge_base", {}), dict) else []
        print("Initialized 'components' entry.")

    components = data["components"]
    print(f"Components type: {type(components)}")

    target_id = "PANEL_PROMPT_TEMPLATE"
    new_component = {
        "id": target_id,
        "type": "prompt",
        "content": "INPUT DATA FOR THE PANEL:\n---\n{input_json}\n---\n{context_section}\n{search_section}\n{linguistics_section}"
    }

    if isinstance(components, list):
        # List handling
        for comp in components:
            if comp.get("id") == target_id:
                print(f"{target_id} already exists in components list.")
                return
        components.append(new_component)
        print(f"Appended {target_id} to components list.")

    elif isinstance(components, dict):
        # Dict handling (TinyDB style usually)
        # Check if exists
        for key, val in components.items():
            if val.get("id") == target_id:
                print(f"{target_id} already exists in components dict (key: {key}).")
                return
        
        # Find next integer key
        # Keys are usually strings of ints "1", "2"...
        try:
            int_keys = [int(k) for k in components.keys() if k.isdigit()]
            next_id = str(max(int_keys) + 1) if int_keys else "1"
        except ValueError:
            # Fallback if keys are not ints
            next_id = str(len(components) + 1)
        
        components[next_id] = new_component
        print(f"Inserted {target_id} into components dict at key '{next_id}'.")

    else:
        print("Unknown components structure. Aborting.")
        sys.exit(1)

    print(f"Writing {DB_PATH}...")
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            # Use indent=4 for readability
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Successfully patched db.json.")
    except Exception as e:
        print(f"Error writing DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    patch_db()
