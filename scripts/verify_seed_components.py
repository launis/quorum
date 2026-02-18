
import json
import sys
from pathlib import Path
from collections import defaultdict
from pydantic import ValidationError, TypeAdapter

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.dtos.config import ComponentResponse

SEED_FILE = PROJECT_ROOT / "backend" / "seed" / "seed_data.json"

def verify_components():
    print(f"Reading seed file: {SEED_FILE}")
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading seed file: {e}")
        sys.exit(1)

    components = data.get("components", [])
    print(f"Checking {len(components)} components...")
    
    comp_adapter = TypeAdapter(ComponentResponse)
    
    error_counts = defaultdict(int)
    field_errors = defaultdict(int)
    
    failures = 0
    
    for item in components:
        try:
            comp_adapter.validate_python(item)
        except ValidationError as e:
            failures += 1
            for err in e.errors():
                # loc is tuple ('body', 'agent') etc.
                loc_str = "->".join(str(l) for l in err['loc'])
                msg = err['msg']
                typ = err['type']
                
                key = f"{typ}: {loc_str}"
                error_counts[key] += 1
                
                # If extra_forbidden, capture the specific field name
                if typ == 'extra_forbidden':
                    # loc usually points to the extra field? No, loc is where validation failed.
                    # For extra_forbidden, loc includes the field name as the last element usually?
                    # Actually, pydantic 2.x puts the extra field in loc.
                    field_errors[loc_str] += 1

    if failures > 0:
        print(f"❌ FOUND {failures} INVALID COMPONENTS")
        print("\n--- Error Summary ---")
        for key, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{key}: {count} occurrences")
            
        print("\n--- Specific Fields (Extra/Missing) ---")
        for field, count in sorted(field_errors.items(), key=lambda x: x[1], reverse=True):
            print(f"{field}: {count}")
            
        sys.exit(1)
    else:
        print("✅ All components passed validation.")
        sys.exit(0)

if __name__ == "__main__":
    verify_components()
