import json

def verify_claims(block_id):
    file_path = "backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for block in data.get("prompt_blocks", []):
        if block.get("id") == block_id:
            print(f"--- Verification Report for {block_id} ---")
            scales = block.get("scales", [])
            all_valid = True
            for i, scale in enumerate(scales):
                num_claims = len(scale.get("claims", []))
                print(f"Scale {scale.get('score')}: {num_claims} claims")
                if num_claims != 3:
                    all_valid = False
            
            if all_valid:
                print("\n✅ SUCCESS: All scales have exactly 3 claims (MECE Rule of 3 validated).")
            else:
                print("\n❌ FAILURE: Not all scales have exactly 3 claims.")
            return

    print(f"Block {block_id} not found.")

if __name__ == "__main__":
    verify_claims("blk_22e3598e06414409")
