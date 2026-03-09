import json

def update_seed():
    seed_file = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for config in data.get("system_config", []):
        if config.get("id") == "model_registry":
            models_dict = config.get("models", {})
            models_dict["chat_parser"] = {
                "provider": "gemini",
                "model_name": "gemini-2.5-flash",
                "max_tokens": 4096,
                "temperature": 0.1
            }
            print("Added chat_parser to model registry.")
            break

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    update_seed()
