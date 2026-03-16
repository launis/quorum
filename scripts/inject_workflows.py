import json
import re
from pathlib import Path


def slugify(text: str, fallback_index: int) -> str:
    if not text:
        return f"item_{fallback_index}"
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    clean = re.sub(r'[\s-]+', '_', clean)
    return clean[:30]

def inject():
    v1_path = Path("c:/src/quorum/data/github_seed_data.json")
    v2_path = Path("c:/src/quorum/backend_v2/seed/seed_data2.json")

    with open(v1_path, encoding="utf-8") as f:
        v1_db = json.load(f)

    with open(v2_path, encoding="utf-8") as f:
        v2_db = json.load(f)

    uuid_to_slug = {}

    # Rebuild matrix UUID mapping
    steps_source = v1_db.get("steps", [])
    if isinstance(steps_source, dict):
        steps_source = list(steps_source.values())

    for idx, step_data in enumerate(steps_source):
        step_id = step_data.get("id", f"missing_id_{idx}")
        v1_name = step_data.get("name") or f"step_{idx}"
        clean_slug = f"matrix_{slugify(v1_name, idx)}"
        original_slug = clean_slug
        counter = 1
        while clean_slug in uuid_to_slug.values():
            clean_slug = f"{original_slug}_{counter}"
            counter += 1
        uuid_to_slug[step_id] = clean_slug

        explanation = step_data.get("explanation", "")
        if step_data.get("type", "") == "instruction":
            explanation = step_data.get("content", "")
        name_lower = v1_name.lower()
        desc_lower = explanation.lower()

        # apply specific assignments from migration script
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
            uuid_to_slug[step_id] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
            uuid_to_slug[step_id] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
            uuid_to_slug[step_id] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
            uuid_to_slug[step_id] = "matrix_goodhart"

    # Rebuild components UUID mapping
    components_db = v1_db.get("components", [])
    if isinstance(components_db, dict):
        components_list = list(components_db.values())
    else:
        components_list = components_db

    for c_idx, comp_data in enumerate(components_list):
        if not comp_data: continue
        c_uuid = comp_data.get("id")
        raw_slug = comp_data.get("slug", "") or comp_data.get("name", "")
        clean_slug = f"block_{slugify(raw_slug, c_idx)}"
        original_slug = clean_slug
        counter = 1
        while clean_slug in uuid_to_slug.values():
            clean_slug = f"{original_slug}_{counter}"
            counter += 1
        uuid_to_slug[c_uuid] = clean_slug

        c_name = comp_data.get("name") or comp_data.get("slug") or f"LegacyPromptBlock {c_idx}"
        c_desc = comp_data.get("description") or ""
        name_lower = c_name.lower()
        desc_lower = c_desc.lower()

        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower:
            uuid_to_slug[c_uuid] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower:
            uuid_to_slug[c_uuid] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower:
            uuid_to_slug[c_uuid] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower:
            uuid_to_slug[c_uuid] = "matrix_goodhart"


    # NOW WE BUILD Task Blueprints from V1 steps
    task_blueprints = []
    for comp_idx, step_data in enumerate(steps_source):
        step_uuid = step_data.get("id", f"missing_tb_{comp_idx}")
        b_name = step_data.get("name") or f"Task {comp_idx}"
        clean_b_slug = f"task_{slugify(b_name, comp_idx)}"
        original_slug = clean_b_slug
        counter = 1
        while clean_b_slug in [t["id"] for t in task_blueprints]:
            clean_b_slug = f"{original_slug}_{counter}"
            counter += 1

        prompt_blocks = []
        inner_uuids = step_data.get("config", {}).get("llm_prompts", [])
        for suuid in inner_uuids:
            if suuid in uuid_to_slug:
                prompt_blocks.append(uuid_to_slug[suuid])

        matrix_id = step_data.get("config", {}).get("matrix_id")
        if matrix_id and matrix_id in uuid_to_slug:
            prompt_blocks.append(uuid_to_slug[matrix_id])

        # Add itself if it was a matrix
        if step_uuid in uuid_to_slug and uuid_to_slug[step_uuid].startswith("matrix_"):
            if uuid_to_slug[step_uuid] not in prompt_blocks:
                prompt_blocks.append(uuid_to_slug[step_uuid])

        # ensure uniqueness
        prompt_blocks = list(dict.fromkeys(prompt_blocks))

        blueprint = {
            "id": clean_b_slug,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": b_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": step_data.get("description", "")}
            },
            "prompt_blocks": prompt_blocks
        }

        uuid_to_slug[step_uuid] = clean_b_slug
        task_blueprints.append(blueprint)

    v2_db["task_blueprints"] = task_blueprints

    # BUILD WORKFLOWS
    workflows_source = v1_db.get("workflows", [])
    if isinstance(workflows_source, dict):
        workflows_source = list(workflows_source.values())

    v2_workflows = []

    for wf_idx, wf_data in enumerate(workflows_source):
        v1_wf_name = wf_data.get("name") or f"workflow_{wf_idx}"
        v1_steps_array = wf_data.get("steps", [])
        clean_wf_slug = f"workflow_{slugify(v1_wf_name, wf_idx)}"

        v2_wf = {
            "id": clean_wf_slug,
            "name": {
                "default_locale": "fi",
                "translations": {"fi": v1_wf_name}
            },
            "description": {
                "default_locale": "fi",
                "translations": {"fi": wf_data.get("description", "")}
            },
            "expected_inputs": {
                "chat_log": "string"
            },
            "steps": []
        }

        for comp_idx, comp_uuid in enumerate(v1_steps_array):
            if comp_uuid not in uuid_to_slug:
                continue

            blueprint_slug = uuid_to_slug[comp_uuid]

            if blueprint_slug.startswith("matrix_") or blueprint_slug.startswith("block_"):
                pseudo_slug = f"task_{blueprint_slug}"
                if pseudo_slug not in [t["id"] for t in task_blueprints]:
                    task_blueprints.append({
                        "id": pseudo_slug,
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
                "context": "$inputs.chat_log"
            }
            if prev_step_id:
                input_mappings[prev_step_id] = f"${prev_step_id}.output"

            step_rule = {
                "id": node_slug,
                "task_blueprint": blueprint_slug,
                "input_mappings": input_mappings,
                "model_strategy": "advanced_reasoning"
            }
            v2_wf["steps"].append(step_rule)

        v2_workflows.append(v2_wf)

    v2_db["workflows"] = v2_workflows

    with open(v2_path, "w", encoding="utf-8") as f:
        json.dump(v2_db, f, indent=4, ensure_ascii=False)

    print(f"Injected {len(task_blueprints)} task blueprints and {len(v2_workflows)} workflows.")

if __name__ == "__main__":
    inject()
