import json
from pathlib import Path

def migrate_seed_data():
    seed_file = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
    
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_blocks = data.get("prompt_blocks", [])
    updated_count = 0
    
    for pb in prompt_blocks:
        scales = pb.get("scales")
        if scales and isinstance(scales, list) and len(scales) > 0:
            # According to Pydantic rules, if scales exist we must have scale_min and scale_max
            # By default we'll use 4-10
            if "scale_min" not in pb:
                pb["scale_min"] = 4
            if "scale_max" not in pb:
                pb["scale_max"] = 10
            
            # Change type to numeric if it's not (matrices need to be parsed as numbers)
            pb["type"] = "numeric"
            
            updated_count += 1
            
    if updated_count > 0:
        with open(seed_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully migrated {updated_count} PromptBlocks with scale_min/max fields.")
    else:
        print("No PromptBlocks needed migration.")

if __name__ == "__main__":
    migrate_seed_data()
