import json

def fix_seed_data():
    seed_file = "c:/src/quorum/backend_v2/seed/seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for wf in data.get("workflows", []):
        for step in wf.get("steps", []):
            if not step.get("hook"):
                if not step.get("model_strategy"):
                    step["model_strategy"] = "fast"

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print("Seed data updated.")

if __name__ == "__main__":
    fix_seed_data()
