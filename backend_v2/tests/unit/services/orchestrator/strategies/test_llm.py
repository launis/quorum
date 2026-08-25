import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_step_by_id = AsyncMock()
    repo.get_all_prompt_blocks = AsyncMock(return_value=[])
    repo.get_output_profile_by_id = AsyncMock(
        return_value={
            "id": "prof_0123456789abcdef0123456789abcdef",
            "slug": "test",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "workflow_id": "wf_123",
            "organization_id": "root",
        }
    )
    repo.get_workflow = AsyncMock(
        return_value={
            "id": "wf_0123456789abcdef",
            "slug": "test",
            "name": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof",
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "steps": [],
        }
    )
    repo.get_execution = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = AsyncMock()
    engine.execute = AsyncMock()
    return engine


from backend_v2.services.orchestrator.strategies.base import StrategyDependencies


@pytest.fixture
def llm_strategy(mock_repo: MagicMock, mock_compiler: MagicMock, mock_engine: MagicMock) -> LLMNodeStrategy:
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
async def test_execute_fails_fast_if_no_blueprint(llm_strategy: LLMNodeStrategy) -> None:
    """Test that LLMNodeStrategy fails fast if task_blueprint is missing."""
    # Create a step without task_blueprint
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = None

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"

    with pytest.raises(AppException) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "has no task_blueprint configured" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_if_blueprint_not_found(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that LLMNodeStrategy fails fast if task_blueprint is not found in database."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "invalid_blueprint_id"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"

    # Mock DB returning None
    mock_repo.get_step_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_profile_id(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that execution fails fast if metadata is missing profile_id."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {}  # MISSING profile_id

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": ["blk_0123456789abcdef0123456789abcdef"],
        "model_strategy": "standard",
    }

    # Needs to bypass pre-hooks smoothly
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import patch

    from backend_v2.exceptions import ConfigurationError

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(ConfigurationError) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "missing mandatory 'profile_id'" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_prompt_block(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that execution fails fast if a referenced prompt block is missing from database."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123"}

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": ["missing_block_999"],
        "model_strategy": "standard",
    }

    # DB returns only the protocol block
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_573802341db9d68c",
            "slug": "zero_trust_extraction_protocol",
            "category_id": "system_rule",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "description": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "ai_description": "Strict extraction protocol.",
        }
    ]

    # Needs to bypass pre-hooks smoothly
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "PromptBlock 'missing_block_999' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_success_path_structured_output(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test a successful execution path using structured output to cover core orchestration."""
    step = MagicMock()
    step.id = "step_success"
    step.task_blueprint = "bp_success"
    step.input_mappings = {"$test": "path.to.test"}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    from backend_v2.models.state import StepOutputDTO

    projector.snapshot = [StepOutputDTO(step_id="path", block_id="to", data_type="matrix", payload={"test": "value"})]

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": ["blk_0123456789abcdef0123456789abcdef"],
        "model_strategy": "standard",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_0123456789abcdef0123456789abcdef",
            "slug": "test_block",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Label", "fi": "Label"}},
            "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
            "ai_description": "Test Block AI Desc",
        },
        {
            "id": "blk_573802341db9d68c",
            "slug": "zero_trust_extraction_protocol",
            "category_id": "system_rule",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "description": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "ai_description": "Strict extraction protocol.",
        },
    ]
    mock_repo.get_workflow.return_value = {
        "id": "wf_0123456789abcdef0123456789abcdef",
        "slug": "test",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prf_123",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"path": {"to": {"test": "value"}}}
    mock_hook_state.global_context_vars = {}

    from unittest.mock import AsyncMock, patch

    from backend_v2.models.dtos.engine import EngineExecutionResult

    llm_strategy._engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[], hydrated_references={}
    )

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"blocks": []}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].event_type == "output"

    # Verify that DAG components were invoked
    llm_strategy._engine.execute.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_llm_strategy_missing_atoms_crash(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test that a matrix step without shuffled_atoms raises a structured AppException."""
    step = MagicMock()
    step.id = "step_missing_atoms"
    step.task_blueprint = "bp_success"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_matrix",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_2222222222222222",
        "criteria_block_ids": ["blk_1111111111111111"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1111111111111111",
            "slug": "matrix_block",
            "category_id": "matrix",
            "type": "float",
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test"}},
            "scales": [
                {
                    "score": 1,
                    "ai_label": "bad",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Test"}},
                            "tda_assertions": [
                                {
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                    "concept_description": "mock concept description",
                                }
                            ],
                        }
                    ],
                },
                {
                    "score": 5,
                    "ai_label": "good",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Test"}},
                            "tda_assertions": [
                                {
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                    "concept_description": "mock concept description",
                                }
                            ],
                        }
                    ],
                },
            ],
        },
        {
            "id": "blk_2222222222222222",
            "slug": "system_block",
            "category_id": "system_rule",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test"}},
        },
    ]
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}  # Missing shuffled_atoms
    mock_hook_state.global_context_vars = {}

    from unittest.mock import AsyncMock, patch

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
    ):
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "missing 'shuffled_atoms'" in exc_info.value.message


@pytest.mark.asyncio
async def test_llm_strategy_invalid_shuffled_atoms_type(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test that a matrix step with invalid shuffled_atoms raises a ValidationError."""
    from pydantic import ValidationError

    step = MagicMock()
    step.id = "step_invalid_atoms"
    step.task_blueprint = "bp_success"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_matrix",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_2222222222222222",
        "criteria_block_ids": ["blk_1111111111111111"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1111111111111111",
            "slug": "matrix_block",
            "category_id": "matrix",
            "type": "float",
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test"}},
            "scales": [
                {
                    "score": 1,
                    "ai_label": "bad",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Test"}},
                            "tda_assertions": [
                                {
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                    "concept_description": "mock concept description",
                                }
                            ],
                        }
                    ],
                },
                {
                    "score": 5,
                    "ai_label": "good",
                    "claims": [
                        {
                            "label": {"default_locale": "en", "translations": {"en": "Test"}},
                            "tda_assertions": [
                                {
                                    "inverse_evidence": False,
                                    "aggregation_mode": "EXISTS",
                                    "concept_description": "mock concept description",
                                }
                            ],
                        }
                    ],
                },
            ],
        },
        {
            "id": "blk_2222222222222222",
            "slug": "system_block",
            "category_id": "system_rule",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Test"}},
            "description": {"default_locale": "en", "translations": {"en": "Test"}},
        },
    ]
