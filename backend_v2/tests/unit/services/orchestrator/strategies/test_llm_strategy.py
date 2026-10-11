"""Unit tests for LLMNodeStrategy output profile prompt directives and system prompt invariance."""

import hashlib
import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import HookState
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import BlockDataType, CognitiveTier, ExecutionStatus, PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class DummySynthesisOutputDTO(BaseModel):
    model_config = ConfigDict(extra="allow")
    output: str = "success"


@pytest.fixture
def test_repo() -> InMemoryUnifiedWorkflowRepository:
    repo = InMemoryUnifiedWorkflowRepository()

    # Setup system config model registry for cognitive tier
    reg = SystemConfigModelRegistry.model_validate(
        {
            "id": "sys_e26807f3bfa3454d",
            "name": "Default Stack",
            "tier_definitions": {
                "fast": {
                    "provider": "google",
                    "model_name": "gemini-2.5-flash",
                    "temperature": 0.0,
                    "max_tokens": 4096,
                    "tpm_limit": 100000,
                    "rpm_limit": 100,
                },
                "balanced": {
                    "provider": "google",
                    "model_name": "gemini-2.5-flash",
                    "temperature": 0.0,
                    "max_tokens": 4096,
                    "tpm_limit": 100000,
                    "rpm_limit": 100,
                },
                "deep": {
                    "provider": "google",
                    "model_name": "gemini-2.5-flash",
                    "temperature": 0.0,
                    "max_tokens": 4096,
                    "tpm_limit": 100000,
                    "rpm_limit": 100,
                },
                "reasoning": {
                    "provider": "google",
                    "model_name": "gemini-2.5-flash",
                    "temperature": 0.0,
                    "max_tokens": 4096,
                    "tpm_limit": 100000,
                    "rpm_limit": 100,
                },
            },
        }
    )
    repo.set_model_registry(reg)

    # Setup Workflow
    repo.set_workflow(
        {
            "id": "wor_0123456789abcdef",
            "slug": "test_wf",
            "name": {"translations": {"en": "Test WF"}},
            "description": {"translations": {"en": "Test Desc"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_0123456789abcdef0123456789abcde1",
            "historical_context_mode": "DISABLED",
            "model_registry_id": "sys_e26807f3bfa3454d",
            "steps": [],
        }
    )

    # Setup Execution Record
    exec_rec = ExecutionRecord(
        id="exc_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PENDING,
        target_locale="en",
        steps=[],
    )
    repo.set_execution(exec_rec)

    # Setup Prompt Blocks
    repo.set_prompt_blocks(
        [
            {
                "id": "blk_0123456789abcdef",
                "slug": "test_protocol",
                "category_id": PromptBlockCategory.PROTOCOL.value,
                "type": BlockDataType.STRING.value,
                "label": {"translations": {"en": "Protocol"}},
                "description": {"translations": {"en": "Protocol"}},
                "protocol_instructions": "Extract all claims strictly according to protocol.",
            },
            {
                "id": "blk_0123456789abcde0",
                "slug": "test_criteria",
                "category_id": PromptBlockCategory.SYSTEM_RULE.value,
                "type": BlockDataType.CRITERIA.value,
                "label": {"translations": {"en": "Criteria"}},
                "description": {"translations": {"en": "Criteria"}},
                "instruction_text": "Criteria instruction.",
            },
        ]
    )

    # Setup Step
    repo.set_step(
        {
            "id": "stp_0123456789abcdef",
            "slug": "test_step",
            "name": {"translations": {"en": "Blueprint"}},
            "description": {"translations": {"en": "Blueprint"}},
            "type": "llm",
            "cognitive_tier": "fast",
            "role_block_id": None,
            "extraction_protocol_block_id": "blk_0123456789abcdef",
            "criteria_block_ids": ["blk_0123456789abcde0"],
            "allowed_mcp_tools": [],
        }
    )

    return repo


@pytest.mark.asyncio
async def test_output_profile_directives_relocated_to_user_payload_and_system_prompt_invariant_neg09(
    test_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify Scenario NEG-09: base_system_prompt SHA-256 hash remains bit-for-bit invariant

    across varying output profiles, and dynamic directives (<tone_instruction>, <matrix_synthesis_groups>)
    are relocated exclusively into user_payload dynamic tail.
    """
    profile_1 = OutputProfile.model_validate(
        {
            "id": "prof_0123456789abcdef0123456789abcde1",
            "slug": "formal_coaching",
            "workflow_id": "wor_0123456789abcdef",
            "name": {"translations": {"en": "Formal Coaching Profile"}},
            "tone_instruction": "Formal coaching tone, rigorous and objective.",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_1111222233334444",
                    "title": {"translations": {"en": "Synthesis Group 1"}},
                    "target_blocks": ["*"],
                }
            ],
        }
    )
    profile_2 = OutputProfile.model_validate(
        {
            "id": "prof_0123456789abcdef0123456789abcde2",
            "slug": "executive_summary",
            "workflow_id": "wor_0123456789abcdef",
            "name": {"translations": {"en": "Executive Summary Profile"}},
            "tone_instruction": "Concise executive summary for CEO.",
            "matrix_synthesis_groups": [
                {
                    "id": "grp_2222333344445555",
                    "title": {"translations": {"en": "Synthesis Group 2"}},
                    "target_blocks": ["*"],
                }
            ],
        }
    )

    test_repo.set_output_profiles([profile_1.model_dump(mode="json"), profile_2.model_dump(mode="json")])

    mock_engine = AsyncMock()
    mock_engine.execute.return_value = EngineExecutionResult(
        results=[],
        hydrated_references={},
        synthesis_output=DummySynthesisOutputDTO(output="ok"),
        usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )

    compiler = PromptCompiler()
    deps = StrategyDependencies(
        exec_repo=test_repo,
        workflow_repo=test_repo,
        comp_repo=test_repo,
        prompt_block_repo=test_repo,
        output_profile_repo=test_repo,
        identity_repo=test_repo,
        audit_repo=test_repo,
        system_repo=test_repo,
        prompt_compiler=compiler,
    )
    strategy = LLMNodeStrategy(deps=deps, engine=mock_engine)

    step = StepRule(
        id="sr_0123456789abcdef",
        task_blueprint="stp_0123456789abcdef",
        input_mappings={},
    )

    context_1 = StrategyContext(
        execution_id="exc_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        output_profile_id="prof_0123456789abcdef0123456789abcde1",
        target_locale="en",
        cognitive_tier=CognitiveTier.FAST,
        model_registry_id="sys_e26807f3bfa3454d",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    context_2 = StrategyContext(
        execution_id="exc_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        output_profile_id="prof_0123456789abcdef0123456789abcde2",
        target_locale="en",
        cognitive_tier=CognitiveTier.FAST,
        model_registry_id="sys_e26807f3bfa3454d",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    projector = AsyncMock()
    projector.snapshot = []

    system_prompts_captured: list[str] = []
    user_payloads_captured: list[str] = []

    # Spy on PromptFactory.build to record base_system_prompt directly
    original_build = PromptFactory.build

    def spy_build(*args: Any, **kwargs: Any) -> Any:
        res = original_build(*args, **kwargs)
        system_prompts_captured.append(res.base_system_prompt)
        return res

    with patch.object(PromptFactory, "build", side_effect=spy_build):
        # 1. Execute with Profile 1
        await strategy.execute(
            step=step,
            projector=projector,
            context=context_1,
            frozen_ctx=None,
            trace=[],
        )
        req_1: EngineExecutionRequest = mock_engine.execute.call_args[0][0]
        user_payloads_captured.append(req_1.system_prompt)

        # 2. Execute with Profile 2
        await strategy.execute(
            step=step,
            projector=projector,
            context=context_2,
            frozen_ctx=None,
            trace=[],
        )
        req_2: EngineExecutionRequest = mock_engine.execute.call_args[0][0]
        user_payloads_captured.append(req_2.system_prompt)

    # Invariant 1: base_system_prompt SHA-256 hashes must be bit-for-bit identical across profiles
    assert len(system_prompts_captured) == 2
    hash_1 = hashlib.sha256(system_prompts_captured[0].encode()).hexdigest()
    hash_2 = hashlib.sha256(system_prompts_captured[1].encode()).hexdigest()
    assert hash_1 == hash_2, (
        f"base_system_prompt violated cache invariance across output profiles!\n"
        f"Profile 1 Hash: {hash_1}\nProfile 2 Hash: {hash_2}"
    )

    # Invariant 2: base_system_prompt must NEVER contain <execution_parameters> or tone instructions
    assert "<execution_parameters>" not in system_prompts_captured[0]
    assert "<tone_instruction>" not in system_prompts_captured[0]
    assert "<matrix_synthesis_groups>" not in system_prompts_captured[0]

    # Invariant 3: Output profile directives must be strictly quarantined in user_payload
    payload_1 = user_payloads_captured[0]
    assert "<execution_parameters>" in payload_1
    assert "<tone_instruction>Formal coaching tone, rigorous and objective.</tone_instruction>" in payload_1
    assert "grp_1111222233334444" in payload_1
    assert "grp_2222333344445555" not in payload_1

    payload_2 = user_payloads_captured[1]
    assert "<execution_parameters>" in payload_2
    assert "<tone_instruction>Concise executive summary for CEO.</tone_instruction>" in payload_2
    assert "grp_2222333344445555" in payload_2
    assert "grp_1111222233334444" not in payload_2
