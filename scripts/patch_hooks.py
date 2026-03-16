import json
from pathlib import Path


def patch_hooks():
    v1_path = Path("c:/src/quorum/data/github_seed_data.json")
    v2_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")

    print(f"Loading V1 data from {v1_path}...")
    with open(v1_path, encoding="utf-8") as f:
        v1_data = json.load(f)

    print(f"Loading V2 data from {v2_path}...")
    with open(v2_path, encoding="utf-8") as f:
        v2_data = json.load(f)

    # Build a lookup for V1 step hooks mapped by their original name/slug since the UUIDs change slightly.
    # We will use the 'task_key' or 'slug' or 'name' as a reliable mapping key.
    # It seems in V2 stitch script, the V2 step id is directly generated from V1 step id (they are identical objects in workflow.steps array but actual step IDs might be different).
    # Wait, in the stitch_v2.py, V2 steps use the exact same 'id' as V1 steps? Let's check.

    # Let's map by slug just to be safe.
    v1_hooks_by_slug = {}
    for step in v1_data.get("steps", []):
        slug = step.get("slug")
        config = step.get("config", {})
        pre_hooks = config.get("pre_hooks", [])
        post_hooks = config.get("post_hooks", [])
        if slug:
            v1_hooks_by_slug[slug] = {
                "pre_hooks": pre_hooks,
                "post_hooks": post_hooks
            }

    patched_count = 0
    # Patch V2 steps
    for step in v2_data.get("steps", []):
        slug = step.get("slug")
        if slug in v1_hooks_by_slug:
            hooks = v1_hooks_by_slug[slug]
            # ONLY add them if they have items, to keep JSON clean. Or explicitly add arrays.
            # V2 core models expect lists.
            step["pre_hooks"] = hooks["pre_hooks"]
            step["post_hooks"] = hooks["post_hooks"]
            patched_count += 1
        else:
            # Initialize empty so validation passes
            step["pre_hooks"] = []
            step["post_hooks"] = []

    print(f"Patched {patched_count} steps with pre_hooks and post_hooks.")

    print(f"Writing updated V2 data to {v2_path}...")
    with open(v2_path, "w", encoding="utf-8") as f:
        json.dump(v2_data, f, indent=4, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    patch_hooks()