@pytest.mark.asyncio
async def test_execute_with_role_and_persona_and_protocol(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test successful execution with role, persona, and extraction protocol blocks."""
    step = MagicMock()
    step.id = "step_full_blocks"
    step.task_blueprint = "bp_full"
    step.input_mappings = {"$doc": "inputs.doc"}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    from backend_v2.models.state import StepOutputDTO

    projector.snapshot = [StepOutputDTO(step_id="inputs", block_id="doc", data_type="text", payload="Sample text for extraction")]

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "fi"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 1

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "full_step",
        "name": {"default_locale": "en", "translations": {"en": "Full Step", "fi": "Täysi vaihe"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Kuvaus"}},
        "role_block_id": "blk_1111111111111111",
        "execution_persona_block_id": "blk_2222222222222222",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1111111111111111",
            "slug": "role_lead",
            "category_id": "agent_role",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Role"}},
            "description": {"default_locale": "en", "translations": {"en": "Role"}},
            "ai_description": "Act as an expert auditor.",
        },
        {
            "id": "blk_2222222222222222",
            "slug": "persona_strict",
            "category_id": "execution_persona",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Persona"}},
            "description": {"default_locale": "en", "translations": {"en": "Persona"}},
            "ai_description": "Strict Persona.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate clarity.",
        },
    ]

    mock_repo.get_workflow.return_value = {
        "id": "wf_0123456789abcdef0123456789abcdef",
        "slug": "test_wf",
        "name": {"default_locale": "en", "translations": {"en": "Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Workflow"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_123",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "steps": [
            {
                "id": "stp_0123456789abcdef0123456789abcdef",
                "task_blueprint": "bp_full",
                "depends_on": [],
                "input_mappings": {},
            }
        ],
    }
    from unittest.mock import AsyncMock, patch

    from backend_v2.models.dtos.engine import EngineExecutionResult
    from backend_v2.models.v2_core import ExecutionRecord, FrozenContext

    mock_repo.get_step = AsyncMock(return_value=mock_repo.get_step_by_id.return_value)

    mock_repo.get_execution.return_value = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        source_identity_manifest={"inputs": "Input Document"},
    )

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[], hydrated_references={}, usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, cost_usd=0.001)
    )

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"inputs": {"doc": "Sample text for extraction"}}
    mock_hook_state.global_context_vars = {}

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"output": "Extracted result"}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=FrozenContext(),
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].event_type == "output"
    assert traces[0].content["_step_metadata"]["token_usage"]["total_tokens"] == 150
    assert traces[0].content["_step_metadata"]["model_strategy"] == "standard"


@pytest.mark.asyncio
async def test_execute_synthesis_engine_path(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test LLM strategy synthesis path with typed output."""
    from unittest.mock import AsyncMock, patch

    step = MagicMock()
    step.id = "step_synthesis"
    step.task_blueprint = "bp_synth"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {
        "__GLOBAL_ATOM_BLACKBOARD__": {"atoms_by_input": {"doc_1": []}}
    }
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "synthesis"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "synth_step",
        "name": {"default_locale": "en", "translations": {"en": "Synth"}},
        "description": {"default_locale": "en", "translations": {"en": "Synth"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "synthesis",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {
        "prev_step": {"evaluations": [{"tda_id": "tda_123", "score": 4.0}]}
    }
    mock_hook_state.global_context_vars = context.global_context_vars

    from pydantic import BaseModel

    class MockSynthesisDTO(BaseModel):
        summary: str

    from backend_v2.models.dtos.engine import EngineExecutionResult

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[],
        hydrated_references={},
        synthesis_output=MockSynthesisDTO(summary="Synthesized Analysis"),
        usage=TokenUsage(prompt_tokens=200, completion_tokens=80, total_tokens=280, cost_usd=0.002),
    )

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"summary": "Synthesized Analysis"}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].content["summary"] == "Synthesized Analysis"


