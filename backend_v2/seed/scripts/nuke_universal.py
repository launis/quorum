import codecs
import re
import json

SEED_FILE = "backend_v2/seed/seed_data.json"

def universal_nuke():
    print(f"Reading {SEED_FILE}...")
    with codecs.open(SEED_FILE, 'r', 'utf-8') as f:
        content = f.read()

    new_id = "prf_executive123"

    # Regex to match the old M1 profile keys like 'prf_7cc661da3f9f405c'
    pattern = r"prf_[0-9a-f]{16}"
    
    matches = set(re.findall(pattern, content))
    if not matches:
        print("No legacy hex-style profiles found.")
    else:
        print(f"Found legacy profiles to nuke: {matches}")
        for match in matches:
            content = content.replace(match, new_id)
            
        with codecs.open(SEED_FILE, 'w', 'utf-8') as f:
            f.write(content)
        print(f"✅ Replaced all legacy profile IDs with '{new_id}' in {SEED_FILE}")

if __name__ == "__main__":
    universal_nuke()
