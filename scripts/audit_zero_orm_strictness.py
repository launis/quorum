"""Zero-ORM Strictness & Closed PostgreSQL 19 Topology AST Auditor.

Statically enforces Quorum's All-in-PostgreSQL 19 Zero-ORM invariants across
backend_v2/database/, backend_v2/models/domain/proposition_graph.py,
and backend_v2/database/migrations/001_pg19_uuidv7_schema.sql:
- ZORM001: Bans imports of sqlalchemy, alembic, or orjson.
- ZORM002: Bans untyped dictionary subscript annotations targeting Any/object and dict(r) row unpacking.
- ZORM003: Bans broad except Exception handlers lacking explicit AppException re-raise.
- ZORM004: Enforces that SQL CREATE TABLE identifiers belong strictly to the closed 15-table set.
- ZORM005: Bans calling llm_client, execute_structured_task, or execute_chat_task inside database/UoW modules.
- ZORM006: Enforces that record subscript column keys in graph_adapter.py and entity_adapter.py map 1:1
  to declared domain model fields.
- ZORM007: Enforces O(1) primary-key lookups (driver.get over Filter('id', '==', ...)), public
  PostgresUnitOfWork.pool_manager access, mandatory apply_migrations() preflight before
  verify_schema_tables(), and idempotent ALTER TABLE ... ADD COLUMN IF NOT EXISTS DDL parity.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts._script_base import (
    ANSIColors,
    GuardrailSeverity,
    setup_script_environment,
)

setup_script_environment()

__all__ = [
    "APPROVED_ADAPTER_RECORD_COLUMNS",
    "BANNED_LLM_IDENTIFIERS",
    "BANNED_ORM_IMPORTS",
    "CANONICAL_ENTITY_PK_TABLES",
    "CANONICAL_NAMED_ENTITY_TABLES",
    "CLOSED_POSTGRES_TABLES",
    "REQUIRED_IDEMPOTENT_ALTER_COLUMNS",
    "ZeroOrmAuditReportDTO",
    "ZeroOrmFindingDTO",
    "ZeroOrmRuleCode",
    "audit_python_file",
    "audit_sql_migration_file",
    "build_arg_parser",
    "main",
    "run_zero_orm_audit",
]

# Canonical entity primary-key and display-name table contracts
CANONICAL_ENTITY_PK_TABLES: frozenset[str] = frozenset(
    {
        "organizations",
        "users",
        "invitations",
        "tenant_secrets",
        "execution_assignments",
        "workflows",
        "steps",
        "prompt_blocks",
        "output_profiles",
        "system_configs",
        "executions",
        "report_artifacts",
    }
)

CANONICAL_NAMED_ENTITY_TABLES: dict[str, str] = {
    "organizations": "name",
    "users": "name",
    "system_configs": "name",
    "prompt_blocks": "label",
    "steps": "name",
    "workflows": "name",
    "output_profiles": "name",
    "report_artifacts": "title",
}

# Define closed 15-table topology and banned symbol sets
CLOSED_POSTGRES_TABLES: frozenset[str] = frozenset(
    {
        "users",
        "organizations",
        "invitations",
        "tenant_secrets",
        "execution_assignments",
        "workflows",
        "steps",
        "prompt_blocks",
        "output_profiles",
        "system_configs",
        "executions",
        "report_artifacts",
        "report_binaries",
        "quorum_nodes",
        "quorum_edges",
    }
)

BANNED_ORM_IMPORTS: frozenset[str] = frozenset({"sqlalchemy", "alembic", "orjson"})

BANNED_LLM_IDENTIFIERS: frozenset[str] = frozenset(
    {
        "llm_client",
        "execute_structured_task",
        "execute_chat_task",
        "from_strategy",
    }
)

APPROVED_ADAPTER_RECORD_COLUMNS: frozenset[str] = frozenset(
    {
        # PropositionNode
        "node_id",
        "run_id",
        "node_type",
        "confidence",
        "payload",
        "created_at",
        # DependencyEdge
        "edge_id",
        "source_id",
        "target_id",
        "relation_type",
        "causal_weight",
        # FalsifiedClaimMatch
        "rebuttal_id",
        "invalidated_warrant_id",
        "falsified_claim_id",
        "rebuttal_confidence",
        "claim_statement",
        # ReportBinaryPayloadDTO & ReportArtifact
        "report_id",
        "mime_type",
        "pdf_bytes",
        "size_bytes",
        "has_pdf",
        # Core entity columns & CTE cycle inspection
        "id",
        "traversal_path",
        "is_cycle",
        "updated_at",
        "workflow_id",
        "workflow_version",
        "state_version",
        "active_profile_id",
        "output_profile_id",
        "status",
        "target_locale",
        "progress",
        "status_message",
        "raw_inputs",
        "frozen_context",
        "frozen_context_storage_path",
        "pdf_report_path",
        "steps",
        "step_states",
        "profile_syntheses",
        "source_identity_manifest",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
        "is_resumable",
        "prompt_tokens",
        "completion_tokens",
        "cached_tokens",
        "reasoning_tokens",
        "cumulative_synthesis_tokens",
        "dag_cost_usd",
        "cumulative_synthesis_cost",
        "cost_estimate",
        "models_used",
        "execution_summary",
        "metadata",
        "duration_ms",
        "error",
        "completed_at",
        "created_by",
        "organization_id",
        "row_count",
        # Organizations & Users
        "slug",
        "name",
        "is_active",
        "tier",
        "contact_email",
        "billing_id",
        "subscription_status",
        "quota_limit",
        "tpm_limit",
        "rpm_limit",
        "allowed_email_domains",
        "firebase_uid",
        "email",
        "role",
        "language",
        "theme_mode",
        "deleted_at",
        # Invitations, TenantSecrets & ExecutionAssignments
        "token_hash",
        "email_delivery_status",
        "invited_by",
        "expires_at",
        "scope",
        "target_identifier",
        "storage_mode",
        "secret_manager_version_uri",
        "encrypted_dek",
        "ciphertext",
        "nonce",
        "kek_version",
        "masked_hint",
        "updated_by",
        "batch_id",
        "assigned_email",
        "assigned_user_id",
        "invited_role",
        "locked_inputs",
        "assignee_input_keys",
        "draft_inputs",
        "result_visibility",
        "hard_deadline_at",
        "relative_duration_seconds",
        "activated_at",
        "submitted_at",
        # SystemConfigs
        "type",
        "default_provider",
        "tier_definitions",
        "endpoint_url",
        "transport_type",
        "auth_type",
        "auth_header_name",
        "auth_env_var",
        "timeout_seconds",
        "tools",
        # PromptBlocks
        "label",
        "description",
        "output_extensions",
        "theory_grounding",
        "category_id",
        "is_evaluative",
        "allow_decimals",
        "allow_contextual_override",
        "is_lightweight_protocol",
        "target_input_key",
        "ai_description",
        "scales",
        "rows",
        "columns",
        "computed_min",
        "computed_max",
        "instruction_text",
        "role_enforcement",
        "tone_directives",
        "protocol_instructions",
        # Steps
        "hook",
        "role_block_id",
        "extraction_protocol_block_id",
        "execution_persona_block_id",
        "criteria_block_ids",
        "pre_hooks",
        "post_hooks",
        "safety",
        "allowed_mcp_tools",
        "mcp_tool_params",
        "cognitive_tier",
        "expected_inputs",
        "is_system_core",
        "engine_type",
        "zone",
        # Workflows
        "version",
        "is_public",
        "default_profile_id",
        "mcp_gateway_id",
        "model_registry_id",
        "default_strictness_level",
        "default_lexical_strictness_level",
        "security_penalty",
        "post_hoc_penalty",
        "passivity_penalty",
        "enable_contextual_overrides",
        "enable_semantic_smoothing",
        "enable_eager_anonymization",
        "system_audit_trail",
        "historical_context_mode",
        # OutputProfiles & ReportArtifacts
        "user_role_label",
        "custom_preface",
        "tone_instruction",
        "executive_summary_directive",
        "matrix_1d_synthesis_directive",
        "matrix_2d_synthesis_directive",
        "matrix_3d_synthesis_directive",
        "matrix_text_synthesis_directive",
        "row_explanation_directive",
        "xai_synthesis_directive",
        "variance_synthesis_directive",
        "visible_metadata",
        "matrix_visible_columns",
        "visible_block_extensions",
        "visible_workflow_extensions",
        "max_extension_items",
        "display_scale",
        "custom_scale_min",
        "custom_scale_max",
        "synthesis_length_constraint",
        "row_explanation_length_constraint",
        "xai_length_constraint",
        "variance_length_constraint",
        "matrix_graph_length_constraint",
        "max_quotes_per_matrix",
        "max_unmet_criteria",
        "target_block_order",
        "matrix_synthesis_groups",
        "content_blocks",
        "show_sources_summary_box",
        "sources_display_mode",
        "variance_target_block",
        "user_role_target_block",
        "execution_id",
        "profile_id",
        "locale",
        "title",
        "storage_paths",
        "custom_preface_md",
        "error_message",
    }
)

_CREATE_TABLE_REGEX = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)",
    re.IGNORECASE,
)

_CREATE_TABLE_BLOCK_REGEX = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\)\s*;",
    re.IGNORECASE,
)

_ALTER_ADD_COLUMN_REGEX = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)\s+"
    r"ADD\s+COLUMN\s+IF\s+NOT\s+EXISTS\s+([a-zA-Z0-9_]+)",
    re.IGNORECASE,
)

# Ban TEXT primary keys across the 15-table PostgreSQL 19 topology
_BANNED_TEXT_PK_REGEX = re.compile(
    r"\bid\s+TEXT\s+PRIMARY\s+KEY\b",
    re.IGNORECASE,
)

# Canonical UUIDv7 PK, FK REFERENCES, SQL DEFAULT, and slug SQL filter regexes
_CANONICAL_UUID_PK_REGEX = re.compile(
    r"\bid\s+UUID\s+PRIMARY\s+KEY\s+DEFAULT\s+uuidv7\(\)",
    re.IGNORECASE,
)
_UUID_VERSION_7_CHECK_REGEX = re.compile(
    r"uuid_extract_version\(\s*id\s*\)\s*=\s*7",
    re.IGNORECASE,
)
_BANNED_SQL_COLUMN_DEFAULT_REGEX = re.compile(
    r"^\s*(?:[a-zA-Z0-9_]+_id|name|label|title|slug|storage_mode)\s+(?!UUID\s+PRIMARY\s+KEY\b)[^\n,]*\bDEFAULT\b",
    re.IGNORECASE | re.MULTILINE,
)
_SQL_REFERENCES_REGEX = re.compile(
    r"\bREFERENCES\s+([a-zA-Z0-9_]+)\s*\(\s*([a-zA-Z0-9_]+)\s*\)",
    re.IGNORECASE,
)
_BANNED_SLUG_UNIQUE_REGEX = re.compile(
    r"(?:\bUNIQUE\s*\([^)]*\bslug\b[^)]*\)|\bslug\s+TEXT\s+[^\n,]*\bUNIQUE\b)",
    re.IGNORECASE,
)
_SQL_SLUG_FILTER_REGEX = re.compile(
    r"\b(?:WHERE|AND|OR|ON)\s+(?:[a-zA-Z0-9_]+\.)?slug\s*(?:=|!=|<>|IN\b|LIKE\b|ILIKE\b)",
    re.IGNORECASE,
)

# Evolved columns in 001_pg19_uuidv7_schema.sql that must maintain idempotent ALTER TABLE ADD COLUMN IF NOT EXISTS
REQUIRED_IDEMPOTENT_ALTER_COLUMNS: dict[str, frozenset[str]] = {
    "organizations": frozenset({"allowed_email_domains"}),
    "users": frozenset({"firebase_uid", "deleted_at"}),
    "executions": frozenset({"state_version"}),
}


class ZeroOrmRuleCode(StrEnum):
    """Rule codes for Zero-ORM architectural strictness checks.

    Attributes:
        ZORM001: Bans imports of sqlalchemy, alembic, or orjson.
        ZORM002: Bans untyped mapping annotations and dict(r) record unpacking.
        ZORM003: Bans broad except Exception handlers without AppException re-raise.
        ZORM004: Enforces closed 15-table PostgreSQL DDL topology.
        ZORM005: Bans LLM client or task execution calls inside database/UoW modules.
        ZORM006: Enforces 1:1 column subscript parity in database adapters.
        ZORM007: Enforces O(1) PK lookups, public UoW pool_manager property, preflight apply_migrations(),
            and idempotent ALTER TABLE ADD COLUMN IF NOT EXISTS schema evolution parity.
    """

    ZORM001 = "ZORM001"
    ZORM002 = "ZORM002"
    ZORM003 = "ZORM003"
    ZORM004 = "ZORM004"
    ZORM005 = "ZORM005"
    ZORM006 = "ZORM006"
    ZORM007 = "ZORM007"


class ZeroOrmFindingDTO(BaseModel):
    """Immutable finding record emitted by the Zero-ORM AST auditor.

    Attributes:
        filepath: Workspace-relative or absolute file path where the violation occurred.
        lineno: 1-based line number of the offending construct.
        rule_code: Specific ZeroOrmRuleCode triggered.
        message: Detailed explanation of the architectural violation.
        severity: GuardrailSeverity classification (always FATAL).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    filepath: Annotated[str, Field(description="File path of the violation.")]
    lineno: Annotated[int, Field(ge=1, description="1-based line number.")]
    rule_code: Annotated[ZeroOrmRuleCode, Field(description="Triggered Zero-ORM rule code.")]
    message: Annotated[str, Field(description="Explanation of the violation.")]
    severity: Annotated[
        GuardrailSeverity,
        Field(default=GuardrailSeverity.FATAL, description="Violation severity."),
    ] = GuardrailSeverity.FATAL


