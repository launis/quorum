"""Unit tests for Scoring Hook Domain Models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.falsifier import FalsifierData, ReasoningFidelity, WaltonStressTest
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.enums import FidelityLevel
from backend_v2.tests.factories.model_factories import StepPanelDTOFactory


def test_scoring_models_exist() -> None:
    """Test that scoring models are successfully exported and immutable."""
    assert StepFalsifierDTO.model_config.get("frozen") is True
    assert StepPanelDTO.model_config.get("frozen") is True


def test_step_panel_dto_requires_at_least_one_payload() -> None:
    """Test StepPanelDTO rejects empty initialization when all 5 analysis payloads are None."""
    with pytest.raises(ValidationError, match=r"StepPanelDTO requires at least one analysis payload to be populated\."):
        StepPanelDTO()


def test_step_panel_dto_accepts_valid_payload() -> None:
    """Test StepPanelDTO accepts initialization when at least one payload is present."""
    panel = StepPanelDTOFactory.build()
    assert panel.falsifier_data is not None
    assert len(panel.falsifier_data.stress_test_findings) == 1


def test_step_panel_dto_forbids_extra_fields() -> None:
    """Test StepPanelDTO strictly forbids unknown extra fields."""
    valid_dump = StepPanelDTOFactory.build().model_dump()
    valid_dump["unauthorized_field"] = "disallowed"
    with pytest.raises(ValidationError):
        StepPanelDTO.model_validate(valid_dump)


def test_step_falsifier_dto_valid_and_negative_bounds() -> None:
    """Test StepFalsifierDTO positive instantiation and inherited ReasoningTrace AppException boundaries."""
    falsifier_data = FalsifierData(
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
    dto = StepFalsifierDTO(
        thought_process="Step-by-step reasoning analysis.",
        conclusion="Falsifier audit completed.",
        confidence_score=0.85,
        falsifier_data=falsifier_data,
    )
    assert dto.confidence_score == 0.85
    assert dto.falsifier_data is not None

    # Negative Case 1: Out-of-bounds confidence_score (> 1.0) raises AppException
    with pytest.raises(AppException) as exc_bounds:
        StepFalsifierDTO(
            thought_process="Step-by-step reasoning analysis.",
            conclusion="Falsifier audit completed.",
            confidence_score=1.1,
            falsifier_data=falsifier_data,
        )
    assert exc_bounds.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative Case 2: Hallucinated empty-equivalent string raises AppException
    with pytest.raises(AppException) as exc_hallucination:
        StepFalsifierDTO(
            thought_process="null",
            conclusion="Falsifier audit completed.",
            confidence_score=0.5,
            falsifier_data=falsifier_data,
        )
    assert exc_hallucination.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
