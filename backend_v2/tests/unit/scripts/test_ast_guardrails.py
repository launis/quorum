"""ISTQB Unit Tests for AST Codebase Guardrails Engine (_ast_guardrails.py).

Verifies QGR000 through QGR012 detection, false-positive immunity, fault domain isolation,
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
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "getattr" in unsuppressed[0].message


def test_qgr001_hasattr_detection() -> None:
    code = "if hasattr(obj, 'attr'):\n    pass\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "hasattr" in unsuppressed[0].message


def test_qgr001_setattr_detection() -> None:
    code = "setattr(obj, 'attr', 42)\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "setattr" in unsuppressed[0].message


def test_qgr001_object_setattr_detection() -> None:
    code = "object.__setattr__(obj, 'attr', 42)\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "object.__setattr__" in unsuppressed[0].message


def test_qgr001_vars_detection() -> None:
    code = "d = vars(obj)\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "vars()" in unsuppressed[0].message
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


def test_qgr001_dict_attribute_detection() -> None:
    code = "d = obj.__dict__\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert ".__dict__" in unsuppressed[0].message
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


def test_qgr001_attrgetter_detection() -> None:
    code = "getter = operator.attrgetter('name')\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert "attrgetter" in unsuppressed[0].message
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


def test_qgr001_test_file_fatal_severity() -> None:
    code = "val = getattr(obj, 'attr', None)\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR001"
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


# ==============================================================================
# Partition 8: QGR002 Lazy .get(key, default) Fallback
# ==============================================================================


def test_qgr002_get_default_detection() -> None:
    code = "val = data.get('missing_key', 'fallback_value')\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR002"
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL
    assert ".get(key, default)" in unsuppressed[0].message


def test_qgr002_single_arg_get_detection() -> None:
    code = "val = data.get('key')\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR002"
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


def test_qgr002_client_get_network_exempt() -> None:
    code = "resp = client.get('https://api.example.com', headers={'Auth': 'Bearer'})\n"
    violations = _scan_snippet(code)
    qgr002 = [v for v in violations if v.rule_code == "QGR002"]
    assert len(qgr002) == 0


def test_qgr002_zero_arg_contextvar_get_exempt() -> None:
    code = "resp = _last_response_var.get()\n"
    violations = _scan_snippet(code)
    qgr002 = [v for v in violations if v.rule_code == "QGR002"]
    assert len(qgr002) == 0


def test_qgr002_request_kwargs_exempt() -> None:
    code = "res = session.get(url, params={'q': 'test'})\n"
    violations = _scan_snippet(code)
    qgr002 = [v for v in violations if v.rule_code == "QGR002"]
    assert len(qgr002) == 0


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
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR003"


def test_qgr003_typed_exception_swallowing_fatal() -> None:
    code = """
try:
    do_something()
except (ValidationError, TypeError):
    return []
"""
    violations = _scan_snippet(code)
    unsuppressed = violations
    assert len(unsuppressed) == 1
    assert unsuppressed[0].rule_code == "QGR003"
    assert unsuppressed[0].severity == GuardrailSeverity.FATAL


def test_qgr003_dlq_push_exempt() -> None:
    code = """
try:
    do_something()
except Exception as e:
    dlq_service.push(e)
"""
    violations = _scan_snippet(code)
    qgr003 = [v for v in violations if v.rule_code == "QGR003"]
    assert len(qgr003) == 0


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
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
    qgr005 = [v for v in unsuppressed if v.rule_code == "QGR005"]
    assert len(qgr005) == 2


# ==============================================================================
# Partition 14: QGR006 asyncio.gather()
# ==============================================================================


def test_qgr006_asyncio_gather_detection() -> None:
    code = "results = await asyncio.gather(task1(), task2())\n"
    violations = _scan_snippet(code)
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
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
    unsuppressed = violations
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
raise AppException(error_code=ErrorCodes.RESOURCE_NOT_FOUND.value, message="Missing item")
raise AppException("Failed", details={"error_code": ErrorCodes.VALIDATION_FAILED})
raise AppException("Failed", details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
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
# Partition 27-31: Unconditional Violation Verification (Zero Comment Suppressions)
# ==============================================================================


def test_inline_suppression_single_line_with_valid_reason() -> None:
    code = "val = getattr(obj, 'attr', None)  # noqa: QGR001 [REASON: Third-party LiteLLM model attribute]\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/sample.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"


def test_inline_suppression_missing_reason_fails_fatal() -> None:
    code = "val = getattr(obj, 'attr', None)  # noqa: QGR001\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/sample.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"


def test_inline_suppression_placeholder_reason_fails_fatal() -> None:
    for placeholder in ["test", "n/a", "ok", "todo", "short"]:
        code = f"val = getattr(obj, 'attr', None)  # noqa: QGR001 [REASON: {placeholder}]\n"
        violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/sample.py")
        assert len(violations) == 1
        assert violations[0].rule_code == "QGR001"


def test_multiline_suppression_call_span_with_reason() -> None:
    code = """
val = getattr(
    obj,
    'attr',
    None,
)  # noqa: QGR001 [REASON: Dynamic model attribute access required]
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/sample.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"


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
    violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/sample.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR003"


def test_inline_suppression_all_rules_with_reasons() -> None:
    code = """
r1 = await asyncio.gather(t1(), t2())  # noqa: QGR006 [REASON: Legacy migration in-flight step]
class LooseDTO(BaseModel):  # noqa: QGR007 [REASON: External third-party payload DTO]
    x: int
await asyncio.sleep(10)  # noqa: QGR008 [REASON: Polling backoff retry loop]
raise AppException("raw")  # noqa: QGR009 [REASON: Legacy translation bridge error]
t = datetime.now()  # noqa: QGR010 [REASON: Local timezone formatting]
val = getattr(obj, "attr", None)  # noqa [REASON: Bare noqa wildcard rule suppression]
"""
    violations = _scan_snippet(code, filepath="scripts/worker_script.py")
    assert len(violations) == 6


def test_qgr000_domain_suppression_fatal() -> None:
    """Any AST violation in domain code emits FATAL violation regardless of # noqa comment."""
    code = "val = getattr(obj, 'attr', None)  # noqa: QGR001 [REASON: Legitimate reason for third party]\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"
    assert violations[0].severity == GuardrailSeverity.FATAL


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


