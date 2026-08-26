"""ISTQB Unit Tests for AST Codebase Guardrails Engine (_ast_guardrails.py).

Verifies QGR000 through QGR010 detection, false-positive immunity, fault domain isolation,
comment suppression across multiline spans, CLI execution, and zero-reflection self-compliance.
"""

from __future__ import annotations

import ast
import sys
import tokenize
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts._ast_guardrails import (
    GuardrailSeverity,
    GuardrailViolation,
    format_violations_table,
    main,
    scan_file_for_guardrails,
    scan_files_for_guardrails,
    scan_source_code_for_guardrails,
)


def _scan_snippet(code: str, filepath: str = "backend_v2/services/sample.py") -> list[GuardrailViolation]:
    """Helper to scan a Python code snippet as source bytes."""
    return scan_source_code_for_guardrails(filepath, code.encode("utf-8"))


# ==============================================================================
# Partition 1-5: QGR000 Syntax Error Resilience & Fault Domain Isolation
# ==============================================================================


def test_qgr000_syntax_error_resilience() -> None:
    code = "def broken(\n"
    violations = _scan_snippet(code)
    assert len(violations) == 1
    v = violations[0]
    assert v.rule_code == "QGR000"
    assert v.severity == GuardrailSeverity.FATAL
    assert not v.is_suppressed
    assert "syntax error" in v.message.lower()


def test_qgr000_indentation_error_resilience() -> None:
    code = "def foo():\npass\n"
    violations = _scan_snippet(code)
    assert len(violations) == 1
    v = violations[0]
    assert v.rule_code == "QGR000"
    assert v.severity == GuardrailSeverity.FATAL


def test_qgr000_tokenize_error_resilience() -> None:
    code = "x = 1\n"
    with patch("tokenize.tokenize", side_effect=tokenize.TokenError("Unclosed string")):
        violations = _scan_snippet(code)
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_code == "QGR000"
        assert v.severity == GuardrailSeverity.FATAL
        assert "token" in v.message.lower()


def test_qgr000_recursion_error_resilience() -> None:
    code = "x = 1\n"
    with patch("ast.NodeVisitor.visit", side_effect=RecursionError("Maximum depth exceeded")):
        violations = _scan_snippet(code)
        assert len(violations) == 1
        assert violations[0].rule_code == "QGR000"
        assert violations[0].severity == GuardrailSeverity.FATAL
        assert "recursion" in violations[0].message.lower()


def test_qgr000_unicode_decode_error() -> None:
    invalid_bytes = b"\xff\xfe\x00\x00Invalid"
    violations = scan_source_code_for_guardrails("test.py", invalid_bytes)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR000"
    assert violations[0].severity == GuardrailSeverity.FATAL
    assert "encoding error" in violations[0].message.lower()


def test_qgr000_immunity_against_suppression() -> None:
    code = "def broken(  # noqa: QGR000\n"
    violations = _scan_snippet(code)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR000"
    assert violations[0].is_suppressed is False


def test_qgr000_os_read_error(tmp_path: Path) -> None:
    missing_file = tmp_path / "non_existent.py"
    violations = scan_file_for_guardrails(missing_file)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR000"
    assert violations[0].severity == GuardrailSeverity.FATAL
    assert "read error" in violations[0].message.lower()


# ==============================================================================
# Partition 6-7: QGR001 Reflection Duck-Typing (getattr / hasattr)
# ==============================================================================


def test_qgr001_getattr_detection() -> None:
    code = "val = getattr(obj, 'attr', None)\n"
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "getattr" in unsuppressed[0].message


def test_qgr001_hasattr_detection() -> None:
    code = "if hasattr(obj, 'attr'):\n    pass\n"
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "hasattr" in unsuppressed[0].message


# ==============================================================================
# Partition 8: QGR002 Lazy .get(key, default) Fallback
# ==============================================================================


def test_qgr002_get_default_detection() -> None:
    code = "val = data.get('missing_key', 'fallback_value')\n"
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR002"
    assert ".get(key, default)" in unsuppressed[0].message


# ==============================================================================
# Partition 9-10: QGR003 Broad Exception Swallowing
# ==============================================================================


