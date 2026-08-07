import json


def update_seed() -> None:
    with open("c:/src/quorum/backend_v2/seed/seed_data.json", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Add prompt block
    new_block = {
        "id": "blk_synthesis_generation",
        "slug": "synthesis_generation_block",
        "category_id": "instruction",
        "type": "instruction",
        "label": {"default_locale": "en", "translations": {"en": "Synthesis Generation", "fi": "Synteesin generointi"}},
        "ai_description": "Generate a high-level executive summary and an urgency level based on the evaluation results.",
        "output_extensions": [],
        "description": {
            "default_locale": "en",
            "translations": {"en": "Synthesis Generation Block", "fi": "Synthesis Generation Block"},
        },
    }

    # Check if exists
    if not any(b["id"] == new_block["id"] for b in data["prompt_blocks"]):
        data["prompt_blocks"].append(new_block)

    # 2. Add step definition
    new_step = {
        "id": "sp_synthesis_generation",
        "slug": "synthesis_generation",
        "type": "llm",
        "model_strategy": "synthesis",
        "name": {"default_locale": "en", "translations": {"en": "Synthesis Generation", "fi": "Synteesin Generointi"}},
        "description": {
            "default_locale": "en",
            "translations": {
                "en": "Generates GlobalSynthesisDTO headless data.",
                "fi": "Generates GlobalSynthesisDTO headless data.",
            },
        },
        "allowed_mcp_tools": [],
        "safety": "safe",
        "pre_hooks": [],
        "post_hooks": [],
        "expected_inputs": ["results", "reduced_matrix"],
        "output_schema": None,
        "organization_id": "SYSTEM",
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_synthesis_generation",
        "criteria_block_ids": [],
    }

    if not any(s["id"] == new_step["id"] for s in data["steps"]):
        data["steps"].append(new_step)

    # 3. Add to workflow wf_9d68c573802341db
    for wf in data.get("workflows", []):
        if wf["id"] == "wf_9d68c573802341db":
            # Check if synthesis_generation is already in steps
            if not any(s["task_blueprint"] == "sp_synthesis_generation" for s in wf["steps"]):
                # Get the last step id to depend on it
                last_step = wf["steps"][-1]["id"] if wf["steps"] else None
                new_wf_step = {
                    "id": "sr_synthesis_generation",
                    "task_blueprint": "sp_synthesis_generation",
                    "depends_on": [last_step] if last_step else [],
                    "input_mappings": {
                        "results": f"$steps.{last_step}" if last_step else "",
                        "reduced_matrix": "$event.reduced_matrix",  # Just as placeholder if not explicitly populated
                    },
                }
                wf["steps"].append(new_wf_step)

    with open("c:/src/quorum/backend_v2/seed/seed_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("seed_data.json updated successfully.")


if __name__ == "__main__":
    update_seed()
