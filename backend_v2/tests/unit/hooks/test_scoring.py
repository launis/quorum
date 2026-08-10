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
                "label": {"default_locale": "en", "translations": {"en": "Test Claim", "fi": "Test Claim"}},
                "ai_description": "Test Claim Desc",
                "tda_assertions": [
                    {
                        "tda_id": f"tda_{hashlib.md5(atom.encode()).hexdigest()[:32]}",
                        "concept_description": atom,
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
        "label": {"default_locale": "en", "translations": {"en": "Test Label", "fi": "Test Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
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
        "name": {"default_locale": "en", "translations": {"en": "Test Step", "fi": "Test Step"}},
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
        "output_profile_id": "prof_1111111111111111",
        "status": "PENDING",
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
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
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
                "justification": "[INITIALIZING]",
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
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
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
                "name": {"default_locale": "en", "translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
                "status": "active",
                "version": 1,
                "default_profile_id": "prof_1111111111111111",
                "allowed_exports": ["pdf"],
                "historical_context_mode": "DISABLED",
                "enable_contextual_overrides": True,
            }

        async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
            return {
                "id": profile_id,
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
                "strictness_level": 85,
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
        prompt_block_repo=cast(Any, MockRepoTapa2()),
        output_profile_repo=cast(Any, MockRepoTapa2()),
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
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
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
            return _build_valid_pb_dict(self.pb_instruction, [], pb_type="instruction", category_id="system_rule")  # noqa: E501

    async def get_execution(self, execution_id: str) -> dict[str, Any]:
        return _build_valid_execution_dict(execution_id)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "WATERFALL",
            "layouts": [],
            "display_scale": "original",
        }


@pytest.mark.asyncio
async def test_matrix_scoring_hook_ignores_instructions() -> None:
    """Test that waterfall scoring gracefully skips instructional PromptBlocks without crashing."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={
            "results": [
                {
                    "tda_id": atom_hash,
                    "status": ExecutionStatus.PASSED,
                    "evaluation_reasoning": "Valid reasoning",
                    "source_quote": "mock quote",
                    "contextual_override": False,
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
        prompt_block_repo=cast(Any, MockRepoWaterfallMixed()),
        output_profile_repo=cast(Any, MockRepoWaterfallMixed()),
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
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        evaluations.append(
            {
                "tda_id": atom_hash,
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta["pb_1234567890123456"]["raw_score"] == 5.0
    assert result.state_delta["pb_1234567890123456"]["justification"] == "[INITIALIZING]"
    assert result.state_delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_waterfall_engine_breakdown"


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_matrix_scoring_hook_ceiling_cap() -> None:
    """Test that the waterfall ceiling caps the final score despite high weighted score."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Level 1: 1/1 (ok), Level 2: 0/1 (fails), Level 3, 4, 5: 1/1 (ok)
    for i in range(1, 6):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = True if i != 2 else False
        evaluations.append(
            {
                "tda_id": atom_hash,
                "status": ExecutionStatus.PASSED if is_hit else "FAIL",
                "evaluation_reasoning": "",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )

    state = HookState(
        execution_id="ex_2222222222222222",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
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
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []
    # Fail level 3
    for i in range(1, 4):
        atom_hash = generate_atom_hash(f"atom_{i}", mandate)
        is_hit = False if i == 3 else True
        reasoning = "Testivaste" if not is_hit else "OK"
        evaluations.append(
            {
                "tda_id": atom_hash,
                "status": ExecutionStatus.PASSED if is_hit else "FAIL",
                "evaluation_reasoning": reasoning,
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )  # noqa: E501
    from backend_v2.exceptions import AppException

    # The hook should now Fail-Fast because `results` list is missing valid AtomResultDTO data (status is string FAIL, not ExecutionStatus)
    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[Any], matrix_scoring_hook(state, deps))

    assert "Strict Fail-Fast" in str(exc_info.value)


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
        return _build_valid_execution_dict(execution_id, strategy="AVERAGE")

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return {
            "id": "wflow_1234567890123456",
            "slug": "test_workflow",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Test Desc"}},
            "status": "active",
            "version": 1,
            "default_profile_id": "prof_1111111111111111",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "enable_contextual_overrides": True,
        }

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any]:
        return {
            "id": profile_id,
            "slug": "test_slug",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
            "strictness_level": 85,
            "scoring_strategy": "AVERAGE",
            "layouts": [],
            "display_scale": "original",
        }


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_matrix_scoring_hook_full_simulation() -> None:
    """Simulates a complex real-world evaluation trace to ensure mathematical perfection."""
    from backend_v2.models.enums import ExecutionStatus

    evaluations = []

    # Taso 1 (100% osuma)
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )

    # Taso 2 (100% osuma)
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )

    # Taso 3 (50% osuma -> Hit Rate < 90% -> VESIPUTOUS PYSÄHTYY)
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Oikein",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )
    evaluations.append(
        {
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Aihetodistetta EI esitetty.",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )

    # Taso 4 (100% osuma -> Menee painotukseen bonuksena)
    evaluations.append(
        {
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Hieno oivallus!",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )

    # Taso 5 (0% osuma -> Hylätään)
    evaluations.append(
        {
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Ei yltänyt tälle tasolle.",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    )

    state = HookState(
        execution_id="ex_9999999999999999",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfallSimulation()),
        workflow_repo=cast(Any, MockRepoWaterfallSimulation()),
        comp_repo=cast(Any, MockRepoWaterfallSimulation()),
        prompt_block_repo=cast(Any, MockRepoWaterfallSimulation()),
        output_profile_repo=cast(Any, MockRepoWaterfallSimulation()),
        identity_repo=cast(Any, MockRepoWaterfallSimulation()),
        audit_repo=cast(Any, MockRepoWaterfallSimulation()),
        system_repo=cast(Any, MockRepoWaterfallSimulation()),
    )  # noqa: E501

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta["pb_1234567890123456"]["raw_score"] > 1.0
    assert result.state_delta["pb_1234567890123456"]["justification"] == "[INITIALIZING]"
    assert (
        result.state_delta["pb_1234567890123456"]["xai_log"]["pedagogical_key"] == "xai_pure_average_engine_breakdown"
    )


@pytest.mark.asyncio
async def test_matrix_scoring_hook_missing_status_key() -> None:
    """Test that matrix_scoring_hook operates robustly even when evaluations omit the 'status' key."""
    evaluations = []

    # Successful atom evaluation: lacks 'status' key (optional field)
    evaluations.append(
        {
            "evaluation_reasoning": "Valid analytical statement",
            "source_quote": "mock quote",
            "contextual_override": False,
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
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    # The hook should now Fail-Fast because the first atom is missing 'tda_id' and 'status'
    from backend_v2.exceptions import AppException

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[Any], matrix_scoring_hook(state, deps))

    assert "Strict Fail-Fast" in str(exc_info.value)





@pytest.mark.asyncio
async def test_matrix_scoring_hook_dynamic_penalty() -> None:
    """Test that matrix_level score correctly applies the dynamic penalty without affecting the global scale improperly."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # Total 5 atoms, 1 CONTESTED, 4 PASS
    for i in range(1, 5):
        evaluations.append(
            {
                "tda_id": generate_atom_hash(f"atom_{i}", mandate),
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )
    evaluations.append(
        {
            "tda_id": generate_atom_hash("atom_5", mandate),
            "status": ExecutionStatus.PASSED,
            "evaluation_reasoning": "Contested",
            "source_quote": "mock quote",
            "contextual_override": True,
        }
    )

    state = HookState(
        execution_id="exec_0123456789abcdef",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None

    # 5 atoms -> 100% hits. Unpenalized score is 5.0.
    # 1 CONTESTED atom -> relative penalty (1/5 * 15% = 3%) -> 5.0 * 0.97 = 4.85.
    raw_score = result.state_delta["pb_1234567890123456"]["raw_score"]
    assert abs(raw_score - 4.85) < 0.01
    assert (
        "DYNAMIC PENALTY APPLIED: -3.0% for CONTESTED atoms"
        in result.state_delta["pb_1234567890123456"]["justification"]
    )


@pytest.mark.asyncio
async def test_matrix_scoring_hook_cognitive_collapse() -> None:
    """Test that Cognitive Collapse lock correctly rejects a matrix exceeding the 3 atom or 50% threshold."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    evaluations = []

    # 5 atoms, 4 CONTESTED, 1 PASS -> >3 contested atoms AND >50% contested
    for i in range(1, 2):
        evaluations.append(
            {
                "tda_id": generate_atom_hash(f"atom_{i}", mandate),
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Hyväksytty",
                "source_quote": "mock quote",
                "contextual_override": False,
            }
        )
    for i in range(2, 6):
        evaluations.append(
            {
                "tda_id": generate_atom_hash(f"atom_{i}", mandate),
                "status": ExecutionStatus.PASSED,
                "evaluation_reasoning": "Contested",
                "source_quote": "mock quote",
                "contextual_override": True,
            }
        )

    state = HookState(
        execution_id="exec_abcdef0123456789",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None

    # Should trigger cognitive collapse lock but assign the minimum mathematical score (1.0)
    raw_score = result.state_delta["pb_1234567890123456"].get("raw_score")
    assert raw_score == 1.0
    assert (
        "[INDETERMINATE] Matrix score invalidated because the cognitive collapse safety lock was triggered"
        in result.state_delta["pb_1234567890123456"]["justification"]
    )


@pytest.mark.asyncio
async def test_matrix_scoring_hook_quote_evidence_crash() -> None:
    """Test to reproduce the ValidationInfo.context crash when generating QuoteEvidenceDTO."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    # Provide exact_quotes to trigger the QuoteEvidenceDTO instantiation
    # Nyt status = FAIL (todistamaan uusi toiminnallisuus)
    evaluations = [
        {
            "tda_id": atom_hash,
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Hyväksytty",
            "source_quote": "mock quote",
            "contextual_override": False,
        }
    ]

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    # This should crash because QuoteEvidenceDTO is created without validation context
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True


@pytest.mark.asyncio
async def test_matrix_scoring_hook_empty_evaluations() -> None:
    from backend_v2.hooks.scoring import matrix_scoring_hook
    from backend_v2.models.v2_core import PromptBlock

    pb = _build_valid_pb_dict("blk_1111111111111111", [_build_valid_scale(1, ["atom_test"])])
    state = HookState(
        inputs={"results": [], "extracted_facts": {}, "execution_metadata": {}},
        step_id="sp_empty_evals",
        execution_id="exe_1111111111111111",
        workflow_id="wf_1",
        task_blueprint="sp_1",
        metadata={},
        global_context_vars={
            "matrix_blocks": [("blk_1111111111111111", PromptBlock(**pb))],
            "scoring_profile": {"id": "prof_1", "scoring_strategy": "baseline", "strictness_level": "normal"},
        },
    )
    from typing import cast

    from backend_v2.tests.unit.hooks.test_scoring import MockRepoWaterfall

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockRepoWaterfall()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )
    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result is not None
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta["results"] == []


@pytest.mark.asyncio
async def test_matrix_scoring_hook_propagates_extensions() -> None:
    """Test that matrix_scoring_hook aggregates atom-level extensions into the Matrix output."""
    from backend_v2.models.enums import EvaluationMandate, ExecutionStatus

    mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
    atom_hash = generate_atom_hash("atom_1", mandate)

    # Simulate a DAG-mode response where AtomResultDTO has extensions
    evaluations = [
        {
            "tda_id": atom_hash,
            "status": ExecutionStatus.FAILED,
            "evaluation_reasoning": "Missing requirement",
            "source_quote": "mock quote",
            "contextual_override": False,
            "extensions": {"coaching": "This is a coaching tip."},
        }
    ]

    state = HookState(
        execution_id="ex_3333333333333333",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": evaluations, "extracted_facts": {}},
        global_context_vars={},
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": ["coaching", "falsification", "remediation_steps"],
                "visible_workflow_extensions": [],
                "layouts": [],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )
    from backend_v2.hooks.scoring import matrix_scoring_hook

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    matrix_output = result.state_delta.get("pb_1234567890123456")
    assert matrix_output is not None, "Matrix output should be in state_delta"

    # The bug: extensions is an empty dict {} because they were ignored
    extensions = matrix_output.get("extensions", {})
    assert "coaching" in extensions, "Coaching extension was not propagated to Matrix output"
    assert extensions["coaching"] == "This is a coaching tip.", "Coaching extension text mismatch"


@pytest.mark.asyncio
async def test_scoring_matrix_namespace_isolation() -> None:
    """Test that Matrix B evaluations leaking into Matrix A's loop are ignored."""
    from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
    from backend_v2.hooks.scoring import matrix_scoring_hook
    from backend_v2.models.enums import ExecutionStatus

    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_1", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": "pb_OTHER_MATRIX",
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Reason",
        "source_quote": "mock quote",
        "contextual_override": False,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": [ev_dict], "extracted_facts": {}},
        global_context_vars={},
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "layouts": [],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    matrix_output = result.state_delta.get("pb_1234567890123456")
    assert matrix_output is not None
    # Because it's isolated, the atom should NOT be evaluated in this matrix
    assert matrix_output.get("evaluated_atoms", {}).get(atom_hash) is False
    assert matrix_output.get("raw_score") == 1.0


@pytest.mark.asyncio
async def test_scoring_regular_tda_path_bypasses_namespace_check() -> None:
    """Test that Regular TDA evaluations (matrix_id=None) bypass the namespace check."""
    from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
    from backend_v2.hooks.scoring import matrix_scoring_hook
    from backend_v2.models.enums import ExecutionStatus

    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_3", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": None,
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Reason",
        "source_quote": "mock quote",
        "contextual_override": False,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": [ev_dict], "extracted_facts": {}},
        global_context_vars={},
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "layouts": [],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    matrix_output = result.state_delta.get("pb_1234567890123456")
    assert matrix_output is not None
    # Because matrix_id=None bypasses isolation, it should be evaluated in this matrix
    assert atom_hash in matrix_output.get("evaluated_atoms", {})
    assert matrix_output.get("evaluated_atoms", {}).get(atom_hash) is True
    # Score may still be 1.0 due to waterfall cascade failure on other levels, but the atom was evaluated!


@pytest.mark.asyncio
async def test_failed_atom_with_override_does_not_inflate_score() -> None:
    """Test that a FAILED atom with contextual_override=True does NOT inflate the matrix score."""
    from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
    from backend_v2.hooks.scoring import matrix_scoring_hook
    from backend_v2.models.enums import ExecutionStatus

    mandate = "FAIL_FAST_NO_EVIDENCE"
    atom_hash = generate_atom_hash("atom_3", mandate)

    ev_dict = {
        "tda_id": atom_hash,
        "matrix_id": "pb_1234567890123456",
        "status": ExecutionStatus.FAILED,
        "evaluation_reasoning": "Failed reason",
        "source_quote": None,
        "contextual_override": True,
    }

    state = HookState(
        execution_id="ex_1111111111111111",
        workflow_id="wf1",
        step_id="step1",
        task_blueprint="step1",
        metadata={},
        inputs={"results": [ev_dict], "extracted_facts": {}},
        global_context_vars={},
    )

    class MockOutputProfileRepoWaterfallPropagates(MockRepoWaterfall):
        async def get_output_profile_by_id(self, _id: str) -> dict[str, Any]:
            return {
                "id": "prof_1111111111111111",
                "slug": "test_slug",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Test Profile", "fi": "Test Profile"}},
                "strictness_level": 100,
                "scoring_strategy": "WATERFALL",
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "layouts": [],
            }

    deps = HookDependencies(
        exec_repo=cast(Any, MockRepoWaterfall()),
        workflow_repo=cast(Any, MockRepoWaterfall()),
        comp_repo=cast(Any, MockRepoWaterfall()),
        prompt_block_repo=cast(Any, MockRepoWaterfall()),
        output_profile_repo=cast(Any, MockOutputProfileRepoWaterfallPropagates()),
        identity_repo=cast(Any, MockRepoWaterfall()),
        audit_repo=cast(Any, MockRepoWaterfall()),
        system_repo=cast(Any, MockRepoWaterfall()),
    )

    result = await cast(Awaitable[HookResult], matrix_scoring_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    matrix_output = result.state_delta.get("pb_1234567890123456")
    assert matrix_output is not None
    # Defense-in-depth ensures is_satisfied = False despite contextual_override
    assert matrix_output.get("evaluated_atoms", {}).get(atom_hash) is False