class ZeroOrmAuditReportDTO(BaseModel):
    """Aggregated summary report of a Zero-ORM strictness audit run.

    Attributes:
        scanned_files: Total number of Python and SQL files analyzed.
        findings: Immutable tuple of ZeroOrmFindingDTO records discovered.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    scanned_files: Annotated[int, Field(ge=0, description="Number of files analyzed.")]
    findings: Annotated[tuple[ZeroOrmFindingDTO, ...], Field(default=(), description="Collected findings.")]

    @property
    def is_clean(self) -> bool:
        """Return True when zero violations were discovered.

        Returns:
            Boolean indicating a clean audit pass.
        """
        return len(self.findings) == 0


class _ZeroOrmAstVisitor(ast.NodeVisitor):
    """AST node visitor enforcing ZORM001, ZORM002, ZORM003, ZORM005, ZORM006, and ZORM007.

    Attributes:
        filepath: String representation of the file being visited.
        is_adapter_file: Whether the file is graph_adapter.py or entity_adapter.py.
        is_db_scope: Whether database/UoW-specific rules (ZORM002, ZORM003, ZORM005) apply.
        is_uow_file: Whether the file is uow.py (allowed to access self._pool_manager).
        findings: List of ZeroOrmFindingDTO instances collected during traversal.
    """

    def __init__(
        self,
        filepath: str,
        is_adapter_file: bool,
        is_db_scope: bool = True,
        *,
        is_uow_file: bool = False,
    ) -> None:
        """Initialize the AST visitor for a target Python source file.

        Args:
            filepath: File path string for diagnostic reporting.
            is_adapter_file: True if checking SQL column subscript parity (ZORM006).
            is_db_scope: True if enforcing database/UoW-specific rules (ZORM002, ZORM003, ZORM005).
            is_uow_file: True if visiting uow.py where _pool_manager is defined.
        """
        self.filepath = filepath
        self.is_adapter_file = is_adapter_file
        self.is_db_scope = is_db_scope
        self.is_uow_file = is_uow_file
        self.findings: list[ZeroOrmFindingDTO] = []
        self._in_finally: bool = False

    def _record(self, lineno: int, rule_code: ZeroOrmRuleCode, message: str) -> None:
        """Append a ZeroOrmFindingDTO to the visitor's findings list.

        Args:
            lineno: 1-based source line number.
            rule_code: Rule identifier.
            message: Diagnostic message.
        """
        self.findings.append(
            ZeroOrmFindingDTO(
                filepath=self.filepath,
                lineno=max(1, lineno),
                rule_code=rule_code,
                message=message,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        """Inspect standard import statements for ZORM001 banned libraries.

        Args:
            node: AST Import node.
        """
        for alias in node.names:
            root_pkg = alias.name.split(".")[0].lower()
            if root_pkg in BANNED_ORM_IMPORTS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM001,
                    f"Banned import '{alias.name}' detected; use Zero-ORM asyncpg + pydantic_core.",
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspect from-import statements for ZORM001 banned libraries.

        Args:
            node: AST ImportFrom node.
        """
        if node.module is not None:
            root_pkg = node.module.split(".")[0].lower()
            if root_pkg in BANNED_ORM_IMPORTS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM001,
                    f"Banned import from '{node.module}' detected; use Zero-ORM asyncpg + pydantic_core.",
                )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Inspect subscript expressions for ZORM002 untyped mappings and ZORM006 row columns.

        Args:
            node: AST Subscript node.
        """
        if (
            self.is_db_scope
            and isinstance(node.value, ast.Name)
            and node.value.id.lower() in {"dict", "mapping", "mutablemapping"}
        ):
            if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2:
                val_node = node.slice.elts[1]
                if isinstance(val_node, ast.Name) and val_node.id in {"Any", "object"}:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM002,
                        f"Untyped mapping annotation targeting '{val_node.id}' is banned in Zero-ORM modules.",
                    )
        if (
            self.is_adapter_file
            and isinstance(node.value, ast.Name)
            and node.value.id in {"row", "record", "r", "rec"}
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            col_name = node.slice.value
            if col_name not in APPROVED_ADAPTER_RECORD_COLUMNS:
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM006,
                    f"Record column '{col_name}' does not map to any approved Pydantic V2 domain model field.",
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Inspect attribute access for ZORM007 private _pool_manager usage outside uow.py.

        Args:
            node: AST Attribute node.
        """
        if not self.is_uow_file and node.attr == "_pool_manager":
            if not (isinstance(node.value, ast.Name) and node.value.id == "self"):
                self._record(
                    node.lineno,
                    ZeroOrmRuleCode.ZORM007,
                    "Direct access to private attribute '._pool_manager' is banned; use public '.pool_manager' property.",
                )
        self.generic_visit(node)

    def _check_function_preflight_migrations(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Verify that any function calling verify_schema_tables() also calls apply_migrations() (ZORM007).

        Args:
            node: AST FunctionDef or AsyncFunctionDef node.
        """
        verify_calls: list[int] = []
        has_apply_migrations = False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr == "verify_schema_tables":
                    verify_calls.append(sub.lineno)
                elif sub.func.attr == "apply_migrations":
                    has_apply_migrations = True
        if verify_calls and not has_apply_migrations:
            self._record(
                verify_calls[0],
                ZeroOrmRuleCode.ZORM007,
                f"Function '{node.name}' calls 'verify_schema_tables()' without executing 'apply_migrations()' preflight.",
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Inspect synchronous functions for ZORM007 preflight migration ordering.

        Args:
            node: AST FunctionDef node.
        """
        self._check_function_preflight_migrations(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Inspect asynchronous functions for ZORM007 preflight migration ordering.

        Args:
            node: AST AsyncFunctionDef node.
        """
        self._check_function_preflight_migrations(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Inspect function calls for ZORM002 dict(row) unpacking, ZORM005 LLM invocations, and ZORM007 PK Filter('id').

        Args:
            node: AST Call node.
        """
        if self.is_db_scope:
            if isinstance(node.func, ast.Name):
                if node.func.id == "dict" and len(node.args) >= 1:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM002,
                        "Direct dict(...) conversion on database records is banned; use direct subscripting into DTOs.",
                    )
                if node.func.id in BANNED_LLM_IDENTIFIERS:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM005,
                        f"Banned LLM call '{node.func.id}' inside database/UoW layer violates Post-Wave Atomic Commit.",
                    )
                if (
                    node.func.id in {"Filter", "QueryCondition"}
                    and len(node.args) >= 2
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "id"
                ):
                    op_node = node.args[1]
                    is_eq = (isinstance(op_node, ast.Constant) and op_node.value == "==") or (
                        isinstance(op_node, ast.Attribute) and op_node.attr == "EQ"
                    )
                    if is_eq:
                        self._record(
                            node.lineno,
                            ZeroOrmRuleCode.ZORM007,
                            f"Primary-key equality filter {node.func.id}('id', '==', ...) is banned; use O(1) await self.driver.get(collection, entity_id).",
                        )
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in BANNED_LLM_IDENTIFIERS:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM005,
                        f"Banned LLM method '{node.func.attr}' inside database/UoW layer violates Post-Wave Atomic Commit.",
                    )
                if isinstance(node.func.value, ast.Name) and node.func.value.id in BANNED_LLM_IDENTIFIERS:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM005,
                        f"Banned LLM client usage '{node.func.value.id}.{node.func.attr}' inside database/UoW layer.",
                    )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Traverse try/except/finally blocks while tracking finally cleanup scope.

        Args:
            node: AST Try node.
        """
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            self.visit(handler)
        for stmt in node.orelse:
            self.visit(stmt)
        prev_finally = self._in_finally
        self._in_finally = True
        for stmt in node.finalbody:
            self.visit(stmt)
        self._in_finally = prev_finally

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Inspect exception handlers for ZORM003 broad exception swallowing.

        Args:
            node: AST ExceptHandler node.
        """
        if self.is_db_scope and not self._in_finally:
            is_broad = node.type is None or (
                isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
            )
            if is_broad:
                has_raise = any(isinstance(sub, ast.Raise) for sub in ast.walk(node))
                if not has_raise:
                    self._record(
                        node.lineno,
                        ZeroOrmRuleCode.ZORM003,
                        "Broad exception handler without explicit AppException re-raise is banned.",
                    )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """Inspect string constants in database scope for banned SQL slug WHERE/JOIN predicates.

        Args:
            node: AST Constant node.
        """
        # Ban SQL WHERE/JOIN predicates on informational slug column
        if self.is_db_scope and isinstance(node.value, str) and _SQL_SLUG_FILTER_REGEX.search(node.value):
            self._record(
                node.lineno,
                ZeroOrmRuleCode.ZORM007,
                "SQL query filters or joins on informational column 'slug'; "
                "all relational lookups and joins must use canonical 'id' columns.",
            )
        self.generic_visit(node)


