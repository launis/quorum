"""Tests for the dynamic linguistic context generation in ChunkWorker."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


@pytest.mark.asyncio
async def test_linguistic_context_dynamic_injection() -> None:
    """Verify that linguistic context correctly injects target_locale and source_language."""
    # Mock compiler
    schema_mock = MagicMock()
    schema_mock.model_validate.return_value = MagicMock()
    compiler_mock = MagicMock()
    compiler_mock.build_dynamic_schema.return_value = schema_mock
    compiler_mock.compile_static_instructions.return_value = ""
    compiler_mock.compile_xml_rubrics.return_value = ""
    compiler_mock.compile_dynamic_instructions.return_value = ""
    compiler_mock.generate_mcp_instruction.return_value = ""
    compiler_mock.calibrate_strictness.return_value = "SCORING_STRICTNESS: 100/100"

    # Mock LLM Client
    mock_model = MagicMock()
    mock_model.model_dump.return_value = {"evaluations": []}

    bound_client_mock = MagicMock()
    bound_client_mock.run_structured_task = AsyncMock(
        return_value=(mock_model, {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})
    )
    bound_client_mock.execute_task = AsyncMock(return_value="{}")

    # Test variables
    chunk = MagicMock()
    chunk.items = []
    sem = asyncio.Semaphore(1)
    criteria_blocks: list[PromptBlock] = []
    has_search = False
    has_shuffled_atoms = False
    atom_to_block_ids: dict[str, set[str]] = {}
    effective_mcp_tools: list[str] = []
    step_id = "step_1"
    target_locale = "fi"
    synthesis_instructions = None
    output_profile = None
    strictness_level = 100

    step_metadata = {"source_language": "fr", "document_language": "fr"}

    # We want to catch the exact call to execute_structured_task
    await ChunkWorker.process_chunk(
        chunk=chunk,
        sem=sem,
        compiler=compiler_mock,
        criteria_blocks=criteria_blocks,
        user_payload="A source text in Finnish.",
        global_source_text="A source text in Finnish.",
        base_system_prompt="System prompt.",
        has_search=has_search,
        has_shuffled_atoms=has_shuffled_atoms,
        atom_to_block_ids=atom_to_block_ids,
        effective_mcp_tools=effective_mcp_tools,
        bound_client=bound_client_mock,
        step_id=step_id,
        target_locale=target_locale,
        synthesis_instructions=synthesis_instructions,
        output_profile=output_profile,
        strictness_level=strictness_level,
        step_metadata=step_metadata,
    )

    # Assert
    assert compiler_mock.compile_chunk_prompt.called, "compile_chunk_prompt was not called"

    kwargs = compiler_mock.compile_chunk_prompt.call_args.kwargs
    base_system_prompt_used = kwargs.get("base_system_prompt", "")

    # Centralized linguistic module assertions
    assert "<linguistic_context>" in base_system_prompt_used
    assert "<source_data_language>fr</source_data_language>" in base_system_prompt_used
    assert "<required_output_language>fi</required_output_language>" in base_system_prompt_used
    assert "<required_reasoning_language>English</required_reasoning_language>" in base_system_prompt_used
