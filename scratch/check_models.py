import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))
reg = d["system_config"][0]
models = reg["models"]

print("=== MODEL REGISTRY ===")
for k, v in models.items():
    print(f"  Strategy '{k}': {v['model_name']} | RPM={v['rpm_limit']} | temp={v['temperature']} | top_p={v.get('top_p')} | top_k={v.get('top_k')}")

# Check which steps use which model strategy
steps = d.get("steps", [])
print(f"\n=== WORKFLOW STEPS ({len(steps)} total) ===")
for s in steps:
    strategy = s.get("llm_strategy", "?")
    name = s.get("name", s.get("id", "?"))
    print(f"  Step '{name}': llm_strategy={strategy}")
