import json

def update_seed():
    seed_file = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for wf in data.get("workflows", []):
        if wf.get("id") == "workflow_courtroom_30_fused_dual":
            # Target the specific workflow
            step = wf["steps"][0]
            step["hook"] = "process_inputs"
            step["model_strategy"] = None
            step["matrix_ids"] = []
            step["input_mappings"] = {
                "history_text": "$inputs.history_text", 
                "product_text": "$inputs.product_text", 
                "reflection_text": "$inputs.reflection_text", 
                "guided_reflection": "$inputs.guided_reflection"
            }
            
            # Map downstream step 2 to output of step 1 hook
            wf["steps"][1]["input_mappings"] = {
                "context": "$steps.step_input_processing.history_text", 
                "document": "$steps.step_input_processing.product_text", 
                "reflection": "$steps.step_input_processing.reflection_text"
            }
            break

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print("Updated workflow_courtroom_30_fused_dual hook parameters.")

if __name__ == "__main__":
    update_seed()