def audit_python_file(filepath: Path, *, is_db_scope: bool = True) -> list[ZeroOrmFindingDTO]:
    """Parse and audit a single Python file against Zero-ORM AST rules.

    Args:
        filepath: Path to the Python file to inspect.
        is_db_scope: Whether database/UoW-specific rules (ZORM002, ZORM003, ZORM005) apply.

    Returns:
        List of ZeroOrmFindingDTO findings discovered in the file.
    """
    source = filepath.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        return [
            ZeroOrmFindingDTO(
                filepath=str(filepath),
                lineno=max(1, exc.lineno if exc.lineno is not None else 1),
                rule_code=ZeroOrmRuleCode.ZORM001,
                message=f"SyntaxError while parsing Python file: {exc.msg}",
            )
        ]

    # Enforce ZORM006 column subscript parity across entity_adapter sub-modules
    is_adapter = filepath.name in {"graph_adapter.py", "entity_adapter.py"} or "entity_adapter" in filepath.parts
    visitor = _ZeroOrmAstVisitor(
        filepath=str(filepath),
        is_adapter_file=is_adapter,
        is_db_scope=is_db_scope,
        is_uow_file=filepath.name == "uow.py",
    )
    visitor.visit(tree)
    return visitor.findings


_SQL_STRING_OR_COMMENT_REGEX = re.compile(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|--[^\n]*|/\*[\s\S]*?\*/)")


