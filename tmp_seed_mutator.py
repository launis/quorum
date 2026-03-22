import json
import os
import shutil
from datetime import datetime
from collections import Counter
import sys

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"C:\src\quorum\backend_v2\seed\backups"

def main():
    # 1. Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"seed_data_backup_{timestamp}.json")
    shutil.copy2(SEED_FILE, backup_file)
    print(f"BACKUP CREATED: {backup_file}")
    
    # 2. Load the data
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_blocks = data.get("prompt_blocks", [])
    if isinstance(prompt_blocks, dict):
        raise ValueError("seed_data.json prompt_blocks is a dict, expected a list!")
        
    # Variables that constitute a "runtime_variable"
    RUNTIME_VARS = ["{CURRENT_DATE}", "{DYNAMIC_TIME}", "{DYNAMIC_LOCATION}"]
    
    # 3. Calculate BEFORE counts
    before_counts = Counter()
    for pb in prompt_blocks:
        comb = f"{pb.get('type', 'UNKNOWN')} | {pb.get('category_id', 'UNKNOWN')}"
        before_counts[comb] += 1
        
    # 4. Mutate
    mutated_ids = []
    for pb in prompt_blocks:
        desc = str(pb.get("ai_description", "")).upper()
        label = str(pb.get("label", "")).upper()
        
        # Check if it has any runtime variable
        has_runtime_var = any(var in desc for var in RUNTIME_VARS) or any(var in label for var in RUNTIME_VARS)
        
        if has_runtime_var:
            mutated_ids.append(pb.get("id"))
            pb["type"] = "instruction"
            pb["category_id"] = "runtime_variables"
            
    # 5. Calculate AFTER counts
    after_counts = Counter()
    for pb in prompt_blocks:
        comb = f"{pb.get('type', 'UNKNOWN')} | {pb.get('category_id', 'UNKNOWN')}"
        after_counts[comb] += 1
        
    # 6. Verification 1: Total prompt blocks length check
    v1_success = len(prompt_blocks) == sum(before_counts.values())
    if not v1_success:
        print("VERIFICATION 1 FAILED: Total PromptBlock count mismatch.")
        sys.exit(1)
        
    # 7. Verification 2: Check that exactly mutated_ids were changed
    changed_count = 0
    with open(backup_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    old_blocks = {b["id"]: b for b in old_data["prompt_blocks"]}
    
    for new_pb in prompt_blocks:
        pb_id = new_pb["id"]
        old_pb = old_blocks[pb_id]
        if old_pb.get("category_id") != new_pb.get("category_id") or old_pb.get("type") != new_pb.get("type"):
            changed_count += 1
            if pb_id not in mutated_ids:
                print(f"VERIFICATION 2 FAILED: Block {pb_id} changed unexpectedly.")
                sys.exit(1)
                
    v2_success = changed_count == len(mutated_ids)
    if not v2_success:
        print("VERIFICATION 2 FAILED: Number of changes does not match number of targets.")
        sys.exit(1)
        
    # 8. Verification 3: Pydantic parsing test (Strict Validate)
    sys.path.insert(0, r"C:\src\quorum")
    try:
        from backend_v2.models.v2_core import PromptBlock
        for pb in prompt_blocks:
            PromptBlock(**pb)
        v3_success = True
    except Exception as e:
        v3_success = False
        print(f"VERIFICATION 3 FAILED: Pydantic Validation Error: {e}")
        sys.exit(1)
        
    # 9. Save back to seed_data.json
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    # 10. Print Report
    print("\n--- BEFORE COUNTS ---")
    for k, v in dict(before_counts).items():
        print(f"  {k}: {v}")
        
    print("\n--- AFTER COUNTS ---")
    for k, v in dict(after_counts).items():
        print(f"  {k}: {v}")
        
    print(f"\nTargeted & Mutated PromptBlock IDs: {mutated_ids}")
    
    print("\n--- VERIFICATION RESULTS ---")
    print(f"V1: Total Object Count Immutable? {'PASSED' if v1_success else 'FAILED'} (Total: {len(prompt_blocks)})")
    print(f"V2: Targeted Mutation Sovereignty? {'PASSED' if v2_success else 'FAILED'} (Only {changed_count} rows touched)")
    print(f"V3: Pydantic Schema Consistency? {'PASSED' if v3_success else 'FAILED'}")
    
if __name__ == "__main__":
    main()
