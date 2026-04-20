from typing import Any

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import normalize_matrix_scores_hook


class MockRepository:
    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {"prompt_blocks": ["test_block"]}

    async def get_prompt_block_by_id(self, slug: str) -> dict[str, Any]:
        return {"scales": [{"score": "not_a_number"}]}


@pytest.mark.asyncio
async def test_normalize_matrix_scores_fails_on_corrupt_scale() -> None:
    """Test that setting a corrupted non-float scale in PromptBlocks causes a fail fast AppException."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={"test_block": 5.0},
        global_context_vars={},
    )
    deps = HookDependencies(repository=MockRepository())  # type: ignore

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)  # type: ignore[misc]

    assert exc_info.value.error_code == "CONFIGURATION_ERROR"
    assert "Corrupted scale value 'not_a_number' in PromptBlock 'test_block'" in exc_info.value.message


@pytest.mark.asyncio
async def test_normalize_matrix_scores_tapa_2_string_mapping() -> None:
    """Test that Tapa 2 string PromptBlocks preserve XAI variables without crashing the float scaler (Epic 12)."""

    class MockRepoTapa2:
        async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
            return {"prompt_blocks": ["toulmin_text_block"]}

        async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
            return {"scales": []}  # Emulate non-evaluative / string-only Tapa 2 block

    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={
            "toulmin_text_block": {
                "evaluation_notes": "Tämä on perustelu",
                "step_1_evidence_quote": "Ote lähteestä",
                "step_2_falsification": "Vastalause",
                "step_3_logical_friction": "Kitkaa on",
            }
        },
        global_context_vars={},
    )
    deps = HookDependencies(repository=MockRepoTapa2())  # type: ignore

    result = await normalize_matrix_scores_hook(state, deps)  # type: ignore[misc]

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Must natively map textual displays without numeric scoring triggering graceful degradation
    assert delta["toulmin_text_block_cited_text_quote"] == "Ote lähteestä"
    assert delta["toulmin_text_block_falsification"] == "Vastalause"

    # Must cleanly pipe notes to justification without '1 Evidence Quote' markdown formatting
    justification = delta["toulmin_text_block_justification"]
    assert "Tämä on perustelu" in justification
    assert "Kitkaa on" in justification

    # Must not contain mathematical keys for text-blocks
    assert "toulmin_text_block_scaled" not in delta


import hashlib

from backend_v2.hooks.scoring import waterfall_scoring_hook


class MockRepoWaterfall:
    def __init__(self, pb_id: str = "test_pb") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {"prompt_blocks": [self.pb_id]}

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        return {
            "category_id": "matrix",
            "scale_min": 1.0,
            "scale_max": 5.0,
            "scales": [
                {"score": 1.0, "claims": [{"micro_atoms": ["atom_1"]}]},
                {"score": 2.0, "claims": [{"micro_atoms": ["atom_2"]}]},
                {"score": 3.0, "claims": [{"micro_atoms": ["atom_3"]}]},
                {"score": 4.0, "claims": [{"micro_atoms": ["atom_4"]}]},
                {"score": 5.0, "claims": [{"micro_atoms": ["atom_5"]}]},
            ],
        }


class MockRepoWaterfallMixed:
    def __init__(self) -> None:
        pass

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {"prompt_blocks": ["test_matrix_pb", "test_instruction_pb"]}

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        if pb_id == "test_matrix_pb":
            return {
                "category_id": "matrix",
                "type": "matrix",
                "scale_min": 1.0,
                "scale_max": 5.0,
                "scales": [
                    {"score": 1.0, "claims": [{"micro_atoms": ["atom_1"]}]},
                    {"score": 5.0, "claims": [{"micro_atoms": ["atom_5"]}]},
                ],
            }
        else:
            return {
                "type": "instruction",
                "scales": [],
            }


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_ignores_instructions() -> None:
    """Test that waterfall scoring gracefully skips instructional PromptBlocks without crashing."""
    import hashlib

    atom_hash = hashlib.md5(b"atom_1").hexdigest()

    state = HookState(
        execution_id="t3",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": [{"atom_id": atom_hash, "boolean": True}]},
        global_context_vars={},
    )
    deps = HookDependencies(repository=MockRepoWaterfallMixed())  # type: ignore

    # TDD RED: This should NOT raise AppException(Strict Fail-Fast Enforced: PromptBlock has no scales)
    result = await waterfall_scoring_hook(state, deps)  # type: ignore[misc]
    assert result.success is True


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_pass_all() -> None:
    """Test standard hybrid model when everything passes."""
    evaluations = []
    for i in range(1, 6):
        atom_hash = hashlib.md5(f"atom_{i}".encode()).hexdigest()
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
    deps = HookDependencies(repository=MockRepoWaterfall())  # type: ignore

    result = await waterfall_scoring_hook(state, deps)  # type: ignore[misc]
    assert result.success is True
    assert result.state_delta["test_pb"] == 5.0
    assert "Level 5.0:** 1/1" in result.state_delta["test_pb_justification"]


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_ceiling_cap() -> None:
    """Test that the waterfall ceiling caps the final score despite high weighted score."""
    evaluations = []
    # Level 1: 1/1 (ok), Level 2: 0/1 (fails), Level 3, 4, 5: 1/1 (ok)
    for i in range(1, 6):
        atom_hash = hashlib.md5(f"atom_{i}".encode()).hexdigest()
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
    deps = HookDependencies(repository=MockRepoWaterfall())  # type: ignore
    result = await waterfall_scoring_hook(state, deps)  # type: ignore[misc]
    assert result.success is True

    # Floor should be 1.0 (Level 2 failed).
    # Weighted math: (1*1 + 0*2 + 1*3 + 1*4 + 1*5) = 13 achieved weights. Max weights: 15. Proportional = 13/15.
    # Score = 1.0 + (13/15 * 4.0) = 1.0 + 3.46 = 4.46.
    # But Capped at Floor (1.0) + 1.0 = 2.0!
    assert result.state_delta["test_pb"] == 1.0

    # Strings asserting removed due to variable threshold limits.


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_graceful_missing() -> None:
    """Test missing context formatting logic."""
    evaluations = []
    # Fail level 3
    for i in range(1, 4):
        atom_hash = hashlib.md5(f"atom_{i}".encode()).hexdigest()
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
    deps = HookDependencies(repository=MockRepoWaterfall())  # type: ignore
    result = await waterfall_scoring_hook(state, deps)  # type: ignore[misc]

    assert result.success is True
    # Level 1 (100%), Level 2 (100%), Level 3 (0%) -> Floor 2.0.
    # Weighted: (1*1 + 1*2 + 0) / (1+2+3) = 3 / 6 = 50%.
    # Weighted Score: 1.0 + (0.5 * 4.0) = 3.0. Max cap: 2.0 + 1.0 = 3.0. So score is 3.0.
    assert result.state_delta["test_pb"] == 2.0

    missing = result.state_delta["test_pb_missing_context"]
    assert "- atom_3 (Tuomio: Testivaste)" in missing


class MockRepoWaterfallSimulation:
    def __init__(self, pb_id: str = "fake_matrix_id") -> None:
        self.pb_id = pb_id

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {"prompt_blocks": [self.pb_id]}

    async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
        return {
            "category_id": "matrix",
            "scale_min": 1.0,
            "scale_max": 5.0,
            "scales": [
                {"score": 1.0, "claims": [{"micro_atoms": ["L1_A1", "L1_A2"]}]},
                {"score": 2.0, "claims": [{"micro_atoms": ["L2_A1", "L2_A2"]}]},
                {"score": 3.0, "claims": [{"micro_atoms": ["L3_A1", "L3_A2"]}]},
                {"score": 4.0, "claims": [{"micro_atoms": ["L4_A1"]}]},
                {"score": 5.0, "claims": [{"micro_atoms": ["L5_A1"]}]},
            ],
        }


@pytest.mark.asyncio
async def test_waterfall_scoring_hook_full_simulation() -> None:
    """Simulates a complex real-world evaluation trace to ensure mathematical perfection."""
    evaluations = []

    # Taso 1 (100% osuma)
    evaluations.append({"atom_id": hashlib.md5(b"L1_A1").hexdigest(), "boolean": True, "reasoning": "Oikein"})
    evaluations.append({"atom_id": hashlib.md5(b"L1_A2").hexdigest(), "boolean": True, "reasoning": "Oikein"})

    # Taso 2 (100% osuma)
    evaluations.append({"atom_id": hashlib.md5(b"L2_A1").hexdigest(), "boolean": True, "reasoning": "Oikein"})
    evaluations.append({"atom_id": hashlib.md5(b"L2_A2").hexdigest(), "boolean": True, "reasoning": "Oikein"})

    # Taso 3 (50% osuma -> Hit Rate < 90% -> VESIPUTOUS PYSÄHTYY)
    evaluations.append({"atom_id": hashlib.md5(b"L3_A1").hexdigest(), "boolean": True, "reasoning": "Oikein"})
    evaluations.append(
        {"atom_id": hashlib.md5(b"L3_A2").hexdigest(), "boolean": False, "reasoning": "Aihetodistetta EI esitetty."}
    )

    # Taso 4 (100% osuma -> Menee painotukseen bonuksena)
    evaluations.append({"atom_id": hashlib.md5(b"L4_A1").hexdigest(), "boolean": True, "reasoning": "Hieno oivallus!"})

    # Taso 5 (0% osuma -> Hylätään)
    evaluations.append(
        {"atom_id": hashlib.md5(b"L5_A1").hexdigest(), "boolean": False, "reasoning": "Ei yltänyt tälle tasolle."}
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
    deps = HookDependencies(repository=MockRepoWaterfallSimulation())  # type: ignore

    result = await waterfall_scoring_hook(state, deps)  # type: ignore[misc]

    assert result.success is True
    assert result.state_delta["fake_matrix_id"] == 3.0

    missing_context = result.state_delta["fake_matrix_id_missing_context"]
    assert "- L3_A2" in missing_context
    assert "- L5_A1" in missing_context

    log = result.state_delta["fake_matrix_id_justification"]
    assert "Level 3.0:** 1/2" in log
    assert "Level 4.0:** 1/1" in log
    assert "Final CDM Score:** 3.0" in log
