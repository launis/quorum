import json
from pathlib import Path


def test_seed_data_output_profiles_have_synthesis_block_id() -> None:
    """Ensure all OutputProfile synthesis configurations in seed_data.json specify synthesis_block_id."""
    seed_file = Path("backend_v2/seed/seed_data.json")
    assert seed_file.exists(), "seed_data.json file must exist"

    with seed_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in seed_data.json"

    missing_references: list[str] = []
    for profile in profiles:
        profile_id = profile.get("id", "unknown")
        slug = profile.get("slug", "unknown")
        layouts = profile.get("layouts", [])
        for idx, layout in enumerate(layouts):
            preset_view = layout.get("preset_view", "")
            # Matrix layouts resolve their synthesis directives programmatically via synthesis_directives.py
            if preset_view in ("1d_metrics", "1d", "2d_compare", "2d", "3d_matrix", "3d"):
                continue

            synthesis = layout.get("synthesis")
            is_enabled = layout.get("is_synthesis_enabled", False)
            if synthesis is not None and is_enabled:
                synthesis_block_id = synthesis.get("synthesis_block_id")
                row_block_id = synthesis.get("row_explanations_block_id")
                if not synthesis_block_id and not row_block_id:
                    missing_references.append(f"Profile '{profile_id}' ({slug}) layout index {idx}")

    assert not missing_references, (
        "Fail-Fast: The following OutputProfile layouts are missing 'synthesis_block_id' and 'row_explanations_block_id': "
        + ", ".join(missing_references)
    )
