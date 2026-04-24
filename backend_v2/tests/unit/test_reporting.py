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
        "inputs": {"true_atoms_count": 5, "false_atoms_count": 2},
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
            "step_overseer": {"overseer_data": {"ethical_issues": ["minor bias detected"]}},
        },
    }

    dto = ReportSynthesisDTO.model_validate(valid_data)

    assert dto.inputs.true_atoms_count == 5
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
        "inputs": {"true_atoms_count": 5, "false_atoms_count": 0},
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


@pytest.mark.asyncio
async def test_generate_report_hook_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the reporting hook can successfully parse a Zero-Compromise strict DTO."""
    from pathlib import Path
    
    # Mock template directory existence to avoid filesystem dependence
    monkeypatch.setattr(Path, "exists", lambda self: True)
    
    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.hooks.reporting import generate_report_hook

    state = HookState(
        execution_id="test",
        workflow_id="test",
        step_id="test",
        task_blueprint="test",
        metadata={},
        inputs={
            "true_atoms_count": 5,
            "false_atoms_count": 0,
            "test_pb": {"step_4_final_score": 5.0, "justification": "Test block", "extensions": {}}
        },
        global_context_vars={
            "step_xai": {
                "executive_summary": "System performs well.",
                "score_cards": []
            },
            "step_overseer": {"overseer_data": {"ethical_issues": ["No bias"]}}
        },
    )
    deps = HookDependencies(repository=None)

    result = generate_report_hook(state, deps)
    
    assert result.success is True
    assert "report_context" in result.state_delta
    ctx = result.state_delta["report_context"]
    assert ctx["summary"] == "System performs well."
    assert ctx["ethical_issues"] == ["No bias"]
    
@pytest.mark.asyncio
async def test_generate_report_hook_missing_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the reporting hook strictly fails fast on missing inputs."""
    from pathlib import Path
    
    # Mock template directory existence to avoid filesystem dependence
    monkeypatch.setattr(Path, "exists", lambda self: True)
    
    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.exceptions import AppException, ErrorCodes
    from backend_v2.hooks.reporting import generate_report_hook

    state = HookState(
        execution_id="test",
        workflow_id="test",
        step_id="test",
        task_blueprint="test",
        metadata={},
        inputs={}, # Missing inputs (empty dict triggers EMPTY_INPUT error in hook)
        global_context_vars={},
    )
    deps = HookDependencies(repository=None)

    with pytest.raises(AppException) as exc:
        generate_report_hook(state, deps)
        
    assert exc.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA
