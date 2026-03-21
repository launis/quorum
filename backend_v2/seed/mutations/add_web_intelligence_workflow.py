import json
import os
import shutil
from datetime import datetime

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"C:\src\quorum\backend_v2\seed\backups"

def main():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"seed_data_{timestamp}.json.bak")
    shutil.copy2(SEED_FILE, backup_file)
    print(f"Backed up seed_data.json to {backup_file}")

    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    target_block_id = "blk_044f6bad09854aa8bb646f63c7571ceb"
    global_steps = data.get("steps", [])

    # Cleanse ALL steps of the hypothesis block and the search hook so it doesn't conflict
    for s in global_steps:
        if target_block_id in s.get("prompt_blocks", []):
            s["prompt_blocks"].remove(target_block_id)
            print(f"Removed {target_block_id} from {s.get('slug')} prompt_blocks.")

        if "execute_google_search" in s.get("pre_hooks", []):
            s["pre_hooks"].remove("execute_google_search")
            print(f"Removed execute_google_search from {s.get('slug')} pre_hooks.")

        if "execute_google_search" in s.get("post_hooks", []):
            s["post_hooks"].remove("execute_google_search")
            print(f"Removed execute_google_search from {s.get('slug')} post_hooks.")

    # Create new isolated Fact-Checker
    fact_checker_id = "step_factchecker1234abcd"

    # Clean up old fact_checker node if it existed from previous script runs
    data["steps"] = [s for s in data["steps"] if s.get("id") not in ("step_fact_checker_v2_001", fact_checker_id)]

    new_step = {
        "id": fact_checker_id,
        "slug": "step_fact_checker",
        "name": {"default_locale": "en", "translations": {"fi": "Faktantarkistaja", "en": "Fact Checker"}},
        "description": {"default_locale": "en", "translations": {"fi": "Hakee taustatietoa tieteelliseen analyysiin.", "en": "Extracts hypotheses and runs Google Search in background"}},
        "prompt_blocks": [target_block_id],
        "pre_hooks": ["inject_step_metadata"],
        "post_hooks": ["execute_google_search"]
    }
    data["steps"].append(new_step)
    print(f"Added {fact_checker_id} global step definition.")

    workflow = data["workflows"][0]
    wf_steps = workflow.get("steps", [])
    fact_checker_rule_id = "steprule_factcheck1234ab"

    # Strip previous fact checker rule from workflow if it existed
    workflow["steps"] = [r for r in wf_steps if r.get("id") not in ("steprule_fact_checker_v2_001", fact_checker_rule_id)]
    wf_steps = workflow["steps"]

    # Find ID of input_processing and guard to NOT make them depend on fact checker
    exempt_blueprints = [
        s.get("id") for s in global_steps
        if s.get("slug") in ("step_input_processing", "step_guard")
    ]

    exempt_rule_ids = [r.get("id") for r in wf_steps if r.get("task_blueprint") in exempt_blueprints]

    for rule in wf_steps:
         if rule.get("id") not in exempt_rule_ids:
             depends_on = rule.get("depends_on", [])
             if fact_checker_rule_id not in depends_on:
                 rule["depends_on"] = depends_on + [fact_checker_rule_id]

    new_rule = {
        "id": fact_checker_rule_id,
        "task_blueprint": fact_checker_id,
        "depends_on": exempt_rule_ids, # Fact checker depends on input processing and guard
        "input_mappings": {"inputs": "$inputs"},
        "model_strategy": "fast",
        "pre_hooks": ["inject_step_metadata"],
        "post_hooks": []
    }

    # Insert right after exempt edges
    wf_steps.insert(len(exempt_rule_ids), new_rule)
    print(f"Injected {fact_checker_rule_id} into workflow DAG.")

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully updated seed_data.json!")

if __name__ == "__main__":
    main()
