import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

target_ids = [
    "matrix_analyst",
    "matrix_coach",
    "matrix_guard",
    "matrix_logician",
    "matrix_overseer",
    "matrix_profiler",
    "block_oprule4",
    "block_protocol1"
]

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block["id"] in target_ids:
        print(f"========== {block['id']} ==========")
        # Print basic info
        print(f"Type: {block.get('type')}")
        print(f"Description (FI): {block.get('description', {}).get('translations', {}).get('fi')}")
        
        # Print claims if it's a matrix to see what the logic was
        if "scales" in block:
            for scale in block["scales"]:
                score = scale.get("score")
                name = scale.get("name", {}).get("translations", {}).get("fi", "N/A")
                print(f"  Score {score}: {name}")
                for claim in scale.get("claims", []):
                    print(f"    - {claim.get('translations', {}).get('fi')}")
                    
        print("\n" + "="*50 + "\n")
