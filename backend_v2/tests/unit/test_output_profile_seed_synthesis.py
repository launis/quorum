import json
from pathlib import Path

from backend_v2.models.v2_core import OutputProfile


def test_seed_data_output_profiles_have_valid_synthesis_config() -> None:
    """Ensure all OutputProfile items in seed_data.json have zero legacy synthesis sub-object and validate strictly."""
    seed_file = Path("backend_v2/seed/seed_data.json")
    assert seed_file.exists(), "seed_data.json file must exist"

    with seed_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in seed_data.json"

    for profile in profiles:
        assert "synthesis" not in profile, f"Profile {profile.get('id')} must not contain legacy 'synthesis' key"
        op = OutputProfile.model_validate(profile, strict=True)
        assert isinstance(op, OutputProfile)
        assert isinstance(op.requires_executive_synthesis, bool)
        assert isinstance(op.requires_group_synthesis, bool)
        assert isinstance(op.requires_row_explanations, bool)
        assert isinstance(op.is_synthesis_expected, bool)

