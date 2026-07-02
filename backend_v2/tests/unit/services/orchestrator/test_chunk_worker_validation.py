import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

import backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker as cw
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock, TDAAssertion
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


@pytest.mark.asyncio
async def test_chunk_worker_pop_reasoning_steps_bug():
    """Test that reproduces the Bug in ChunkWorker.process_chunk where
    reasoning_steps and override_reason are erroneously popped from the payload
    before Pydantic validation, causing a fatal ExceptionGroup -> DLQ.
    """
    # 1. Setup mock compiler and models
    compiler = PromptCompiler()

    class MockCompiledPrompt:
        static_messages = []
        dynamic_messages = []
        metadata = {}

    compiler.compile_chunk_prompt = MagicMock(return_value=MockCompiledPrompt())

    tda_id = "tda_12345678901234567890123456789012"
    sr_id = "sr_1234567890123456"

    i18n_label = I18nText(default_locale="en", translations={"en": "Test"})

    tda = TDAAssertion(tda_id=tda_id, concept_description="Test", aggregation_mode="EXISTS", inverse_evidence=False)
    claim = MatrixClaim(label=i18n_label, ai_description="Test", tda_assertions=[tda])
    scale = MatrixScale(score=1, ai_label="TEST", claims=[claim])
    block = PromptBlock(
        id=sr_id,
        slug="test",
        category_id="matrix",
        scales=[scale],
        label=i18n_label,
        description=i18n_label,
        type="string",
    )

    bound_client = MagicMock()

    # 2. Mock the LLM Task Executor to return a perfectly valid LLM response
    class DummyAtomResponse(BaseModel):
        atom_id: str = tda_id
        rule_internalization: str = "Test internalization"
        used_source_aliases: list[str] = []
        source_document_aliases: list[str] = ["N/A"]
        exact_quotes: list[str] = []
        reasoning_steps: str = "I reasoned this carefully."
        falsification_argument: str = "No falsification possible."
        decision: bool = True
        semantic_reasoning: str = "It is true."
        contextual_override: bool = False
        override_reason: str | None = None

    class DummyResponse(BaseModel):
        evaluations: list[DummyAtomResponse]
        reasoning_trace: str = "Global reasoning trace."
        evaluation_notes: str = "Global evaluation notes."
        global_matrices: dict[str, dict] = {}

    async def mock_execute_structured_task(*args, **kwargs):
        # Simulate a successful LLM parsing returning the Pydantic schema
        return DummyResponse(
            evaluations=[DummyAtomResponse()],
            reasoning_trace="Global reasoning trace.",
            evaluation_notes="Global evaluation notes.",
            global_matrices={sr_id: {"semantic_reasoning": "Test reasoning"}},
        ), None

    executor_mock = MagicMock()
    executor_mock.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    original_executor = cw.LLMTaskExecutor
    cw.LLMTaskExecutor = MagicMock(return_value=executor_mock)

    try:

        class DummyChunk:
            items = [{"atom_id": tda_id, "question": "test"}]

            def model_copy(self, **kwargs):
                return self

        chunk = DummyChunk()
        sem = asyncio.Semaphore(1)

        # 3. Execute
        result, usage, traces, context = await ChunkWorker.process_chunk(
            chunk=chunk,
            sem=sem,
            compiler=compiler,
            criteria_blocks=[block],
            user_payload="Test payload",
            global_source_text="Test source text",
            base_system_prompt="Test base",
            has_search=False,
            has_shuffled_atoms=True,
            atom_to_block_ids={tda_id: {sr_id}},
            effective_mcp_tools=[],
            bound_client=bound_client,
            step_id="test_step",
            target_locale="fi",
            synthesis_instructions=None,
            output_profile=None,
            strictness_level=50,
            step_metadata={"is_lightweight_extraction": False},
        )

        # 4. Assert Bug Reproduction
        # The bug causes process_chunk to catch the Pydantic ValidationError (caused by its own .pop)
        # and forcefully route the chunk to DLQ.

        print("\n--- BUG REPRODUCTION TRACE ---")
        print(f"DLQ Status: {result.get('_dlq_status')}")
        print(f"Reason: {result.get('reason')}")
        print("------------------------------\n")

        assert "_dlq_status" not in result, f"Expected chunk to succeed, but got DLQ: {result.get('reason')}"
        assert result.get("evaluations") is not None, "Expected evaluations in the result"

    finally:
        cw.LLMTaskExecutor = original_executor
