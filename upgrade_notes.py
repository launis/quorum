import json

seed_path = "backend_v2/seed/seed_data.json"
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    if wf["id"] == "wf_d653170e174847559e08af42b938d826":
        bps = wf.get("render_blueprints", {})
        
        if "2d_compare" in bps:
            for comp in bps["2d_compare"].get("components", []):
                if comp.get("type") == "notes":
                    comp["type"] = "evaluation_notes_panel"
                    
        if "3d_complex" in bps:
            for comp in bps["3d_complex"].get("components", []):
                if comp.get("type") == "grid_row":
                    for child in comp.get("children", []):
                        if child.get("type") == "notes":
                            child["type"] = "evaluation_notes_panel"
                            

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Changed 'notes' to 'evaluation_notes_panel' in seed data!")
