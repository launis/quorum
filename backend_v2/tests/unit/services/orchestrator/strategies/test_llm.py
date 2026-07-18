import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
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
            "id": "wf_123",
            "slug": "test",
            "name": {"translations": {}},
            "description": {"translations": {}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof",
            "steps": [],
        }
    )
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.fixture
def llm_strategy(mock_repo: MagicMock, mock_compiler: MagicMock) -> LLMNodeStrategy:
    return LLMNodeStrategy(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )  # noqa: E501


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
    }

    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"path": {"to": {"test": "value"}}}
    mock_hook_state.global_context_vars = {}

    from unittest.mock import AsyncMock, patch

    with (
        patch.object(llm_strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(llm_strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock),
        patch(
            "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_0", new_callable=AsyncMock
        ) as mock_phase_0,
        patch(
            "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_1", new_callable=AsyncMock
        ) as mock_phase_1,
        patch(
            "backend_v2.services.orchestrator.sliding_window_linker.SlidingWindowLinker.link_graph",
            new_callable=AsyncMock,
        ) as mock_link,
        patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.EnrichedDagExecutor.execute_graph",
            new_callable=AsyncMock,
        ) as mock_execute_graph,
        patch("backend_v2.services.orchestrator.result_projector.ResultProjector.project") as mock_project,
    ):
        mock_pre.return_value = (mock_hook_state, [])
        mock_post_hook_state = MagicMock()
        mock_post_hook_state.inputs = {"blocks": []}
        mock_post.return_value = (mock_post_hook_state, [])

        mock_project.return_value = ([], {})

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
    mock_phase_0.assert_called_once()
    mock_phase_1.assert_called_once()
    mock_link.assert_called_once()
    mock_execute_graph.assert_called_once()


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
        from typing import cast

        from backend_v2.core.hook_registry import HookResult

        result = cast(HookResult, configure_llm_context_hook(state, deps))

        assert result.success is True
        assert result.state_delta is not None
        assert "llm_config" in result.state_delta
        assert result.state_delta["llm_config"]["provider"] == "google"


def test_configure_llm_context_hook_empty_state() -> None:
    from typing import cast
    from unittest.mock import MagicMock

    from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
    from backend_v2.hooks.llm import configure_llm_context_hook

    result = cast(
        HookResult,
        configure_llm_context_hook(
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
        ),
    )
    assert result.success is True
    assert result.state_delta == {}


def test_configure_llm_context_hook_error() -> None:
    from unittest.mock import MagicMock

    import pytest

    from backend_v2.core.hook_registry import HookDependencies, HookState
    from backend_v2.exceptions import AppException
    from backend_v2.hooks.llm import configure_llm_context_hook

    state = HookState(
        execution_id="123", workflow_id="wf1", step_id="step1", inputs={}, global_context_vars={}, metadata={}
    )

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