def test_qgr003_silent_except_pass_detection() -> None:
    code = """
try:
    do_something()
except Exception:
    pass
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR003"


def test_qgr003_except_return_dict_detection() -> None:
    code = """
try:
    do_something()
except (Exception, BaseException):
    return {}
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR003"


def test_qgr003_bare_except_detection() -> None:
    code = """
try:
    do_something()
except:
    pass
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR003"


# ==============================================================================
# Partition 11-12: QGR004 BaseModel Pseudo-Class Overrides (__new__, model_construct)
# ==============================================================================


def test_qgr004_new_on_basemodel_detection() -> None:
    code = """
class ChameleonModel(BaseModel):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr004 = [v for v in unsuppressed if v.rule_code == "QGR004"]
    assert len(qgr004) == 1
    assert "__new__" in qgr004[0].message


def test_qgr004_model_construct_on_basemodel_detection() -> None:
    code = """
class ChameleonModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    @classmethod
    def model_construct(cls, *args, **kwargs):
        return cls()
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr004 = [v for v in unsuppressed if v.rule_code == "QGR004"]
    assert len(qgr004) == 1
    assert "model_construct" in qgr004[0].message


# ==============================================================================
# Partition 13: QGR005 Raw String Category Routing
# ==============================================================================


def test_qgr005_raw_string_category_routing() -> None:
    code = """
if block.category_id == "matrix":
    do_matrix()
elif category == "system_rule":
    do_rule()
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr005 = [v for v in unsuppressed if v.rule_code == "QGR005"]
    assert len(qgr005) == 2


# ==============================================================================
# Partition 14: QGR006 asyncio.gather()
# ==============================================================================


def test_qgr006_asyncio_gather_detection() -> None:
    code = "results = await asyncio.gather(task1(), task2())\n"
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR006"


# ==============================================================================
# Partition 15: QGR007 Pydantic Model Strictness Configuration
# ==============================================================================


def test_qgr007_basemodel_missing_strictness_config() -> None:
    code = """
class BadModel(BaseModel):
    name: str
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr007 = [v for v in unsuppressed if v.rule_code == "QGR007"]
    assert len(qgr007) == 1
    assert "ConfigDict" in qgr007[0].message


def test_qgr007_basemodel_incomplete_strictness_config() -> None:
    code = """
class LooseModel(BaseModel):
    model_config = ConfigDict(strict=True)  # missing extra='forbid'
    name: str
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr007 = [v for v in unsuppressed if v.rule_code == "QGR007"]
    assert len(qgr007) == 1


def test_qgr007_annassign_config_detection() -> None:
    code = """
class ValidAnnModel(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    name: str
"""
    violations = _scan_snippet(code)
    qgr007 = [v for v in violations if v.rule_code == "QGR007"]
    assert len(qgr007) == 0


def test_qgr007_inherited_local_model() -> None:
    code = """
class BaseParentDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str

class ChildDTO(BaseParentDTO):
    name: str
"""
    violations = _scan_snippet(code)
    qgr007 = [v for v in violations if v.rule_code == "QGR007"]
    assert len(qgr007) == 0


# ==============================================================================
# Partition 16: QGR008 Hardcoded Magic Timeouts and Sleep in Domain Services
# ==============================================================================


def test_qgr008_hardcoded_timeout_and_sleep() -> None:
    code = """
client = httpx.AsyncClient(timeout=10)
await asyncio.sleep(5)
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/network.py")
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr008 = [v for v in unsuppressed if v.rule_code == "QGR008"]
    assert len(qgr008) == 2


# ==============================================================================
# Partition 17: QGR009 AppException Untyped Error Code
# ==============================================================================


def test_qgr009_app_exception_untyped_error_code() -> None:
    code = """
raise AppException("Direct raw string message")
raise AppException(error_code="invalid_string", message="error")
raise AppException()
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr009 = [v for v in unsuppressed if v.rule_code == "QGR009"]
    assert len(qgr009) == 3


# ==============================================================================
# Partition 18: QGR010 Naive Datetime / Deprecated Utcnow
# ==============================================================================