@pytest.mark.asyncio
async def test_execute_anomaly_retry_flow(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test LLM anomaly retry loop triggering execution state update and retry."""
    from unittest.mock import AsyncMock, patch

    step = MagicMock()
    step.id = "step_retry"
    step.task_blueprint = "bp_retry"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "retry_step",
        "name": {"default_locale": "en", "translations": {"en": "Retry"}},
        "description": {"default_locale": "en", "translations": {"en": "Retry"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, ExecutionStepState

    mock_exec_record = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        step_states={
            "step_retry": ExecutionStepState(id="step_retry", label="Retry Step", status=ExecutionStatus.RUNNING)
        },
    )
    mock_repo.get_execution.return_value = mock_exec_record
    mock_repo.update_execution = AsyncMock()

    from backend_v2.models.dtos.engine import EngineExecutionResult

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[], hydrated_references={}
    )

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}
    mock_hook_state.global_context_vars = {}

    from unittest.mock import AsyncMock, patch

    call_count = 0

    async def _post_hooks_side_effect(*args: Any, **kwargs: Any) -> tuple[Any, list[Any]]:
        nonlocal call_count
        call_count += 1
        post_state = MagicMock()
        if call_count == 1:
            post_state.inputs = {"llm_anomaly_retry_requested": True}
        else:
            post_state.inputs = {"output": "Success after retry"}
        return (post_state, [])

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", side_effect=_post_hooks_side_effect),
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].content["output"] == "Success after retry"
    mock_repo.update_execution.assert_called_once()


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_role_block(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when configured role block is missing in database."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123"}

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "role_block_id": "blk_1111111111111111",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }
    mock_repo.get_all_prompt_blocks.return_value = []

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    from backend_v2.exceptions import ConfigurationError

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(ConfigurationError) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "Role Block 'blk_1111111111111111' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_persona_block(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when configured execution persona block is missing in database."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123"}

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "role_block_id": None,
        "execution_persona_block_id": "blk_2222222222222222",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        }
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    from backend_v2.exceptions import ConfigurationError

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(ConfigurationError) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "Execution Persona Block 'blk_2222222222222222' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_output_profile(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when output profile is not found in database."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "nonexistent_profile", "target_locale": "en"}

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate clarity.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]
    mock_repo.get_output_profile_by_id.return_value = None

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert "OutputProfile 'nonexistent_profile' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_no_engine_configured(
    mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test fail-fast when LLMNodeStrategy has no ExecutionEngine configured."""
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
    strategy_no_engine = LLMNodeStrategy(deps=deps, engine=None)

    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate clarity.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with (
        patch.object(strategy_no_engine, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await strategy_no_engine.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "has no ExecutionEngine configured" in exc_info.value.message


def test_configure_llm_context_hook_success() -> None:
    """Test that the LLM hook correctly resolves provider configuration."""
    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.hooks.llm import configure_llm_context_hook

    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        step_id="step1",
        inputs={},
        global_context_vars={"workflow_model_mapping": {"step1": "fast"}},
        metadata={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with patch("backend_v2.hooks.llm.get_settings") as mock_settings:
        mock_settings.return_value.default_model_strategy = "fast"
        mock_settings.return_value.model_registry = {
            "id": "reg_0123456789abcdef0123456789abcdef",
            "slug": "model_registry",
            "type": "model_registry",
            "models": {
                "fast": {
                    "provider": "google",
                    "model_name": "gemini",
                    "temperature": 0.7,
                    "tpm_limit": 100000,
                    "rpm_limit": 100,
                }
            },
        }

        result = configure_llm_context_hook(state, deps)

        assert result.success is True
        assert result.state_delta is not None
        assert "llm_config" in result.state_delta
        assert result.state_delta["llm_config"]["provider"] == "google"


def test_configure_llm_context_hook_empty_state() -> None:
    from typing import cast
    from unittest.mock import MagicMock

    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.hooks.llm import configure_llm_context_hook

    result = configure_llm_context_hook(
        cast(HookState, None),
        HookDependencies(
            exec_repo=MagicMock(),
            workflow_repo=MagicMock(),
            comp_repo=MagicMock(),
            prompt_block_repo=AsyncMock(),
            output_profile_repo=AsyncMock(),
            identity_repo=MagicMock(),
            audit_repo=MagicMock(),
            system_repo=MagicMock(),
        ),
    )
    assert result.success is True
    assert result.state_delta == {}


def test_configure_llm_context_hook_error() -> None:
    from unittest.mock import MagicMock, patch

    import pytest

    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.exceptions import AppException
    from backend_v2.hooks.llm import configure_llm_context_hook

    state = HookState(
        execution_id="123", workflow_id="wf1", step_id="step1", inputs={}, global_context_vars={}, metadata={}
    )

    with patch("backend_v2.hooks.llm.get_settings") as mock_settings:
        mock_settings.return_value.default_model_strategy = "fast"
        mock_settings.return_value.model_registry = None

        with pytest.raises(AppException):
            configure_llm_context_hook(
                state,
                HookDependencies(
                    exec_repo=MagicMock(),
                    workflow_repo=MagicMock(),
                    comp_repo=MagicMock(),
                    prompt_block_repo=AsyncMock(),
                    output_profile_repo=AsyncMock(),
                    identity_repo=MagicMock(),
                    audit_repo=MagicMock(),
                    system_repo=MagicMock(),
                ),
            )


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_target_locale(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when execution metadata is missing target_locale."""
    from backend_v2.exceptions import ConfigurationError

    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123"}  # No target_locale

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(ConfigurationError) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "missing mandatory 'target_locale'" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_exec_record_fetch_error(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when fetching execution record throws an exception."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_repo.get_execution.side_effect = RuntimeError("DB connection dropped")

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert exc_info.value.status_code == 404
    assert "Execution record 'exec_1' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_matrix_chunking_flow(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test full matrix execution with chunking and tone instruction."""
    from unittest.mock import AsyncMock, patch

    from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
    from backend_v2.models.dtos.engine import EngineExecutionResult

    step = MagicMock()
    step.id = "step_matrix"
    step.task_blueprint = "bp_matrix"
    step.input_mappings = {}
    step.allowed_mcp_tools = ["custom_tool"]

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 1

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "matrix_step",
        "name": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "description": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_5555555555555555"],
        "model_strategy": "standard",
    }

    matrix_block_dict = {
        "id": "blk_5555555555555555",
        "slug": "eval_matrix",
        "category_id": "matrix",
        "type": "float",
        "label": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "description": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "ai_description": "Analyze against theoretical framework.",
        "theory_grounding": None,
        "allow_contextual_override": True,
        "is_lightweight_protocol": True,
        "scales": [
            {
                "score": 1,
                "ai_label": "LOW",
                "claims": [],
            },
            {
                "score": 5,
                "ai_label": "HIGH",
                "claims": [],
            },
        ],
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        matrix_block_dict,
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_0123456789abcdef0123456789abcdef",
        "slug": "exec_profile",
        "workflow_id": "wf_0123456789abcdef0123456789abcdef",
        "name": {"default_locale": "en", "translations": {"en": "Profile"}},
        "description": {"default_locale": "en", "translations": {"en": "Profile"}},
        "tone_instruction": {
            "default_locale": "en",
            "translations": {"en": "Professional and analytical."},
        },
        "layouts": [],
    }

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {
        "shuffled_atoms": [
            {"atom_id": "atm_1111111111111111", "question": "Atom 1"},
            {"atom_id": "atm_2222222222222222", "question": "Atom 2"},
        ]
    }
    mock_hook_state.global_context_vars = {}

    from backend_v2.models.v2_core import ExecutionRecord, FrozenContext

    mock_repo.get_execution.return_value = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        source_identity_manifest={"doc_1": "Uploaded Document"},
    )

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[],
        hydrated_references={},
        usage=TokenUsage(prompt_tokens=300, completion_tokens=100, total_tokens=400, cost_usd=0.005),
    )

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"results": [{"tda_id": "tda_1111111111111111", "score": 5}]}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=FrozenContext(),
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].content["results"][0]["score"] == 5