def test_multifile_scanning_qgr013_fatal(tmp_path: Path) -> None:
    # QGR013 (TypeVar instantiation) is FATAL severity
    file1 = tmp_path / "warning_only.py"
    file1.write_text("from typing import TypeVar\nT = TypeVar('T')\n", encoding="utf-8")

    violations, is_success = scan_files_for_guardrails([tmp_path], strict=False)
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR013"
    assert violations[0].severity == GuardrailSeverity.FATAL
    assert is_success is False  # In advisory mode, fatal violations fail


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
    test_path = Path("backend_v2/tests/unit/scripts/test_ast_guardrails.py")

    for path in (engine_path, audit_loop_path, test_path):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr"):
                    pytest.fail(f"Banned reflection call `{node.func.id}()` found in {path} at line {node.lineno}")


# ==============================================================================
# Partition 36: QGR011 Creation DTO & Request ID Banning Tests
# ==============================================================================


def test_qgr011_detects_id_in_create_dto() -> None:
    code = """
class ItemCreateDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    name: str
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/item.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR011"
    assert "ItemCreateDTO" in violations[0].message


def test_qgr011_detects_id_in_create_request() -> None:
    code = """
class ItemCreateRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str = Field(description="Custom ID")
    name: str
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/item.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR011"
    assert "ItemCreateRequest" in violations[0].message


def test_qgr011_allows_id_in_response_or_domain() -> None:
    code = """
class ItemResponseDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    name: str

class DomainItem(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    name: str
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/item.py")
    assert len(violations) == 0


def test_qgr011_allows_create_dto_without_id() -> None:
    code = """
class ItemCreateDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    name: str
    description: str | None = None
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/item.py")
    assert len(violations) == 0


# ==============================================================================
# Partition 37: QGR012 isinstance(..., dict) Detection & Relative Path Hardening
# ==============================================================================


def test_qgr012_detects_direct_isinstance_dict() -> None:
    code = "if isinstance(payload, dict):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR012"
    assert violations[0].severity == GuardrailSeverity.FATAL
    assert "isinstance(..., dict)" in violations[0].message


def test_qgr012_detects_tuple_isinstance_with_dict() -> None:
    code = "if isinstance(payload, (str, dict, list)):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/hooks/scoring.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR012"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_qgr012_allows_isinstance_non_dict() -> None:
    code = "if isinstance(payload, (str, list, int)):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    assert len(violations) == 0


def test_qgr012_boundary_exemption_honored() -> None:
    code = "if isinstance(payload, dict):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/database/tinydb_driver.py")
    qgr012 = [v for v in violations if v.rule_code == "QGR012"]
    assert len(qgr012) == 0


def test_qgr012_isinstance_dict_in_domain_fatal() -> None:
    code = "if isinstance(payload, dict):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr012 = [v for v in violations if v.rule_code == "QGR012"]
    assert len(qgr012) == 1
    assert qgr012[0].rule_code == "QGR012"
    assert qgr012[0].severity == GuardrailSeverity.FATAL


def test_relative_path_fatal_enforcement() -> None:
    """Verifies that relative path inputs (models/foo.py, services/foo.py, hooks/bar.py) trigger FATAL severity."""
    code_qgr001 = "x = getattr(obj, 'attr', None)\n"
    code_qgr002 = "x = data.get('key', 'default')\n"
    code_qgr012 = "if isinstance(data, dict):\n    pass\n"

    # Services relative path -> FATAL
    v1 = scan_source_code_for_guardrails("services/foo.py", code_qgr001.encode("utf-8"))
    assert len(v1) == 1
    assert v1[0].rule_code == "QGR001"
    assert v1[0].severity == GuardrailSeverity.FATAL

    v2 = scan_source_code_for_guardrails("services/foo.py", code_qgr002.encode("utf-8"))
    assert len(v2) == 1
    assert v2[0].rule_code == "QGR002"
    assert v2[0].severity == GuardrailSeverity.FATAL

    v3 = scan_source_code_for_guardrails("services/foo.py", code_qgr012.encode("utf-8"))
    assert len(v3) == 1
    assert v3[0].rule_code == "QGR012"
    assert v3[0].severity == GuardrailSeverity.FATAL

    # Hooks relative path -> FATAL
    v4 = scan_source_code_for_guardrails("hooks/bar.py", code_qgr012.encode("utf-8"))
    assert len(v4) == 1
    assert v4[0].rule_code == "QGR012"
    assert v4[0].severity == GuardrailSeverity.FATAL

    # Models relative path -> FATAL
    v5 = scan_source_code_for_guardrails("backend_v2/models/sample.py", code_qgr012.encode("utf-8"))
    assert len(v5) == 1
    assert v5[0].rule_code == "QGR012"
    assert v5[0].severity == GuardrailSeverity.FATAL


def test_qgr012_fatal_severity_in_test_files() -> None:
    """Verifies that test files receive FATAL severity for isinstance dict checks."""
    code = "if isinstance(payload, dict):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_item.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR012"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_qgr012_mapping_fatal_in_domain_code() -> None:
    """Verifies that domain code receives FATAL severity for isinstance Mapping checks."""
    code = "from collections.abc import Mapping\nif isinstance(payload, Mapping):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR012"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_qgr012_match_case_dict_patterns() -> None:
    """Verifies that match/case dict, MatchMapping, and MatchOr dict patterns are detected."""
    code_match_class = "match data:\n    case dict():\n        pass\n"
    v1 = _scan_snippet(code_match_class, filepath="backend_v2/services/execution.py")
    assert len(v1) == 1
    assert v1[0].rule_code == "QGR012"
    assert v1[0].severity == GuardrailSeverity.FATAL

    code_match_mapping = "match data:\n    case {'key': val}:\n        pass\n"
    v2 = _scan_snippet(code_match_mapping, filepath="backend_v2/services/execution.py")
    assert len(v2) == 1
    assert v2[0].rule_code == "QGR012"
    assert v2[0].severity == GuardrailSeverity.FATAL

    code_match_or = "match data:\n    case int() | dict():\n        pass\n"
    v3 = _scan_snippet(code_match_or, filepath="backend_v2/services/execution.py")
    assert len(v3) == 1
    assert v3[0].rule_code == "QGR012"
    assert v3[0].severity == GuardrailSeverity.FATAL


# ==============================================================================
# Contract Tests: Explicit Epic 150 Phase 4 Test Contracts
# ==============================================================================


