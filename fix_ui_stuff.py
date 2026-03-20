import json

seed_path = "backend_v2/seed/seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    if wf["id"] == "wf_d653170e174847559e08af42b938d826":
        bps = wf.get("render_blueprints", {})
        
        # 1. Fix 1D Metrics Titles
        if "1d_metrics" in bps:
            for comp in bps["1d_metrics"].get("components", []):
                if comp.get("type") == "1d_gauge" and "title" in comp:
                    # Remove the hardcoded 'Score 1' / 'Score 2'
                    del comp["title"]

        # 2. Fix Notes data_paths to not dump dicts
        # 2D Compare
        if "2d_compare" in bps:
            notes_panel = bps["2d_compare"]["components"][3]
            paths = notes_panel.get("data_paths", [])
            new_paths = []
            for p in paths:
                if "evaluation_notes" not in p and "reasoning_trace" not in p:
                     new_paths.extend([p + ".reasoning_trace", p + ".evaluation_notes"])
                else:
                     new_paths.append(p)
            notes_panel["data_paths"] = new_paths

        # 3D Complex
        if "3d_complex" in bps:
            try:
                notes_panel = bps["3d_complex"]["components"][2]["children"][1]
                paths = notes_panel.get("data_paths", [])
                new_paths = []
                for p in paths:
                    if "evaluation_notes" not in p and "reasoning_trace" not in p:
                         new_paths.extend([p + ".reasoning_trace", p + ".evaluation_notes"])
                    else:
                         new_paths.append(p)
                notes_panel["data_paths"] = new_paths
            except (KeyError, IndexError):
                pass
                
        break

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Removed hardcoded titles and fixed notes data paths!")