def test_qgr010_naive_datetime_and_utcnow() -> None:
    code = """
t1 = datetime.now()
t2 = datetime.utcnow()
t3 = datetime.now(tz=None)
"""
    violations = _scan_snippet(code)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    qgr010 = [v for v in unsuppressed if v.rule_code == "QGR010"]
    assert len(qgr010) == 3


# ==============================================================================
# Partition 19-26: False-Positive Immunity Verification
# ==============================================================================


def test_false_positive_immunity_string_literals() -> None:
    code = """
label1 = "getattr"
label2 = "hasattr"
label3 = "utcnow"
label4 = "matrix"
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_comments_and_docstrings() -> None:
    code = '''
"""
This docstring mentions getattr(), hasattr(), datetime.now(), and asyncio.gather().
"""
# A comment mentioning except Exception: pass and timeout=10
def safe_func():
    pass
'''
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_environ_and_headers() -> None:
    code = """
port = os.environ.get("PORT", "8000")
auth = request.headers.get("Authorization", "")
custom_header = headers.get("X-Custom", "default")
env_port = environ.get("HOST", "localhost")
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_enum_label_map() -> None:
    code = """
label = _LABEL_MAP.get(key, "Unknown")
other = LABEL_MAP.get(key, "Default")
val = _VALUE_MAP.get(k, 0)
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_datetime_utc() -> None:
    code = """
t1 = datetime.now(UTC)
t2 = datetime.now(timezone.utc)
t3 = datetime.now(tz=UTC)
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_taskgroup() -> None:
    code = """
async with asyncio.TaskGroup() as tg:
    tg.create_task(task1())
    tg.create_task(task2())
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_app_exception_typed() -> None:
    code = """
raise AppException(ErrorCodes.VALIDATION_FAILED, "Payload is invalid")
raise AppException(error_code=ErrorCodes.RESOURCE_NOT_FOUND, message="Missing item")
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


def test_false_positive_immunity_timeouts_in_test_files() -> None:
    code = """
client = httpx.AsyncClient(timeout=10)
await asyncio.sleep(5)
class TestFixtureModel(BaseModel):
    name: str
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    assert len(violations) == 0


# ==============================================================================
# Partition 27-31: Inline and Multiline Suppression Verification
# ==============================================================================


def test_inline_suppression_single_line_with_valid_reason() -> None:
    code = "val = getattr(obj, 'attr', None)  # noqa: QGR001 [REASON: Third-party LiteLLM model attribute]\n"
    violations = _scan_snippet(code)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"
    assert violations[0].is_suppressed is True


def test_inline_suppression_missing_reason_fails_fatal() -> None:
    code = "val = getattr(obj, 'attr', None)  # noqa: QGR001\n"
    violations = _scan_snippet(code)
    assert len(violations) == 2
    # First violation is QGR000 FATAL for missing reason
    qgr000 = next(v for v in violations if v.rule_code == "QGR000")
    assert qgr000.severity == GuardrailSeverity.FATAL
    assert "Missing or insufficient '[REASON:" in qgr000.message
    # Original violation is NOT suppressed
    qgr001 = next(v for v in violations if v.rule_code == "QGR001")
    assert qgr001.is_suppressed is False


def test_inline_suppression_placeholder_reason_fails_fatal() -> None:
    for placeholder in ["test", "n/a", "ok", "todo", "short"]:
        code = f"val = getattr(obj, 'attr', None)  # noqa: QGR001 [REASON: {placeholder}]\n"
        violations = _scan_snippet(code)
        qgr000 = next((v for v in violations if v.rule_code == "QGR000"), None)
        assert qgr000 is not None, f"Expected QGR000 for placeholder '{placeholder}'"
        assert qgr000.severity == GuardrailSeverity.FATAL


def test_multiline_suppression_call_span_with_reason() -> None:
    code = """
val = getattr(
    obj,
    'attr',
    None,
)  # noqa: QGR001 [REASON: Dynamic model attribute access required]
"""
    violations = _scan_snippet(code)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"
    assert violations[0].is_suppressed is True


def test_multiline_suppression_except_span_with_reason() -> None:
    code = """
