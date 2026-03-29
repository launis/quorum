import json
import os
import shutil

f = "backend_v2/seed/seed_data.json"
backup_dir = "backend_v2/seed/backups"
os.makedirs(backup_dir, exist_ok=True)
shutil.copy(f, f"{backup_dir}/seed_data.backup_before_strategies.json")

with open(f, encoding="utf-8") as fh:
    data = json.load(fh)

mapping = {
    "step_fact_checker": "search",
    "step_causal_analyst": "precise",
    "step_coach": "deep",
    "step_performativity_detector": "strict",
    "step_falsifier": "deep",
    "step_guard": "strict",
    "step_judge": "precise",
    "step_logician": "strict",
    "step_overseer": "precise",
    "step_profiler": "precise",
    "step_xai_reporter": "deep",
}

for step in data.get("steps", []):
    if step.get("type") == "llm":
        slug = step.get("slug")
        if slug in mapping:
            step["model_strategy"] = mapping[slug]

with open(f, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)

print("--- STEP STRATEGIES APPLIED ---")
for step in data.get("steps", []):
    if step.get("type") == "llm":
        print(f"{step.get('slug')}: {step.get('model_strategy')}")
