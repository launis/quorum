from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

import backend_v2.hooks.archival
from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.archival import retrieve_precedent_hook
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.hook_delta import ArchivistPrecedentsResultDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture(autouse=True)
def configure_archival_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure positive precedent scan depth and return count for unit tests in development mode."""
    test_settings = Settings(max_precedent_scan_depth=5, max_precedent_return_count=3)
    monkeypatch.setattr(backend_v2.hooks.archival, "get_settings", lambda: test_settings)


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_none_state() -> None:
    deps = MagicMock(spec=HookDependencies)
    result = await retrieve_precedent_hook(None, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_missing_repo_raises() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = None

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_missing_updated_at_integrity_error() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord.model_construct(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
        created_at=now,
        raw_inputs={},
        updated_at=None,
    )

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_success() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
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
                    "matrix_id": "mat_0195f3a00000700384567890abcdef12",
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

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert isinstance(result.state_delta.delta, ArchivistPrecedentsResultDTO)
    precedents = result.state_delta.delta.archivist_precedents
    assert len(precedents) == 1
    assert precedents[0].id == "exe_0195f3a00000700384567890abcdef12"


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
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

    monkeypatch.setattr(backend_v2.hooks.archival, "get_storage_driver", lambda: MockDiskStorage())

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert isinstance(result.state_delta.delta, ArchivistPrecedentsResultDTO)
    assert len(result.state_delta.delta.archivist_precedents) == 1


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_invalid_judge_output_raises() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
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

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 400
    assert exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_file_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
        created_at=now,
        updated_at=now,
        completed_at=now,
        raw_inputs={},
        execution_trace=[],
    )

    class MockDiskStorageMissing:
        async def exists(self, path: str) -> bool:
            return False

    monkeypatch.setattr(backend_v2.hooks.archival, "get_storage_driver", lambda: MockDiskStorageMissing())

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert isinstance(result.state_delta.delta, ArchivistPrecedentsResultDTO)
    assert result.state_delta.delta.archivist_precedents == []


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_disk_read_error(monkeypatch: pytest.MonkeyPatch) -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    mock_record = ExecutionRecord(
        id="exe_0195f3a00000700384567890abcdef12",
        workflow_id="wor_0195f3a00000700384567890abcdef12",
        organization_id="org_0195f3a00000700384567890abcdef12",
        output_profile_id="prof_123",
        status="PASSED",
        target_locale="en",
        metadata=ExecutionMetadata(),
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

    monkeypatch.setattr(backend_v2.hooks.archival, "get_storage_driver", lambda: MockDiskStorageError())

    exec_repo = InMemoryUnifiedWorkflowRepository()
    await exec_repo.save_execution(mock_record)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    with pytest.raises(AppException) as exc:
        await retrieve_precedent_hook(state, deps)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value


@pytest.mark.asyncio
async def test_retrieve_precedent_hook_repository_failure_raises() -> None:
    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    exec_repo = InMemoryUnifiedWorkflowRepository()
    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    exec_repo.inject_fault("get_recent_completed_executions", RuntimeError("Database connection error"))
    try:
        with pytest.raises(AppException) as exc:
            await retrieve_precedent_hook(state, deps)
        assert exc.value.status_code == 500
        assert exc.value.details["error_code"] == ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED.value
    finally:
        exec_repo.clear_faults()


@pytest.mark.asyncio
async def test_archival_hook_uses_settings_scan_depth_and_unbounded_verdicts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify retrieve_precedent_hook uses settings scan/return bounds and preserves full 250-char verdicts by default."""
    custom_settings = Settings(
        max_precedent_scan_depth=4,
        max_precedent_return_count=2,
        archival_verdict_part_max_chars=0,
        archival_verdict_summary_max_chars=0,
    )
    monkeypatch.setattr(backend_v2.hooks.archival, "get_settings", lambda: custom_settings)

    state = HookState(
        workflow_id="wf_1",
        execution_id="exec_1",
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    now = datetime.now(timezone.utc)
    verdict_250 = "V" * 250

    exec_repo = InMemoryUnifiedWorkflowRepository()
    for idx in range(3):
        rec = ExecutionRecord(
            id=f"exe_0195f3a00000700384567890abcdef1{idx}",
            workflow_id="wor_0195f3a00000700384567890abcdef12",
            organization_id="org_0195f3a00000700384567890abcdef12",
            output_profile_id="prof_123",
            status="PASSED",
            target_locale="en",
            metadata=ExecutionMetadata(),
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
                        "matrix_id": "mat_0195f3a00000700384567890abcdef12",
                        "scale_min": 1.0,
                        "scale_max": 5.0,
                        "score_card": {
                            "agent_name": "Standard Judge",
                            "total_score": 4.5,
                            "max_score": 5,
                            "verdict": verdict_250,
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
        await exec_repo.save_execution(rec)

    deps = MagicMock(spec=HookDependencies)
    deps.exec_repo = exec_repo

    result = await retrieve_precedent_hook(state, deps)
    assert result.success is True
    assert isinstance(result.state_delta.delta, ArchivistPrecedentsResultDTO)
    precedents = result.state_delta.delta.archivist_precedents
    assert len(precedents) == 2
    assert verdict_250 in precedents[0].verdict
    assert len(precedents[0].verdict) > 250

    # Verify explicit positive bounds slice part and summary deterministically
    bounded_settings = Settings(
        max_precedent_scan_depth=4,
        max_precedent_return_count=2,
        archival_verdict_part_max_chars=40,
        archival_verdict_summary_max_chars=50,
    )
    monkeypatch.setattr(backend_v2.hooks.archival, "get_settings", lambda: bounded_settings)
    bounded_result = await retrieve_precedent_hook(state, deps)
    assert isinstance(bounded_result.state_delta.delta, ArchivistPrecedentsResultDTO)
    bounded_precedents = bounded_result.state_delta.delta.archivist_precedents
    assert len(bounded_precedents[0].verdict) <= 50
