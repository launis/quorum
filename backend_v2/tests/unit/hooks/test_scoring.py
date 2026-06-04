import hashlib
from collections.abc import Awaitable
from typing import Any, cast

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import normalize_matrix_scores_hook
from backend_v2.models.enums import XaiExtensionType


def generate_atom_hash(text: str, mandate: Any = None) -> str:
    return f"tda_{hashlib.md5(text.encode()).hexdigest()[:32]}"


def _build_valid_scale(score: Any, micro_atoms: list[str] | None = None) -> dict[str, Any]:
    claims = []
    if micro_atoms is not None:
        claims.append(
            {
                "label": {"default_locale": "en", "translations": {"en": "Test Claim"}},
                "ai_description": "Test Claim Desc",
                "tda_assertions": [
                    {
                        "tda_id": f"tda_{hashlib.md5(atom.encode()).hexdigest()[:32]}",
                        "ai_rule_description": atom,
                        "inverse_evidence": False,
                        "aggregation_mode": "EXISTS",
                    }
                    for atom in micro_atoms
                ],
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
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": prompt_blocks,
    }


def _build_valid_execution_dict(execution_id: str, strategy: str = "WATERFALL") -> dict[str, Any]:
    from datetime import datetime, timezone

    return {
        "id": execution_id,
        "workflow_id": "wf_123",
        "organization_id": "org_123",
        "created_by": "usr_123",
        "output_profile_id": "prof_123",
        "status": "running",
        "raw_inputs": {},
        "execution_trace": [],
        "step_states": {},
        "frozen_context": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


class MockRepository:
    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return _build_valid_step_dict(["pb_1234567890123456"])

    async def get_prompt_block_by_id(self, slug: str) -> dict[str, Any]:
        return _build_valid_pb_dict("pb_1234567890123456", [_build_valid_scale("not_a_number")])

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_123",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "strictness_level": 50,
            "scoring_strategy": "WATERFALL",
            "layouts": [],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_normalize_matrix_scores_fails_on_corrupt_scale() -> None:
    """Test that setting a corrupted non-float scale in PromptBlocks causes a fail fast AppException."""
    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={
            "pb_1234567890123456": {
                "raw_score": 5.0,
                "normalized_score": 100.0,
                "justification": "",
                "evaluated_atoms": {},
                "extensions": {},
            }
        },
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

        async def get_execution(self, execution_id: str) -> dict[str, Any]:
            return _build_valid_execution_dict(execution_id)

        async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
            return {
                "id": "wflow_1234567890123456",
                "slug": "test_workflow",
                "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
                "status": "active",
                "version": 1,
                "default_profile_id": "prof_123",
                "enable_contextual_overrides": True,
            }

        async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
            return {
                "id": profile_id,
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test"}},
                "strictness_level": 50,
                "scoring_strategy": "WATERFALL",
                "layouts": [],
                "display_scale": "original",
            }

    state = HookState(
        execution_id="ex_1234567890abcdef",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        metadata={},
        inputs={
            "tb_1234567890123456": {
                "raw_score": 5.0,
                "normalized_score": 100.0,
                "justification": "Tämä on perustelu\n\nKitkaa on",
                "evaluated_atoms": {},
                "extensions": {
                    XaiExtensionType.CITATION: "Ote lähteestä",
                    XaiExtensionType.FALSIFICATION: "Vastalause",
                },
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


from backend_v2.hooks.scoring import matrix_scoring_hook


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

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_123",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "strictness_level": 50,
            "scoring_strategy": "WATERFALL",
            "layouts": [],
            "display_scale": "original",
        }


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

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_123",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "strictness_level": 50,
            "scoring_strategy": "WATERFALL",
            "layouts": [],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_matrix_scoring_hook_ignores_instructions() -> None:
    """Test that waterfall scoring gracefully skips instructional PromptBlocks without crashing."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={
            "evaluations": [
                {
                    "atom_id": atom_hash,
                    "status": "PASS",
                    "semantic_reasoning": "",
                    "contextual_override": False,
                    "structural_location": "",
                }
            ],
            "extracted_facts": {},
        },
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
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_pass_all() -> None:
    """Test standard hybrid model when everything passes."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        evaluations.append(
            {
                "atom_id": atom_hash,
                "status": "PASS",
                "semantic_reasoning": "Hyväksytty",
                "contextual_override": False,
                "structural_location": "",
            }
        )

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations, "extracted_facts": {}},
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

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta["pb_1234567890123456"]["raw_score"] == 5.0
    assert result.state_delta["pb_1234567890123456"]["justification"] == ""
    assert result.state_delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_waterfall_engine_breakdown"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_ceiling_cap() -> None:
    """Test that the waterfall ceiling caps the final score despite high weighted score."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Level 1: 1/1 (ok), Level 2: 0/1 (fails), Level 3, 4, 5: 1/1 (ok)
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = True if i != 2 else False
        evaluations.append(
            {
                "atom_id": atom_hash,
                "status": "PASS" if is_hit else "FAIL",
                "semantic_reasoning": "",
                "contextual_override": False,
                "structural_location": "",
            }
        )

    state = HookState(
        execution_id="ex_2222222222222222",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations, "extracted_facts": {}},
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
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None

    # Floor should be 1.0 (Level 2 failed).
    # Weighted math: (1*1 + 0*2 + 1*3 + 1*4 + 1*5) = 13 achieved weights. Max weights: 15. Proportional = 13/15.  # noqa: E501
    # Score = 1.0 + (13/15 * 4.0) = 1.0 + 3.46 = 4.46.
    # But Capped at Floor (1.0) + 1.0 = 2.0!
    assert abs(result.state_delta["pb_1234567890123456"]["raw_score"] - 1.9) < 0.01


@pytest.mark.asyncio
async def test_matrix_scoring_hook_graceful_missing() -> None:
    """Test missing context formatting logic."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Fail level 3
    for i in range(1, 4):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = False if i == 3 else True
        reasoning = "Testivaste" if not is_hit else "OK"
        evaluations.append(
            {
                "atom_id": atom_hash,
                "status": "PASS" if is_hit else "FAIL",
                "semantic_reasoning": reasoning,
                "contextual_override": False,
                "structural_location": "",
            }
        )

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations, "extracted_facts": {}},
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
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    # Level 1 (100%), Level 2 (100%), Level 3 (0%) -> Floor 2.0.
    # Weighted: (1*1 + 1*2 + 0) / (1+2+3) = 3 / 6 = 50%.
    # Weighted Score: 1.0 + (0.5 * 4.0) = 3.0. Max cap: 2.0 + 1.0 = 3.0. So score is 3.0.
    assert result.state_delta["pb_1234567890123456"]["raw_score"] == 2.0


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

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return _build_valid_execution_dict(execution_id, strategy="DAMPENING")

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_123",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "strictness_level": 50,
            "scoring_strategy": "DAMPENING",
            "layouts": [],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_matrix_scoring_hook_full_simulation() -> None:
    """Simulates a complex real-world evaluation trace to ensure mathematical perfection."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Taso 1 (100% osuma)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L1_A1", mandate),
            "status": "PASS",
            "semantic_reasoning": "Oikein",
            "contextual_override": False,
            "structural_location": "",
        }
    )
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L1_A2", mandate),
            "status": "PASS",
            "semantic_reasoning": "Oikein",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    # Taso 2 (100% osuma)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L2_A1", mandate),
            "status": "PASS",
            "semantic_reasoning": "Oikein",
            "contextual_override": False,
            "structural_location": "",
        }
    )
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L2_A2", mandate),
            "status": "PASS",
            "semantic_reasoning": "Oikein",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    # Taso 3 (50% osuma -> Hit Rate < 90% -> VESIPUTOUS PYSÄHTYY)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L3_A1", mandate),
            "status": "PASS",
            "semantic_reasoning": "Oikein",
            "contextual_override": False,
            "structural_location": "",
        }
    )
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L3_A2", mandate),
            "status": "FAIL",
            "semantic_reasoning": "Aihetodistetta EI esitetty.",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    # Taso 4 (100% osuma -> Menee painotukseen bonuksena)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L4_A1", mandate),
            "status": "PASS",
            "semantic_reasoning": "Hieno oivallus!",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    # Taso 5 (0% osuma -> Hylätään)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("L5_A1", mandate),
            "status": "FAIL",
            "semantic_reasoning": "Ei yltänyt tälle tasolle.",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    state = HookState(
        execution_id="ex_9999999999999999",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations, "extracted_facts": {}},
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

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert abs(result.state_delta["pb_1234567890123456"]["raw_score"] - 3.306) < 0.01
    assert result.state_delta["pb_1234567890123456"]["justification"] == ""
    assert result.state_delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_dampening_engine_breakdown"


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_status_key() -> None:
    """Test that matrix_scoring_hook operates robustly even when evaluations omit the 'status' key."""
    from backend_v2.models.enums import EvaluationMandate

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Successful atom evaluation: lacks 'status' key (optional field)
    evaluations.append(
        {
            "atom_id": generate_atom_hash("atom_1", mandate),
            "semantic_reasoning": "Valid analytical statement",
            "contextual_override": False,
            "structural_location": "",
        }
    )

    # Failed/DLQ item: lacks 'atom_id' but has '_dlq_status'
    evaluations.append(
        {
            "_dlq_status": "FAILED/DLQ",
            "reason": "Simulated pipeline timeout",
        }
    )

    state = HookState(
        execution_id="exe_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"evaluations": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    # The run should succeed and process the valid atom, ignoring the DLQ item in cognitive loop
    assert result.success is True
    assert result.state_delta is not None
    # Verify it processed atom_1 and not the DLQ chunk
    assert "pb_1234567890123456" in result.state_delta