def test_ast_guardrails_fatal_rejection_on_dict_messages() -> None:
    """Contract 1: isinstance(payload, dict) in models returns QGR012 with FATAL severity."""
    code = "if isinstance(payload, dict):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/sample.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR012"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_ast_guardrails_exempt_driver_fatal_severity() -> None:
    """Contract 2: Exempt boundary files receive FATAL severity unconditionally."""
    code = "val = getattr(obj, 'x', None)\n"
    violations = _scan_snippet(code, filepath="backend_v2/database/tinydb_driver.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_ast_guardrails_qgr001_fatal_in_models() -> None:
    """Contract 3: getattr(obj, 'attr') in domain models returns QGR001 with FATAL severity."""
    code = "val = getattr(obj, 'attr', None)\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/domain.py")
    assert len(violations) == 1
    assert violations[0].rule_code == "QGR001"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_qgr013_typevar_fatal() -> None:
    """QGR013: Banned TypeVar instantiation returns FATAL severity."""
    code = "from typing import TypeVar\nT = TypeVar('T')\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample.py")
    qgr013 = [v for v in violations if v.rule_code == "QGR013"]
    assert len(qgr013) == 1
    assert qgr013[0].severity == GuardrailSeverity.FATAL
    assert "TypeVar" in qgr013[0].message


def test_qgr014_asyncmock_repository_fatal() -> None:
    """QGR014: AsyncMock(spec=IWorkflowRepository) returns FATAL severity."""
    code = "from unittest.mock import AsyncMock\nfrom backend_v2.database.interfaces import IWorkflowRepository\nmock = AsyncMock(spec=IWorkflowRepository)\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/services/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) >= 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL


def test_qgr014_mock_repo_variable_assignment_fatal() -> None:
    """QGR014: Variable assignment to mock_repo = AsyncMock() returns FATAL severity."""
    code = "from unittest.mock import AsyncMock\nmock_repo = AsyncMock()\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/services/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) >= 1
    assert any(v.severity == GuardrailSeverity.FATAL for v in qgr014)


def test_qgr014_mock_report_variable_assignment_emits_no_violation() -> None:
    """QGR014 False-Positive Defense: mock_report = MagicMock() emits 0 violations."""
    code = "from unittest.mock import MagicMock\nmock_report = MagicMock()\nmock_report_dto = MagicMock()\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/scripts/test_matrix_slice_engine.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 0


