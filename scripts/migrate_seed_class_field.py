
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SEED_FILE = PROJECT_ROOT / "backend" / "seed" / "seed_data.json"

def migrate_components():
    print(f"Reading seed file: {SEED_FILE}")
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading seed file: {e}")
        sys.exit(1)

    components = data.get("components", [])
    print(f"Scanning {len(components)} components for 'class' field...")
    
    migrated_count = 0
    
    for item in components:
        # Check for 'class' -> 'component_class'
        if "class" in item:
            # If both exist, warn and prefer 'class' (source of truth from seed) or just move it?
            if "component_class" in item:
                 print(f"Warning: Item {item.get('id')} has BOTH 'class' and 'component_class'. Overwriting 'component_class' with 'class'.")
            
            item["component_class"] = item.pop("class")
            migrated_count += 1

    if migrated_count > 0:
        print(f"Migrated {migrated_count} components.")
        try:
            with open(SEED_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Successfully saved {SEED_FILE}")
        except Exception as e:
            print(f"Error saving file: {e}")
            sys.exit(1)
    else:
        print("No components needed migration.")

if __name__ == "__main__":
    migrate_components()