try:
    do_something()
except (
    Exception,
    BaseException,
):  # noqa: QGR003 [REASON: Outer crash boundary for background worker]
    return {}
"""
    violations = _scan_snippet(code)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR003"
    assert violations[0].is_suppressed is True


def test_inline_suppression_all_rules_with_reasons() -> None:
    code = """
r1 = await asyncio.gather(t1(), t2())  # noqa: QGR006 [REASON: Legacy migration in-flight step]
class LooseDTO(BaseModel):  # noqa: QGR007 [REASON: External third-party payload DTO]
    x: int
await asyncio.sleep(10)  # noqa: QGR008 [REASON: Polling backoff retry loop]
raise AppException("raw")  # noqa: QGR009 [REASON: Legacy translation bridge error]
t = datetime.now()  # noqa: QGR010 [REASON: Local timezone formatting]
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/worker.py")
    assert len(violations) == 5
    for v in violations:
        assert v.is_suppressed is True


def test_valid_except_exception_with_raise() -> None:
    code = """
try:
    process()
except Exception as e:
    logger.error("Processing failed", extra={"error": str(e)})
    raise AppException(ErrorCodes.PROCESSING_FAILED, str(e))
"""
    violations = _scan_snippet(code)
    assert len(violations) == 0


# ==============================================================================
# Partition 32-35: Multi-File Scanning, Table Formatting, CLI & Zero-Reflection Self-Test
# ==============================================================================


def test_multifile_scanning_resilience(tmp_path: Path) -> None:
    file1 = tmp_path / "broken.py"
    file1.write_text("def broken(\n", encoding="utf-8")

    file2 = tmp_path / "reflection.py"
    file2.write_text("val = getattr(obj, 'x', None)\n", encoding="utf-8")

    violations, is_success = scan_files_for_guardrails([tmp_path], strict=True)
    assert len(violations) == 2
    assert is_success is False

    rule_codes = {v.rule_code for v in violations}
    assert rule_codes == {"QGR000", "QGR001"}


def test_multifile_scanning_advisory_pass(tmp_path: Path) -> None:
    file1 = tmp_path / "warning_only.py"
    file1.write_text("val = getattr(obj, 'x', None)\n", encoding="utf-8")

    violations, is_success = scan_files_for_guardrails([tmp_path], strict=False)
    assert len(violations) == 1
    assert is_success is True  # In advisory mode, warnings don't fail


def test_format_violations_table() -> None:
    v_clean = format_violations_table([])
    assert "No AST guardrail violations found" in v_clean

    violations = [
        GuardrailViolation(
            filepath="backend_v2/sample.py",
            lineno=10,
            col_offset=4,
            rule_code="QGR001",
            message="Reflection duck typing",
            remediation="Use match/case",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        )
    ]
    report = format_violations_table(violations)
    assert "QGR001" in report
    assert "backend_v2/sample.py:10:4" in report
    assert "Use match/case" in report


def test_cli_execution_clean(tmp_path: Path) -> None:
    clean_file = tmp_path / "clean.py"
    clean_file.write_text("x = 1\n", encoding="utf-8")

    with patch.object(sys, "argv", ["_ast_guardrails.py", str(clean_file), "--strict"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


def test_cli_execution_violation_failure(tmp_path: Path) -> None:
    dirty_file = tmp_path / "dirty.py"
    dirty_file.write_text("val = getattr(obj, 'x', None)\n", encoding="utf-8")

    with patch.object(sys, "argv", ["_ast_guardrails.py", str(dirty_file), "--strict"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


def test_cli_execution_no_args() -> None:
    with patch.object(sys, "argv", ["_ast_guardrails.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


def test_zero_reflection_self_verification() -> None:
    """Verifies that the guardrail engine scripts themselves contain zero getattr/hasattr calls."""
    engine_path = Path("scripts/_ast_guardrails.py")
    audit_loop_path = Path("scripts/backend_audit_loop.py")

    for path in (engine_path, audit_loop_path):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr"):
                    pytest.fail(f"Banned reflection call `{node.func.id}()` found in {path} at line {node.lineno}")