def test_qgr014_patch_repository_fatal() -> None:
    """QGR014: patch('backend_v2.database.interfaces.IWorkflowRepository') returns FATAL."""
    code = (
        "from unittest.mock import patch\nwith patch('backend_v2.database.interfaces.IWorkflowRepository'):\n    pass\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/services/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) >= 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL


def test_qgr014_detection_a_fixture_returning_mock_fatal() -> None:
    """QGR014 (a): Function/fixture with repo identifier returning AsyncMock raises QGR014 FATAL."""
    code = "from unittest.mock import AsyncMock\ndef repo_fixture():\n    return AsyncMock()\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "repo_fixture" in qgr014[0].message


def test_qgr014_detection_b_return_value_assignment_fatal() -> None:
    """QGR014 (b): repo.get_step.return_value = {} raises QGR014 FATAL."""
    code = "repo.get_step.return_value = {}\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "return_value" in qgr014[0].message


def test_qgr014_detection_c_attribute_replacement_fatal() -> None:
    """QGR014 (c): exec_repo.get_execution = AsyncMock(return_value=rec) raises QGR014 FATAL."""
    code = "from unittest.mock import AsyncMock\nexec_repo.get_execution = AsyncMock(return_value=rec)\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "exec_repo.get_execution" in qgr014[0].message


def test_qgr014_detection_d_monkeypatch_object_fatal() -> None:
    """QGR014 (d): monkeypatch.setattr(system_repo, 'get_model_registry', AsyncMock()) raises QGR014 FATAL."""
    code = "from unittest.mock import AsyncMock\nmonkeypatch.setattr(system_repo, 'get_model_registry', AsyncMock())\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) >= 1
    assert any(v.severity == GuardrailSeverity.FATAL for v in qgr014)
    assert any("system_repo" in v.message for v in qgr014)


def test_qgr014_detection_e_keyword_injected_mock_fatal() -> None:
    """QGR014 (e): HookDependencies(exec_repo=MagicMock()) raises QGR014 FATAL."""
    code = "from unittest.mock import MagicMock\ndeps = HookDependencies(exec_repo=MagicMock())\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "exec_repo" in qgr014[0].message


def test_qgr014_detection_f_string_target_patch_without_fake_fatal() -> None:
    """QGR014 (f): patch('backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository') raises QGR014 FATAL."""
    code = (
        "from unittest.mock import patch\n"
        "@patch('backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository')\n"
        "def test_worker(mock_repo_cls):\n"
        "    pass\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "UnifiedWorkflowRepository" in qgr014[0].message


def test_qgr014_detection_g_adhoc_repository_class_fatal() -> None:
    """QGR014 (g): Class MockRepoWaterfall defining get_output_profile_by_id in test module raises QGR014 FATAL."""
    code = "class MockRepoWaterfall:\n    def get_output_profile_by_id(self, profile_id: str):\n        pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL
    assert "MockRepoWaterfall" in qgr014[0].message
    assert "get_output_profile_by_id" in qgr014[0].message


def test_qgr014_positive_immunity_non_repository_mock() -> None:
    """QGR014 Immunity 1: mock_report_service.get_report.return_value = ReportDataDTO(...) produces 0 violations."""
    code = "mock_report_service.get_report.return_value = ReportDataDTO()\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 0


def test_qgr014_positive_immunity_settings_monkeypatch() -> None:
    """QGR014 Immunity 2: monkeypatch.setattr('backend_v2.services.execution.stream_service.get_settings', factory) produces 0 violations."""
    code = "monkeypatch.setattr('backend_v2.services.execution.stream_service.get_settings', factory)\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 0


def test_qgr014_positive_immunity_fake_bound_patch() -> None:
    """QGR014 Immunity 3: patch('backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository', return_value=InMemoryUnifiedWorkflowRepository()) produces 0 violations."""
    code = (
        "from unittest.mock import patch\n"
        "with patch('backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository', return_value=InMemoryUnifiedWorkflowRepository()):\n"
        "    pass\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 0


def test_qgr014_positive_immunity_storage_driver_patch() -> None:
    """QGR014 Immunity 4: patch('backend_v2.database.repositories.execution.get_storage_driver') produces 0 violations."""
    code = (
        "from unittest.mock import patch\n"
        "with patch('backend_v2.database.repositories.execution.get_storage_driver'):\n"
        "    pass\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 0


def test_qgr015_typeguard_import_and_usage_fatal() -> None:
    """QGR015: TypeGuard import and annotation returns FATAL severity."""
    code = "from typing import TypeGuard\ndef is_str(val: object) -> TypeGuard[str]:\n    return isinstance(val, str)\n"
    violations = _scan_snippet(code, filepath="backend_v2/utils/narrowing.py")
    qgr015 = [v for v in violations if v.rule_code == "QGR015"]
    assert len(qgr015) >= 1
    assert qgr015[0].severity == GuardrailSeverity.FATAL


def test_purged_boundary_exemption_files() -> None:
    """Verify non-driver files are purged and BOUNDARY_EXEMPTION_FILES contains exactly the 15 SSOT paths."""
    from scripts._ast_guardrails import BOUNDARY_EXEMPTION_FILES

    purged = [
        "backend_v2/models/dtos/telemetry.py",
        "backend_v2/api/routers/system/telemetry.py",
        "backend_v2/services/sdui/adapters/base_adapter.py",
        "backend_v2/core/interfaces.py",
        "backend_v2/exceptions.py",
        "backend_v2/services/alias_engine.py",
        "backend_v2/services/state_reducer.py",
    ]
    for filename in purged:
        assert filename not in BOUNDARY_EXEMPTION_FILES

    assert BOUNDARY_EXEMPTION_FILES == frozenset(
        {
            "backend_v2/database/tinydb_driver.py",
            "backend_v2/database/firestore_driver.py",
            "backend_v2/database/driver.py",
            "backend_v2/database/wrapper.py",
            "backend_v2/llm/provider.py",
            "backend_v2/llm/handler.py",
            "backend_v2/logging_config.py",
            "backend_v2/core/telemetry.py",
            "backend_v2/llm/adapters/base_adapter.py",
            "backend_v2/llm/adapters/vertex_adapter.py",
            "backend_v2/llm/adapters/ai_studio_adapter.py",
            "backend_v2/llm/adapters/openai_adapter.py",
            "backend_v2/llm/adapters/anthropic_adapter.py",
            "backend_v2/llm/adapters/deepseek_adapter.py",
            "backend_v2/llm/adapters/mock_adapter.py",
        }
    )


# ==============================================================================
# Partition: QGR016 Lazy Fallback Prohibition
# ==============================================================================


def test_qgr016_literal_string_fallback_fatal_in_domain() -> None:
    """QGR016: x = val or 'default' in domain code emits FATAL violation."""
    code = "locale = requested_locale or 'fi'\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 1
    assert qgr016[0].severity == GuardrailSeverity.FATAL
    assert "lazy literal fallback" in qgr016[0].message


def test_qgr016_literal_collection_fallback_fatal_in_domain() -> None:
    """QGR016: x = val or [] and x = val or {} in domain code emit FATAL violations."""
    code = "items = user_items or []\nmeta = data or {}\n"
    violations = _scan_snippet(code, filepath="backend_v2/hooks/scoring/matrix_hook.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 2
    assert all(v.severity == GuardrailSeverity.FATAL for v in qgr016)


def test_qgr016_literal_none_and_number_fallback_fatal_in_domain() -> None:
    """QGR016: x = val or None and x = val or 0 in domain code emit FATAL violations."""
    code = "score = raw_score or 0\nfallback = user_val or None\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/domain/synthesis.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 2
    assert all(v.severity == GuardrailSeverity.FATAL for v in qgr016)


def test_qgr016_multivariable_fallback_chain_fatal() -> None:
    """QGR016: multi-variable fallback chains (>= 3 operands) emit FATAL violation in domain code."""
    code = "profile_id = opt_profile or active_profile or default_profile\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/orchestration.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 1
    assert qgr016[0].severity == GuardrailSeverity.FATAL
    assert "multi-fallback chain" in qgr016[0].message


def test_qgr016_boolean_condition_allowed_false_positive_immunity() -> None:
    """QGR016: Boolean branching conditions (e.g. if a or b:) emit 0 violations."""
    code = "if is_admin or is_super_admin:\n    proceed()\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/auth.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 0


def test_qgr016_boundary_exempt_file_fatal() -> None:
    """QGR016: Boundary exemption files emit FATAL severity unconditionally."""
    code = "conn = raw_conn or 'localhost'\n"
    violations = _scan_snippet(code, filepath="backend_v2/database/drivers/tinydb_driver.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 1
    assert qgr016[0].severity == GuardrailSeverity.FATAL


def test_qgr016_comment_suppression_rejected() -> None:
    """QGR016: Comment suppression does not suppress the violation."""
    code = "x = val or 'default'  # noqa: QGR016 [REASON: legacy compatibility boundary]\n"
    violations = _scan_snippet(code, filepath="backend_v2/database/tinydb_driver.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 1
    assert qgr016[0].severity == GuardrailSeverity.FATAL


def test_qgr016_ternary_literal_fallback_in_domain() -> None:
    """QGR016: Ternary fallback (e.g. x if x is not None else 'default') emits FATAL violation in domain code."""
    code = "loc = user_locale if user_locale else 'fi'\nitems = raw_items if raw_items is not None else []\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 2
    assert all(v.severity == GuardrailSeverity.FATAL for v in qgr016)
    assert all("ternary lazy fallback" in v.message for v in qgr016)


def test_qgr016_ternary_constant_branching_allowed() -> None:
    """QGR016: Ternary conditional selection between two constants (e.g. 'PASSED' if is_ok else 'FAILED') is permitted."""
    code = "status = 'PASSED' if is_ok else 'FAILED'\nflag = True if mode == 1 else False\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr016 = [v for v in violations if v.rule_code == "QGR016"]
    assert len(qgr016) == 0


# ==============================================================================
# Partition: QGR017 Eradicated Facade Import Ban (v2_core)
# ==============================================================================


def test_qgr017_import_from_v2_core_fatal() -> None:
    """QGR017: from backend_v2.models.v2_core import ... emits FATAL violation."""
    code = "from backend_v2.models.v2_core import Step, ExecutionRecord\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/foo.py")
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017) == 1
    assert qgr017[0].severity == GuardrailSeverity.FATAL
    assert "backend_v2.models.v2_core" in qgr017[0].message


def test_qgr017_import_v2_core_module_fatal() -> None:
    """QGR017: import backend_v2.models.v2_core emits FATAL violation."""
    code = "import backend_v2.models.v2_core\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/foo.py")
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017) == 1
    assert qgr017[0].severity == GuardrailSeverity.FATAL
    assert "backend_v2.models.v2_core" in qgr017[0].message


def test_qgr017_import_symbol_from_models_fatal() -> None:
    """QGR017: from backend_v2.models import v2_core emits FATAL violation."""
    code = "from backend_v2.models import v2_core\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/foo.py")
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017) == 1
    assert qgr017[0].severity == GuardrailSeverity.FATAL
    assert "v2_core" in qgr017[0].message


def test_qgr017_canonical_imports_allowed_false_positive_immunity() -> None:
    """QGR017: Canonical domain and DTO imports produce zero violations."""
    code = (
        "from backend_v2.models.domain.step import Step\n"
        "from backend_v2.models.domain.execution import ExecutionRecord\n"
        "from backend_v2.models.dtos.atom_result import AtomEvaluationResultDTO\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/services/foo.py")
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017) == 0


