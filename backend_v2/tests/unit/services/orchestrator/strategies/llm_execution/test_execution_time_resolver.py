"""Unit tests for ExecutionTimeResolver."""

import datetime
from pathlib import Path
from unittest.mock import patch

from backend_v2.services.orchestrator.strategies.llm_execution.execution_time_resolver import (
    ExecutionTimeResolver,
)


def test_resolve_client_supplied_document_date() -> None:
    """Positive test: Resolves client-supplied document_date from raw_inputs.dynamic_inputs."""
    context = {
        "raw_inputs": {
            "dynamic_inputs": {
                "document_date": "2026-05-15T10:30:00Z",
            }
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 5
    assert resolved.day == 15


def test_resolve_client_supplied_datetime_object() -> None:
    """Positive test: Resolves client-supplied datetime instance directly."""
    expected_dt = datetime.datetime(2026, 8, 20, 12, 0, tzinfo=datetime.timezone.utc)
    context = {
        "raw_inputs": {
            "dynamic_inputs": {
                "input_file_date": expected_dt,
            }
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved == expected_dt


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
        # Mock Path so Path("data") points to tmp_path / "data"
        def side_effect(*args: str) -> Path:
            return tmp_path.joinpath(*args)

        mock_path_cls.side_effect = side_effect

        resolved = ExecutionTimeResolver.resolve(
            llm_context_data={},
            execution_id=execution_id,
        )
        assert resolved is not None
        assert isinstance(resolved, datetime.datetime)


def test_resolve_metadata_timestamp_fallback() -> None:
    """Positive test: Resolves context metadata timestamp fallback."""
    context = {
        "metadata": {
            "created_at": "2026-07-04T08:00:00+00:00",
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 7
    assert resolved.day == 4


def test_resolve_raw_inputs_timestamp_fallback() -> None:
    """Positive test: Resolves raw_inputs timestamp fallback."""
    context = {
        "raw_inputs": {
            "timestamp": "2026-03-10T15:00:00Z",
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 3
    assert resolved.day == 10


def test_resolve_raw_inputs_datetime_object() -> None:
    """Positive test: Resolves raw_inputs datetime instance directly."""
    expected = datetime.datetime(2026, 9, 1, 10, 0, tzinfo=datetime.timezone.utc)
    context = {
        "raw_inputs": {
            "timestamp": expected,
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved == expected


def test_resolve_raw_inputs_nested_metadata_timestamp() -> None:
    """Positive test: Resolves raw_inputs.metadata timestamp."""
    context = {
        "raw_inputs": {
            "metadata": {
                "timestamp": "2026-11-11T11:11:11Z",
            }
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved is not None
    assert resolved.year == 2026
    assert resolved.month == 11
    assert resolved.day == 11


def test_resolve_metadata_datetime_object() -> None:
    """Positive test: Resolves metadata datetime instance directly."""
    expected = datetime.datetime(2026, 4, 1, 8, 0, tzinfo=datetime.timezone.utc)
    context = {
        "metadata": {
            "created_at": expected,
        }
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved == expected


def test_resolve_top_level_context_timestamp() -> None:
    """Positive test: Resolves top-level created_at / timestamp."""
    expected = datetime.datetime(2026, 12, 25, 0, 0, tzinfo=datetime.timezone.utc)
    assert ExecutionTimeResolver.resolve(llm_context_data={"created_at": expected}) == expected
    resolved_str = ExecutionTimeResolver.resolve(llm_context_data={"timestamp": "2026-06-01T12:00:00Z"})
    assert resolved_str is not None
    assert resolved_str.year == 2026
    assert resolved_str.month == 6


def test_resolve_physical_file_os_error_handling(tmp_path: Path) -> None:
    """Negative test: Handles OSError when stat-ing physical file."""
    execution_id = "exec_os_error"
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
                llm_context_data={"created_at": "2026-02-02T02:02:02Z"},
                execution_id=execution_id,
            )
            assert resolved is not None
            assert resolved.year == 2026
            assert resolved.month == 2


def test_resolve_empty_context_returns_none() -> None:
    """Negative test 1: Empty context dictionary returns None without crashing."""
    assert ExecutionTimeResolver.resolve(llm_context_data={}) is None
    assert ExecutionTimeResolver.resolve(llm_context_data=None) is None


def test_resolve_invalid_context_types_returns_none() -> None:
    """Negative test 2: Non-dictionary or corrupted context types return None safely."""
    assert ExecutionTimeResolver.resolve(llm_context_data="not a dict") is None  # type: ignore[arg-type]
    assert ExecutionTimeResolver.resolve(llm_context_data=[1, 2, 3]) is None  # type: ignore[arg-type]


def test_resolve_unparseable_date_falls_back() -> None:
    """Negative test 3: Unparseable date string falls back to secondary sources or None."""
    context = {
        "raw_inputs": {
            "dynamic_inputs": {
                "document_date": "invalid-date-string",
            },
            "timestamp": "invalid-raw-timestamp",
        },
        "metadata": {
            "created_at": "invalid-meta-timestamp",
        },
        "timestamp": "invalid-top-timestamp",
    }
    resolved = ExecutionTimeResolver.resolve(llm_context_data=context)
    assert resolved is None