def _strip_sql_comments(sql_text: str) -> str:
    """Replace SQL line and block comments with spaces while preserving string literals and newlines.

    Args:
        sql_text: Raw SQL DDL source text.

    Returns:
        Comment-stripped SQL text with identical line numbers and character offsets.
    """

    def _replace_match(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith("--") or token.startswith("/*"):
            return "".join("\n" if ch == "\n" else " " for ch in token)
        return token

    return _SQL_STRING_OR_COMMENT_REGEX.sub(_replace_match, sql_text)


def _extract_create_table_columns(table_body: str) -> set[str]:
    """Extract declared column identifiers from a SQL CREATE TABLE body.

    Args:
        table_body: Inner text between '(' and ');' of a CREATE TABLE statement.

    Returns:
        Set of lowercase column names declared in the table.
    """
    columns: set[str] = set()
    for raw_line in table_body.splitlines():
        stripped = raw_line.strip().rstrip(",")
        if not stripped:
            continue
        first_token = stripped.split()[0].upper()
        if first_token in {"CONSTRAINT", "PRIMARY", "FOREIGN", "UNIQUE", "CHECK"}:
            continue
        col_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\b", stripped)
        if col_match is not None:
            columns.add(col_match.group(1).lower())
    return columns


def audit_sql_migration_file(filepath: Path) -> list[ZeroOrmFindingDTO]:
    """Audit a SQL DDL migration file across full multi-line source against ZORM004 and ZORM007.

    Args:
        filepath: Path to the SQL DDL file.

    Returns:
        List of ZeroOrmFindingDTO findings discovered in the SQL file.
    """
    findings: list[ZeroOrmFindingDTO] = []
    content = filepath.read_text(encoding="utf-8")
    uncommented = _strip_sql_comments(content)

    for match in _CREATE_TABLE_REGEX.finditer(uncommented):
        table_name = match.group(1).lower()
        if table_name not in CLOSED_POSTGRES_TABLES:
            lineno = content.count("\n", 0, match.start()) + 1
            findings.append(
                ZeroOrmFindingDTO(
                    filepath=str(filepath),
                    lineno=lineno,
                    rule_code=ZeroOrmRuleCode.ZORM004,
                    message=(
                        f"Table '{table_name}' is outside the closed 15-table PostgreSQL topology: "
                        f"{sorted(CLOSED_POSTGRES_TABLES)}."
                    ),
                )
            )

    for match in _BANNED_TEXT_PK_REGEX.finditer(uncommented):
        lineno = content.count("\n", 0, match.start()) + 1
        findings.append(
            ZeroOrmFindingDTO(
                filepath=str(filepath),
                lineno=lineno,
                rule_code=ZeroOrmRuleCode.ZORM004,
                message=(
                    "SQL table declares 'id TEXT PRIMARY KEY'; all 15 PostgreSQL 19 tables "
                    "must use 'id UUID PRIMARY KEY DEFAULT uuidv7()'."
                ),
            )
        )

    # ZORM004 & ZORM007: Verify canonical PK/display columns, SQL DEFAULT bans, and CREATE/ALTER column parity
    table_columns: dict[str, set[str]] = {}
    table_linenos: dict[str, int] = {}
    for block_match in _CREATE_TABLE_BLOCK_REGEX.finditer(uncommented):
        t_name = block_match.group(1).lower()
        t_body = block_match.group(2)
        t_lineno = content.count("\n", 0, block_match.start()) + 1
        table_columns[t_name] = _extract_create_table_columns(t_body)
        table_linenos[t_name] = t_lineno

        # Enforce ZORM004 canonical PK, UUIDv7 check, display column, and SQL DEFAULT bans
        if t_name in CANONICAL_ENTITY_PK_TABLES and not _BANNED_TEXT_PK_REGEX.search(t_body):
            if not _CANONICAL_UUID_PK_REGEX.search(t_body):
                findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(filepath),
                        lineno=t_lineno,
                        rule_code=ZeroOrmRuleCode.ZORM004,
                        message=(
                            f"Entity table '{t_name}' must declare canonical 'id UUID PRIMARY KEY DEFAULT uuidv7()'."
                        ),
                    )
                )
            if not _UUID_VERSION_7_CHECK_REGEX.search(t_body):
                findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(filepath),
                        lineno=t_lineno,
                        rule_code=ZeroOrmRuleCode.ZORM004,
                        message=(
                            f"Entity table '{t_name}' is missing 'CHECK (uuid_extract_version(id) = 7)' "
                            "constraint on primary key 'id'."
                        ),
                    )
                )
            if t_name in CANONICAL_NAMED_ENTITY_TABLES:
                required_display_col = CANONICAL_NAMED_ENTITY_TABLES[t_name]
                if not re.search(
                    rf"^\s*{required_display_col}\s+(?:TEXT|JSONB)\b", t_body, re.IGNORECASE | re.MULTILINE
                ):
                    findings.append(
                        ZeroOrmFindingDTO(
                            filepath=str(filepath),
                            lineno=t_lineno,
                            rule_code=ZeroOrmRuleCode.ZORM004,
                            message=(
                                f"Named entity table '{t_name}' must declare canonical human-readable "
                                f"display column '{required_display_col}'."
                            ),
                        )
                    )
            for default_match in _BANNED_SQL_COLUMN_DEFAULT_REGEX.finditer(t_body):
                def_lineno = content.count("\n", 0, block_match.start(2) + default_match.start()) + 1
                findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(filepath),
                        lineno=def_lineno,
                        rule_code=ZeroOrmRuleCode.ZORM004,
                        message=(
                            "Banned SQL DEFAULT clause on relational foreign-key, name, label, title, slug, "
                            f"or storage_mode column in table '{t_name}'."
                        ),
                    )
                )

    # Enforce ZORM004 foreign-key REFERENCES <table>(id)
    for ref_match in _SQL_REFERENCES_REGEX.finditer(uncommented):
        target_table = ref_match.group(1).lower()
        ref_col = ref_match.group(2).lower()
        if (target_table in CANONICAL_ENTITY_PK_TABLES and ref_col != "id") or ref_col in {"slug", "name"}:
            ref_lineno = content.count("\n", 0, ref_match.start()) + 1
            findings.append(
                ZeroOrmFindingDTO(
                    filepath=str(filepath),
                    lineno=ref_lineno,
                    rule_code=ZeroOrmRuleCode.ZORM004,
                    message=(
                        f"Foreign key REFERENCES '{target_table}({ref_col})' violates canonical ID relational policy; "
                        "foreign keys to entity tables must reference '(id)' exclusively."
                    ),
                )
            )

    # Enforce ZORM007 bans on SQL UNIQUE (... slug ...) and WHERE/JOIN slug predicates
    for uq_match in _BANNED_SLUG_UNIQUE_REGEX.finditer(uncommented):
        uq_lineno = content.count("\n", 0, uq_match.start()) + 1
        findings.append(
            ZeroOrmFindingDTO(
                filepath=str(filepath),
                lineno=uq_lineno,
                rule_code=ZeroOrmRuleCode.ZORM007,
                message=(
                    "Informational column 'slug' must never have a UNIQUE constraint; "
                    "only canonical 'id' (or cryptographic token_hash/email/firebase_uid) identifies entities."
                ),
            )
        )

    for slug_q_match in _SQL_SLUG_FILTER_REGEX.finditer(uncommented):
        sq_lineno = content.count("\n", 0, slug_q_match.start()) + 1
        findings.append(
            ZeroOrmFindingDTO(
                filepath=str(filepath),
                lineno=sq_lineno,
                rule_code=ZeroOrmRuleCode.ZORM007,
                message=(
                    "SQL query filters or joins on informational column 'slug'; "
                    "all relational lookups and joins must use canonical 'id' columns."
                ),
            )
        )

    alter_columns_by_table: dict[str, set[str]] = {}
    for alter_match in _ALTER_ADD_COLUMN_REGEX.finditer(uncommented):
        t_name = alter_match.group(1).lower()
        c_name = alter_match.group(2).lower()
        alter_columns_by_table.setdefault(t_name, set()).add(c_name)
        lineno = content.count("\n", 0, alter_match.start()) + 1
        if t_name in table_columns and c_name not in table_columns[t_name]:
            findings.append(
                ZeroOrmFindingDTO(
                    filepath=str(filepath),
                    lineno=lineno,
                    rule_code=ZeroOrmRuleCode.ZORM007,
                    message=(
                        f"Column '{c_name}' in 'ALTER TABLE {t_name} ADD COLUMN IF NOT EXISTS' is missing "
                        f"from 'CREATE TABLE IF NOT EXISTS {t_name}'."
                    ),
                )
            )

    # When auditing the full canonical schema (containing organizations, users, and executions),
    # ensure all required evolved columns retain their idempotent ALTER TABLE ADD COLUMN IF NOT EXISTS statements.
    if REQUIRED_IDEMPOTENT_ALTER_COLUMNS.keys() <= table_columns.keys():
        for req_table, req_cols in REQUIRED_IDEMPOTENT_ALTER_COLUMNS.items():
            present_alters = alter_columns_by_table[req_table] if req_table in alter_columns_by_table else set()
            for req_col in sorted(req_cols):
                if req_col in table_columns[req_table] and req_col not in present_alters:
                    findings.append(
                        ZeroOrmFindingDTO(
                            filepath=str(filepath),
                            lineno=table_linenos[req_table],
                            rule_code=ZeroOrmRuleCode.ZORM007,
                            message=(
                                f"Evolved column '{req_table}.{req_col}' in CREATE TABLE IF NOT EXISTS "
                                f"is missing idempotent 'ALTER TABLE {req_table} ADD COLUMN IF NOT EXISTS {req_col}'."
                            ),
                        )
                    )

    findings.sort(key=lambda f: f.lineno)
    return findings


