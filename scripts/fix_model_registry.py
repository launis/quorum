import json
import os

def fix_db(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    registry = None
    # Locate model_registry in system_config
    if isinstance(data.get("system_config"), list):
        # seed_data.json format (list)
        registry = next((x for x in data["system_config"] if x.get("type") == "model_registry"), None)
    elif isinstance(data.get("system_config"), dict):
         # db.json format (dict of dicts)
         registry = next((x for x in data["system_config"].values() if x.get("type") == "model_registry"), None)
    
    if not registry:
        print(f"No model_registry in {path}")
        return

    models = registry.get("models", {})
    # Should be {'google': {'deep': ..., 'fast': ...}}
    
    for provider, strategies in models.items():
        # Add agent mappings pointing to 'deep'
        new_mappings = {
            "AnalystAgent": "deep",
            "InteractionAnalystAgent": "deep",
            "ProfilerAgent": "deep",
            "LogicianAgent": "deep",
            "LogicalFalsifierAgent": "deep",
            "CausalAnalystAgent": "deep",
            "PerformativityDetectorAgent": "deep",
            "FactualOverseerAgent": "deep",
            "ArchivistAgent": "deep",
            "JudgeAgent": "deep",
            "CoachAgent": "deep",
            "XAIReporterAgent": "deep",
            "PanelAgent": "deep",
            "GuardAgent": "fast"
        }
        
        for agent, strategy in new_mappings.items():
            # Only add if missing to avoid overwriting custom configs? 
            # Actually, we want to ensure they exist.
            if agent not in strategies:
                strategies[agent] = strategy
                print(f"Added {agent} -> {strategy} to {path}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Updated {path}")

if __name__ == "__main__":
    fix_db('backend/seed/seed_data.json')
    fix_db('data/db.json')
