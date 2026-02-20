
import json
import os

DB_PATH = "c:/src/quorum/data/db.json"

def patch_db():
    print(f"Reading {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("File not found!")
        return

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "system_config" not in data:
        print("No system_config table found.")
        return

    sys_conf = data["system_config"]
    registry_doc = None
    registry_key = None

    # Find model_registry document
    for k, v in sys_conf.items():
        if v.get("id") == "model_registry":
            registry_doc = v
            registry_key = k
            break
            
    if not registry_doc:
        print("No model_registry document found in system_config.")
        return

    print("Found model_registry. Patching models...")
    
    models_map = registry_doc.get("models", {})
    patched_count = 0
    
    for provider, strategies in models_map.items():
        print(f"Processing provider: {provider}")
        for strategy, config in strategies.items():
            # Config can be a string (alias) or dict
            if isinstance(config, dict):
                updated = False
                if "tpm_limit" not in config:
                    config["tpm_limit"] = 1000000 # 1M TPM
                    updated = True
                if "rpm_limit" not in config:
                    config["rpm_limit"] = 1000 # 1000 RPM
                    updated = True
                
                if updated:
                    patched_count += 1
                    # print(f"  Patched {strategy}")
            elif isinstance(config, str):
                # Convert string alias to dict to support limits?
                # Actually, AgentRegistry handles strings by resolving them.
                # But if the BASE model (the one being pointed to) has limits, it should be fine.
                # However, if the alias itself needs limits... 
                # AgentRegistry says: "Chained resolution... values from alias override base."
                # So we can leave aliases as strings, assuming the resolved model has limits.
                # But wait, if the resolved model is also an alias... eventually it hits a real model definition.
                # Real model definitions MUST have limits.
                # Let's see if we have real model definitions here.
                # Usually: "gemini-1.5-flash": { ... }
                pass

    print(f"Patched {patched_count} model configurations.")
    
    # Save back
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=None, separators=(',', ':')) # Minified
    
    print("Database updated successfully.")

if __name__ == "__main__":
    patch_db()
