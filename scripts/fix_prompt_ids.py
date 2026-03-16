import json
from pathlib import Path


def fix_prompt_ids():
    seed_file = Path(r"c:\src\quorum\backend\seed\seed_data.json")
    with open(seed_file, encoding='utf-8') as f:
        data = json.load(f)

    # Build slug -> id map for components
    comp_map = {}
    if "components" in data:
        for comp in data["components"]:
            if "slug" in comp and "id" in comp:
                comp_map[comp["slug"]] = comp["id"]

    # Also for workflows etc if any references remain, but mostly steps and llm_prompts
    changes_made = 0
    if "steps" in data:
        for step in data["steps"]:
            if "config" in step:
                config = step["config"]
                if "llm_prompts" in config and isinstance(config["llm_prompts"], list):
                    new_prompts = []
                    for prompt in config["llm_prompts"]:
                        if prompt in comp_map:
                            new_prompts.append(comp_map[prompt])
                            changes_made += 1
                        else:
                            new_prompts.append(prompt)
                    config["llm_prompts"] = new_prompts

                if "matrix_id" in config:
                    mat_id = config["matrix_id"]
                    if mat_id in comp_map:
                        config["matrix_id"] = comp_map[mat_id]
                        changes_made += 1

    print(f"Made {changes_made} replacements in steps.")

    if changes_made > 0:
        with open(seed_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved seed_data.json")

if __name__ == "__main__":
    fix_prompt_ids()
