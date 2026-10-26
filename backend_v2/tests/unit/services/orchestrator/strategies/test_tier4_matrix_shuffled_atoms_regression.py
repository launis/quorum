"""Regression tests for Tier 4 bug: Matrix step missing 'shuffled_atoms' in state data.

Root Cause:
In commit cb0549e6b, FlatteningHookOutput was refactored in state_reducer.py to route
shuffled_atoms directly to GlobalContextVarsDTO.shuffled_atoms (eliminating dict mutation
in ExecutionInputsDTO.dynamic_inputs). However, LLMNodeStrategy.execute still read
shuffled_atoms from state_data["shuffled_atoms"] (which derives from inputs.dynamic_inputs),
causing KeyError: 'shuffled_atoms' and failing every matrix step with:
AppException: Matrix step missing 'shuffled_atoms' in state data.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import ExecutionInputsDTO, HookState
from backend_v2.exceptions import AppException
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionResult, FlattenedAtom
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    repo = InMemoryUnifiedWorkflowRepository()
    repo.set_output_profiles(
        [
            {
                "id": "prof_0123456789abcdef0123456789abcdef",
                "slug": "test",
                "name": {"translations": {"en": "Test"}},
                "workflow_id": "wf_0123456789abcdef0123456789abcdef",
                "organization_id": "root",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_1234567890123456",
                        "title": {"translations": {"en": "Test"}},
                        "target_blocks": ["*"],
                    }
                ],
            }
        ]
    )
    repo.set_workflow(
        {
            "id": "wf_0123456789abcdef0123456789abcdef",
            "slug": "test",
            "name": {"translations": {"en": "Test"}},
            "description": {"translations": {"en": "Test"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_0123456789abcdef0123456789abcdef",
            "historical_context_mode": "DISABLED",
            "model_registry_id": "cfg_model_registry_01",
            "steps": [],
        }
    )
    repo.set_step(
        {
            "id": "stp_0123456789abcdef0123456789abcdef",
            "slug": "matrix_step",
            "name": {"translations": {"en": "Matrix"}},
            "description": {"translations": {"en": "Matrix"}},
            "role_block_id": None,
            "extraction_protocol_block_id": "blk_3333333333333333",
            "criteria_block_ids": ["blk_5555555555555555"],
        }
    )
    repo.set_prompt_blocks(
        [
            {
                "id": "blk_5555555555555555",
                "slug": "eval_matrix",
                "category_id": "matrix",
                "type": "float",
                "label": {"translations": {"en": "Matrix"}},
                "description": {"translations": {"en": "Matrix"}},
                "ai_description": "Analyze against theoretical framework.",
                "theory_grounding": None,
                "allow_contextual_override": True,
                "is_lightweight_protocol": True,
                "scales": [
                    {"score": 1, "ai_label": "LOW", "claims": []},
                    {"score": 5, "ai_label": "HIGH", "claims": []},
                ],
            },
            {
                "id": "blk_3333333333333333",
                "slug": "zero_trust",
                "category_id": "protocol",
                "type": "instruction",
                "label": {"translations": {"en": "Protocol"}},
                "description": {"translations": {"en": "Protocol"}},
                "protocol_instructions": "Zero trust protocol.",
            },
        ]
    )
    repo.set_execution(
        ExecutionRecord(
            id="exe_0123456789abcdef0123456789abcdef",
            workflow_id="wf_0123456789abcdef0123456789abcdef",
            output_profile_id="prof_0123456789abcdef0123456789abcdef",
            target_locale="en",
            metadata=ExecutionMetadata(),
            source_identity_manifest={"doc_1": "Uploaded Document"},
        )
    )
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    compiler = MagicMock()
    compiler.compile_static_instructions.return_value = "Static instructions"
    mock_schema = MagicMock()
    mock_schema.model_json_schema.return_value = {"type": "object"}
    compiler.build_dynamic_schema.return_value = mock_schema
    return compiler


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = AsyncMock()
    engine.execute = AsyncMock(
        return_value=EngineExecutionResult(
            results=[],
            hydrated_references={},
            usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, cost_usd=0.001),
        )
    )
    return engine


@pytest.fixture
def llm_strategy(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
    mock_engine: MagicMock,
) -> LLMNodeStrategy:
    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    return LLMNodeStrategy(deps=deps, engine=mock_engine)


@pytest.mark.asyncio
async def test_matrix_step_resolves_shuffled_atoms_from_global_context_vars(
    llm_strategy: LLMNodeStrategy,
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify that a matrix step reads shuffled_atoms from HookState.global_context_vars.

    In the buggy code, LLMNodeStrategy queries state_data["shuffled_atoms"], raising:
    AppException: Matrix step missing 'shuffled_atoms' in state data.
    When fixed, it resolves shuffled_atoms from global_context_vars and passes them to
    EngineExecutionRequest.
    """
    sample_atoms = [
        FlattenedAtom(
            atom_id="atm_1111111111111111",
            question="Question 1",
            depends_on=(),
            acceptance_criteria=(),
            anti_patterns=(),
            syntactic_anchors=(),
        ),
        FlattenedAtom(
            atom_id="atm_2222222222222222",
            question="Question 2",
            depends_on=(),
            acceptance_criteria=(),
            anti_patterns=(),
            syntactic_anchors=(),
        ),
    ]

    hook_state_with_gvars = HookState(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        step_id="step_1",
        task_blueprint="stp_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(shuffled_atoms=sample_atoms),
        inputs=ExecutionInputsDTO(),  # Note: dynamic_inputs is empty, does NOT have shuffled_atoms
    )

    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "stp_0123456789abcdef0123456789abcdef"
    step.input_mappings = {}
    step.allowed_mcp_tools = []
    step.expected_sdui_type = "grid"

    context = MagicMock()
    context.execution_id = "exe_0123456789abcdef0123456789abcdef"
    context.workflow_id = "wf_0123456789abcdef0123456789abcdef"
    context.global_context_vars = GlobalContextVarsDTO(shuffled_atoms=sample_atoms)
    context.target_locale = "en"
    context.output_profile_id = "prof_0123456789abcdef0123456789abcdef"
    context.organization_id = None
    context.metadata = ExecutionMetadata()
    context.expected_inputs = []
    context.cognitive_tier = "fast"
    context.strictness_level = 0.7
    context.model_registry_id = None
    context.prompt_blocks = None

    projector = MagicMock()
    projector.get_state_for_step.return_value = {}

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm_strategy.LLMClient.from_tier", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm_strategy.EngineExecutionRequest") as mock_req,
        patch("litellm.token_counter", return_value=10),
    ):
        mock_req.side_effect = lambda **kwargs: MagicMock(**kwargs)
        mock_pre.return_value = (hook_state_with_gvars, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"results": []}
        mock_post.return_value = (mock_post_hook_state, [])

        # In buggy code, this raises AppException("Matrix step missing 'shuffled_atoms' in state data.")
        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=FrozenContext(),
            trace=[],
        )

    assert traces is not None
    assert mock_req.called
    req_kwargs = mock_req.call_args.kwargs
    assert req_kwargs["shuffled_atoms"] is not None
    assert len(req_kwargs["shuffled_atoms"]) == 2
    assert req_kwargs["shuffled_atoms"][0].atom_id == "atm_1111111111111111"


