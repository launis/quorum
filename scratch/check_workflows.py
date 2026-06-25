import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))
blocks = d.get("prompt_blocks", [])
targets = {"Analyst", "Falsifier", "Logician", "Overseer", "Judge"}
print(f"Total blocks: {len(blocks)}")
for b in blocks:
    label = b.get("label", {}).get("translations", {}).get("en", "")
    if label in targets:
        print(f"Block: {label}, ID: {b.get('id')}, Strategy: {b.get('model_strategy')}")
        
    # Also check fallback if they are role names or similar
    if any(t.lower() in label.lower() for t in targets):
         print(f"Partial match: {label}, ID: {b.get('id')}, Strategy: {b.get('model_strategy')}")
