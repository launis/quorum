import json
from pathlib import Path

seed_file = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
with open(seed_file, encoding="utf-8") as f:
    data = json.load(f)

targets = {
    "sp_bd0b3054fe664960": ("Causal Analyst", "strict", "standard"),
    "sp_6a45d484ad5b497c": ("Profiler", "strict", "standard"),
    "sp_7f9649114d2344dc": ("Perperformitivity Detector", "strict", "standard"),
    "sp_76eedbc020274f66": ("Fact Checker", "strict", "standard"),
    "sp_192910b5f5a34c79": ("XAI Reporter", "deep", "standard"),
}

found = 0
changes_made = 0

print("--- CURRENT STATE & PLANNED CHANGES ---")
for step in data.get("steps", []):
    sid = step.get("id")
    if sid in targets:
        found += 1
        name, new_model, new_run = targets[sid]
        old_model = step.get("model_type")
        old_run = step.get("evaluation_run_count")
        print(f"[{name}] ID: {sid}")
        print(f"  Current: model_type={old_model}, evaluation_run_count={old_run}")

        if old_model != new_model or old_run != new_run:
            print(f"  Target:  model_type={new_model}, evaluation_run_count={new_run} -> WILL UPDATE")
            step["model_type"] = new_model
            step["evaluation_run_count"] = new_run
            changes_made += 1
        else:
            print("  Target matches current state. No change needed.")

print(f"\nTotal targets found: {found} / 5")
print(f"Total changes planned: {changes_made}")

if changes_made > 0:
    print("\nApplying changes and saving...")
    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Changes saved successfully to seed_data.json.")
else:
    print("\nNo changes needed. File was not modified.")
