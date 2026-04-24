from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report import (
    GlobalContextVarsDTO,
    ReportSynthesisDTO,
    XAIFlatReportDTO,
)


def test_report_synthesis_dto_validation_success() -> None:
    """Test successful validation of ReportSynthesisDTO with valid nested data."""
    valid_data = {
        "inputs": {"workflow_type": "audit", "user_id": "usr_123"},
        "global_context_vars": {
            "step_xai": {
                "executive_summary": "System performs well.",
                "score_cards": [
                    {
                        "total_score": 4.5,
                        "dimensions": [
                            {
                                "dimension_id": "dim_1",
                                "dimension_label": "Clarity",
                                "score": 4.5,
                                "reasoning": "Clear output.",
                            }
                        ],
                    }
                ],
            },
            "step_judge": {"critical_findings": ["No severe issues found."]},
            "step_overseer": {"overseer_data": {"ethical_issues": [{"severity": "low", "issue": "bias"}]}},
            "extra_unmapped_step": {"some": "data"},  # Should be ignored by extra='ignore'
        },
    }

    dto = ReportSynthesisDTO.model_validate(valid_data)

    assert dto.inputs["workflow_type"] == "audit"
    assert dto.global_context_vars.step_xai is not None
    assert dto.global_context_vars.step_xai.executive_summary == "System performs well."
    assert dto.global_context_vars.step_xai is not None
    assert dto.global_context_vars.step_xai.score_cards is not None
    assert len(dto.global_context_vars.step_xai.score_cards) == 1
    assert dto.global_context_vars.step_xai.score_cards[0].dimensions[0].dimension_id == "dim_1"
    assert dto.global_context_vars.step_judge is not None
    assert dto.global_context_vars.step_judge.critical_findings == ["No severe issues found."]


def test_report_synthesis_dto_validation_failure() -> None:
    """Test that validation fails (Fail-Fast) when structural typing is violated."""
    invalid_data = {
        "inputs": {"workflow_type": "audit"},
        "global_context_vars": {
            "step_xai": {
                # executive_summary expects a string, passing a list to trigger ValidationError
                "executive_summary": ["this", "should", "fail"]
            }
        },
    }

    with pytest.raises(ValidationError) as exc:
        ReportSynthesisDTO.model_validate(invalid_data)

    errors = exc.value.errors()
    assert len(errors) > 0
    assert "executive_summary" in str(errors[0]["loc"])


def test_global_context_vars_dto_optionality() -> None:
    """Test that all steps are truly optional and default to None."""
    dto = GlobalContextVarsDTO.model_validate({})
    assert dto.step_xai is None
    assert dto.step_judge is None
    assert dto.step_overseer is None


def test_xai_flat_report_dto_serialization() -> None:
    """Test XAIFlatReportDTO instantiation and serialization correctness."""
    uid = uuid4()
    now = datetime.now()

    flat_report = XAIFlatReportDTO(
        execution_id=uid,
        timestamp=now,
        verdict="Approved",
        score_total=4.8,
        confidence_score=0.95,
        top_strength_id="dim_logic",
        top_weakness_id="dim_clarity",
        flattened_scores={"dim_logic": 5.0, "dim_clarity": 3.5},
    )

    dumped = flat_report.model_dump(mode="json")
    assert dumped["execution_id"] == str(uid)
    assert dumped["verdict"] == "Approved"
    assert dumped["flattened_scores"]["dim_logic"] == 5.0
