import json
from pathlib import Path

def update_seed_static_inputs():
    seed_path = Path("data/seed_data.json")
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for step in data.get("steps", []):
        if step["id"] == "step_9":
            config = step.get("execution_config", {})
            
            # Add static_inputs
            config["static_inputs"] = ["HEADER_TEXT", "DISCLAIMER_TEXT"]
            
            # Optional: Remove them from llm_prompts if you don't want LLM to see them
            # But for now, let's keep them in llm_prompts too so LLM knows context.
            # prompts = config.get("llm_prompts", [])
            # if "HEADER_TEXT" in prompts: prompts.remove("HEADER_TEXT")
            # if "DISCLAIMER_TEXT" in prompts: prompts.remove("DISCLAIMER_TEXT")
            # config["llm_prompts"] = prompts
            
            step["execution_config"] = config
            print("Updated step_9 with static_inputs.")
            break
            
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("seed_data.json updated.")

if __name__ == "__main__":
    update_seed_static_inputs()
