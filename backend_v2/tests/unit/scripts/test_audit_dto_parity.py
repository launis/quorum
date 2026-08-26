"""ISTQB Unit Tests for DTO Parity Verification Script (audit_dto_parity.py).

Verifies zero-reflection AST parsing, Pydantic V2 DTOs, Freezed model extraction,
field parity reports, and fault domain resilience.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# Add scripts directory to sys.path
scripts_dir = Path("scripts").resolve()
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from scripts.audit_dto_parity import (
    DtoFieldMismatchDTO,
    DtoParityReportDTO,
    audit_parity,
    audit_parity_report,
    camel_to_snake,
    extract_freezed_fields,
    extract_pydantic_fields,
    snake_to_camel,
)
from scripts.audit_dto_parity import (
    main as audit_dto_parity_main,
)


def test_snake_to_camel_and_camel_to_snake() -> None:
    """Test bi-directional casing conversion utilities."""
    assert snake_to_camel("execution_status") == "executionStatus"
    assert snake_to_camel("tda_id") == "tdaId"
    assert snake_to_camel("simple") == "simple"

    assert camel_to_snake("executionStatus") == "execution_status"
    assert camel_to_snake("tdaId") == "tda_id"
    assert camel_to_snake("simple") == "simple"


def test_extract_pydantic_fields_success(tmp_path: Path) -> None:
    """Test extract_pydantic_fields extracting model class names and field names via AST."""
    py_file = tmp_path / "models.py"
    py_file.write_text(
        "from pydantic import BaseModel, ConfigDict\n\n"
        "class ExecutionRecordDTO(BaseModel):\n"
        "    model_config = ConfigDict(strict=True, extra='forbid')\n"
        "    _internal_cache: dict[str, str]\n"
        "    execution_id: str\n"
        "    step_count: int\n"
        "    is_active: bool = True\n\n"
        "class SecondDTO(BaseModel):\n"
        "    user_id: str\n",
        encoding="utf-8",
    )

    models = extract_pydantic_fields(py_file)
    assert "ExecutionRecordDTO" in models
    assert models["ExecutionRecordDTO"] == {"execution_id", "step_count", "is_active"}
    assert "_internal_cache" not in models["ExecutionRecordDTO"]
    assert "model_config" not in models["ExecutionRecordDTO"]

    assert "SecondDTO" in models
    assert models["SecondDTO"] == {"user_id"}


def test_extract_pydantic_fields_fault_resilience(tmp_path: Path) -> None:
    """Test extract_pydantic_fields fault domain resilience on syntax errors and binary streams."""
    # Syntax error file
    bad_py = tmp_path / "broken.py"
    bad_py.write_text("class BrokenModel(:\n    field: int\n", encoding="utf-8")
    assert extract_pydantic_fields(bad_py) == {}

    # Binary non-UTF8 file
    bad_bytes = tmp_path / "bad_bytes.py"
    bad_bytes.write_bytes(b"\xff\xfe\x00\x00class X: pass")
    assert extract_pydantic_fields(bad_bytes) == {}

    # Non-existent file
    assert extract_pydantic_fields(tmp_path / "missing.py") == {}

    # Non-Python file
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("class Model:\n    x: int\n", encoding="utf-8")
    assert extract_pydantic_fields(txt_file) == {}


def test_extract_freezed_fields_success(tmp_path: Path) -> None:
    """Test extract_freezed_fields extracting Dart Freezed models and mapping @JsonKey names."""
    dart_file = tmp_path / "execution_models.dart"
    dart_file.write_text(
        "import 'package:freezed_annotation/freezed_annotation.dart';\n\n"
        "part 'execution_models.freezed.dart';\n\n"
        "@freezed\n"
        "abstract class ExecutionRecordDTO with _$ExecutionRecordDTO {\n"
        "  const factory ExecutionRecordDTO({\n"
        "    @JsonKey(name: 'execution_id') required String executionId,\n"
        "    required int stepCount,\n"
        "    @Default(true) bool isActive,\n"
        "  }) = _ExecutionRecordDTO;\n"
        "}\n\n"
        "@Freezed()\n"
        "class SecondDTO with _$SecondDTO {\n"
        "  const factory SecondDTO({\n"
        "    required String userId,\n"
        "  }) = _SecondDTO;\n"
        "}\n",
        encoding="utf-8",
    )

    models = extract_freezed_fields(dart_file)
    assert "ExecutionRecordDTO" in models
    assert models["ExecutionRecordDTO"] == {"execution_id", "step_count", "is_active"}

    assert "SecondDTO" in models
    assert models["SecondDTO"] == {"user_id"}


def test_extract_freezed_fields_fault_resilience(tmp_path: Path) -> None:
    """Test extract_freezed_fields fault domain resilience on binary and missing files."""
    bad_bytes = tmp_path / "bad.dart"
    bad_bytes.write_bytes(b"\xff\xfe\x00\x00@freezed class X {}")
    assert extract_freezed_fields(bad_bytes) == {}

    assert extract_freezed_fields(tmp_path / "missing.dart") == {}

    txt_file = tmp_path / "test.txt"
    txt_file.write_text("@freezed class X {}", encoding="utf-8")
    assert extract_freezed_fields(txt_file) == {}


def test_audit_parity_report_matching_and_mismatches(tmp_path: Path) -> None:
    """Test audit_parity_report generating structured DtoParityReportDTO."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    # Model 1: Fully matching
    (backend_dir / "user.py").write_text("class UserDTO:\n    user_id: str\n    email: str\n", encoding="utf-8")
    (frontend_dir / "user.dart").write_text(
        "@freezed\nabstract class UserDTO with _$UserDTO {\n  const factory UserDTO({\n    @JsonKey(name: 'user_id') required String userId,\n    required String email,\n  }) = _UserDTO;\n}\n",
        encoding="utf-8",
    )

    report = audit_parity_report(backend_dir, frontend_dir)
    assert isinstance(report, DtoParityReportDTO)
    assert report.is_success is True
    assert report.shared_models_count == 1
    assert report.mismatches == []

    # Model 2: Missing field in Frontend
    (backend_dir / "profile.py").write_text("class ProfileDTO:\n    profile_id: str\n    bio: str\n", encoding="utf-8")
    (frontend_dir / "profile.dart").write_text(
        "@freezed\nabstract class ProfileDTO with _$ProfileDTO {\n  const factory ProfileDTO({\n    @JsonKey(name: 'profile_id') required String profileId,\n  }) = _ProfileDTO;\n}\n",
        encoding="utf-8",
    )

    report2 = audit_parity_report(backend_dir, frontend_dir)
    assert report2.is_success is False
    assert report2.shared_models_count == 2
    assert len(report2.mismatches) == 1
    mismatch = report2.mismatches[0]
    assert isinstance(mismatch, DtoFieldMismatchDTO)
    assert mismatch.model_name == "ProfileDTO"
    assert mismatch.field_name == "bio"
    assert "Missing in Frontend" in report2.summary_messages[0]

    # Legacy tuple wrapper verification
    is_success, msgs = audit_parity(backend_dir, frontend_dir)
    assert is_success is False
    assert len(msgs) == 1


