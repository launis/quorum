import json

def fix_reflection_text():
    file_path = "backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changes = 0

    # 1. Lisätään reflection_text TaskBlueprinteihin, joissa voisi olla sille käyttöä.
    # Kognitiiviset roolit (Analyst, Profiler, Logician, Falsifier, Causal) analysoivat myös reflektiota!
    target_blueprints = [
        "task_analyst", 
        "task_profiler", 
        "task_logician", 
        "task_falsifier", 
        "task_causal",
        "task_overseer",
        "task_judge"
    ]
    
    for bp in data.get("task_blueprints", []):
        if bp.get("id") in target_blueprints or bp.get("slug") in target_blueprints:
            params = bp.get("expected_inputs", {})
            if "reflection_text" not in params:
                params["reflection_text"] = "Optional reflection document or guided reflection."
                bp["expected_inputs"] = params
                changes += 1

    # 2. Lisätään reflection_text Workflow Noden input_mappingeihin
    for wf in data.get("workflows", []):
        for node_id, node_data in wf.get("nodes", {}).items():
            bp_ref = node_data.get("blueprint_slug")
            if bp_ref in target_blueprints:
                mappings = node_data.get("input_mappings", {})
                if "reflection_text" not in mappings:
                    # InputProcessingHook tuottaa $inputs.reflection_text
                    mappings["reflection_text"] = "$inputs.reflection_text"
                    node_data["input_mappings"] = mappings
                    changes += 1

    if changes > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ Lisätty reflection_text reititys {changes} paikkaan.")
    else:
        print("ℹ️ Ei muutettavaa, reflection_text reititykset ovat jo olemassa.")

if __name__ == "__main__":
    fix_reflection_text()
