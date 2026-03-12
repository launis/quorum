import json
from pathlib import Path

def fix_migration():
    seed_file = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
    
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_blocks = data.get("prompt_blocks", [])
    updated_count = 0
    
    for pb in prompt_blocks:
        if pb.get("type") == "numeric":
            pb["type"] = "float" # Valid Enum Value
            updated_count += 1
            
    if updated_count > 0:
        with open(seed_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully fixed {updated_count} PromptBlocks.")
    else:
        print("No PromptBlocks needed fixing.")

if __name__ == "__main__":
    fix_migration()