def test_qgr017_comment_suppression_rejected() -> None:
    """QGR017: Comment suppression does not suppress the violation."""
    code = "from backend_v2.models.v2_core import Step  # noqa: QGR017 [REASON: temporary historical testing fixture]\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/fakes/foo.py")
    qgr017 = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017) == 1


# ==============================================================================
# Partition: QGR018 TypeAdapter Dictionary Laundering Ban & Boundary Exemptions
# ==============================================================================


def test_qgr018_typeadapter_dict_laundering_fatal() -> None:
    code = "adapter = TypeAdapter(dict" + "[str, Any])\n"
    violations = _scan_snippet(code)
    qgr018 = [v for v in violations if v.rule_code == "QGR018"]
    assert len(qgr018) == 1
    assert qgr018[0].severity == GuardrailSeverity.FATAL
    assert "TypeAdapter" in qgr018[0].message


def test_qgr018_typeadapter_dto_allowed() -> None:
    code = "adapter = TypeAdapter(WorkflowResponseDTO)\n"
    violations = _scan_snippet(code)
    qgr018 = [v for v in violations if v.rule_code == "QGR018"]
    assert len(qgr018) == 0


def test_qgr018_typeadapter_mapping_laundering_fatal() -> None:
    code = "from collections.abc import Mapping\nfrom pydantic import JsonValue, TypeAdapter\nadapter = TypeAdapter(Mapping[str, JsonValue])\n"
    violations = _scan_snippet(code)
    qgr018 = [v for v in violations if v.rule_code == "QGR018"]
    assert len(qgr018) == 1
    assert qgr018[0].severity == GuardrailSeverity.FATAL
    assert "TypeAdapter" in qgr018[0].message


def test_boundary_exemption_files_preserved() -> None:
    code = "val = getattr(obj, 'k', None)\n"
    for exempt_file in ["tinydb_driver.py", "firestore_driver.py", "provider.py", "logging_config.py"]:
        violations = _scan_snippet(code, filepath=f"backend_v2/database/drivers/{exempt_file}")
        assert all(v.severity == GuardrailSeverity.FATAL for v in violations)


def test_qgr013_qgr015_emit_fatal_severity() -> None:
    """Contract: Scan code snippets containing TypeVar (QGR013) or TypeGuard (QGR015) emit FATAL severity."""
    typevar_code = "from typing import TypeVar\nT = TypeVar('T')\n"
    v_typevar = _scan_snippet(typevar_code, filepath="backend_v2/services/typevar_service.py")
    assert len(v_typevar) == 1
    assert v_typevar[0].rule_code == "QGR013"
    assert v_typevar[0].severity == GuardrailSeverity.FATAL

    typeguard_code = "from typing import TypeGuard\ndef is_str(val: object) -> TypeGuard[str]:\n    return True\n"
    v_typeguard = _scan_snippet(typeguard_code, filepath="backend_v2/services/guard_service.py")
    assert any(v.rule_code == "QGR015" and v.severity == GuardrailSeverity.FATAL for v in v_typeguard)


def test_ast_guardrails_python3_tuple_exceptions() -> None:
    """Verify that Python AST guardrail engine executes without comma syntax errors."""
    code = "try:\n    pass\nexcept (AttributeError, io.UnsupportedOperation):\n    raise\n"
    violations = _scan_snippet(code)
    assert len(violations) == 0


# ==============================================================================
# Partition: QGR012 Mapping Duck-Typing & QGR019 Dict Pop Mutation Ban
# ==============================================================================


def test_qgr012_mapping_duck_typing_detected() -> None:
    """QGR012: isinstance(..., Mapping) in domain code triggers QGR012 violation."""
    code = "if isinstance(payload, Mapping):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample_service.py")
    qgr012 = [v for v in violations if v.rule_code == "QGR012"]
    assert len(qgr012) == 1
    assert "Mapping" in qgr012[0].message


def test_qgr019_dict_pop_detected() -> None:
    """QGR019: d.pop('key', None) in domain code triggers QGR019 violation."""
    code = "payload.pop('shuffled_atoms', None)\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample_service.py")
    qgr019 = [v for v in violations if v.rule_code == "QGR019"]
    assert len(qgr019) == 1
    assert qgr019[0].rule_code == "QGR019"
    assert ".pop(key, ...)" in qgr019[0].message


def test_qgr019_list_pop_exempt() -> None:
    """QGR019: list.pop() and queue.pop(0) are exempt from QGR019."""
    code = "last_item = items.pop()\nfirst_item = queue.pop(0)\npos_item = items.pop(index)\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample_service.py")
    qgr019 = [v for v in violations if v.rule_code == "QGR019"]
    assert len(qgr019) == 0


def test_qgr012_tuple_mapping_duck_typing_detected() -> None:
    """QGR012: isinstance(..., (list, Mapping)) in domain code triggers QGR012 violation."""
    code = "if isinstance(payload, (list, Mapping)):\n    pass\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample_service.py")
    qgr012 = [v for v in violations if v.rule_code == "QGR012"]
    assert len(qgr012) == 1
    assert "Mapping" in qgr012[0].message


def test_qgr012_union_bitor_mapping_and_dict_duck_typing_detected() -> None:
    """QGR012: isinstance(..., BaseModel | Mapping) and isinstance(..., BaseModel | dict) trigger QGR012 violation."""
    code_mapping = "if isinstance(payload, BaseModel | Mapping):\n    pass\n"
    violations_mapping = _scan_snippet(code_mapping, filepath="backend_v2/services/sample_service.py")
    qgr012_mapping = [v for v in violations_mapping if v.rule_code == "QGR012"]
    assert len(qgr012_mapping) == 1
    assert "Mapping" in qgr012_mapping[0].message

    code_dict = "if isinstance(payload, BaseModel | dict):\n    pass\n"
    violations_dict = _scan_snippet(code_dict, filepath="backend_v2/services/sample_service.py")
    qgr012_dict = [v for v in violations_dict if v.rule_code == "QGR012"]
    assert len(qgr012_dict) == 1
    assert "dict" in qgr012_dict[0].message


def test_qgr019_dict_pop_variable_and_two_args() -> None:
    """QGR019: d.pop(key_var) and d.pop('k', 'default') are detected."""
    code = "payload.pop(key_var)\npayload.pop('k', 'default')\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/sample_service.py")
    qgr019 = [v for v in violations if v.rule_code == "QGR019"]
    assert len(qgr019) == 2


def test_qgr014_attribute_repository_spec_detected() -> None:
    """QGR014: spec=interfaces.IUserRepository triggers QGR014."""
    code = "mock = MagicMock(spec=interfaces.IUserRepository)\n"
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr014 = [v for v in violations if v.rule_code == "QGR014"]
    assert len(qgr014) == 1
    assert qgr014[0].severity == GuardrailSeverity.FATAL


