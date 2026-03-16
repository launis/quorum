import json
import re
from pathlib import Path


def slugify(text: str, fallback_index: int) -> str:
    if not text:
        return f"item_{fallback_index}"
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    clean = re.sub(r'[\s-]+', '_', clean)
    return clean[:30]

def build_normalized_v2():
    v1_path = Path("c:/src/quorum/data/github_seed_data.json")
    v2_base_path = Path("c:/src/quorum/backend_v2/seed/seed_data2.json")
    out_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")

    with open(v1_path, encoding="utf-8") as f:
        v1_db = json.load(f)

    with open(v2_base_path, encoding="utf-8") as f:
        v2_base = json.load(f)

    # Build UUID -> Slug mapping from V1 to correctly map steps
    uuid_to_slug = {}

    matrices_db = v1_db.get("matrices", [])
    if isinstance(matrices_db, dict): matrices_db = list(matrices_db.values())
    for idx, m in enumerate(matrices_db):
        uid = m.get("id")
        raw_name = m.get("label") or m.get("slug", "") or f"Matrix {idx}"
        clean_slug = f"matrix_{slugify(raw_name, idx)}"
        uuid_to_slug[uid] = clean_slug

        name_lower = raw_name.lower()
        desc_lower = m.get("description", "").lower()
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
            uuid_to_slug[uid] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
            uuid_to_slug[uid] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
            uuid_to_slug[uid] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
            uuid_to_slug[uid] = "matrix_goodhart"

    components_db = v1_db.get("components", [])
    if isinstance(components_db, dict): components_db = list(components_db.values())
    for idx, c in enumerate(components_db):
        uid = c.get("id")
        raw_name = c.get("name") or c.get("slug", "") or f"Block {idx}"
        clean_slug = f"block_{slugify(raw_name, idx)}"
        uuid_to_slug[uid] = clean_slug

        name_lower = raw_name.lower()
        desc_lower = c.get("description", "").lower()
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
             uuid_to_slug[uid] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
             uuid_to_slug[uid] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
             uuid_to_slug[uid] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
             uuid_to_slug[uid] = "matrix_goodhart"


    # Create Steps
    normalized_steps = []
    v1_steps = v1_db.get("steps", [])
    if isinstance(v1_steps, dict): v1_steps = list(v1_steps.values())

    for idx, st in enumerate(v1_steps):
        s_id = st.get("id")
        raw_name = st.get("name") or f"Task {idx}"
        clean_slug = f"step_{slugify(raw_name, idx)}"

        # Resolve duplicates
        orig = clean_slug
        counter = 1
        while clean_slug in [x["id"] for x in normalized_steps]:
             clean_slug = f"{orig}_{counter}"
             counter += 1

        prompt_blocks_list = []
        config = st.get("config", {})
        inner_uuids = config.get("llm_prompts", [])
        matrix_id = config.get("matrix_id")

        for p_uuid in inner_uuids:
             if p_uuid in uuid_to_slug:
                  prompt_blocks_list.append(uuid_to_slug[p_uuid])

        if matrix_id and matrix_id in uuid_to_slug:
             prompt_blocks_list.append(uuid_to_slug[matrix_id])

        # Fallback if step itself was translated to a matrix previously
        if s_id in uuid_to_slug and uuid_to_slug[s_id].startswith("matrix_"):
             prompt_blocks_list.append(uuid_to_slug[s_id])

        prompt_blocks_list = list(dict.fromkeys(prompt_blocks_list))

        blueprint = {
            "id": clean_slug,
            "slug": clean_slug,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": raw_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": st.get("description") or ""}
            },
            "prompt_blocks": prompt_blocks_list,
            "pre_hooks": config.get("pre_hooks", []),
            "post_hooks": config.get("post_hooks", [])
        }

        uuid_to_slug[s_id] = clean_slug
        normalized_steps.append(blueprint)


    # Create Workflows
    v2_workflows = []
    v1_workflows = v1_db.get("workflows", [])
    if isinstance(v1_workflows, dict): v1_workflows = list(v1_workflows.values())

    for idx, wf in enumerate(v1_workflows):
        wf_name = wf.get("name") or f"Workflow {idx}"
        clean_wf_slug = f"workflow_{slugify(wf_name, idx)}"

        v2_wf = {
            "id": clean_wf_slug,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": wf_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": wf.get("description", "")}
            },
            "expected_inputs": {
                "chat_log": "string"
            },
            "steps": []
        }

        v1_steps_array = wf.get("steps", [])

        for comp_idx, comp_uuid in enumerate(v1_steps_array):
            if comp_uuid not in uuid_to_slug:
                 continue

            blueprint_slug = uuid_to_slug[comp_uuid]

            # Wrap raw components if needed
            if blueprint_slug.startswith("matrix_") or blueprint_slug.startswith("block_"):
                 pseudo_slug = f"step_{blueprint_slug}"
                 if pseudo_slug not in [t["id"] for t in normalized_steps]:
                      normalized_steps.append({
                          "id": pseudo_slug,
                          "slug": pseudo_slug,
                          "name": {"default_locale": "fi", "translations": {"fi": f"Auto-Wrapper for {blueprint_slug}"}},
                          "description": None,
                          "prompt_blocks": [blueprint_slug]
                      })
                 blueprint_slug = pseudo_slug

            node_slug = f"step_node_{comp_idx+1}"

            existing_steps = v2_wf["steps"]
            prev_step_id = None
            if len(existing_steps) > 0:
                 prev_step_id = existing_steps[-1].get("id")

            input_mappings = {
                "context": "$inputs.chat_log",
                "document": "$inputs.document_text"
            }
            if prev_step_id:
                 input_mappings[prev_step_id] = f"${prev_step_id}.output"

            step_rule = {
                "id": node_slug,
                "task_blueprint": blueprint_slug,
                "depends_on": [prev_step_id] if prev_step_id else [],
                "input_mappings": input_mappings,
                "hook": None,
                "model_strategy": "advanced_reasoning"
            }
            v2_wf["steps"].append(step_rule)

        v2_workflows.append(v2_wf)


    # Extract organizations and users directly from github_seed_data.json
    orgs = v1_db.get("organizations", {})
    if isinstance(orgs, dict):
         orgs = list(orgs.values())
    users = v1_db.get("users", {})
    if isinstance(users, dict):
         users = list(users.values())

    normalized_v2_seed = {
        "system_config": v2_base.get("system_config", []),
        "prompt_blocks": v2_base.get("prompt_blocks", []),
        "workflows": v2_workflows,
        "steps": normalized_steps,
        "organizations": orgs,
        "users": users
    }

    with open(out_path, "w", encoding="utf-8") as f:
         json.dump(normalized_v2_seed, f, indent=4, ensure_ascii=False)

    print(f"DONE! Wrote purely normalized JSON to {out_path}")
    print(f"Extracted {len(normalized_v2_seed['system_config'])} system_configs")
    print(f"Extracted {len(normalized_v2_seed['prompt_blocks'])} prompt_blocks")
    print(f"Extracted {len(normalized_v2_seed['workflows'])} workflows")
    print(f"Extracted {len(normalized_v2_seed['steps'])} steps")
    print(f"Extracted {len(normalized_v2_seed['organizations'])} organizations")
    print(f"Extracted {len(normalized_v2_seed['users'])} users")

if __name__ == "__main__":
    build_normalized_v2()
