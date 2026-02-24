import json

def fix_seed_data():
    path = "c:/src/quorum/backend/seed/seed_data.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    wfs = data.get("workflows", [])
    steps = data.setdefault("steps", [])
    
    # Track existing step IDs to avoid duplicates
    existing_step_ids = {s.get("id") for s in steps}
    
    added = 0
    for wf in wfs:
        wf_steps = wf.get("steps", [])
        for i, s in enumerate(wf_steps):
            if isinstance(s, dict):
                sid = s.get("id")
                if sid not in existing_step_ids:
                    steps.append(s)
                    existing_step_ids.add(sid)
                    added += 1
                # Replace the full dict with just the ID string in the workflow
                wf_steps[i] = sid

    print(f"Added {added} nested steps to root 'steps' collection.")
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    fix_seed_data()