def test_qgr011_plain_assign_id_detected() -> None:
    """QGR011: plain assignment of id in create request model triggers QGR011."""
    code = "class WorkflowCreateRequest(BaseModel):\n    id = 'custom_id'\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/workflow.py")
    qgr011 = [v for v in violations if v.rule_code == "QGR011"]
    assert len(qgr011) == 1


def test_qgr020_duplicate_field_on_annotated_detected() -> None:
    """QGR020: Duplicate Field() assignment on Annotated field triggers QGR020."""
    from scripts._ast_guardrails import GuardrailSeverity

    code = (
        "from typing import Annotated\n"
        "from pydantic import BaseModel, Field\n\n"
        "class StepDTO(BaseModel):\n"
        "    steps: Annotated[list[str], Field(default_factory=list)] = Field(default_factory=list)\n"
        "    valid: Annotated[list[str], Field(default_factory=list)]\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/step.py")
    qgr020 = [v for v in violations if v.rule_code == "QGR020"]
    assert len(qgr020) == 1
    assert "Duplicate `Field()` assignment on Annotated field `steps`" in qgr020[0].message
    assert qgr020[0].severity == GuardrailSeverity.FATAL


def test_qgr020_mutable_class_default_detected() -> None:
    """QGR020: Class-level mutable defaults (list, dict, set) trigger QGR020."""
    from scripts._ast_guardrails import GuardrailSeverity

    code = (
        "class ConfigData:\n"
        "    fields_to_translate: list[str] = []\n"
        "    dynamic_mappings: dict[str, str] = {}\n"
        "    _private_cache = {}\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/config.py")
    qgr020 = [v for v in violations if v.rule_code == "QGR020"]
    assert len(qgr020) == 2
    assert any("fields_to_translate" in v.message for v in qgr020)
    assert any("dynamic_mappings" in v.message for v in qgr020)
    assert not any("_private_cache" in v.message for v in qgr020)
    assert all(v.severity == GuardrailSeverity.FATAL for v in qgr020)


def test_qgr021_llm_debug_logger_import_detected() -> None:
    """QGR021: Banned direct imports of eradicated llm_debug_logger trigger FATAL violation."""
    from scripts._ast_guardrails import GuardrailSeverity

    code = (
        "import llm_debug_logger\n"
        "from backend_v2.utils import llm_debug_logger as legacy_logger\n"
        "from backend_v2.utils.llm_debug_logger import log_prompt\n"
        "from backend_v2.core.telemetry import get_tracer\n"
    )
    violations = _scan_snippet(code, filepath="backend_v2/services/execution/facade.py")
    qgr021 = [v for v in violations if v.rule_code == "QGR021"]
    assert len(qgr021) == 3
    for v in qgr021:
        assert v.severity == GuardrailSeverity.FATAL
        assert "llm_debug_logger" in v.message


def test_qgr022_unshielded_fstring_prompt_xml_detected() -> None:
    """QGR022: Unshielded f-strings containing prompt XML tags or raw payload variables trigger FATAL violation."""
    from scripts._ast_guardrails import GuardrailSeverity

    code1 = 'prompt = f"<user_payload>{content}</user_payload>"\n'
    v1 = _scan_snippet(code1, filepath="backend_v2/services/orchestrator/pipeline.py")
    qgr022_1 = [v for v in v1 if v.rule_code == "QGR022"]
    assert len(qgr022_1) >= 1
    assert qgr022_1[0].severity == GuardrailSeverity.FATAL

    code2 = 'prompt = f"<prompt_instructions>{rules}</prompt_instructions>"\n'
    v2 = _scan_snippet(code2, filepath="backend_v2/services/orchestrator/prompts/builder.py")
    qgr022_2 = [v for v in v2 if v.rule_code == "QGR022"]
    assert len(qgr022_2) >= 1
    assert qgr022_2[0].severity == GuardrailSeverity.FATAL

    code3 = 'text = f"Processing: {raw_paste}"\n'
    v3 = _scan_snippet(code3, filepath="backend_v2/services/orchestrator/pipeline.py")
    qgr022_3 = [v for v in v3 if v.rule_code == "QGR022"]
    assert len(qgr022_3) >= 1
    assert qgr022_3[0].severity == GuardrailSeverity.FATAL


def test_qgr023_anonymous_state_tuple_detected() -> None:
    """QGR023: Anonymous 3+ tuples and 2-tuples with identical primitives trigger QGR023 warning."""
    code1 = "def run() -> tuple[str, int, bool]:\n    pass\n"
    v1 = _scan_snippet(code1, filepath="backend_v2/services/runner.py")
    qgr023_1 = [v for v in v1 if v.rule_code == "QGR023"]
    assert len(qgr023_1) == 1
    assert "Tuple Hell" in qgr023_1[0].message

    code2 = "coords: tuple[str, str] = ('a', 'b')\n"
    v2 = _scan_snippet(code2, filepath="backend_v2/services/runner.py")
    qgr023_2 = [v for v in v2 if v.rule_code == "QGR023"]
    assert len(qgr023_2) == 1
    assert "identical primitive types" in qgr023_2[0].message

    code3 = "items: tuple[str, ...] = ('a',)\n"
    v3 = _scan_snippet(code3, filepath="backend_v2/services/runner.py")
    qgr023_3 = [v for v in v3 if v.rule_code == "QGR023"]
    assert len(qgr023_3) == 0


def test_qgr024_string_quoted_annotation_raises_fatal() -> None:
    """QGR024: String-quoted forward-reference annotations trigger FATAL violation."""
    code = 'target: "StepOutputDTO"\n'
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr024 = [v for v in violations if v.rule_code == "QGR024"]
    assert len(qgr024) == 1
    assert qgr024[0].severity == GuardrailSeverity.FATAL
    assert "StepOutputDTO" in qgr024[0].message


def test_qgr024_literal_string_slice_permitted() -> None:
    """QGR024: Literal string slices pass cleanly with zero violations."""
    code = "env: Literal['development', 'production']\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/config.py")
    qgr024 = [v for v in violations if v.rule_code == "QGR024"]
    assert len(qgr024) == 0


def test_qgr024_annotated_metadata_description_permitted() -> None:
    """QGR024: Annotated metadata descriptions pass cleanly with zero violations."""
    code = "field: Annotated[int, 'Description string']\n"
    violations = _scan_snippet(code, filepath="backend_v2/models/config.py")
    qgr024 = [v for v in violations if v.rule_code == "QGR024"]
    assert len(qgr024) == 0


