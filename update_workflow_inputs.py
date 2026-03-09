import json

def update_seed():
    seed_file = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for wf in data.get("workflows", []):
        if wf.get("id") == "workflow_courtroom_30_fused_dual":
            # 1. Update expected inputs
            wf["expected_inputs"] = {
                "history_text": "string",
                "product_text": "string",
                "reflection_text": "string",
                "guided_reflection": "object"
            }
            
            # 2. Update input mappings for steps that need them
            for step in wf.get("steps", []):
                # Update input mapping to include all 4 input fields into the XML context
                step["input_mappings"] = {
                    "history_text": "$inputs.history_text",
                    "product_text": "$inputs.product_text",
                    "reflection_text": "$inputs.reflection_text",
                    "guided_reflection": "$inputs.guided_reflection"
                }

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print("Updated workflow courtroom inputs mapping.")

if __name__ == "__main__":
    update_seed()
