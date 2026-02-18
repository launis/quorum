
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import deepdiff  # type: ignore

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_FILE = PROJECT_ROOT / "verifier_report.txt"

def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        sys.exit(1)

def log(msg: str):
    print(msg)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def get_db_collection(db_data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    if table_name not in db_data:
        return {}
    
    table_content = db_data.get(table_name, {})
    by_id = {}
    for doc_id, record in table_content.items():
        if "id" in record:
            by_id[record["id"]] = record
        elif "uid" in record:
            by_id[record["uid"]] = record
        else:
            log(f"⚠️ Warning: Record in {table_name} (doc_id {doc_id}) has no 'id' or 'uid'. Skipping.")
            
    return by_id

def verify_collection(collection_name: str, seed_list: List[Dict[str, Any]], db_map: Dict[str, Any]) -> bool:
    log(f"\n🔍 Verifying Collection: {collection_name}")
    
    seed_ids = set()
    for item in seed_list:
        item_id = item.get("id") or item.get("uid")
        if not item_id:
            log(f"❌ Error: Seed item in {collection_name} missing 'id' or 'uid': {item}")
            return False
        seed_ids.add(item_id)
        
    db_ids = set(db_map.keys())
    
    missing = seed_ids - db_ids
    extras = db_ids - seed_ids
    
    success = True
    
    if missing:
        log(f"❌ MISSING in DB ({len(missing)}): {sorted(list(missing))}")
        success = False
        
    if extras:
        log(f"⚠️ EXTRA in DB ({len(extras)}): {sorted(list(extras))}")
        
    common = seed_ids & db_ids
    mismatches = 0
    soft_mismatches = 0
    
    for item_id in common:
        seed_item = next(i for i in seed_list if (i.get("id") == item_id or i.get("uid") == item_id))
        db_item = db_map[item_id]
        
        # Paths to exclude from strict diff
        exclude_paths = ["root['_id']", "root['doc_id']", "root['created_at']", "root['updated_at']", "root['report_generated_at']"]

        diff = deepdiff.DeepDiff(seed_item, db_item, ignore_order=True, exclude_paths=exclude_paths)
        
        if diff:
            # Analyze diff to see if it's "soft" (None vs Missing)
            is_soft = True
            hard_errors = []

            # Check for 'dictionary_item_added' (in DB but not in Seed) allowed if value is None?
            # Or 'dictionary_item_removed' (in Seed but not in DB)
            # Or 'values_changed'
            
            # Check added items (keys present in DB, missing in Seed)
            if 'dictionary_item_added' in diff:
                for path in diff['dictionary_item_added']:
                    # Extract key and check value in DB item
                    # path looks like "root['key']"
                    # We can try to access it. 
                    # Simpler: just check if it's None. If DB has None and Seed has missing, that's fine Pydantic default.
                    val = eval(f"db_item{path[4:]}", {"db_item": db_item})
                    if val is not None:
                        is_soft = False
                        hard_errors.append(f"Added key {path} with value {val} (expected missing or None)")

            if 'dictionary_item_removed' in diff:
                # Key present in Seed, missing in DB. This is usually bad unless Seed has None and DB drops it.
                for path in diff['dictionary_item_removed']:
                     val = eval(f"seed_item{path[4:]}", {"seed_item": seed_item})
                     if val is not None:
                         is_soft = False
                         hard_errors.append(f"Missing key {path} (expected {val})")

            if 'values_changed' in diff:
                for path, change in diff['values_changed'].items():
                    old_val = change['old_value'] # Seed value
                    new_val = change['new_value'] # DB value
                    # Allow formatting diffs? No.
                    is_soft = False
                    hard_errors.append(f"Value mismatch at {path}: {old_val} != {new_val}")

            if 'type_changes' in diff:
                 # e.g. int vs float?
                 for path, change in diff['type_changes'].items():
                     is_soft = False
                     hard_errors.append(f"Type mismatch at {path}: {change['old_value']} ({type(change['old_value'])}) != {change['new_value']} ({type(change['new_value'])})")

            if 'iterable_item_added' in diff or 'iterable_item_removed' in diff:
                is_soft = False
                hard_errors.append(f"List mismatch at {path}")

            if is_soft and not hard_errors:
                 soft_mismatches += 1
            else:
                 log(f"❌ MISMATCH [{item_id}]:")
                 for err in hard_errors:
                     log(f"  - {err}")
                 mismatches += 1
                 success = False
            
    if success:
        log(f"✅ OK ({len(common)} items matched, {soft_mismatches} soft mismatches ignored)")
    
    return success

def main():
    if len(sys.argv) < 3:
        print("Usage: python verifier_v2.py <seed_data.json> <db.json>")
        sys.exit(1)
        
    seed_path = Path(sys.argv[1])
    db_path = Path(sys.argv[2])
    
    # Reset report file
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Verification Report\nSEED: {seed_path}\nDB: {db_path}\n\n")

    print(f"Report will be written to: {REPORT_FILE}")
    
    seed_data = load_json(seed_path)
    db_data = load_json(db_path)
    
    collections_to_verify = [
        "system_config", 
        "steps", 
        "workflows", 
        "components", 
        "prompts",
        "organizations",
        "users",
        "dimensions",
        "knowledge_base"
    ]
    
    all_passed = True
    
    for col in collections_to_verify:
        if col not in seed_data:
            log(f"ℹ️ Skipping {col} (not in seed data)")
            continue
            
        seed_list = seed_data[col]
        db_map = get_db_collection(db_data, col)
        
        if not verify_collection(col, seed_list, db_map):
            all_passed = False
            
    if all_passed:
        log("\n🎉 VERIFICATION SUCCESS: All collections match (ignoring soft limits).")
        sys.exit(0)
    else:
        log("\n❌ VERIFICATION FAILED: See above failures.")
        sys.exit(1)

if __name__ == "__main__":
    main()
