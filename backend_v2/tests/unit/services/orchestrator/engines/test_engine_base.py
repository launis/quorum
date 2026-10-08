"""Tests for ExecutionEngine protocol."""

from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.services.orchestrator.engines.base import ExecutionEngine


class DummyEngine:
    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        return EngineExecutionResult(results=[], hydrated_references={})


class NonEngine:
    pass


def test_execution_engine_protocol_runtime_checkable() -> None:
    """Verify ExecutionEngine protocol is runtime checkable."""
    assert isinstance(DummyEngine(), ExecutionEngine)
    assert not isinstance(NonEngine(), ExecutionEngine)
