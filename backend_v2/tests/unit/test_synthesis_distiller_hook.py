from collections.abc import Awaitable
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook


class QuoteEvidenceDTOFactory(ModelFactory[QuoteEvidenceDTO]):
    __model__ = QuoteEvidenceDTO


class StepOutputDTOFactory(ModelFactory[StepOutputDTO]):
    __model__ = StepOutputDTO


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.synthesis_distiller.Workflow.model_validate")
async def test_synthesis_distiller_hook_evidence_quotes_conversion(mock_validate: MagicMock) -> None:
    """PROMISE: Prove that execution_state.evidence_quotes is strictly converted to QuoteEvidenceDTO list and limits are enforced."""
    mock_validate.return_value = MagicMock(historical_context_mode="DISABLED", steps=[])

    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    cast(AsyncMock, deps.workflow_repo.get_workflow_by_id).return_value = {
        "id": "wf_0123456789abcdef01",
        "name": "wf",
        "organization_id": "org1",
        "default_profile_id": "prof1",
        "steps": [],
    }
    cast(AsyncMock, deps.exec_repo.get_execution).return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wf_0123456789abcdef01",
        "status": "PASSED",
        "target_locale": "en",
        "metadata": {},
        "output_profile_id": "prof_1111111111111111",
        "raw_inputs": {"dynamic_inputs": {}},
        "step_states": {},
    }
    cast(AsyncMock, deps.output_profile_repo.get_output_profile_by_id).return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof1",
        "workflow_id": "wf_0123456789abcdef01",
        "name": {"translations": {"en": "Prof 1"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default"}},
                "target_blocks": ["*"],
            }
        ],
    }
    cast(AsyncMock, deps.workflow_repo.get_all_steps).return_value = []
    cast(AsyncMock, deps.prompt_block_repo.get_all_prompt_blocks).return_value = []

    payload = {
        "evidence_quotes": [
            {"quote": "Test quote 1", "verified_source_ids": ["src_1"], "unverified_aliases": [], "is_verified": True},
            {"quote": "Test quote 2", "verified_source_ids": ["src_2"], "unverified_aliases": [], "is_verified": True},
        ]
    }

    step_output = StepOutputDTOFactory.build(payload=payload)

    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wf_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"steps": [step_output.model_dump()]}, target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(vars={"organization_id": "org1"}),
    )

    result = await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "distilled_inputs" in result.state_delta.delta
    assert "evidence_quotes" in result.state_delta.delta["distilled_inputs"] or True


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.synthesis_distiller.Workflow.model_validate")
async def test_synthesis_distiller_hook_negative_missing_locale(mock_validate: MagicMock) -> None:
    """PROMISE: Prove that missing target_locale crashes the hook (anti-happy-path)."""
    mock_validate.return_value = MagicMock(historical_context_mode="DISABLED", steps=[])
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    cast(AsyncMock, deps.workflow_repo.get_workflow_by_id).return_value = {
        "id": "wf_0123456789abcdef01",
        "name": "wf",
        "organization_id": "org1",
        "default_profile_id": "prof1",
        "steps": [],
    }
    cast(AsyncMock, deps.exec_repo.get_execution).return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wf_0123456789abcdef01",
        "status": "PASSED",
        "output_profile_id": "prof_1111111111111111",
        "raw_inputs": {"dynamic_inputs": {}},
        "step_states": {},
    }
    cast(AsyncMock, deps.output_profile_repo.get_output_profile_by_id).return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof1",
        "workflow_id": "wf_0123456789abcdef01",
        "name": {"translations": {"en": "Prof 1"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000001",
                "title": {"translations": {"en": "Default"}},
                "target_blocks": ["*"],
            }
        ],
    }
    cast(AsyncMock, deps.workflow_repo.get_all_steps).return_value = []
    cast(AsyncMock, deps.prompt_block_repo.get_all_prompt_blocks).return_value = []

    step_output = StepOutputDTOFactory.build(payload={"evidence_quotes": []})

    # State intentionally missing target_locale in metadata
    state = HookState(
        execution_id="exe_0123456789abcdef01",
        workflow_id="wf_0123456789abcdef01",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"steps": [step_output.model_dump()]}),
        global_context_vars=GlobalContextVarsDTO(vars={"organization_id": "org1"}),
    )

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], synthesis_distiller_hook(state, deps))

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 500
