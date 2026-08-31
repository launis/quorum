from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.archival import retrieve_precedent_hook
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_none_state() -> None:
    deps = MagicMock(spec=HookDependencies)
    result = await retrieve_precedent_hook(None, deps)  # type: ignore[arg-type]
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_missing_repo_raises() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = None

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_missing_updated_at_integrity_error() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        raw_inputs={},
    )
    object.__setattr__(mock_record, "updated_at", None)

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_success() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_judge_accuracy",
                timestamp=now,
                content={
                    "thought_process": "Clear evaluation reasoning.",
                    "conclusion": "Accurate output.",
                    "confidence_score": 0.95,
                    "matrix_id": "mat_1234567890abcdef12",
                    "scale_min": 1.0,
                    "scale_max": 5.0,
                    "score_card": {
                        "agent_name": "Standard Judge",
                        "total_score": 4.5,
                        "max_score": 5,
                        "verdict": "Very good performance and adherence to guidelines.",
                        "scale_min": 1.0,
                        "scale_max": 5.0,
                        "dimensions": [
                            {
                                "dimension_id": "dim_1",
                                "dimension_label": "Accuracy",
                                "score": 4.5,
                                "reasoning": "Well supported facts.",
                            }
                        ],
                    },
                },
            )
        ],
    )

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert "archivist_precedents" in result.state_delta.delta
    precedents = result.state_delta.delta["archivist_precedents"]
    assert len(precedents) == 1
    assert precedents[0]["id"] == "exe_1234567890abcdef12"


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[],
    )

    class MockDiskStorage:
        async def exists(self, path: str) -> bool:
            return True

        async def read(self, path: str) -> str:
            return (
                '[{"event_type": "output", "step_name": "step_judge_accuracy", '
                '"timestamp": "2026-08-31T10:00:00Z", "content": {'
                '"thought_process": "Thought", "conclusion": "Concl", "confidence_score": 1.0, '
                '"matrix_id": "mat_1", "scale_min": 1.0, "scale_max": 5.0, '
                '"score_card": {"agent_name": "Judge", "total_score": 4.0, "max_score": 5, '
                '"verdict": "Good", "scale_min": 1.0, "scale_max": 5.0, "dimensions": ['
                '{"dimension_id": "d1", "score": 4.0, "reasoning": "R"}]}}}]'
            )

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockDiskStorage())

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert len(result.state_delta.delta["archivist_precedents"]) == 1


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_invalid_judge_output_raises() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_judge_accuracy",
                timestamp=now,
                content={"invalid_judge_content": True},
            )
        ],
    )

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_file_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[],
    )

    class MockDiskStorageMissing:
        async def exists(self, path: str) -> bool:
            return False

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockDiskStorageMissing())

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert result.state_delta.delta["archivist_precedents"] == []


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_read_error(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef12",
        workflow_id="wor_1234567890abcdef12",
        organization_id="org_1234567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(target_locale="en"),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[],
    )

    class MockDiskStorageError:
        async def exists(self, path: str) -> bool:
            return True

        async def read(self, path: str) -> str:
            raise OSError("Disk read error")

    import backend_v2.services.storage

    monkeypatch.setattr(backend_v2.services.storage, "get_storage_driver", lambda: MockDiskStorageError())

    mock_exec_repo = AsyncMock()
    mock_exec_repo.get_recent_completed_executions.return_value = [mock_record]

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = mock_exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500
