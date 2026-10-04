"""Unit tests for ExecutionTimeResolver."""

import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.prompt import LLMContextDataDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver import (
    ExecutionTimeResolver,
)


def test_resolve_client_supplied_document_date_from_inputs() -> None:
    """Positive test: Resolves client-supplied document_date from ExecutionInputsDTO.dynamic_inputs."""
    inputs = ExecutionInputsDTO(dynamic_inputs={"document_date": "2026-05-15T10:30:00Z"})
    resolved = ExecutionTimeResolver.resolve(inputs=inputs)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 5
    assert resolved.day == 15


def test_resolve_client_supplied_iso_date_from_inputs() -> None:
    """Positive test: Resolves ISO date string directly from ExecutionInputsDTO."""
    inputs = ExecutionInputsDTO(dynamic_inputs={"input_file_date": "2026-08-20T12:00:00+00:00"})
    resolved = ExecutionTimeResolver.resolve(inputs=inputs)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 8
    assert resolved.day == 20


def test_resolve_client_supplied_raw_inputs_date() -> None:
    """Positive test: Resolves client-supplied document_date from ExecutionInputsDTO.raw_inputs."""
    inputs = ExecutionInputsDTO(raw_inputs={"last_modified": "2026-09-12T14:00:00Z"})
    resolved = ExecutionTimeResolver.resolve(inputs=inputs)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 9
    assert resolved.day == 12


def test_resolve_client_supplied_iso_date_from_raw_inputs() -> None:
    """Positive test: Resolves ISO date from ExecutionInputsDTO.raw_inputs."""
    inputs = ExecutionInputsDTO(raw_inputs={"document_date": "2026-10-01T09:30:00+00:00"})
    resolved = ExecutionTimeResolver.resolve(inputs=inputs)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 10
    assert resolved.day == 1


def test_parse_datetime_direct_datetime_and_string() -> None:
    """Positive test: Verifies _parse_datetime handles direct datetime, ISO strings, and None."""
    now = datetime.datetime.now(datetime.timezone.utc)
    assert ExecutionTimeResolver._parse_datetime(now) == now
    parsed = ExecutionTimeResolver._parse_datetime("2026-01-01T00:00:00Z")
    assert parsed is not None
    assert parsed.year == 2026
    assert ExecutionTimeResolver._parse_datetime(None) is None
    assert ExecutionTimeResolver._parse_datetime(12345) is None


def test_resolve_llm_context_data_dto_execution_time() -> None:
    """Positive test: Resolves execution_time directly from LLMContextDataDTO."""
    expected = datetime.datetime(2026, 3, 25, 8, 0, tzinfo=datetime.timezone.utc)
    context_data = LLMContextDataDTO(execution_time=expected)
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context_data)
    assert resolved == expected


def test_resolve_llm_context_data_dto_inputs_date() -> None:
    """Positive test: Resolves document_date from LLMContextDataDTO.inputs."""
    context_data = LLMContextDataDTO(inputs={"document_date": "2026-07-21T08:00:00Z"})
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context_data)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 7
    assert resolved.day == 21


def test_resolve_llm_context_data_dto_raw_inputs_date() -> None:
    """Positive test: Resolves last_modified from LLMContextDataDTO.raw_inputs."""
    context_data = LLMContextDataDTO(raw_inputs={"last_modified": "2026-08-10T14:30:00Z"})
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context_data)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 8
    assert resolved.day == 10


def test_resolve_physical_disk_file_mtime(tmp_path: Path) -> None:
    """Positive test: Resolves physical input file st_mtime when disk file exists."""
    execution_id = "exec_1234567890abcdef"
    input_dir = tmp_path / "data" / "files" / "executions" / execution_id / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)
    target_file = input_dir / "input_chat_log.md"
    target_file.write_text("# Chat Log", encoding="utf-8")
    target_file.touch()

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver.Path"
    ) as mock_path_cls:

        def side_effect(*args: str) -> Path:
            return tmp_path.joinpath(*args)

        mock_path_cls.side_effect = side_effect

        resolved = ExecutionTimeResolver.resolve(
            execution_id=execution_id,
        )
        assert resolved is not None
        assert isinstance(resolved, datetime.datetime)


def test_resolve_physical_file_os_error_handling(tmp_path: Path) -> None:
    """Negative test: Handles OSError when stat-ing physical file without crashing."""
    execution_id = "exec_1234567890abcdef"
    input_dir = tmp_path / "data" / "files" / "executions" / execution_id / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)
    target_file = input_dir / "input_chat_log.md"
    target_file.write_text("# Chat Log", encoding="utf-8")

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver.Path"
    ) as mock_path_cls:

        def side_effect(*args: str) -> Path:
            return tmp_path.joinpath(*args)

        mock_path_cls.side_effect = side_effect

        with patch.object(Path, "stat", side_effect=OSError("Disk error")):
            resolved = ExecutionTimeResolver.resolve(
                execution_id=execution_id,
            )
            assert resolved is None


def test_resolve_empty_context_returns_none() -> None:
    """Negative test: Empty context or None returns None without crashing."""
    assert ExecutionTimeResolver.resolve(llm_context_data=LLMContextDataDTO()) is None
    assert ExecutionTimeResolver.resolve(llm_context_data=None) is None
    assert ExecutionTimeResolver.resolve() is None


def test_resolve_unparseable_date_returns_none() -> None:
    """Negative test: Unparseable date string returns None safely."""
    inputs = ExecutionInputsDTO(dynamic_inputs={"document_date": "invalid-date-string"})
    resolved = ExecutionTimeResolver.resolve(inputs=inputs)
    assert resolved is None


def test_resolve_with_valid_execution_metadata() -> None:
    """Positive test: Passing valid ExecutionMetadata instance."""
    metadata = ExecutionMetadata(workflow_version=1)
    resolved = ExecutionTimeResolver.resolve(metadata=metadata)
    assert resolved is None


def test_resolve_invalid_context_type_raises_app_exception() -> None:
    """ISTQB Negative test: Passing invalid context type raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ExecutionTimeResolver.resolve(llm_context_data="not a dto")  # type: ignore[arg-type]
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_resolve_invalid_inputs_type_raises_app_exception() -> None:
    """ISTQB Negative test: Passing invalid inputs type raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ExecutionTimeResolver.resolve(inputs={"document_date": "2026-01-01"})  # type: ignore[arg-type]
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_resolve_invalid_metadata_type_raises_app_exception() -> None:
    """ISTQB Negative test: Passing invalid metadata type raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ExecutionTimeResolver.resolve(metadata={"invalid": "meta"})  # type: ignore[arg-type]
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_resolve_path_traversal_execution_id_raises_app_exception() -> None:
    """ISTQB Negative test: Path traversal in execution_id raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ExecutionTimeResolver.resolve(execution_id="../../etc/shadow")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
