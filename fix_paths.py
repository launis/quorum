import json
import os

seed_path = "backend_v2/seed/seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find WF
wf_id = "wf_d653170e174847559e08af42b938d826"
wf_index = -1
for i, wf in enumerate(data.get("workflows", [])):
    if wf["id"] == wf_id:
        wf_index = i
        break

if wf_index >= 0:
    bps = data["workflows"][wf_index].get("render_blueprints", {})
    
    # We will prepend "$results" to any path that starts with ".steprule_"
    def fix_path(path):
        if path and path.startswith(".steprule_"):
            return "$results" + path
        return path
        
    for bp_name, bp in bps.items():
        if bp_name == "default":
            continue # Default might be correct or not, let's fix it anyway
            
        for comp in bp.get("components", []):
            if "data_path" in comp:
                comp["data_path"] = fix_path(comp["data_path"])
            if "x_data_path" in comp:
                comp["x_data_path"] = fix_path(comp["x_data_path"])
            if "y_data_path" in comp:
                comp["y_data_path"] = fix_path(comp["y_data_path"])
            if "z_data_path" in comp:
                comp["z_data_path"] = fix_path(comp["z_data_path"])
            if "x_axis_note" in comp:
                comp["x_axis_note"] = fix_path(comp["x_axis_note"])
            if "y_axis_note" in comp:
                comp["y_axis_note"] = fix_path(comp["y_axis_note"])
            if "z_axis_note" in comp:
                comp["z_axis_note"] = fix_path(comp["z_axis_note"])
            
            if "data_paths" in comp and isinstance(comp["data_paths"], list):
                comp["data_paths"] = [fix_path(p) for p in comp["data_paths"]]

            if "children" in comp:
                for child in comp["children"]:
                    if "data_path" in child:
                        child["data_path"] = fix_path(child["data_path"])
                    if "x_data_path" in child:
                        child["x_data_path"] = fix_path(child["x_data_path"])
                    if "y_data_path" in child:
                        child["y_data_path"] = fix_path(child["y_data_path"])
                    if "z_data_path" in child:
                        child["z_data_path"] = fix_path(child["z_data_path"])
                    if "x_axis_note" in child:
                        child["x_axis_note"] = fix_path(child["x_axis_note"])
                    if "y_axis_note" in child:
                        child["y_axis_note"] = fix_path(child["y_axis_note"])
                    if "z_axis_note" in child:
                        child["z_axis_note"] = fix_path(child["z_axis_note"])
                    if "data_paths" in child and isinstance(child["data_paths"], list):
                        child["data_paths"] = [fix_path(p) for p in child["data_paths"]]
                        
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Fixed paths in seed_data.json!")
else:
    print("WF not found")