def run_zero_orm_audit(target_paths: list[Path] | None = None) -> ZeroOrmAuditReportDTO:
    """Execute the Zero-ORM strictness audit across target paths or canonical defaults.

    Args:
        target_paths: Optional explicit list of files or directories to scan. When None,
            scans all of backend_v2/ (excluding tests/) and scripts/reconcile_storage.py,
            enforcing ZORM001/ZORM004 universally and ZORM002/ZORM003/ZORM005/ZORM006 on
            database/UoW and proposition graph modules.

    Returns:
        Immutable ZeroOrmAuditReportDTO containing file count and findings.
    """
    explicit_mode = target_paths is not None and len(target_paths) > 0
    resolved_targets: list[Path] = (
        list(target_paths)
        if explicit_mode and target_paths is not None
        else [
            _WORKSPACE_ROOT / "backend_v2",
            _WORKSPACE_ROOT / "scripts" / "reconcile_storage.py",
        ]
    )

    scanned_count = 0
    all_findings: list[ZeroOrmFindingDTO] = []

    for target in resolved_targets:
        if not target.exists():
            if explicit_mode:
                all_findings.append(
                    ZeroOrmFindingDTO(
                        filepath=str(target),
                        lineno=1,
                        rule_code=ZeroOrmRuleCode.ZORM001,
                        message=f"Explicitly specified target path does not exist: {target}",
                    )
                )
            continue

        if target.is_dir():
            for py_file in sorted(target.rglob("*.py")):
                if not explicit_mode and "tests" in py_file.parts:
                    continue
                scanned_count += 1
                file_is_db_scope = (
                    explicit_mode
                    or "database" in py_file.parts
                    or py_file.name in {"proposition_graph.py", "reconcile_storage.py"}
                )
                all_findings.extend(audit_python_file(py_file, is_db_scope=file_is_db_scope))
            for sql_file in sorted(target.rglob("*.sql")):
                if not explicit_mode and "tests" in sql_file.parts:
                    continue
                scanned_count += 1
                all_findings.extend(audit_sql_migration_file(sql_file))
        elif target.suffix.lower() == ".py":
            scanned_count += 1
            file_is_db_scope = (
                explicit_mode
                or "database" in target.parts
                or target.name in {"proposition_graph.py", "reconcile_storage.py"}
            )
            all_findings.extend(audit_python_file(target, is_db_scope=file_is_db_scope))
        elif target.suffix.lower() == ".sql":
            scanned_count += 1
            all_findings.extend(audit_sql_migration_file(target))

    return ZeroOrmAuditReportDTO(scanned_files=scanned_count, findings=tuple(all_findings))


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI ArgumentParser for audit_zero_orm_strictness.py.

    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Zero-ORM Strictness & Closed PostgreSQL 19 Topology AST Auditor.\n\n"
            "Enforces ZORM001-ZORM007 across backend_v2/database/postgres/, "
            "proposition_graph.py, and 001_pg19_uuidv7_schema.sql."
        ),
        epilog=(
            "PowerShell Examples:\n"
            "  uv run python scripts/audit_zero_orm_strictness.py\n"
            "  uv run python scripts/audit_zero_orm_strictness.py backend_v2/database/postgres/\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional explicit file or directory paths to scan.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Zero-ORM AST verification.

    Args:
        argv: Optional list of CLI argument strings.

    Returns:
        Exit code 0 if zero violations are found, 1 otherwise.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    target_paths: list[Path] | None = args.paths if args.paths else None
    report = run_zero_orm_audit(target_paths=target_paths)

    if not report.is_clean:
        print(
            f"{ANSIColors.RED}{ANSIColors.BOLD}[ZORM AUDIT FAILED]{ANSIColors.RESET} "
            f"Found {len(report.findings)} violation(s) across {report.scanned_files} file(s):"
        )
        for item in report.findings:
            print(f"  - [{item.rule_code.value}] {item.filepath}:{item.lineno} -> {item.message}")
        return 1

    print(
        f"{ANSIColors.GREEN}{ANSIColors.BOLD}[ZORM AUDIT PASSED]{ANSIColors.RESET} "
        f"0 violations across {report.scanned_files} scanned file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
