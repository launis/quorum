"""Unit tests for script base SSOT (scripts/_script_base.py).

Tests workspace root resolution, stdout/stderr UTF-8 reconfiguration across TTY and Non-TTY streams,
ANSI color constants, StrEnum serialization, and strict Pydantic V2 DTO validation.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from scripts._script_base import (
    ANSIColors,
    BaseAuditFindingDTO,
    GuardrailSeverity,
    get_repo_root,
    setup_script_environment,
)


def test_get_repo_root() -> None:
    """Test get_repo_root returns valid workspace containing pyproject.toml."""
    root = get_repo_root()
    assert isinstance(root, Path)
    assert root.exists()
    assert (root / "pyproject.toml").is_file()


def test_setup_script_environment_standard() -> None:
    """Test setup_script_environment executes cleanly and adds root to sys.path."""
    root = get_repo_root()
    root_str = str(root)

    # Temporarily remove all variants of root from sys.path to exercise insertion
    orig_path = list(sys.path)
    try:
        sys.path[:] = [p for p in sys.path if Path(p).resolve() != root.resolve()]
        returned_root = setup_script_environment()
        assert isinstance(returned_root, Path)
        assert root_str in sys.path
    finally:
        sys.path[:] = orig_path


def test_setup_script_environment_non_tty_and_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test setup_script_environment handles non-TextIOWrapper and unsupported operation gracefully."""
    # Test non-TextIOWrapper stream (e.g. BytesIO)
    bytes_stream = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", bytes_stream)
    monkeypatch.setattr(sys, "stderr", bytes_stream)

    root = setup_script_environment()
    assert isinstance(root, Path)

    # Test TextIOWrapper stream that raises UnsupportedOperation on reconfigure
    mock_wrapper = MagicMock(spec=io.TextIOWrapper)
    mock_wrapper.reconfigure.side_effect = io.UnsupportedOperation("Not supported")
    monkeypatch.setattr(sys, "stdout", mock_wrapper)
    monkeypatch.setattr(sys, "stderr", mock_wrapper)

    root2 = setup_script_environment()
    assert isinstance(root2, Path)

    # Test AttributeError on reconfigure
    mock_wrapper_attr = MagicMock(spec=io.TextIOWrapper)
    del mock_wrapper_attr.reconfigure
    monkeypatch.setattr(sys, "stdout", mock_wrapper_attr)
    monkeypatch.setattr(sys, "stderr", mock_wrapper_attr)

    root3 = setup_script_environment()
    assert isinstance(root3, Path)


def test_guardrail_severity_enum() -> None:
    """Test GuardrailSeverity enum members and string serialization."""
    assert GuardrailSeverity.WARNING == "WARNING"
    assert GuardrailSeverity.FATAL == "FATAL"
    assert str(GuardrailSeverity.WARNING) == "WARNING"
    assert str(GuardrailSeverity.FATAL) == "FATAL"
    assert list(GuardrailSeverity) == [GuardrailSeverity.WARNING, GuardrailSeverity.FATAL]


def test_ansi_colors_constants() -> None:
    """Test ANSIColors constants format and values."""
    assert ANSIColors.RED == "\033[91m"
    assert ANSIColors.GREEN == "\033[92m"
    assert ANSIColors.YELLOW == "\033[93m"
    assert ANSIColors.CYAN == "\033[96m"
    assert ANSIColors.BOLD == "\033[1m"
    assert ANSIColors.RESET == "\033[0m"


def test_base_audit_finding_dto_valid() -> None:
    """Test BaseAuditFindingDTO valid instantiation with and without remediation."""
    finding1 = BaseAuditFindingDTO(
        rule_code="QGR001",
        message="getattr reflection detected",
        severity=GuardrailSeverity.WARNING,
    )
    assert finding1.rule_code == "QGR001"
    assert finding1.message == "getattr reflection detected"
    assert finding1.severity == GuardrailSeverity.WARNING
    assert finding1.remediation is None

    finding2 = BaseAuditFindingDTO(
        rule_code="QGR006",
        message="asyncio.gather() is banned",
        severity=GuardrailSeverity.FATAL,
        remediation="Use asyncio.TaskGroup instead.",
    )
    assert finding2.remediation == "Use asyncio.TaskGroup instead."


def test_base_audit_finding_dto_negative_partitions() -> None:
    """Test BaseAuditFindingDTO rejects extra fields, missing fields, and frozen mutation."""
    # Extra fields rejected per extra="forbid"
    with pytest.raises(ValidationError) as exc_info:
        BaseAuditFindingDTO.model_validate(
            {
                "rule_code": "QGR001",
                "message": "msg",
                "severity": "WARNING",
                "unauthorized_field": "disallowed",
            }
        )
    assert "extra_forbidden" in str(exc_info.value)

    # Missing mandatory field
    with pytest.raises(ValidationError) as exc_info_missing:
        BaseAuditFindingDTO.model_validate(
            {
                "rule_code": "QGR001",
                "message": "msg",
            }
        )
    assert "Field required" in str(exc_info_missing.value)

    # Frozen state mutation rejected
    finding = BaseAuditFindingDTO(
        rule_code="QGR001",
        message="msg",
        severity=GuardrailSeverity.WARNING,
    )
    with pytest.raises(ValidationError):
        finding.__setattr__("rule_code", "QGR002")
