import json
from copy import deepcopy

SEED_FILE = "backend_v2/seed/seed_data.json"
BACKUP_FILE = "backend_v2/seed/seed_data.backup.json"

MODEL_REGISTRY_SNIPPET = {
    "id": "model_registry",
    "slug": "config_model_registry",
    "type": "model_registry",
    "models": {
        "google": {
            "deep": {
                "max_tokens": 65536,
                "model_name": "vertex_ai/gemini-2.5-pro",
                "temperature": 0.5,
                "supports_grounding": True,
                "tpm_limit": 100000,
                "rpm_limit": 10,
                "parsing_mode": "GEMINI_JSON"
            },
            "fast": {
                "max_tokens": 65536,
                "model_name": "vertex_ai/gemini-2.5-flash",
                "temperature": 0.1,
                "supports_grounding": False,
                "tpm_limit": 100000,
                "rpm_limit": 15,
                "parsing_mode": "GEMINI_JSON"
            },
            "search": {
                "max_tokens": 65536,
                "model_name": "vertex_ai/gemini-2.5-flash",
                "temperature": 0.0,
                "supports_grounding": True,
                "tpm_limit": 100000,
                "rpm_limit": 15,
                "parsing_mode": "GEMINI_JSON"
            },
            "precise": {
                "max_tokens": 65536,
                "model_name": "vertex_ai/gemini-2.5-pro",
                "temperature": 0.2,
                "supports_grounding": False,
                "tpm_limit": 100000,
                "rpm_limit": 10,
                "parsing_mode": "GEMINI_JSON"
            },
            "strict": {
                "max_tokens": 65536,
                "model_name": "vertex_ai/gemini-2.5-pro",
                "temperature": 0.0,
                "supports_grounding": False,
                "tpm_limit": 100000,
                "rpm_limit": 10,
                "parsing_mode": "GEMINI_JSON"
            },
            "AnalystAgent": "fast",
            "JudgeAgent": "precise",
            "RetrievalAgent": "fast",
            "SearchHook": "search"
        }
    }
}

def count_keys(obj):
    if isinstance(obj, dict):
        count = len(obj.keys())
        for v in obj.values():
            count += count_keys(v)
        return count
    elif isinstance(obj, list):
        count = len(obj)
        for item in obj:
            count += count_keys(item)
        return count
    return 1

def main():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    old_data = deepcopy(data)
    
    # 1. Update data
    system_config = data.get("system_config", [])
    
    # Remove existing if any
    system_config = [c for c in system_config if c.get("id") != "model_registry"]
    
    # Append new snippet
    system_config.append(MODEL_REGISTRY_SNIPPET)
    data["system_config"] = system_config
    
    # 2. Write back
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    # 3. Math verification
    old_keys = count_keys(old_data)
    new_keys = count_keys(data)
    delta = new_keys - old_keys
    snippet_keys = count_keys(MODEL_REGISTRY_SNIPPET)
    
    print(f"Old Keys/Values: {old_keys}")
    print(f"New Keys/Values: {new_keys}")
    print(f"Delta: {delta}")
    print(f"Snippet Keys/Values: {snippet_keys}")
    if delta == snippet_keys:
        print("MATH VERIFICATION: SUCCESS (Delta matches expected snippet size exactly)")
    else:
        print("MATH VERIFICATION: FAILURE (Delta does not match expected snippet size)")

if __name__ == "__main__":
    main()
