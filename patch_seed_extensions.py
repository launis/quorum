import json
import os

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

print(f"Reading {seed_path}...")
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Mapping of matrix IDs to their specific output_extensions
matrix_extensions = {
    "matrix_kahneman": ["justification", "falsification", "confidence"],
    "matrix_goodhart": ["justification", "risk_flag", "theory_link"],
    "matrix_archivist": ["justification", "citation", "missing_context"],
    "matrix_causal_analyst": ["justification", "falsification", "remediation_steps"],
    "matrix_falsifier": ["justification", "falsification", "theory_link"],
    "matrix_judge": ["justification", "risk_flag", "confidence"],
    "matrix_xai_reporter": ["justification", "missing_context", "confidence"]
}

# Default minimal extensions for any other evaluative block that might need them
default_minimal = ["justification", "confidence"]

updated_count = 0
for block in data.get("prompt_blocks", []):
    block_id = block.get("id", "")
    if block_id in matrix_extensions:
        block["output_extensions"] = matrix_extensions[block_id]
        updated_count += 1
        print(f"Updated {block_id} with {block['output_extensions']}")
    elif "matrix" in block.get("category_id", "") or block_id.startswith("matrix_"):
        # Fallback for any matrix not explicitly mapped
        block["output_extensions"] = default_minimal
        updated_count += 1
        print(f"Updated FALLBACK {block_id} with {block['output_extensions']}")

print(f"\nUpdating {updated_count} PromptBlocks with refined matrix-specific output_extensions...")

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nSeeding required. Please run the seed command manually:")
print("uv run python backend_v2\\seed\\run_seed.py")
