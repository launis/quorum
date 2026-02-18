
import json

DB_PATH = r"c:\src\quorum\backend\data\db.json"

def list_structure():
    print(f"--- DB STRUCTURE ({DB_PATH}) ---")
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for key, value in data.items():
            print(f"\n[{key}]")
            if isinstance(value, dict):
                print(f"  Type: Dict, Len: {len(value)}")
                for subkey in value.keys():
                    subval = value[subkey]
                    info = ""
                    if isinstance(subval, dict):
                        info = f"(Dict, keys={list(subval.keys())})"
                        # check for knowledge markers
                        if "content" in subval or "text" in subval or "source" in subval:
                             info += " [HAS CONTENT]"
                    elif isinstance(subval, list):
                        info = f"(List, len={len(subval)})"
                    print(f"  - {subkey} {info}")
            elif isinstance(value, list):
                print(f"  Type: List, Len: {len(value)}")
                # Inspect first few items
                for i, item in enumerate(value[:5]):
                    info = ""
                    if isinstance(item, dict):
                        info = f"(Dict, keys={list(item.keys())})"
                        if "content" in item: info += " [HAS CONTENT]"
                    print(f"  - [{i}] {info}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_structure()
