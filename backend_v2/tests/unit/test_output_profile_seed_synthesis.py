import json
from pathlib import Path

from backend_v2.models.v2_core import SynthesisConfigDTO


def test_seed_data_output_profiles_have_valid_synthesis_config() -> None:
    """Ensure all OutputProfile synthesis configurations in seed_data.json have valid structure."""
    seed_file = Path("backend_v2/seed/seed_data.json")
    assert seed_file.exists(), "seed_data.json file must exist"

    with seed_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.get("output_profiles", [])
    assert profiles, "At least one output profile must exist in seed_data.json"

    for profile in profiles:
        synthesis = profile.get("synthesis")
        if synthesis is not None:
            dto = SynthesisConfigDTO.model_validate(synthesis, strict=True)
            assert isinstance(dto, SynthesisConfigDTO)
