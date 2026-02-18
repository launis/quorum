import json
import os

DB_PATH = os.path.join("data", "db.json")

def inspect_root():
    if not os.path.exists(DB_PATH):
        print(f"File not found: {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Top-level keys in db.json: {list(data.keys())}")

    if "steps" in data:
        steps = data["steps"]
        print(f"Found 'steps' collection with {len(steps)} items.")
        if "step_falsifier" in steps:
            print("Found 'step_falsifier' in global steps:")
            print(json.dumps(steps["step_falsifier"], indent=2))
        else:
            print("'step_falsifier' NOT found in global steps.")
    else:
        print("No 'steps' collection found.")

if __name__ == "__main__":
    inspect_root()
