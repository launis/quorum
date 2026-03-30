import json
import re
import sys
from pathlib import Path

def main():
    seed_file = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    if not seed_file.exists():
        print("seed_data.json not found")
        sys.exit(1)
        
    try:
        data = json.loads(seed_file.read_text(encoding='utf-8'))
    except UnicodeError:
        data = json.loads(seed_file.read_text(encoding='utf-16le'))
        
    prefixes = set()
    invalid_prefixes = set()
    
    def traverse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    # Check if it looks like an opaque ID: "letters_alphanumeric"
                    match = re.match(r"^([a-z]+)_[a-zA-Z0-9]{6,}$", v)
                    if match:
                        prefix = match.group(1)
                        prefixes.add(prefix)
                        if len(prefix) > 5 or len(prefix) < 2:
                            invalid_prefixes.add(prefix)
                else:
                    traverse(v)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)
                
    traverse(data)
    
    print("--- OPAQUE ID PREFIX ANALYSIS ---")
    print(f"Total unique prefixes found: {len(prefixes)}")
    print(f"All prefixes: {sorted(list(prefixes))}")
    print("\nViolations to the 2-5 character limit mandate:")
    if not invalid_prefixes:
        print("  None! All prefixes are 2-5 characters.")
    else:
        for p in sorted(list(invalid_prefixes)):
            print(f"  - {p}_ (Length: {len(p)})")
            
if __name__ == '__main__':
    main()
