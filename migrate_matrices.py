import json
import os
import shutil
from datetime import datetime
import sys

sys.path.append(r"c:\src\quorum")
from backend_v2.models.v2_core import PromptBlock

def run_migration():
    seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
    backup_dir = r"c:\src\quorum\backend_v2\seed\backups"

    print("Loading seed_data.json...")
    with open(seed_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    modified_count = 0
    matrix_ids = []

    for prompt in db.get("prompt_blocks", []):
        is_matrix = prompt.get("category_id") == "matrix" or "scales" in prompt
        if not is_matrix:
            continue
        
        matrix_ids.append(prompt.get("id"))

        # Migrate Rows
        if "rows" in prompt and isinstance(prompt["rows"], list):
            new_rows = []
            for r in prompt["rows"]:
                if isinstance(r, dict) and "label" in r and "ai_description" in r:
                    new_rows.append(r)
                else:
                    new_rows.append({
                        "label": r,
                        "ai_description": "CRITICAL MANDATE: Evaluate this specific row dimension strictly based on empirical evidence."
                    })
            prompt["rows"] = new_rows
        
        # Migrate Scales & Claims
        if "scales" in prompt and isinstance(prompt["scales"], list):
            for scale in prompt["scales"]:
                old_desc = scale.get("ai_description", "CRITICAL EVALUATION DIRECTIVE: Strict adherence required.")
                
                new_claims = []
                for claim in scale.get("claims", []):
                    if isinstance(claim, dict) and "label" in claim and "ai_description" in claim:
                        new_claims.append(claim)
                    else:
                        new_claims.append({
                            "label": claim,
                            "ai_description": old_desc
                        })
                
                scale["claims"] = new_claims
                if "ai_description" in scale:
                    del scale["ai_description"]
        
        modified_count += 1
        
        # PRE-FLIGHT VALIDATION
        try:
            PromptBlock.model_validate(prompt, strict=True)
        except Exception as e:
            print(f"FAILED VALIDATION for {prompt.get('id')}:\n{e}")
            raise

    print(f"Total matrices identified and validated: {len(matrix_ids)}")
    print(f"Total modified blocks: {modified_count}")

    if modified_count == 0:
        print("Nothing to migrate!")
        return

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"seed_data_backup_{timestamp}.json")
    
    shutil.copy2(seed_path, backup_path)
    print(f"Created backup at {backup_path}")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4)
    print("Pre-flight passed. Successfully migrated seed_data.json!")

if __name__ == "__main__":
    run_migration()
