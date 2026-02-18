
import json
import os

DB_PATH = r"c:\src\quorum\backend\data\db.json"
ROOT_DB_PATH = r"c:\src\quorum\data\db.json"
SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"

def analyze_json(path, label, outfile):
    outfile.write(f"\n--- ANALYZING {label} ({path}) ---\n")
    if not os.path.exists(path):
        outfile.write("File not found.\n")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        outfile.write(f"Error reading {path}: {e}\n")
        return

    if not isinstance(data, dict):
        outfile.write(f"Root is not a dict, it is {type(data)}\n")
        return

    outfile.write(f"Top-level keys: {list(data.keys())}\n")

    for key, value in data.items():
        outfile.write(f"\nCollection: '{key}'\n")
        if isinstance(value, dict):
            outfile.write(f"  Type: Dict (len={len(value)})\n")
            keys = list(value.keys())
            if keys:
                outfile.write(f"  Sample Keys: {keys[:3]}\n")
                first_key = keys[0]
                outfile.write(f"  Sample Item ({first_key}): {json.dumps(value[first_key], indent=2, ensure_ascii=False)[:500]}...\n")
        elif isinstance(value, list):
            outfile.write(f"  Type: List (len={len(value)})\n")
            if value:
                 outfile.write(f"  Sample Item: {json.dumps(value[0], indent=2, ensure_ascii=False)[:500]}...\n")
        else:
            outfile.write(f"  Type: {type(value)}\n")

if __name__ == "__main__":
    with open(r"c:\src\quorum\db_snapshot.txt", "w", encoding="utf-8") as f:
        analyze_json(DB_PATH, "PRODUCTION DB", f)
        f.write("\n" + "="*40 + "\n")
        # analyze_json(ROOT_DB_PATH, "ROOT DB", f) # Optional, can uncomment
        analyze_json(SEED_PATH, "SEED DATA", f)