@pytest.mark.asyncio
async def test_matrix_step_missing_shuffled_atoms_fails_fast(
    llm_strategy: LLMNodeStrategy,
) -> None:
    """Verify that a matrix step raises AppException when shuffled_atoms is None."""
    hook_state_missing = HookState(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        step_id="step_1",
        task_blueprint="stp_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(),
    )

    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "stp_0123456789abcdef0123456789abcdef"
    step.input_mappings = {}
    step.allowed_mcp_tools = []
    step.expected_sdui_type = "grid"

    context = MagicMock()
    context.execution_id = "exe_0123456789abcdef0123456789abcdef"
    context.workflow_id = "wf_0123456789abcdef0123456789abcdef"
    context.global_context_vars = GlobalContextVarsDTO()
    context.target_locale = "en"
    context.output_profile_id = "prof_0123456789abcdef0123456789abcdef"
    context.organization_id = None
    context.metadata = ExecutionMetadata()
    context.expected_inputs = []
    context.cognitive_tier = "fast"
    context.strictness_level = 0.7
    context.model_registry_id = None
    context.prompt_blocks = None

    projector = MagicMock()
    projector.get_state_for_step.return_value = {}

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (hook_state_missing, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=FrozenContext(),
                trace=[],
            )

    assert exc_info.value.status_code == 500
    assert "Matrix step missing 'shuffled_atoms' in global_context_vars." in exc_info.value.message


@pytest.mark.asyncio
async def test_matrix_step_empty_shuffled_atoms_fails_fast(
    llm_strategy: LLMNodeStrategy,
) -> None:
    """Verify that a matrix step raises AppException when shuffled_atoms is an empty list."""
    hook_state_empty = HookState(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        step_id="step_1",
        task_blueprint="stp_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(shuffled_atoms=[]),
        inputs=ExecutionInputsDTO(),
    )

    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "stp_0123456789abcdef0123456789abcdef"
    step.input_mappings = {}
    step.allowed_mcp_tools = []
    step.expected_sdui_type = "grid"

    context = MagicMock()
    context.execution_id = "exe_0123456789abcdef0123456789abcdef"
    context.workflow_id = "wf_0123456789abcdef0123456789abcdef"
    context.global_context_vars = GlobalContextVarsDTO(shuffled_atoms=[])
    context.target_locale = "en"
    context.output_profile_id = "prof_0123456789abcdef0123456789abcdef"
    context.organization_id = None
    context.metadata = ExecutionMetadata()
    context.expected_inputs = []
    context.cognitive_tier = "fast"
    context.strictness_level = 0.7
    context.model_registry_id = None
    context.prompt_blocks = None

    projector = MagicMock()
    projector.get_state_for_step.return_value = {}

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (hook_state_empty, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=FrozenContext(),
                trace=[],
            )

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast Enforced: 'shuffled_atoms' is empty" in exc_info.value.message