def test_qgr024_function_returns_and_parameters_detected() -> None:
    """QGR024: String-quoted return annotations and parameter annotations trigger FATAL violation."""
    code1 = 'def execute(step: "StepDef") -> "StepResult":\n    pass\n'
    v1 = _scan_snippet(code1, filepath="backend_v2/services/executor.py")
    qgr024_1 = [v for v in v1 if v.rule_code == "QGR024"]
    assert len(qgr024_1) == 2
    for v in qgr024_1:
        assert v.severity == GuardrailSeverity.FATAL


def test_qgr024_annotated_with_quoted_type_detected() -> None:
    """QGR024: Annotated with string-quoted type (first element) triggers FATAL violation."""
    code = 'field: Annotated["MyModel", "Description string"]\n'
    violations = _scan_snippet(code, filepath="backend_v2/models/config.py")
    qgr024 = [v for v in violations if v.rule_code == "QGR024"]
    assert len(qgr024) == 1
    assert qgr024[0].severity == GuardrailSeverity.FATAL


def test_qgr025_dynamic_dict_in_model_copy_raises_fatal() -> None:
    """QGR025: Passing dynamic dictionary variable to model_copy(update=...) triggers FATAL violation."""
    code = "model.model_copy(update=untyped_dict)\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr025 = [v for v in violations if v.rule_code == "QGR025"]
    assert len(qgr025) == 1
    assert qgr025[0].severity == GuardrailSeverity.FATAL
    assert "untyped_dict" in qgr025[0].message


def test_qgr025_typed_literal_dict_in_model_copy_permitted() -> None:
    """QGR025: Passing statically known typed dictionary literal to model_copy(update=...) is permitted."""
    code = "model.model_copy(update={'status': ExecutionStatus.RUNNING})\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr025 = [v for v in violations if v.rule_code == "QGR025"]
    assert len(qgr025) == 0


def test_qgr025_dict_unpacking_in_model_copy_raises_fatal() -> None:
    """QGR025: Passing dictionary with unpacking ({**untyped}) to model_copy(update=...) triggers FATAL."""
    code = "model.model_copy(update={**untyped_data})\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr025 = [v for v in violations if v.rule_code == "QGR025"]
    assert len(qgr025) == 1
    assert qgr025[0].severity == GuardrailSeverity.FATAL


def test_qgr025_none_update_in_model_copy_permitted() -> None:
    """QGR025: Passing update=None to model_copy is permitted."""
    code = "model.model_copy(update=None)\n"
    violations = _scan_snippet(code, filepath="backend_v2/services/execution.py")
    qgr025 = [v for v in violations if v.rule_code == "QGR025"]
    assert len(qgr025) == 0


def test_qgr025_update_lock_concurrency_defense_permitted() -> None:
    """QGR025: Concurrency progress updates inside async with _update_lock are permitted."""
    code = """
async def sync_progress():
    async with _update_lock:
        record = record.model_copy(update=dynamic_progress_dict)
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/orchestrator/dag_executor.py")
    qgr025 = [v for v in violations if v.rule_code == "QGR025"]
    assert len(qgr025) == 0


# ==============================================================================
# Partition 27: BOUNDARY_EXEMPTION_FILES SSOT & Admission Ratchet
# ==============================================================================


def test_boundary_exemption_files_contains_only_relative_paths() -> None:
    """Verifies that all 15 BOUNDARY_EXEMPTION_FILES members are workspace-relative POSIX paths matching physical files."""
    from scripts._ast_guardrails import BOUNDARY_EXEMPTION_FILES, REPO_ROOT

    assert len(BOUNDARY_EXEMPTION_FILES) == 15
    for file_path_str in BOUNDARY_EXEMPTION_FILES:
        path = Path(file_path_str)
        assert not path.is_absolute(), f"Exemption path must be relative: {file_path_str}"
        assert "\\" not in file_path_str, f"Exemption path must use POSIX separators: {file_path_str}"
        physical_file = REPO_ROOT / path
        assert physical_file.is_file(), f"Exemption file must exist on disk: {physical_file}"


def test_boundary_exemption_files_rejects_models_services_hooks_api() -> None:
    """Negative test verifying zero exemption members belong to core domain directories (models, services, hooks, api)."""
    from scripts._ast_guardrails import BOUNDARY_EXEMPTION_FILES

    banned_prefixes = (
        "backend_v2/models",
        "backend_v2/services",
        "backend_v2/hooks",
        "backend_v2/api",
    )
    for file_path_str in BOUNDARY_EXEMPTION_FILES:
        for prefix in banned_prefixes:
            assert not file_path_str.startswith(prefix), (
                f"Core domain path {file_path_str} is strictly banned from boundary exemptions"
            )


def test_admission_ratchet_asserts_clean_baseline_for_new_members() -> None:
    """Admission ratchet: 9 newly admitted boundary files scanned with empty exemption set return 0 AST violations."""
    from scripts._ast_guardrails import REPO_ROOT, scan_file_for_guardrails

    nine_new_members = [
        "backend_v2/database/driver.py",
        "backend_v2/database/wrapper.py",
        "backend_v2/llm/handler.py",
        "backend_v2/llm/adapters/vertex_adapter.py",
        "backend_v2/llm/adapters/ai_studio_adapter.py",
        "backend_v2/llm/adapters/openai_adapter.py",
        "backend_v2/llm/adapters/anthropic_adapter.py",
        "backend_v2/llm/adapters/deepseek_adapter.py",
        "backend_v2/llm/adapters/mock_adapter.py",
    ]
    with patch("scripts._ast_guardrails.BOUNDARY_EXEMPTION_FILES", frozenset()):
        for rel_path in nine_new_members:
            abs_path = REPO_ROOT / rel_path
            violations = scan_file_for_guardrails(abs_path)
            assert len(violations) == 0, f"Expected 0 violations for {rel_path}, got: {violations}"


# ==============================================================================
# Partition 28: QGR026 Unconditional Skip and Xfail Test Ban
# ==============================================================================


def test_qgr026_unconditional_skip_marker_raises_fatal() -> None:
    """QGR026: Function decorated with unconditional skip marker triggers FATAL violation."""
    marker = "skip"
    code = f"""
import pytest

@pytest.mark.{marker}(reason="temporarily broken")
def test_foo():
    assert True
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr026 = [v for v in violations if v.rule_code == "QGR026"]
    assert len(qgr026) == 1
    assert qgr026[0].severity == GuardrailSeverity.FATAL
    assert "pytest.mark.skip" in qgr026[0].message


