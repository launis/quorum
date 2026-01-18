import json
import argparse
import sys
from pathlib import Path

def analyze_json(file_path: str, search_key: str = None, list_keys: bool = False):
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    try:
        # Robust encoding handling
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="utf-16") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to decode file with UTF-8 or UTF-16: {e}")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        sys.exit(1)

    print(f"File: {path.name}")
    print(f"Size: {path.stat().st_size / 1024:.2f} KB")

    if isinstance(data, dict):
        keys = list(data.keys())
        print(f"Top-level keys ({len(keys)}): {keys}")
        
        if search_key:
            if search_key in data:
                val = data[search_key]
                print(f"\n[FOUND] Key '{search_key}' exists.")
                if isinstance(val, list):
                    print(f"Type: List, Count: {len(val)}")
                    # Sample first few items if they have 'id' or 'name'
                    for i, item in enumerate(val[:5]):
                        if isinstance(item, dict):
                            ident = item.get('id') or item.get('name') or "No ID"
                            print(f"  - [{i}] {ident}")
                else:
                    print(f"Type: {type(val).__name__}, Value: (complex/large)")
            else:
                print(f"\n[MISSING] Key '{search_key}' NOT found in top-level.")
                # Optional: Recursive search could go here
    else:
        print("Root element is a List, not a Dict.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable JSON Inspector for Windows/PowerShell")
    parser.add_argument("file", help="Path to JSON file")
    parser.add_argument("--key", help="Check for specific key and summarize it", default=None)
    args = parser.parse_args()

    analyze_json(args.file, args.key)
