import json

DB_PATH = "c:/src/quorum/data/db.json"


def verify():
    try:
        with open(DB_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"FAIL: Database file not found at {DB_PATH}")
        return

    # TinyDB structure: {"_default": { "1": {...}, "2": {...} }, "system_models": { ... }}
    # We need to find "step_context" and "step_xai" in "system_models" table or "steps" table?
    # The seeder upsets into "steps" table?
    # In seed_data.json they are under "steps".
    # Let's check "steps" table. Or "system_models"?
    # Usually "steps" in seed_data -> "steps" table (or "system_config"?)
    # Let's look for them in all tables.

    found_context = False
    context_passed = False

    found_xai = False
    xai_passed = False

    for _table_name, table_data in data.items():
        for _key, record in table_data.items():
            if record.get("id") == "step_context":
                found_context = True
                config = record.get("config", {})
                prompts = config.get("llm_prompts", [])
                if prompts and len(prompts) > 0:
                    context_passed = True
                    print(f"PASS: step_context found with {len(prompts)} prompts.")
                else:
                    print(f"FAIL: step_context found but llm_prompts is empty: {prompts}")

            if record.get("id") == "step_xai":
                found_xai = True
                config = record.get("config", {})
                post_hooks = config.get("post_hooks", [])
                pre_hooks = config.get("pre_hooks", [])

                if "generate_report" in post_hooks:
                    if "generate_report" not in pre_hooks:
                        xai_passed = True
                        print("PASS: step_xai found with generate_report in post_hooks.")
                    else:
                        print("FAIL: step_xai has generate_report in BOTH pre and post hooks.")
                else:
                    print(f"FAIL: step_xai does not have generate_report in post_hooks. Hooks: {post_hooks}")

    if not found_context:
        print("FAIL: step_context NOT found in database.")
    if not found_xai:
        print("FAIL: step_xai NOT found in database.")

    if context_passed and xai_passed:
        print("\nALL CHECKS PASSED.")
    else:
        print("\nSOME CHECKS FAILED.")


if __name__ == "__main__":
    verify()
