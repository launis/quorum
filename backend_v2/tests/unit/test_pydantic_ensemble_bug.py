import asyncio
from typing import Any, cast

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


class DummyEvaluationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    atom_id: str
    exact_quotes: list[str] = []
    contextual_override: bool = False
    decision: bool = True
    semantic_reasoning: str = "Test reasoning"


class DummyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evaluations: list[DummyEvaluationItem]


class MockChunk:
    def __init__(self, items: list[dict[str, Any]]) -> None:
        self.items = items

    def model_copy(self, update: dict[str, Any] | None = None) -> Any:
        return MockChunk(update.get("items", self.items) if update else self.items)


class MockCompiler:
    def build_dynamic_schema(self, *args: Any, **kwargs: Any) -> type:
        return DummyResponse

    def compile_chunk_prompt(self, *args: Any, **kwargs: Any) -> Any:
        class DummyCompiledPrompt:
            static_messages: list[Any] = []
            dynamic_messages: list[Any] = []
            metadata: dict[str, Any] = {}

            def to_flat_messages(self) -> list[Any]:
                return []

        return DummyCompiledPrompt()


class MockLLMClient:
    pass


@pytest.mark.asyncio
async def test_ensemble_pydantic_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate LLM returning a valid response WITHOUT status/confidence (as expected by strict schema)
    async def mock_execute(*args: Any, **kwargs: Any) -> tuple[Any, Any]:
        resp = DummyResponse(evaluations=[DummyEvaluationItem(atom_id="atom_1", exact_quotes=["hello"])])
        return resp, None

    monkeypatch.setattr(LLMTaskExecutor, "execute_structured_task", mock_execute)

    chunk = MockChunk([{"atom_id": "atom_1"}])
    sem = asyncio.Semaphore(5)
    compiler = MockCompiler()

    # is_lightweight_extraction = False forces ENSEMBLE mode (llm_count = 3)
    step_metadata = {"is_lightweight_extraction": False}

    # We pass empty criteria to avoid ExtractiveSensor matching for testing
    chunk_criteria: list[PromptBlock] = []

    # This should reproduce the ValidationError because the ENSEMBLE merge logic
    # inside process_chunk injects `status` and `confidence` into chunk_final,
    # which then violates DummyResponse's `extra="forbid"` rule.
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
        atom_to_block_ids={"atom_1": set()},
        effective_mcp_tools=[],
        bound_client=cast(Any, MockLLMClient()),
        step_id="step_test",
        target_locale="en",
        synthesis_instructions=None,
        output_profile=None,
        step_metadata=step_metadata,
    )

    # If the bug is fixed, the test will pass and we assert that status is preserved.
    assert "evaluations" in chunk_final
    assert "status" in chunk_final["evaluations"][0], "Status must be preserved in final output"
