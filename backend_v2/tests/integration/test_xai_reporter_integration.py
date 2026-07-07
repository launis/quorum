from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.reporting import generate_report_hook

valid_execution_data = {
    "id": "exe_123",
    "workflow_id": "wf_123",
    "organization_id": "org_1",
    "status": "running",
    "output_profile_id": "prof_123",
}

valid_workflow_data = {
    "id": "wf_123",
    "slug": "test_workflow",
    "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
    "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
    "status": "draft",
    "version": 1,
    "default_profile_id": "prof_123",
    "expected_inputs": [],
    "steps": [],
}


def test_generate_report_hook_variance_aligned() -> None:
    """Verify that reporting hook correctly aggregates aligned cognitive and mechanical data."""
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={
            "true_atoms_count": 0,
            "false_atoms_count": 0,
            "matrices": {},
        },
        global_context_vars={
            "step_xai": {"executive_summary": "Summary."},
            # Cognitive score: 1.0 (Low authenticity)
            "step_detector": {"raw_score": 1.0},
            # Mechanical fill phrases: 10 (High performativity -> targets 1.0 dampener)
            "step_linguistics": {
                "performative_patterns": [
                    {"pattern_id": f"pat_{i}", "detected_phrase": "filler", "category": "performative_filler"}
                    for i in range(10)
                ]
            },
        },
    )
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_exec_repo.get_execution.return_value = valid_execution_data
    mock_workflow_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_workflow_repo.get_output_profile_by_id.return_value = {
        "id": "prof_123",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
        "layouts": [],
        "display_scale": "original",
        "visible_block_extensions": [],
        "visible_workflow_extensions": ["variance_validation"],
    }
    deps = HookDependencies(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    result = cast(HookResult, generate_report_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    ctx = result.state_delta["report_context"]

    # Assert output_extensions has our VarianceValidationExtension
    extensions = ctx.get("output_extensions", [])
    assert len(extensions) == 1
    ext = extensions[0]
    assert ext["extension_type"] == "variance_validation"
    assert ext["mechanical_metric_ref"] == "performative_phrases_count"
    assert ext["cognitive_metric_ref"] == "llm_authenticity_score"
    # Target dampener for 10 filler phrases is 3.0 - 2.0 = 1.0. Variance: abs(1.0 - 1.0) = 0.0
    assert ext["variance_score"] == 0.0
    assert ext["alignment_verdict"] == "ALIGNED"


def test_generate_report_hook_variance_misaligned_sycophancy() -> None:
    """Verify that reporting hook correctly identifies misaligned sycophancy."""
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={
            "true_atoms_count": 0,
            "false_atoms_count": 0,
            "matrices": {},
        },
        global_context_vars={
            "step_xai": {"executive_summary": "Summary."},
            # Cognitive score: 3.0 (Claiming perfect authenticity)
            "step_detector": {"raw_score": 3.0},
            # Mechanical fill phrases: 10 (But highly performative in reality -> targets 1.0)
            "step_linguistics": {
                "performative_patterns": [
                    {"pattern_id": f"pat_{i}", "detected_phrase": "filler", "category": "performative_filler"}
                    for i in range(10)
                ]
            },
        },
    )
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_exec_repo.get_execution.return_value = valid_execution_data
    mock_workflow_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_workflow_repo.get_output_profile_by_id.return_value = {
        "id": "prof_123",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
        "layouts": [],
        "display_scale": "original",
        "visible_block_extensions": [],
        "visible_workflow_extensions": ["variance_validation"],
    }
    deps = HookDependencies(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    result = cast(HookResult, generate_report_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    ctx = result.state_delta["report_context"]

    extensions = ctx.get("output_extensions", [])
    assert len(extensions) == 1
    ext = extensions[0]
    assert ext["extension_type"] == "variance_validation"
    # Target dampener is 1.0. Variance: abs(3.0 - 1.0) = 2.0
    assert ext["variance_score"] == 2.0
    assert ext["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"
