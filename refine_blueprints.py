import json

seed_path = "backend_v2/seed/seed_data.json"
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    if wf["id"] == "wf_d653170e174847559e08af42b938d826":
        bps = wf.get("render_blueprints", {})
        
        # 1. 2D Compare: Remove the notes panel entirely!
        if "2d_compare" in bps:
            comps = bps["2d_compare"].get("components", [])
            # Filter out any notes or evaluation_notes_panel components
            bps["2d_compare"]["components"] = [
                c for c in comps if c.get("type") not in ("notes", "evaluation_notes_panel")
            ]
                    
        # 2. 3D Complex: Clean up the notes panel (keep only evaluation_notes, change type)
        if "3d_complex" in bps:
            for comp in bps["3d_complex"].get("components", []):
                if comp.get("type") == "grid_row":
                    # The second child is the notes panel!
                    children = comp.get("children", [])
                    if len(children) > 1:
                        notes_panel = children[1]
                        if notes_panel.get("type") in ("notes", "evaluation_notes_panel"):
                            notes_panel["type"] = "evaluation_notes_panel"
                            # Keep ONLY paths that end with .evaluation_notes
                            paths = notes_panel.get("data_paths", [])
                            clean_paths = [p for p in paths if not p.endswith(".reasoning_trace")]
                            # Ensure we don't have raw strings anymore either
                            final_paths = []
                            for cp in clean_paths:
                                if not cp.endswith(".evaluation_notes"):
                                    final_paths.append(cp + ".evaluation_notes")
                                else:
                                    final_paths.append(cp)
                            notes_panel["data_paths"] = final_paths
                            
                            # Also clear its title if any, so jinja template can decide or it just defaults
                            if "title" in notes_panel:
                                del notes_panel["title"]

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Blueprint UI layouts refined successfully!")
