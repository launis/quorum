import uuid
import pytest
from unittest.mock import AsyncMock

from backend_v2.core.hook_registry import HookState, HookDependencies
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import (
    _extract_guard_flag,
    _extract_falsifier_data,
    _calculate_falsifier_penalty,
    apply_scoring_logic_hook,
    enforce_passivity_penalty_hook,
    normalize_matrix_scores_hook,
    waterfall_scoring_hook,
)


def _make_state(inputs: dict, step_id: str = "step_judge") -> HookState:
    return HookState(
        execution_id=str(uuid.uuid4()),
        workflow_id="wf_dummy",
        step_id=step_id,
        inputs=inputs,
        global_context_vars={},
    )


def test_extract_guard_flag() -> None:
    assert _extract_guard_flag({"step_guard": {"security_check": {"threat_detected": True}}}) is True
    assert _extract_guard_flag({"step_guard": {"security_check": {"threat_detected": False}}}) is False
    assert _extract_guard_flag({}) is False


def test_extract_falsifier_data() -> None:
    assert _extract_falsifier_data({"step_falsifier": {"falsifier_data": {"val": 1}}}) == {"val": 1}
    assert _extract_falsifier_data({"step_panel": {"falsifier_data": {"val": 2}}}) == {"val": 2}
    assert _extract_falsifier_data({}) is None


def test_calculate_falsifier_penalty() -> None:
    assert _calculate_falsifier_penalty({"fidelity_audit": {"post_hoc_rationalization": True}}) is True
    assert _calculate_falsifier_penalty({"fidelity_audit": {"post_hoc_rationalization": False}}) is False
    assert _calculate_falsifier_penalty(None) is False


def test_apply_scoring_logic_hook_empty_state() -> None:
    res = apply_scoring_logic_hook(None, None)
    assert res.success is True
    assert res.state_delta == {}


def test_apply_scoring_logic_hook_calculates_average(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.settings import Settings

    monkeypatch.setattr(
        "backend_v2.hooks.scoring.get_settings",
        lambda: Settings(scoring_security_penalty=0.1, scoring_post_hoc_penalty=0.1, scoring_passivity_multiplier=0.8),
    )

    state = _make_state(
        inputs={
            "matrix_1_is_evaluative": True,
            "matrix_1_normalized": 80.0,
            "matrix_2_is_evaluative": True,
            "matrix_2_normalized": 90.0,
        }
    )

    res = apply_scoring_logic_hook(state, None)
    assert res.success is True
    delta = res.state_delta["scoring_result"]  # type: ignore
    assert delta["total_score"] == 85.0
    assert delta["penalties_applied"] == []


def test_apply_scoring_logic_hook_applies_penalties(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.settings import Settings

    monkeypatch.setattr(
        "backend_v2.hooks.scoring.get_settings",
        lambda: Settings(scoring_security_penalty=0.5, scoring_post_hoc_penalty=0.5, scoring_passivity_multiplier=0.8),
    )

    state = _make_state(
        inputs={
            "matrix_1_is_evaluative": True,
            "matrix_1_normalized": 100.0,
            "step_guard": {"security_check": {"threat_detected": True}},
            "step_falsifier": {"falsifier_data": {"fidelity_audit": {"post_hoc_rationalization": True}}},
        }
    )

    res = apply_scoring_logic_hook(state, None)
    assert res.success is True
    delta = res.state_delta["scoring_result"]  # type: ignore
    # Initial average: 100.0. Guard (+50%) and Post-Hoc (+50%) penalties sum to 1.0 (100%).
    # This is capped at PENALTY_CAP (0.25). 
    # Final score = 100.0 * (1.0 - 0.25) = 75.0
    assert abs(delta["total_score"] - 75.0) < 0.01
    assert len(delta["penalties_applied"]) == 2




def test_enforce_passivity_penalty_hook_v2_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.settings import Settings

    monkeypatch.setattr(
        "backend_v2.hooks.scoring.get_settings",
        lambda: Settings(scoring_passivity_multiplier=0.5),
    )

    state = _make_state(
        inputs={
            "matrix_a": 1.0,  # <= 1.0, triggers penalty
            "matrix_b": 5.0,
        }
    )
    res = enforce_passivity_penalty_hook(state, None)
    # matrix_a is clamped to 1.0 (unchanged), so it won't appear in state_delta
    assert "matrix_a" not in res.state_delta
    assert res.state_delta["matrix_b"] == 2.5


@pytest.mark.asyncio
async def test_normalize_matrix_scores_hook_missing_repo() -> None:
    deps = HookDependencies(repository=None)
    state = _make_state(inputs={})
    res = await normalize_matrix_scores_hook(state, deps)
    assert res.success is True


@pytest.mark.asyncio
async def test_normalize_matrix_scores_hook_success() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"prompt_blocks": ["blk_1"]}
    mock_repo.get_prompt_block_by_id.return_value = {
        "scales": [{"score": 1}, {"score": 5}],
        "scale_min": 1,
        "scale_max": 5,
        "is_evaluative": True,
    }

    deps = HookDependencies(repository=mock_repo)
    state = _make_state(
        step_id="step_1",
        inputs={
            "blk_1": 3.0,
            "other_field": "test",
        }
    )
    # Override task_blueprint to match original test
    state = state.model_copy(update={"task_blueprint": "step_1"})

    res = await normalize_matrix_scores_hook(state, deps)
    assert "blk_1_scaled" in res.state_delta
    assert "blk_1_normalized" in res.state_delta
    assert res.state_delta["blk_1_is_evaluative"] is True


@pytest.mark.asyncio
async def test_normalize_matrix_scores_micro_cot() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"prompt_blocks": ["blk_1"]}
    mock_repo.get_prompt_block_by_id.return_value = {
        "scales": [{"score": 1}, {"score": 5}],
        "scale_min": 1,
        "scale_max": 5,
    }

    deps = HookDependencies(repository=mock_repo)
    state = _make_state(
        step_id="step_1",
        inputs={
            "blk_1": {
                "step_4_final_score": 5.0,
                "step_1_evidence_quote": "q1",
                "evaluation_notes": "note",
                "step_3_logical_friction": "fric",
            }
        }
    )
    state = state.model_copy(update={"task_blueprint": "step_1"})

    res = await normalize_matrix_scores_hook(state, deps)
    assert res.state_delta["blk_1_cited_text_quote"] == "q1"
    assert "note\n\nfric" in res.state_delta["blk_1_justification"]
    assert res.state_delta["blk_1_scaled"] == 5.0