def test_qgr026_unconditional_xfail_marker_raises_fatal() -> None:
    """QGR026: Function decorated with unconditional xfail marker triggers FATAL violation."""
    marker = "xfail"
    code = f"""
import pytest

@pytest.mark.{marker}(reason="known bug")
def test_bar():
    assert False
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr026 = [v for v in violations if v.rule_code == "QGR026"]
    assert len(qgr026) == 1
    assert qgr026[0].severity == GuardrailSeverity.FATAL
    assert "pytest.mark.xfail" in qgr026[0].message


def test_qgr026_environment_skipif_permitted() -> None:
    """QGR026: Function decorated with conditional @pytest.mark.skipif emits zero violations."""
    code = """
import os
import pytest

@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION"), reason="requires live api")
def test_integration():
    assert True
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr026 = [v for v in violations if v.rule_code == "QGR026"]
    assert len(qgr026) == 0


def test_qgr026_module_level_pytestmark_skip_raises_fatal() -> None:
    """QGR026: Module-level pytestmark = pytest.mark.skip triggers FATAL violation."""
    code = """
import pytest

pytestmark = pytest.mark.skip(reason="legacy file")
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr026 = [v for v in violations if v.rule_code == "QGR026"]
    assert len(qgr026) == 1
    assert qgr026[0].severity == GuardrailSeverity.FATAL


def test_qgr026_pytest_xfail_call_raises_fatal() -> None:
    """QGR026: Direct call to pytest.xfail() triggers FATAL violation."""
    code = """
import pytest

def test_baz():
    pytest.xfail("cannot run here")
"""
    violations = _scan_snippet(code, filepath="backend_v2/tests/unit/test_sample.py")
    qgr026 = [v for v in violations if v.rule_code == "QGR026"]
    assert len(qgr026) == 1
    assert qgr026[0].severity == GuardrailSeverity.FATAL


# ==============================================================================
# Partition 27: QGR027 Unauthorized Open-JSON / JsonValue in Domain & DTO Models
# ==============================================================================


def test_qgr027_unauthorized_open_json_fatal() -> None:
    """QGR027: dict[str, JsonValue] on non-exempt models triggers FATAL violation."""
    code = """
from pydantic import BaseModel, JsonValue

class SimulationResponse(BaseModel):
    trace: dict[str, JsonValue]
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/dtos/studio.py")
    qgr027 = [v for v in violations if v.rule_code == "QGR027"]
    assert len(qgr027) == 1
    assert qgr027[0].severity == GuardrailSeverity.FATAL
    assert "Open-JSON" in qgr027[0].message
    assert "StepSimulationTraceDTO" in qgr027[0].remediation or "EPIC 157" in qgr027[0].remediation


def test_qgr027_open_json_exemption_permitted() -> None:
    """QGR027: Approved Open-JSON specifications (e.g. validation.py, mcp.py) emit zero violations."""
    code = """
from pydantic import BaseModel, JsonValue

class McpToolCall(BaseModel):
    arguments: dict[str, JsonValue]
"""
    violations = _scan_snippet(code, filepath="backend_v2/models/domain/validation.py")
    qgr027 = [v for v in violations if v.rule_code == "QGR027"]
    assert len(qgr027) == 0


def test_qgr027_boundary_exempt_file_permitted() -> None:
    """QGR027: Boundary exempt files (e.g. llm/provider.py) emit zero violations."""
    code = """
from pydantic import BaseModel, JsonValue

class ProviderPayload(BaseModel):
    raw_payload: dict[str, JsonValue]
"""
    violations = _scan_snippet(code, filepath="backend_v2/llm/provider.py")
    qgr027 = [v for v in violations if v.rule_code == "QGR027"]
    assert len(qgr027) == 0


# ==============================================================================
# Partition 28: QGR028 Redundant Model Reconstitution & Domain State Dict-Casting
# ==============================================================================


def test_qgr028_redundant_model_validate_on_tracked_repo_var_triggers_fatal() -> None:
    """QGR028: Model.model_validate() on variable assigned from repository call triggers FATAL."""
    code = """
async def get_execution_record(self, execution_id: str):
    exec_dict = await self.repo.get_execution(execution_id)
    return ExecutionRecord.model_validate(exec_dict)
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/report_service.py")
    qgr028 = [v for v in violations if v.rule_code == "QGR028"]
    assert len(qgr028) == 1
    assert qgr028[0].severity == GuardrailSeverity.FATAL
    assert "redundant repository model reconstitution" in qgr028[0].message
    assert "Consume the typed domain model returned directly" in qgr028[0].remediation


def test_qgr028_redundant_model_validate_on_direct_repo_call_triggers_fatal() -> None:
    """QGR028: Model.model_validate() directly wrapping repository call triggers FATAL."""
    code = """
async def fetch_workflow(self, workflow_id: str):
    return Workflow.model_validate(await self.repo.get_workflow(workflow_id))
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/report_service.py")
    qgr028 = [v for v in violations if v.rule_code == "QGR028"]
    assert len(qgr028) == 1
    assert qgr028[0].severity == GuardrailSeverity.FATAL


def test_qgr028_domain_state_dict_cast_triggers_fatal() -> None:
    """QGR028: dict(execution.step_states) or dict(execution.profile_syntheses) triggers FATAL."""
    code = """
def update_state(execution, step_id, profile_id):
    step_states = dict(execution.step_states)
    syntheses = dict(execution.profile_syntheses)
    return step_states, syntheses
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/report_service.py")
    qgr028 = [v for v in violations if v.rule_code == "QGR028"]
    assert len(qgr028) == 2
    assert all(v.severity == GuardrailSeverity.FATAL for v in qgr028)
    assert "domain state dictionary conversion" in qgr028[0].message
    assert "with_step_passed" in qgr028[0].remediation


def test_qgr028_direct_model_consumption_and_domain_methods_allowed() -> None:
    """QGR028: Directly using typed repository returns and pure immutable domain methods emits zero violations."""
    code = """
async def compile_artifact(self, execution_id: str, profile_id: str, step_id: str):
    execution = await self.repo.get_execution(execution_id)
    if execution is not None:
        execution = execution.without_profile_synthesis(profile_id)
        execution = execution.with_step_passed(step_id, "Report Render")
    return execution
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/report_service.py")
    qgr028 = [v for v in violations if v.rule_code == "QGR028"]
    assert len(qgr028) == 0


def test_qgr028_residual_future_phase_exemption() -> None:
    """QGR028: Files in RESIDUAL_FUTURE_PHASE_QGR028_FILES emit zero violations."""
    code = """
def legacy_override(record):
    new_states = dict(record.step_states)
    return new_states
"""
    violations = _scan_snippet(code, filepath="backend_v2/services/execution/override_service.py")
    qgr028 = [v for v in violations if v.rule_code == "QGR028"]
    assert len(qgr028) == 0
