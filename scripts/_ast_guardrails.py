"""Automated AST Codebase Guardrails Engine (QGR000-QGR015).

Single Source of Truth for static AST architectural rules enforcement across Quorum.
Operates with zero reflection (no getattr/hasattr) using strict pattern matching and isinstance type narrowing.
"""

from __future__ import annotations

import ast
import io
import os
import re
import sys
import tokenize
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "BANNED_REASON_PLACEHOLDERS",
    "BOUNDARY_EXEMPTION_FILES",
    "CommentSuppressor",
    "GuardrailSeverity",
    "GuardrailViolation",
    "QuorumGuardrailVisitor",
    "format_violations_table",
    "main",
    "scan_file_for_guardrails",
    "scan_files_for_guardrails",
    "scan_source_code_for_guardrails",
]

# Force UTF-8 encoding for stdout to support emojis on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass


class GuardrailSeverity(StrEnum):
    """Severity classification for guardrail violations."""

    WARNING = "WARNING"
    FATAL = "FATAL"


class GuardrailViolation(BaseModel):
    """Pydantic V2 DTO representing an AST architectural violation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    filepath: Annotated[str, Field(description="Target file path relative to workspace")]
    lineno: Annotated[int, Field(ge=0, description="1-indexed line number where violation occurred")]
    col_offset: Annotated[int, Field(ge=0, description="Column offset of violation")]
    rule_code: Annotated[str, Field(pattern=r"^QGR\d{3}$", description="Rule code e.g. QGR001")]
    message: Annotated[str, Field(description="Descriptive violation message")]
    remediation: Annotated[str, Field(description="Deterministic remediation guidance")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    is_suppressed: Annotated[bool, Field(description="Whether violation is suppressed via inline comment")]


BANNED_REASON_PLACEHOLDERS: set[str] = {
    "n/a",
    "na",
    "ok",
    "none",
    "test",
    "todo",
    "fix",
    "pass",
    "fail",
    "temporary",
    "temp",
    "",
}


BOUNDARY_EXEMPTION_FILES: set[str] = {
    "tinydb_driver.py",
    "firestore_driver.py",
    "provider.py",
    "logging_config.py",
}


class CommentSuppressor:
    """Parses inline comment suppressions (# noqa: QGRxxx [REASON: ...]) across physical source lines."""

    def __init__(self, source_bytes: bytes, filepath: str = "unknown") -> None:
        self.filepath = filepath
        self.suppressions: dict[int, set[str]] = {}
        self.invalid_suppressions: list[GuardrailViolation] = []
        self._parse_comments(source_bytes)

    def _parse_comments(self, source_bytes: bytes) -> None:
        try:
            tokens = tokenize.tokenize(io.BytesIO(source_bytes).readline)
            for tok in tokens:
                if tok.type == tokenize.COMMENT:
                    text = tok.string
                    match = re.search(
                        r"#\s*noqa(?::\s*([A-Za-z0-9_,\s]+))?(?:\s*\[(?:REASON|reason):\s*([^\]]+)\])?",
                        text,
                        re.IGNORECASE,
                    )
                    if match:
                        rules_str = match.group(1)
                        raw_reason = match.group(2)
                        line_num = tok.start[0]
                        col_offset = tok.start[1]
                        if rules_str:
                            rule_codes = {r.strip().upper() for r in rules_str.split(",") if r.strip()}
                        else:
                            rule_codes = {"*"}

                        qgr_rules = [r for r in rule_codes if r.startswith("QGR") or r == "*"]
                        if qgr_rules:
                            cleaned_reason = raw_reason.strip() if raw_reason else ""
                            if (
                                not cleaned_reason
                                or len(cleaned_reason) < 10
                                or cleaned_reason.lower() in BANNED_REASON_PLACEHOLDERS
                            ):
                                self.invalid_suppressions.append(
                                    GuardrailViolation(
                                        filepath=self.filepath,
                                        lineno=line_num,
                                        col_offset=col_offset,
                                        rule_code="QGR000",
                                        message=(
                                            f"Unjustified # noqa suppression for rule(s) '{', '.join(sorted(rule_codes))}': "
                                            f"Missing or insufficient '[REASON: <substantive justification>]' block (minimum 10 characters)."
                                        ),
                                        remediation="Append an explicit reason block to your suppression comment, e.g., '# noqa: QGR001 [REASON: Third-party LiteLLM model attribute]'.",
                                        severity=GuardrailSeverity.FATAL,
                                        is_suppressed=False,
                                    )
                                )
                                continue

                        if line_num not in self.suppressions:
                            self.suppressions[line_num] = set()
                        self.suppressions[line_num].update(rule_codes)
        except tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError:
            pass

    def is_suppressed(self, rule_code: str, start_line: int, end_line: int | None = None) -> bool:
        if rule_code == "QGR000":
            return False  # Fatal rule QGR000 is immune to suppression
        last_line = end_line if end_line is not None else start_line
        for line in range(start_line, last_line + 1):
            if line in self.suppressions:
                rules_on_line = self.suppressions[line]
                if "*" in rules_on_line or rule_code in rules_on_line:
                    return True
        return False


class QuorumGuardrailVisitor(ast.NodeVisitor):
    """AST Visitor detecting domain architectural violations with zero reflection."""

    def __init__(self, filepath: str, suppressor: CommentSuppressor) -> None:
        self.filepath = filepath
        self.suppressor = suppressor
        self.violations: list[GuardrailViolation] = []
        path_parts = set(filepath.replace("\\", "/").strip("/").split("/"))
        self._is_test_file = "tests" in path_parts or Path(filepath).name.startswith("test_")
        self._is_domain_code = not (
            "tests" in path_parts or "scripts" in path_parts or Path(filepath).name.startswith("test_")
        )
        self._is_boundary_exempt = Path(filepath).name in BOUNDARY_EXEMPTION_FILES
        self._pydantic_base_classes_in_file: set[str] = set()

    def _add_violation(
        self,
        node: ast.AST,
        rule_code: str,
        message: str,
        remediation: str,
        severity: GuardrailSeverity = GuardrailSeverity.WARNING,
    ) -> None:
        lineno = (
            node.lineno
            if isinstance(
                node, (ast.expr, ast.stmt, ast.ExceptHandler, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            )
            else 1
        )
        col_offset = (
            node.col_offset
            if isinstance(
                node, (ast.expr, ast.stmt, ast.ExceptHandler, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            )
            else 0
        )
        end_lineno = (
            node.end_lineno
            if isinstance(
                node, (ast.expr, ast.stmt, ast.ExceptHandler, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            )
            and node.end_lineno is not None
            else lineno
        )

        is_suppressed = self.suppressor.is_suppressed(rule_code, lineno, end_lineno)
        self.violations.append(
            GuardrailViolation(
                filepath=self.filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code=rule_code,
                message=message,
                remediation=remediation,
                severity=severity,
                is_suppressed=is_suppressed,
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        # QGR001: getattr / hasattr / setattr reflection duck-typing and frozen mutations
        qgr001_sev = (
            GuardrailSeverity.FATAL
            if (self._is_domain_code and not self._is_boundary_exempt)
            else GuardrailSeverity.WARNING
        )
        match node.func:
            case ast.Name(id="getattr" | "hasattr" | "setattr"):
                self._add_violation(
                    node,
                    "QGR001",
                    f"Banned reflection duck-typing or in-place mutation call: `{node.func.id}()`.",
                    "Use strict Pydantic V2 schema modeling, typed DTO fields, or class hierarchy properties instead of reflection.",
                    severity=qgr001_sev,
                )
            case ast.Attribute(value=ast.Name(id="object"), attr="__setattr__"):
                self._add_violation(
                    node,
                    "QGR001",
                    "Banned `object.__setattr__()` in-place model mutation call.",
                    "Use pre-instantiation field validation or .model_copy(update=...) instead of mutating frozen models.",
                    severity=qgr001_sev,
                )
            case _:
                pass

        # QGR002: 2-argument .get(key, default) fallback in domain code
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get" and len(node.args) >= 2:
            # Exemptions: os.environ, headers, _LABEL_MAP, LABEL_MAP, database driver calls (self.driver.get / driver.get)
            exempt = False
            match node.func.value:
                case ast.Attribute(value=ast.Name(id="os"), attr="environ") | ast.Name(id="environ"):
                    exempt = True
                case ast.Attribute(attr="headers") | ast.Name(id="headers"):
                    exempt = True
                case (
                    ast.Name(
                        id="_LABEL_MAP" | "LABEL_MAP" | "_VALUE_MAP" | "_NAME_MAP" | "_L10N_MAP" | "L10N_MAP" | "driver"
                    )
                    | ast.Attribute(
                        attr="_LABEL_MAP"
                        | "LABEL_MAP"
                        | "_VALUE_MAP"
                        | "_NAME_MAP"
                        | "_L10N_MAP"
                        | "L10N_MAP"
                        | "driver"
                    )
                ):
                    exempt = True
                case _:
                    exempt = False

            if not exempt:
                qgr002_sev = (
                    GuardrailSeverity.FATAL
                    if (self._is_domain_code and not self._is_boundary_exempt)
                    else GuardrailSeverity.WARNING
                )
                self._add_violation(
                    node,
                    "QGR002",
                    "Banned lazy fallback call: `.get(key, default)` in domain code.",
                    "Use strict Pydantic model validation with default schema fields or direct DTO property access instead of lazy fallbacks.",
                    severity=qgr002_sev,
                )

        # QGR006: asyncio.gather() calls
        match node.func:
            case ast.Attribute(value=ast.Name(id="asyncio"), attr="gather") | ast.Name(id="gather"):
                self._add_violation(
                    node,
                    "QGR006",
                    "Banned `asyncio.gather()` call detected.",
                    "Replace `asyncio.gather()` with `asyncio.TaskGroup()` for Python 3.14+ fail-fast concurrency and automatic cancellation.",
                )
            case _:
                pass

        # QGR008: Hardcoded magic timeouts in domain services
        if not self._is_test_file:
            # Check timeout=literal in kwargs
            for kw in node.keywords:
                if (
                    kw.arg == "timeout"
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, (int, float))
                ):
                    self._add_violation(
                        kw.value,
                        "QGR008",
                        f"Hardcoded timeout={kw.value.value} detected in domain logic.",
                        "Import timeouts centrally from `backend_v2/settings.py` instead of hardcoding magic numbers.",
                    )

            # Check asyncio.sleep(literal > 0) or time.sleep(literal > 0)
            is_sleep = False
            match node.func:
                case ast.Attribute(value=ast.Name(id="asyncio" | "time"), attr="sleep") | ast.Name(id="sleep"):
                    is_sleep = True
                case _:
                    is_sleep = False

            if is_sleep and node.args:
                first_arg = node.args[0]
                if (
                    isinstance(first_arg, ast.Constant)
                    and isinstance(first_arg.value, (int, float))
                    and first_arg.value > 0
                ):
                    self._add_violation(
                        first_arg,
                        "QGR008",
                        f"Hardcoded sleep duration ({first_arg.value}) detected in domain logic.",
                        "Import retry/sleep intervals centrally from `backend_v2/settings.py` instead of hardcoding magic durations.",
                    )

        # QGR010: Naive datetime.now() without tz or deprecated datetime.utcnow()
        match node.func:
            case ast.Attribute(value=ast.Name(id="datetime"), attr="utcnow") | ast.Name(id="utcnow"):
                self._add_violation(
                    node,
                    "QGR010",
                    "Deprecated `datetime.utcnow()` call detected.",
                    "Use timezone-aware `datetime.now(UTC)` or `datetime.now(timezone.utc)` instead.",
                )
            case ast.Attribute(value=ast.Name(id="datetime"), attr="now") | ast.Name(id="now"):
                has_tz = False
                if node.args:
                    has_tz = True
                else:
                    for kw in node.keywords:
                        if kw.arg == "tz" and not (isinstance(kw.value, ast.Constant) and kw.value.value is None):
                            has_tz = True
                if not has_tz:
                    self._add_violation(
                        node,
                        "QGR010",
                        "Naive `datetime.now()` call without timezone detected.",
                        "Use timezone-aware `datetime.now(UTC)` or `datetime.now(timezone.utc)` instead of naive timestamps.",
                    )
            case _:
                pass

        # QGR012: isinstance(..., dict) or composite isinstance(..., (..., dict, ...)) duck-typing check
        if isinstance(node.func, ast.Name) and node.func.id == "isinstance" and len(node.args) >= 2:
            types_arg = node.args[1]
            is_dict_check = False
            match types_arg:
                case ast.Name(id="dict"):
                    is_dict_check = True
                case ast.Tuple(elts=elts):
                    for elt in elts:
                        match elt:
                            case ast.Name(id="dict"):
                                is_dict_check = True
                                break
                            case _:
                                pass
                case _:
                    pass

            if is_dict_check:
                qgr012_sev = (
                    GuardrailSeverity.FATAL
                    if (self._is_domain_code and not self._is_boundary_exempt)
                    else GuardrailSeverity.WARNING
                )
                self._add_violation(
                    node,
                    "QGR012",
                    "Banned `isinstance(..., dict)` duck-typing check in domain code.",
                    "Use native Pydantic V2 model validation (e.g. DTO fields, Enums, or @model_validator(mode='after')) instead of ad-hoc dict inspection.",
                    severity=qgr012_sev,
                )

        # QGR013: TypeVar() instantiation ban
        match node.func:
            case (
                ast.Name(id="TypeVar")
                | ast.Attribute(value=ast.Name(id="typing" | "typing_extensions"), attr="TypeVar")
            ):
                self._add_violation(
                    node,
                    "QGR013",
                    "Banned legacy `TypeVar()` instantiation detected.",
                    "Use modern Python 3.12+ PEP 695 generic syntax `[T]` or `[F: HookFunction]` instead of TypeVar.",
                    severity=GuardrailSeverity.WARNING,
                )
            case _:
                pass

        # QGR014: AsyncMock / MagicMock on repository interfaces in tests
        match node.func:
            case (
                ast.Name(id="AsyncMock" | "MagicMock" | "Mock")
                | ast.Attribute(
                    value=ast.Name(id="mock" | "unittest" | "unittest.mock"),
                    attr="AsyncMock" | "MagicMock" | "Mock",
                )
            ):
                is_repo_mock = False
                for kw in node.keywords:
                    if kw.arg in ("spec", "spec_set"):
                        match kw.value:
                            case ast.Name(id=name) if (
                                name.startswith("I") and name.endswith("Repository")
                            ) or name == "IUnifiedWorkflowRepository":
                                is_repo_mock = True
                            case ast.Attribute(attr=attr_name) if (
                                attr_name.startswith("I") and attr_name.endswith("Repository")
                            ) or attr_name == "IUnifiedWorkflowRepository":
                                is_repo_mock = True
                            case _:
                                pass
                if is_repo_mock:
                    self._add_violation(
                        node,
                        "QGR014",
                        "Banned `AsyncMock`/`MagicMock` repository interface mock detected.",
                        "Use strongly typed In-Memory Fakes from `backend_v2/tests/fakes/in_memory_repositories.py` (`InMemoryWorkflowRepository`, etc.) with `inject_fault()` instead of ad-hoc mocks.",
                        severity=GuardrailSeverity.FATAL,
                    )
            case (
                ast.Name(id="patch")
                | ast.Attribute(value=ast.Name(id="mock" | "unittest" | "unittest.mock"), attr="patch")
            ):
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    target_str = node.args[0].value
                    if "interfaces.I" in target_str or (
                        ("repository" in target_str.lower() or "repo" in target_str.lower())
                        and "service" in self.filepath.lower()
                    ):
                        qgr014_patch_sev = (
                            GuardrailSeverity.FATAL
                            if ("service" in self.filepath.lower() or "interfaces.I" in target_str)
                            else GuardrailSeverity.WARNING
                        )
                        self._add_violation(
                            node,
                            "QGR014",
                            f"Banned `@patch` targeting repository `{target_str}` in tests.",
                            "Use dependency-injected In-Memory Fakes from `backend_v2/tests/fakes/in_memory_repositories.py` instead of monkey-patching repositories.",
                            severity=qgr014_patch_sev,
                        )
            case _:
                pass

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        # QGR003: Broad except Exception handlers lacking ast.Raise
        is_broad = False
        if node.type is None:
            is_broad = True
        elif isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException"):
            is_broad = True
        elif isinstance(node.type, ast.Tuple):
            for elt in node.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                    is_broad = True
                    break

        if is_broad:
            has_raise = False
            for stmt in node.body:
                for sub_node in ast.walk(stmt):
                    if isinstance(sub_node, ast.Raise):
                        has_raise = True
                        break
                if has_raise:
                    break

            if not has_raise:
                self._add_violation(
                    node,
                    "QGR003",
                    "Broad `except Exception:` handler lacking `raise` detected.",
                    "Catch specific exception types (e.g. (OSError, UnicodeDecodeError)) or re-raise typed AppException inside handlers.",
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Check if class is a BaseModel / DTO / Model
        is_pydantic = False
        for base in node.bases:
            match base:
                case ast.Name(id="BaseModel" | "BaseResponseDTO" | "BaseDTO" | "BaseDomainModel" | "BaseSettings"):
                    is_pydantic = True
                case ast.Attribute(
                    attr="BaseModel" | "BaseResponseDTO" | "BaseDTO" | "BaseDomainModel" | "BaseSettings"
                ):
                    is_pydantic = True
                case ast.Name(id=name) if name in self._pydantic_base_classes_in_file:
                    is_pydantic = True
                case _:
                    pass

        if node.name.endswith(("DTO", "Model", "Request", "Response")):
            is_pydantic = True

        if is_pydantic:
            self._pydantic_base_classes_in_file.add(node.name)

            # QGR004: __new__ and model_construct definitions on BaseModel classes
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name in ("__new__", "model_construct"):
                        self._add_violation(
                            item,
                            "QGR004",
                            f"Banned Pydantic pseudo-class override: `def {item.name}()` on BaseModel `{node.name}`.",
                            "Replace pseudo-class overrides with Pydantic V2 Discriminated Unions (TypeAdapter and Annotated[Union, Field(discriminator=...)]).",
                        )

            # QGR007: Missing ConfigDict(strict=True, extra="forbid")
            if not self._is_test_file:
                has_model_config = False
                has_strict_true = False
                has_extra_forbid = False

                for item in node.body:
                    match item:
                        # model_config = ConfigDict(...)
                        case ast.Assign(targets=[ast.Name(id="model_config")], value=ast.Call() as call):
                            has_model_config = True
                            for kw in call.keywords:
                                if kw.arg == "strict" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                    has_strict_true = True
                                if (
                                    kw.arg == "extra"
                                    and isinstance(kw.value, ast.Constant)
                                    and kw.value.value == "forbid"
                                ):
                                    has_extra_forbid = True
                        case ast.AnnAssign(target=ast.Name(id="model_config"), value=ast.Call() as call):
                            has_model_config = True
                            if call is not None:
                                for kw in call.keywords:
                                    if (
                                        kw.arg == "strict"
                                        and isinstance(kw.value, ast.Constant)
                                        and kw.value.value is True
                                    ):
                                        has_strict_true = True
                                    if (
                                        kw.arg == "extra"
                                        and isinstance(kw.value, ast.Constant)
                                        and kw.value.value == "forbid"
                                    ):
                                        has_extra_forbid = True
                        case _:
                            pass

                # Check if inheriting another model defined in this file (which already defines config)
                has_local_base = any(
                    isinstance(b, ast.Name) and b.id in self._pydantic_base_classes_in_file and b.id != node.name
                    for b in node.bases
                )

                if not has_local_base and (not has_model_config or not has_strict_true or not has_extra_forbid):
                    self._add_violation(
                        node,
                        "QGR007",
                        f"Pydantic model `{node.name}` is missing `model_config = ConfigDict(strict=True, extra='forbid')`.",
                        "Add `model_config = ConfigDict(strict=True, extra='forbid')` to enforce strict validation and reject hallucinated fields.",
                    )

            # QGR011: Banned id field in CreateDTO / CreateRequest models
            if not self._is_test_file and node.name.endswith(("CreateDTO", "CreateRequest")):
                for item in node.body:
                    has_id_target = False
                    match item:
                        case ast.AnnAssign(target=ast.Name(id="id")):
                            has_id_target = True
                        case ast.Assign(targets=targets):
                            for t in targets:
                                if isinstance(t, ast.Name) and t.id == "id":
                                    has_id_target = True
                                    break
                        case _:
                            pass
                    if has_id_target:
                        self._add_violation(
                            item,
                            "QGR011",
                            f"Banned `id` field declaration in creation model `{node.name}`.",
                            "Remove client-provided `id` field from creation DTO/Request models. IDs must be generated exclusively by the backend.",
                        )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        # QGR005: Raw string literals in category discriminator routing
        for comp_op, comparator in zip(node.ops, node.comparators, strict=False):
            if isinstance(comp_op, (ast.Eq, ast.NotEq)):
                # Check if left is a category/discriminator attribute and right is a raw category string
                left_is_discriminator = False
                match node.left:
                    case ast.Attribute(attr="category_id" | "category" | "discriminator" | "block_category"):
                        left_is_discriminator = True
                    case ast.Name(id="category_id" | "category" | "discriminator" | "block_category"):
                        left_is_discriminator = True
                    case _:
                        left_is_discriminator = False

                if left_is_discriminator and isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    if comparator.value in ("matrix", "system_rule", "persona", "synthesis", "text", "rule"):
                        self._add_violation(
                            node,
                            "QGR005",
                            f"Raw string literal `'{comparator.value}'` used in category discriminator comparison.",
                            "Use strict Enum members (e.g. PromptBlockCategory.MATRIX) instead of raw string literals for category routing.",
                        )

        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        # QGR009: raise AppException(...) missing typed ErrorCodes enum argument
        if isinstance(node.exc, ast.Call):
            is_app_exception = False
            match node.exc.func:
                case ast.Name(id="AppException"):
                    is_app_exception = True
                case ast.Attribute(attr="AppException"):
                    is_app_exception = True
                case _:
                    is_app_exception = False

            if is_app_exception:
                valid_error_code = False
                if node.exc.args:
                    first_arg = node.exc.args[0]
                    match first_arg:
                        case ast.Attribute(value=ast.Name(id="ErrorCodes")):
                            valid_error_code = True
                        case ast.Attribute(attr=attr_name) if "ERROR" in attr_name or "FAILED" in attr_name:
                            valid_error_code = True
                        case _:
                            valid_error_code = False
                if not valid_error_code:
                    for kw in node.exc.keywords:
                        if kw.arg == "error_code":
                            match kw.value:
                                case ast.Attribute(value=ast.Name(id="ErrorCodes")):
                                    valid_error_code = True
                                case ast.Attribute(
                                    value=ast.Attribute(value=ast.Name(id="ErrorCodes")), attr="value" | "name"
                                ):
                                    valid_error_code = True
                                case ast.Attribute(attr=attr_name) if "ERROR" in attr_name or "FAILED" in attr_name:
                                    valid_error_code = True
                                case _:
                                    pass
                        elif kw.arg == "details" and isinstance(kw.value, ast.Dict):
                            for k, v in zip(kw.value.keys, kw.value.values, strict=False):
                                if isinstance(k, ast.Constant) and k.value == "error_code":
                                    match v:
                                        case ast.Attribute(value=ast.Name(id="ErrorCodes")):
                                            valid_error_code = True
                                        case ast.Attribute(
                                            value=ast.Attribute(value=ast.Name(id="ErrorCodes")), attr="value" | "name"
                                        ):
                                            valid_error_code = True
                                        case ast.Attribute(attr=attr_name) if (
                                            "ERROR" in attr_name or "FAILED" in attr_name
                                        ):
                                            valid_error_code = True
                                        case _:
                                            pass

                if not valid_error_code:
                    self._add_violation(
                        node.exc,
                        "QGR009",
                        "AppException instantiated without a typed `ErrorCodes` enum member.",
                        "Pass a typed `ErrorCodes` enum member as the first argument or in details={'error_code': ErrorCodes.XXX} to `AppException`.",
                    )

        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        # QGR012: Structural pattern matching unpacking dictionaries (match/case dict)
        if not self._is_test_file:
            for case in node.cases:
                is_dict_pattern = False
                match case.pattern:
                    case ast.MatchClass(cls=ast.Name(id="dict")):
                        is_dict_pattern = True
                    case ast.MatchAs(pattern=ast.MatchClass(cls=ast.Name(id="dict"))):
                        is_dict_pattern = True
                    case ast.MatchMapping():
                        is_dict_pattern = True
                    case ast.MatchOr(patterns=sub_pats):
                        for p in sub_pats:
                            match p:
                                case ast.MatchClass(cls=ast.Name(id="dict")) | ast.MatchMapping():
                                    is_dict_pattern = True
                                    break
                                case _:
                                    pass
                    case _:
                        pass

                if is_dict_pattern:
                    qgr012_sev = (
                        GuardrailSeverity.FATAL
                        if (self._is_domain_code and not self._is_boundary_exempt)
                        else GuardrailSeverity.WARNING
                    )
                    self._add_violation(
                        node,
                        "QGR012",
                        "Banned `match/case dict()` or dictionary mapping pattern matching in domain code.",
                        "Use native Pydantic V2 model validation (e.g. DTO fields, Enums, Discriminated Unions) instead of match/case dictionary unpacking.",
                        severity=qgr012_sev,
                    )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # QGR014: mock repository variable assignment in test files
        if self._is_test_file:
            for target in node.targets:
                if isinstance(target, ast.Name) and (
                    "_repo" in target.id or "repo_" in target.id or target.id.endswith("repo")
                ):
                    match node.value:
                        case ast.Call(
                            func=ast.Name(id="AsyncMock" | "MagicMock" | "Mock")
                            | ast.Attribute(attr="AsyncMock" | "MagicMock" | "Mock")
                        ):
                            self._add_violation(
                                node,
                                "QGR014",
                                f"Banned mock repository variable `{target.id} = AsyncMock/MagicMock()` detected.",
                                "Use strongly typed In-Memory Fakes from `backend_v2/tests/fakes/in_memory_repositories.py` instead of mock repository fixtures.",
                                severity=GuardrailSeverity.WARNING,
                            )
                        case _:
                            pass
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # QGR015: TypeGuard import ban per PEP 742 (pep742_typeis_over_typeguard)
        if node.module in ("typing", "typing_extensions"):
            for alias in node.names:
                if alias.name == "TypeGuard":
                    self._add_violation(
                        node,
                        "QGR015",
                        "Banned `TypeGuard` import detected.",
                        "Use modern PEP 742 `TypeIs` from `typing` (or `typing_extensions`) instead of `TypeGuard` for narrowing.",
                        severity=GuardrailSeverity.WARNING,
                    )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        # QGR015: TypeGuard usage in annotations/expressions
        if node.id == "TypeGuard" and not self._is_test_file:
            self._add_violation(
                node,
                "QGR015",
                "Banned legacy `TypeGuard` type annotation detected.",
                "Use modern PEP 742 `TypeIs` from `typing` (or `typing_extensions`) instead of `TypeGuard` for narrowing.",
                severity=GuardrailSeverity.WARNING,
            )
        self.generic_visit(node)


def scan_source_code_for_guardrails(filepath: str, source_bytes: bytes) -> list[GuardrailViolation]:
    """Scans Python source code bytes for architectural violations with complete fault isolation."""
    # 1. Parse AST with SyntaxError / IndentationError / TabError isolation
    try:
        source_text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [
            GuardrailViolation(
                filepath=filepath,
                lineno=1,
                col_offset=0,
                rule_code="QGR000",
                message=f"Fatal encoding error reading file: {exc}",
                remediation="Ensure file is valid UTF-8 encoded text.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    try:
        tree = ast.parse(source_text, filename=filepath)
    except (SyntaxError, IndentationError, TabError) as exc:
        lineno = exc.lineno if exc.lineno is not None else 1
        col_offset = exc.offset if exc.offset is not None else 0
        return [
            GuardrailViolation(
                filepath=filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code="QGR000",
                message=f"Fatal Python syntax error during AST parse: {exc}",
                remediation="Fix Python syntax or indentation errors to allow AST parsing.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    # 2. Check for tokenization errors and parse comments
    try:
        suppressor = CommentSuppressor(source_bytes, filepath=filepath)
        list(tokenize.tokenize(io.BytesIO(source_bytes).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        return [
            GuardrailViolation(
                filepath=filepath,
                lineno=1,
                col_offset=0,
                rule_code="QGR000",
                message=f"Fatal tokenization error during token parsing: {exc}",
                remediation="Fix unbalanced brackets or unclosed multi-line string literals.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    # 3. Traverse AST with RecursionError isolation
    visitor = QuorumGuardrailVisitor(filepath, suppressor)
    try:
        visitor.visit(tree)
    except RecursionError as exc:
        return [
            GuardrailViolation(
                filepath=filepath,
                lineno=1,
                col_offset=0,
                rule_code="QGR000",
                message=f"Fatal recursion depth exceeded during AST traversal: {exc}",
                remediation="Simplify deeply nested expressions or data structures.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    return suppressor.invalid_suppressions + visitor.violations


def scan_file_for_guardrails(filepath: str | Path) -> list[GuardrailViolation]:
    """Scans a single Python file on disk for architectural violations."""
    path = Path(filepath)
    try:
        source_bytes = path.read_bytes()
    except OSError as exc:
        return [
            GuardrailViolation(
                filepath=str(filepath).replace("\\", "/"),
                lineno=1,
                col_offset=0,
                rule_code="QGR000",
                message=f"Fatal OS read error: {exc}",
                remediation="Verify physical file existence and read permissions.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    return scan_source_code_for_guardrails(str(filepath).replace("\\", "/"), source_bytes)


def _collect_py_files(target: str | Path) -> list[Path]:
    """Recursively collects Python files while ignoring .venv, node_modules, and cache directories."""
    path = Path(target)
    if not path.exists():
        return []

    if path.is_file():
        return [path] if path.suffix == ".py" else []

    collected: list[Path] = []
    ignored_parts = {".venv", "node_modules", "__pycache__", ".git", ".pytest_cache", ".ruff_cache", ".mypy_cache"}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignored_parts]
        for f in files:
            if f.endswith(".py"):
                collected.append(Path(root) / f)

    return sorted(collected)


def scan_files_for_guardrails(
    targets: Sequence[str | Path],
    strict: bool = False,
) -> tuple[list[GuardrailViolation], bool]:
    """Scans multiple target files or directories for AST violations.

    Returns:
        tuple[list[GuardrailViolation], bool]: (violations, is_success)
        In strict mode, passes only if there are 0 unsuppressed violations.
        In advisory mode, passes if there are 0 unsuppressed FATAL violations.
    """
    all_violations: list[GuardrailViolation] = []

    for target in targets:
        py_files = _collect_py_files(target)
        for py_file in py_files:
            file_violations = scan_file_for_guardrails(py_file)
            all_violations.extend(file_violations)

    unsuppressed = [v for v in all_violations if not v.is_suppressed]
    fatal_violations = [v for v in unsuppressed if v.severity == GuardrailSeverity.FATAL]

    if strict:
        is_success = len(unsuppressed) == 0
    else:
        is_success = len(fatal_violations) == 0

    return all_violations, is_success


def format_violations_table(violations: list[GuardrailViolation]) -> str:
    """Formats a list of GuardrailViolation objects into a readable console report."""
    if not violations:
        return "✅ No AST guardrail violations found."

    lines = ["\n🛡️  AST GUARDRAIL VIOLATIONS REPORT", "=" * 80]
    for v in violations:
        status = " [SUPPRESSED]" if v.is_suppressed else ""
        sev_tag = "❌ FATAL" if v.severity == GuardrailSeverity.FATAL else "⚠️  WARN "
        lines.append(f"{sev_tag} [{v.rule_code}]{status} {v.filepath}:{v.lineno}:{v.col_offset}")
        lines.append(f"   Message:     {v.message}")
        lines.append(f"   Remediation: {v.remediation}")
        lines.append("-" * 80)

    return "\n".join(lines)


def main() -> None:
    targets: list[str] = []
    strict_mode = False

    for arg in sys.argv[1:]:
        if arg in ("--strict", "--ast-strict"):
            strict_mode = True
        else:
            targets.append(arg)

    if not targets:
        print("Usage: python scripts/_ast_guardrails.py <target_files_or_directories...> [--strict]")
        sys.exit(1)

    violations, is_success = scan_files_for_guardrails(targets, strict=strict_mode)
    unsuppressed = [v for v in violations if not v.is_suppressed]

    if unsuppressed or (strict_mode and violations):
        print(format_violations_table(unsuppressed))
    else:
        print(f"✅ AST Guardrails passed cleanly for {len(targets)} target(s).")

    sys.exit(0 if is_success else 1)


if __name__ == "__main__":
    main()
