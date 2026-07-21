from unittest.mock import AsyncMock
def test_scoring_models_exist() -> None:
    """Test that scoring models are successfully exported."""
    from backend_v2.models.domain.scoring import StepFalsifierDTO, StepGuardDTO, StepPanelDTO

    assert StepGuardDTO is not None
    assert StepFalsifierDTO is not None
    assert StepPanelDTO is not None
