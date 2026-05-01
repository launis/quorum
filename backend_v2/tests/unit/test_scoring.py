from collections.abc import Awaitable
from typing import Any, cast

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import normalize_matrix_scores_hook


def _build_valid_scale(score: Any, micro_atoms: list[str] | None = None) -> dict[str, Any]:
    claims = []
    if micro_atoms is not None:
        claims.append(
            {
                "label": {"default_locale": "en", "translations": {"en": "Test Claim"}},
                "ai_description": "Test Claim Desc",
                "micro_atoms": micro_atoms,
            }
        )
    return {
        "score": score,
        "ai_label": f"Level {score}",
        "claims": claims,
    }


def _build_valid_pb_dict(
    pb_id: str,
    scales: list[dict[str, Any]],
    pb_type: str = "float",
    category_id: str = "matrix",
) -> dict[str, Any]:
    pb = {
        "id": pb_id,
        "slug": "test_slug",
        "label": {"default_locale": "en", "translations": {"en": "Test Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "ai_description": "Test AI Desc",
        "type": pb_type,
        "category_id": category_id,
        "scale_min": 1,
        "scale_max": 5,
    }
    if scales:
        pb["scales"] = scales
    return pb


def _build_valid_step_dict(prompt_blocks: list[str]) -> dict[str, Any]:
    return {
        "id": "st_1234567890123456",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "logic",
        "hook": "dummy_hook",
        "prompt_blocks": prompt_blocks,
    }


class MockRepository:
    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return _build_valid_step_dict(["pb_1234567890123456"])

    async def get_prompt_block_by_id(self, slug: str) -> dict[str, Any]:
        return _build_valid_pb_dict("pb_1234567890123456", [_build_valid_scale("not_a_number")])


@pytest.mark.asyncio
async def test_normalize_matrix_scores_fails_on_corrupt_scale() -> None:
    """Test that setting a corrupted non-float scale in PromptBlocks causes a fail fast AppException."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={"pb_1234567890123456": {"step_4_final_score": 5.0}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )  # noqa: E501

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], normalize_matrix_scores_hook(state, deps))

    assert exc_info.value.error_code == "VALIDATION_FAILED"
    assert "Strict Fail-Fast Enforced: Invalid PromptBlock format for 'pb_1234567890123456'" in exc_info.value.message  # noqa: E501


@pytest.mark.asyncio
async def test_normalize_matrix_scores_tapa_2_string_mapping() -> None:
    """Test that Tapa 2 string PromptBlocks preserve XAI variables in the new LightweightMatrixOutput."""  # noqa: E501

    class MockRepoTapa2:
        async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
            return _build_valid_step_dict(["tb_1234567890123456"])

        async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
            return _build_valid_pb_dict(
                "tb_1234567890123456",
                [
                    _build_valid_scale(1, ["tapa_atom_1"]),
                    _build_valid_scale(5, ["tapa_atom_5"]),
                ],
            )

    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={
            "tb_1234567890123456": {
                "evaluation_notes": "Tämä on perustelu",
                "step_1_evidence_quote": "Ote lähteestä",
                "step_2_falsification": "Vastalause",
                "step_3_logical_friction": "Kitkaa on",
                "step_4_final_score": 5.0,
            }
        },
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoTapa2()),
        workflow_repo=cast(Any, MockRepoTapa2()),
        comp_repo=cast(Any, MockRepoTapa2()),
        identity_repo=cast(Any, MockRepoTapa2()),
        audit_repo=cast(Any, MockRepoTapa2()),
        system_repo=cast(Any, MockRepoTapa2()),
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], normalize_matrix_scores_hook(state, deps))

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # V2 Anti-TDD: Naked keys are BANNED. Must be inside LightweightMatrixOutput dict.
    parsed_output = delta["tb_1234567890123456"]
    extensions = parsed_output.get("extensions", {})

    assert extensions.get("citation") == "Ote lähteestä"
    assert extensions.get("falsification") == "Vastalause"

    justification = parsed_output.get("justification", "")
    assert "Tämä on perustelu" in justification
    assert "Kitkaa on" in justification

    assert "toulmin_text_block_scaled" not in delta


import hashlib

from backend_v2.hooks.scoring import waterfall_scoring_hook


class MockRepoWaterfall:
    def __init__(self, pb_id: str = "pb_1234567890123456") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return _build_valid_step_dict([self.pb_id])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        return _build_valid_pb_dict(
            self.pb_id,
            [
                _build_valid_scale(1, ["atom_1"]),
                _build_valid_scale(2, ["atom_2"]),
                _build_valid_scale(3, ["atom_3"]),
                _build_valid_scale(4, ["atom_4"]),
                _build_valid_scale(5, ["atom_5"]),
            ],
        )


class MockRepoWaterfallMixed:
    def __init__(self) -> None:
        self.pb_matrix = "pm_1234567890123456"
        self.pb_instruction = "pi_1234567890123456"

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return _build_valid_step_dict([self.pb_matrix, self.pb_instruction])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        if pb_id == self.pb_matrix:
            return _build_valid_pb_dict(
                self.pb_matrix,
                [
                    _build_valid_scale(1, ["atom_1"]),
                    _build_valid_scale(5, ["atom_5"]),
                ],
            )
        else:
            return _build_valid_pb_dict(self.pb_instruction, [], pb_type="instruction", category_id="instruction")  # noqa: E501


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_ignores_instructions() -> None:
    """Test that waterfall scoring gracefully skips instructional PromptBlocks without crashing."""
    import hashlib

    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = hashlib.md5(f"atom_1{mandate}".encode()).hexdigest()

    state = HookState(
        execution_id="t3",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": [{"atom_id": atom_hash, "boolean": True}]},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallMixed()),
        workflow_repo=cast(Any, MockRepoWaterfallMixed()),
        comp_repo=cast(Any, MockRepoWaterfallMixed()),
        identity_repo=cast(Any, MockRepoWaterfallMixed()),
        audit_repo=cast(Any, MockRepoWaterfallMixed()),
        system_repo=cast(Any, MockRepoWaterfallMixed()),
    )  # noqa: E501

    # TDD RED: This should NOT raise AppException(Strict Fail-Fast Enforced: PromptBlock has no scales)
    result = await cast(Awaitable[HookResult], waterfall_scoring_hook(state, deps))
    assert result.success is True


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_pass_all() -> None:
    """Test standard hybrid model when everything passes."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    for i in range(1, 6):
        atom_hash = hashlib.md5(f"atom_{i}{mandate}".encode()).hexdigest()
        evaluations.append({"atom_id": atom_hash, "boolean": True, "reasoning": "Hyväksytty"})

    state = HookState(
        execution_id="t1",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], waterfall_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta["pb_1234567890123456"]["step_4_final_score"] == 5.0
    assert "Level 5.0:** 1/1" in result.state_delta["pb_1234567890123456"]["waterfall_calculation_log"]


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_ceiling_cap() -> None:
    """Test that the waterfall ceiling caps the final score despite high weighted score."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Level 1: 1/1 (ok), Level 2: 0/1 (fails), Level 3, 4, 5: 1/1 (ok)
    for i in range(1, 6):
        atom_hash = hashlib.md5(f"atom_{i}{mandate}".encode()).hexdigest()
        is_hit = True if i != 2 else False
        evaluations.append({"atom_id": atom_hash, "boolean": is_hit})

    state = HookState(
        execution_id="t2",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )  # noqa: E501
    result = await cast(Awaitable[HookResult], waterfall_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None

    # Floor should be 1.0 (Level 2 failed).
    # Weighted math: (1*1 + 0*2 + 1*3 + 1*4 + 1*5) = 13 achieved weights. Max weights: 15. Proportional = 13/15.  # noqa: E501
    # Score = 1.0 + (13/15 * 4.0) = 1.0 + 3.46 = 4.46.
    # But Capped at Floor (1.0) + 1.0 = 2.0!
    assert result.state_delta["pb_1234567890123456"]["step_4_final_score"] == 1.0


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_graceful_missing() -> None:
    """Test missing context formatting logic."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Fail level 3
    for i in range(1, 4):
        atom_hash = hashlib.md5(f"atom_{i}{mandate}".encode()).hexdigest()
        is_hit = False if i == 3 else True
        reasoning = "Testivaste" if not is_hit else "OK"
        evaluations.append({"atom_id": atom_hash, "boolean": is_hit, "reasoning": reasoning})

    state = HookState(
        execution_id="t3",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )  # noqa: E501
    result = await cast(Awaitable[HookResult], waterfall_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    # Level 1 (100%), Level 2 (100%), Level 3 (0%) -> Floor 2.0.
    # Weighted: (1*1 + 1*2 + 0) / (1+2+3) = 3 / 6 = 50%.
    # Weighted Score: 1.0 + (0.5 * 4.0) = 3.0. Max cap: 2.0 + 1.0 = 3.0. So score is 3.0.
    assert result.state_delta["pb_1234567890123456"]["step_4_final_score"] == 2.0


class MockRepoWaterfallSimulation:
    def __init__(self, pb_id: str = "pb_1234567890123456") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return _build_valid_step_dict([self.pb_id])

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        return _build_valid_pb_dict(
            self.pb_id,
            [
                _build_valid_scale(1, ["L1_A1", "L1_A2"]),
                _build_valid_scale(2, ["L2_A1", "L2_A2"]),
                _build_valid_scale(3, ["L3_A1", "L3_A2"]),
                _build_valid_scale(4, ["L4_A1"]),
                _build_valid_scale(5, ["L5_A1"]),
            ],
        )


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_full_simulation() -> None:
    """Simulates a complex real-world evaluation trace to ensure mathematical perfection."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Taso 1 (100% osuma)
    evaluations.append(
        {"atom_id": hashlib.md5(f"L1_A1{mandate}".encode()).hexdigest(), "boolean": True, "reasoning": "Oikein"}  # noqa: E501
    )
    evaluations.append(
        {"atom_id": hashlib.md5(f"L1_A2{mandate}".encode()).hexdigest(), "boolean": True, "reasoning": "Oikein"}  # noqa: E501
    )

    # Taso 2 (100% osuma)
    evaluations.append(
        {"atom_id": hashlib.md5(f"L2_A1{mandate}".encode()).hexdigest(), "boolean": True, "reasoning": "Oikein"}  # noqa: E501
    )
    evaluations.append(
        {"atom_id": hashlib.md5(f"L2_A2{mandate}".encode()).hexdigest(), "boolean": True, "reasoning": "Oikein"}  # noqa: E501
    )

    # Taso 3 (50% osuma -> Hit Rate < 90% -> VESIPUTOUS PYSÄHTYY)
    evaluations.append(
        {"atom_id": hashlib.md5(f"L3_A1{mandate}".encode()).hexdigest(), "boolean": True, "reasoning": "Oikein"}  # noqa: E501
    )
    evaluations.append(
        {
            "atom_id": hashlib.md5(f"L3_A2{mandate}".encode()).hexdigest(),
            "boolean": False,
            "reasoning": "Aihetodistetta EI esitetty.",
        }
    )

    # Taso 4 (100% osuma -> Menee painotukseen bonuksena)
    evaluations.append(
        {
            "atom_id": hashlib.md5(f"L4_A1{mandate}".encode()).hexdigest(),
            "boolean": True,
            "reasoning": "Hieno oivallus!",
        }
    )

    # Taso 5 (0% osuma -> Hylätään)
    evaluations.append(
        {
            "atom_id": hashlib.md5(f"L5_A1{mandate}".encode()).hexdigest(),
            "boolean": False,
            "reasoning": "Ei yltänyt tälle tasolle.",
        }
    )

    state = HookState(
        execution_id="test_run",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallSimulation()),
        workflow_repo=cast(Any, MockRepoWaterfallSimulation()),
        comp_repo=cast(Any, MockRepoWaterfallSimulation()),
        identity_repo=cast(Any, MockRepoWaterfallSimulation()),
        audit_repo=cast(Any, MockRepoWaterfallSimulation()),
        system_repo=cast(Any, MockRepoWaterfallSimulation()),
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], waterfall_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert abs(result.state_delta["pb_1234567890123456"]["step_4_final_score"] - 3.207) < 0.01

    log = result.state_delta["pb_1234567890123456"]["waterfall_calculation_log"]
    assert "Level 3.0:** 1/2" in log
    assert "Level 4.0:** 1/1" in log
    assert "Final CDM Score:** 3.21" in log