@pytest.mark.asyncio
async def test_normalize_matrix_scores_invalid_prompt_block() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"prompt_blocks": ["blk_1"]}
    mock_repo.get_prompt_block_by_id.return_value = {
        "scales": [{"score": "not_a_number"}],
        "scale_min": 1,
        "scale_max": 5,
    }
    deps = HookDependencies(repository=mock_repo)
    state = _make_state(
        step_id="step_1",
        inputs={
            "blk_1": 3.0,
        }
    )
    state = state.model_copy(update={"task_blueprint": "step_1"})

    with pytest.raises(AppException) as exc:
        await normalize_matrix_scores_hook(state, deps)
    assert "CONFIGURATION_ERROR" in exc.value.error_code


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_matrix_category() -> None:
    """TDD Repro: Matrix is correctly identified by category_id='matrix'."""
    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"prompt_blocks": ["blk_1"]}
    # BUG: It used to skip if type != "matrix". Now type="float", category_id="matrix" should pass.
    mock_repo.get_prompt_block_by_id.return_value = {
        "category_id": "matrix",
        "type": "float",
        "scales": [
            {"score": 1, "claims": [{"micro_atoms": ["test_atom"]}]},
            {"score": 5, "claims": [{"micro_atoms": ["test_atom_b"]}]}
        ],
    }

    import hashlib
    atom_hash = hashlib.md5("test_atom".encode("utf-8")).hexdigest()

    deps = HookDependencies(repository=mock_repo)
    state = _make_state(
        step_id="step_1",
        inputs={
            "evaluations": [
                {
                    "atom_id": atom_hash,
                    "boolean": True,
                    "reasoning": "Valid"
                }
            ]
        }
    )
    state = state.model_copy(update={"task_blueprint": "step_1"})

    res = await waterfall_scoring_hook(state, deps)
    
    assert res.success is True
    # The payload update MUST contain the calculated score mapped to blk_1
    assert "blk_1" in res.state_delta
    assert "blk_1_justification" in res.state_delta


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_dina_floor() -> None:
    """Epic 23: Assert that DINA calculations never fall below DINA_FLOOR (0.30)"""
    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"prompt_blocks": ["blk_dina"]}
    mock_repo.get_prompt_block_by_id.return_value = {
        "category_id": "matrix",
        "type": "float",
        "scales": [
            {"score": 1, "claims": [{"micro_atoms": ["test_atom_1"]}]},
            {"score": 5, "claims": [{"micro_atoms": ["test_atom_5"]}]}
        ],
    }

    import hashlib
    atom_hash_1 = hashlib.md5("test_atom_1".encode("utf-8")).hexdigest()
    atom_hash_5 = hashlib.md5("test_atom_5".encode("utf-8")).hexdigest()

    deps = HookDependencies(repository=mock_repo)
    # Give all False answers to trigger the lowest possible native DINA score (modifier = 0 -> score = 1)
    state = _make_state(
        step_id="step_1",
        inputs={
            "evaluations": [
                {
                    "atom_id": atom_hash_1,
                    "boolean": False,
                    "reasoning": "Failed"
                },
                {
                    "atom_id": atom_hash_5,
                    "boolean": False,
                    "reasoning": "Failed"
                }
            ]
        }
    )
    state = state.model_copy(update={"task_blueprint": "step_1"})

    res = await waterfall_scoring_hook(state, deps)
    
    assert res.success is True
    # If scale_min=1, scale_max=5 and DINA_FLOOR=0.30:
    # dina_absolute_floor = 1 + (5 - 1) * 0.30 = 2.2
    assert "blk_dina" in res.state_delta
    score = res.state_delta["blk_dina"]
    assert abs(score - 2.2) < 0.01