@pytest.mark.asyncio
async def test_execute_anomaly_retry_exceeded_limit(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test LLM anomaly retry when max retry limit is exceeded."""
    from unittest.mock import AsyncMock, patch

    step = MagicMock()
    step.id = "step_retry_max"
    step.task_blueprint = "bp_retry_max"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "retry_max_step",
        "name": {"default_locale": "en", "translations": {"en": "Retry Max"}},
        "description": {"default_locale": "en", "translations": {"en": "Retry Max"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    from backend_v2.models.dtos.engine import EngineExecutionResult

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[], hydrated_references={}
    )

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}
    mock_hook_state.global_context_vars = {}

    async def _always_retry_post_hooks(*args: Any, **kwargs: Any) -> tuple[Any, list[Any]]:
        post_state = MagicMock()
        post_state.inputs = {"llm_anomaly_retry_requested": True}
        return (post_state, [])

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", side_effect=_always_retry_post_hooks),
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
        )

    assert len(traces) == 1
    assert traces[0].content.get("anomaly_unresolved") is True


@pytest.mark.asyncio
async def test_execute_fails_fast_on_corrupted_prompt_block_in_db(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when a prompt block in the DB cannot be parsed by PromptBlockAdapter."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.prompt_blocks = None

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {"invalid_field": "corrupted_payload"}
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "Malformed PromptBlock in DB" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_empty_shuffled_atoms_list(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when matrix step contains an empty shuffled_atoms list in state."""
    step = MagicMock()
    step.id = "step_matrix"
    step.task_blueprint = "bp_matrix"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "matrix_step",
        "name": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "description": {"default_locale": "en", "translations": {"en": "Matrix"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_5555555555555555"],
        "model_strategy": "standard",
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_5555555555555555",
            "slug": "eval_matrix",
            "category_id": "matrix",
            "type": "float",
            "label": {"default_locale": "en", "translations": {"en": "Matrix"}},
            "description": {"default_locale": "en", "translations": {"en": "Matrix"}},
            "ai_description": "Analyze.",
            "theory_grounding": None,
            "allow_contextual_override": True,
            "scales": [
                {
                    "score": 1,
                    "ai_label": "LOW",
                    "claims": [],
                },
                {
                    "score": 5,
                    "ai_label": "HIGH",
                    "claims": [],
                },
            ],
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"shuffled_atoms": []}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "Strict Fail-Fast Enforced: 'shuffled_atoms' is empty" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_sets_running_event_and_handles_string_inputs(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
    """Test that execute triggers running_event and unwraps string inputs."""
    from unittest.mock import AsyncMock, patch

    from backend_v2.models.state import StepOutputDTO

    step = MagicMock()
    step.id = "step_str_input"
    step.task_blueprint = "bp_str_input"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = [
        StepOutputDTO(step_id="inputs", block_id="inputs", data_type="text", payload="Direct plain text content"),
    ]

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []
    context.strictness_level = 0

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "str_step",
        "name": {"default_locale": "en", "translations": {"en": "Str Step"}},
        "description": {"default_locale": "en", "translations": {"en": "Str Step"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
        "model_strategy": "standard",
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    from backend_v2.models.dtos.engine import EngineExecutionResult

    mock_engine = llm_strategy._engine
    mock_engine.execute.return_value = EngineExecutionResult(  # type: ignore
        results=[], hydrated_references={}
    )

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}
    mock_hook_state.global_context_vars = {}

    running_evt = asyncio.Event()

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.strategies.llm.EngineExecutionRequest"),
        patch("litellm.token_counter", return_value=10),
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"output": "Direct execution"}
        mock_post.return_value = (mock_post_hook_state, [])

        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
            semaphore=asyncio.Semaphore(2),
            running_event=running_evt,
        )

    assert running_evt.is_set() is True
    assert len(traces) == 1


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_model_strategy_in_context(
    llm_strategy: LLMNodeStrategy, mock_repo: MagicMock
) -> None:
    """Test fail-fast when context has no model_strategy defined."""
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"
    step.input_mappings = {}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = []

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.global_context_vars = {}
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = ""
    context.expected_inputs = []

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "model_strategy": "standard",
        "extraction_protocol_block_id": "blk_3333333333333333",
        "criteria_block_ids": ["blk_4444444444444444"],
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_4444444444444444",
            "slug": "criteria_rule",
            "category_id": "system_rule",
            "type": "string",
            "label": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria"}},
            "ai_description": "Evaluate.",
        },
        {
            "id": "blk_3333333333333333",
            "slug": "zero_trust",
            "category_id": "protocol",
            "type": "instruction",
            "label": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol"}},
            "ai_description": "Zero trust protocol.",
        },
    ]

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}

    from unittest.mock import AsyncMock, patch

    with patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre:
        mock_pre.return_value = (mock_hook_state, [])
        with pytest.raises(AppException) as exc_info:
            await llm_strategy.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=None,
                trace=[],
                semaphore=asyncio.Semaphore(2),
            )

    assert "has no model_strategy defined" in exc_info.value.message
