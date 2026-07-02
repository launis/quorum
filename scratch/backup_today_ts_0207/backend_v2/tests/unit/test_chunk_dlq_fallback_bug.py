import asyncio
from typing import Any, cast

import pytest

from backend_v2.exceptions import LLMSchemaValidationError
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


class MockChunk:
    def __init__(self, items: list[dict[str, str]]) -> None:
        self.items = items

    def model_copy(self, update: dict[str, Any] | None = None) -> MockChunk:
        new_items = update.get("items", self.items) if update else self.items
        return MockChunk(items=new_items)


class MockCompiler:
    def build_dynamic_schema(self, *args: Any, **kwargs: Any) -> type:
        class DummySchema:
            pass

        return DummySchema

    def compile_chunk_prompt(self, *args: Any, **kwargs: Any) -> Any:
        class DummyCompiledPrompt:
            static_messages: list[Any] = []
            dynamic_messages: list[Any] = []
            metadata: dict[str, Any] = {}

            def model_copy(self, *args: Any, **kwargs: Any) -> Any:
                return self

        return DummyCompiledPrompt()


class MockLLMClient:
    pass


class DummyPromptBlock:
    def __init__(self, block_id: str, category_id: str = "matrix", b_type: str = "instruction") -> None:
        self.id = block_id
        self.category_id = category_id
        self.type = b_type
        self.execution_persona = None
        self.scales: list[Any] = []


@pytest.mark.asyncio
async def test_chunk_worker_dlq_fallback_for_shuffled_atoms(monkeypatch: pytest.MonkeyPatch) -> None:
    # We want to test that if execute_structured_task raises an exception,
    # process_chunk returns a graceful DLQ list instead of {"_dlq_status": "FAILED/DLQ"}

    from backend_v2.services.llm_task_executor import LLMTaskExecutor

    async def mock_execute(*args: Any, **kwargs: Any) -> Any:
        raise LLMSchemaValidationError("Mock validation error", "mock_msg")

    monkeypatch.setattr(LLMTaskExecutor, "execute_structured_task", mock_execute)

    chunk = cast(Any, MockChunk([{"atom_id": "atom_123"}, {"atom_id": "atom_456"}]))
    sem = asyncio.Semaphore(1)
    compiler = cast(Any, MockCompiler())

    # We pass empty criteria because has_shuffled_atoms=True maps from chunk.items
    chunk_criteria = cast(Any, [])

    # Pass a dummy object that circumvents Pydantic validation
    class DummyCompiledPrompt:
        static_messages: list[Any] = []
        dynamic_messages: list[Any] = []
        metadata: dict[str, Any] = {}

    chunk_final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=chunk,
        sem=sem,
        compiler=compiler,
        criteria_blocks=chunk_criteria,
        user_payload="test payload",
        global_source_text="test payload",
        base_system_prompt="test",
        has_search=False,
        has_shuffled_atoms=True,
        atom_to_block_ids={"atom_123": {"matrix_abc"}, "atom_456": {"matrix_abc"}},
        effective_mcp_tools=[],
        bound_client=cast(Any, MockLLMClient()),
        step_id="step_test",
        target_locale="en",
        synthesis_instructions=None,
        output_profile=None,
    )

    # Currently, it returns {"_dlq_status": "FAILED/DLQ", "reason": "..."}
    # This test will initially fail because we will assert that it should return:
    # {"evaluations": [{"atom_id": "atom_123", "status": "DLQ", ...}, ...]}

    assert "evaluations" in chunk_final, f"Expected graceful DLQ fallback list, got {chunk_final}"
    assert len(chunk_final["evaluations"]) == 2
    assert chunk_final["evaluations"][0]["atom_id"] == "atom_123"
    assert chunk_final["evaluations"][0]["status"] == "DLQ"


@pytest.mark.asyncio
async def test_chunk_worker_dlq_fallback_for_standard_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.services.llm_task_executor import LLMTaskExecutor

    async def mock_execute(*args: Any, **kwargs: Any) -> Any:
        raise LLMSchemaValidationError("Mock validation error", "mock_msg")

    monkeypatch.setattr(LLMTaskExecutor, "execute_structured_task", mock_execute)

    sem = asyncio.Semaphore(1)
    compiler = cast(Any, MockCompiler())

    crit_1 = cast(Any, DummyPromptBlock("crit_1", "extraction", "criteria"))
    crit_2 = cast(Any, DummyPromptBlock("crit_2", "extraction", "criteria"))

    chunk_criteria = cast(Any, [crit_1, crit_2])

    class DummyCompiledPrompt:
        static_messages: list[Any] = []
        dynamic_messages: list[Any] = []
        metadata: dict[str, Any] = {}

    chunk_final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=None,
        sem=sem,
        compiler=compiler,
        criteria_blocks=chunk_criteria,
        user_payload="test payload",
        global_source_text="test payload",
        base_system_prompt="test",
        has_search=False,
        has_shuffled_atoms=False,
        atom_to_block_ids={},
        effective_mcp_tools=[],
        bound_client=cast(Any, MockLLMClient()),
        step_id="step_test",
        target_locale="en",
        synthesis_instructions=None,
        output_profile=None,
    )

    assert "crit_1" in chunk_final, f"Expected graceful DLQ dict for crit_1, got {chunk_final}"
    assert chunk_final["crit_1"]["status"] == "DLQ"
