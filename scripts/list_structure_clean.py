
import json
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"c:\src\quorum\backend\data\db.json"

def list_clean():
    print(f"--- ANALYZING STRUCTURE: {DB_PATH} ---")
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        keys = sorted(list(data.keys()))
        print(f"ROOT KEYS: {keys}")
        
        for k in keys:
            val = data[k]
            print(f"\n--- {k} ---")
            if isinstance(val, dict):
                print(f"Type: DICT, Size: {len(val)}")
                # Show first 5 keys
                subkeys = sorted(list(val.keys()))
                for sk in subkeys[:5]:
                    item = val[sk]
                    item_type = item.get("type", "N/A") if isinstance(item, dict) else type(item).__name__
                    label = item.get("label", "N/A") if isinstance(item, dict) else "N/A"
                    print(f"  [{sk}] Type: {item_type}, Label: {label}")
                if len(subkeys) > 5:
                    print(f"  ... (+{len(subkeys)-5} more)")
            elif isinstance(val, list):
                print(f"Type: LIST, Size: {len(val)}")
                for i, item in enumerate(val[:5]):
                    print(f"  [{i}] {type(item).__name__}")
                if len(val) > 5:
                    print(f"  ... (+{len(val)-5} more)")
            else:
                 print(f"Type: {type(val).__name__}, Value: {str(val)[:50]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_clean()
