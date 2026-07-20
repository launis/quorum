import json
from pathlib import Path


def test_seed_data_no_synthesis_override_for_matrix_hooks() -> None:
    """Regression test for Bug (Epic 105 Synthesis Engine Unification).
    Ensures that steps with matrix_scoring_hook in their post_hooks or whose
    task_blueprint has matrix_scoring_hook DO NOT use engine_override: SYNTHESIS.
    """
    seed_path = Path("backend_v2/seed/seed_data.json")
    assert seed_path.exists(), "seed_data.json not found"

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    # Map blueprints to their hooks
    blueprint_post_hooks = {}
    for bp in data.get("task_blueprints", []):
        blueprint_post_hooks[bp["id"]] = bp.get("post_hooks", [])

    for workflow in data.get("workflows", []):
        for step in workflow.get("steps", []):
            override = step.get("engine_override")
            bp_id = step.get("task_blueprint")

            # Check if this step has matrix_scoring_hook
            hooks = blueprint_post_hooks.get(bp_id, [])

            if "matrix_scoring_hook" in hooks:
                assert override != "SYNTHESIS", (
                    f"Workflow '{workflow.get('id')}' step '{step.get('id')}' "
                    f"uses blueprint '{bp_id}' which has 'matrix_scoring_hook', "
                    f"but engine_override is set to SYNTHESIS. This will cause a strict Fail-Fast crash."
                )
