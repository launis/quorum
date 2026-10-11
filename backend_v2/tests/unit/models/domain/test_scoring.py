import pytest
from pydantic import ValidationError

from backend_v2.models.domain.falsifier import FalsifierData, ReasoningFidelity, WaltonStressTest
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.enums import FidelityLevel


def test_scoring_models_exist() -> None:
    """Test that scoring models are successfully exported."""
    assert StepFalsifierDTO is not None
    assert StepPanelDTO is not None


def test_step_panel_dto_requires_at_least_one_payload() -> None:
    """Test StepPanelDTO rejects empty initialization when all 5 analysis payloads are None."""
    with pytest.raises(ValidationError, match="StepPanelDTO requires at least one analysis payload to be populated."):
        StepPanelDTO()


def test_step_panel_dto_accepts_valid_payload() -> None:
    """Test StepPanelDTO accepts initialization when at least one payload is present."""
    panel = StepPanelDTO(
        falsifier_data=FalsifierData(
            stress_test_findings=[
                WaltonStressTest(
                    question="Is there reasoning bias?",
                    evidence_held=False,
                    observation="Post-hoc reasoning observed",
                )
            ],
            fidelity_audit=ReasoningFidelity(
                fidelity_score=FidelityLevel.WEAK,
                fidelity_numeric=1.0,
                abductive_score=1.0,
                plausibility_score=1.0,
                justification="Post-hoc reasoning detected",
                post_hoc_rationalization=True,
            ),
        )
    )
    assert panel.falsifier_data is not None
    assert len(panel.falsifier_data.stress_test_findings) == 1


def test_step_panel_dto_forbids_extra_fields() -> None:
    """Test StepPanelDTO strictly forbids unknown extra fields."""
    with pytest.raises(ValidationError):
        StepPanelDTO.model_validate(
            {
                "falsifier_data": {
                    "stress_test_findings": [
                        {
                            "question": "Is there reasoning bias?",
                            "evidence_held": False,
                            "observation": "Observed",
                        }
                    ],
                    "fidelity_audit": {
                        "fidelity_score": "WEAK",
                        "fidelity_numeric": 1.0,
                        "abductive_score": 1.0,
                        "plausibility_score": 1.0,
                        "justification": "Valid justification",
                        "post_hoc_rationalization": False,
                    },
                },
                "unauthorized_field": "disallowed",
            }
        )