def test_audit_dto_parity_main_cli_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI main() for DTO parity auditing."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    (backend_dir / "model.py").write_text("class ModelDTO:\n    id: str\n", encoding="utf-8")
    (frontend_dir / "model.dart").write_text(
        "@freezed\nabstract class ModelDTO with _$ModelDTO {\n  const factory ModelDTO({\n    required String id,\n  }) = _ModelDTO;\n}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["audit_dto_parity.py", "--backend-dir", str(backend_dir), "--frontend-dir", str(frontend_dir)],
    )
    try:
        audit_dto_parity_main()
    except SystemExit as e:
        assert e.code == 0

    # Failure case
    (backend_dir / "model.py").write_text("class ModelDTO:\n    id: str\n    extra_key: str\n", encoding="utf-8")
    try:
        audit_dto_parity_main()
    except SystemExit as e:
        assert e.code == 1


def test_zero_reflection_in_audit_dto_parity() -> None:
    """Zero-Reflection Compliance Test: Verify 0 getattr or hasattr calls in audit_dto_parity.py."""
    source_file = Path("scripts/audit_dto_parity.py").resolve()
    assert source_file.exists()

    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    reflection_calls: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        match node:
            case ast.Call(func=ast.Name(id=func_name)) if func_name in ("getattr", "hasattr"):
                reflection_calls.append((func_name, node.lineno))
            case _:
                pass

    assert reflection_calls == [], f"Forbidden reflection calls found in audit_dto_parity.py: {reflection_calls}"
