import pytest

from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.v2_core import SynthesisConfigDTO

def test_synthesis_config_dto_valid() -> None:
    """Test that SynthesisConfigDTO validates with system_prompt."""
    config = SynthesisConfigDTO(
        system_prompt="You are a holistic auditor.",
        length_constraint=1000,
        historical_context_mode=HistoricalContextMode.DISABLED,
    )
    assert config.system_prompt == "You are a holistic auditor."
    assert config.length_constraint == 1000
    assert config.historical_context_mode == HistoricalContextMode.DISABLED
