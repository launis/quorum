"""PostgreSQL 19 SQL constants, hydration, upsert, and fetch stage for workflows and output_profiles."""

from __future__ import annotations

from pydantic import TypeAdapter
from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    execute_entity_delete,
    execute_entity_upsert,
    resolve_effective_timeout,
    translate_postgres_exception,
    validate_hydrated_row,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EntityPrefix

_STEP_RULE_LIST_ADAPTER: TypeAdapter[list[StepRule]] = TypeAdapter(list[StepRule])

__all__ = [
    "_DELETE_OUTPUT_PROFILE_SQL",
    "_DELETE_TASK_BRIEF_SQL",
    "_DELETE_WORKFLOW_SQL",
    "_GET_OUTPUT_PROFILE_SQL",
    "_GET_TASK_BRIEF_SQL",
    "_GET_WORKFLOW_SQL",
    "_LIST_OUTPUT_PROFILES_SQL",
    "_LIST_TASK_BRIEFS_SQL",
    "_LIST_WORKFLOWS_SQL",
    "_UPSERT_OUTPUT_PROFILE_SQL",
    "_UPSERT_TASK_BRIEF_SQL",
    "_UPSERT_WORKFLOW_SQL",
    "delete_output_profile_row",
    "delete_task_brief_row",
    "delete_workflow_row",
    "get_output_profile_row",
    "get_task_brief_row",
    "get_workflow_row",
    "hydrate_output_profile_row",
    "hydrate_task_brief_row",
    "hydrate_workflow_row",
    "list_output_profile_rows",
    "list_task_brief_rows",
    "list_workflow_rows",
    "upsert_output_profile_row",
    "upsert_task_brief_row",
    "upsert_workflow_row",
]

_UPSERT_WORKFLOW_SQL: str = """INSERT INTO workflows (id, slug, name, description, status, version, is_public,
    organization_id, default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
    default_lexical_strictness_level, security_penalty, post_hoc_penalty, passivity_penalty,
    enable_contextual_overrides, enable_semantic_smoothing, enable_eager_anonymization, system_audit_trail,
    expected_inputs, steps, historical_context_mode)
VALUES ($1::uuid, $2, $3::jsonb, $4::jsonb, $5, $6, $7, $8::uuid, $9::uuid, $10::uuid, $11::uuid,
    $12, $13, $14, $15, $16, $17, $18, $19, $20, $21::jsonb, $22::jsonb, $23)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, name = EXCLUDED.name, description = EXCLUDED.description,
    status = EXCLUDED.status, version = EXCLUDED.version, is_public = EXCLUDED.is_public,
    organization_id = EXCLUDED.organization_id, default_profile_id = EXCLUDED.default_profile_id,
    mcp_gateway_id = EXCLUDED.mcp_gateway_id, model_registry_id = EXCLUDED.model_registry_id,
    default_strictness_level = EXCLUDED.default_strictness_level,
    default_lexical_strictness_level = EXCLUDED.default_lexical_strictness_level,
    security_penalty = EXCLUDED.security_penalty, post_hoc_penalty = EXCLUDED.post_hoc_penalty,
    passivity_penalty = EXCLUDED.passivity_penalty,
    enable_contextual_overrides = EXCLUDED.enable_contextual_overrides,
    enable_semantic_smoothing = EXCLUDED.enable_semantic_smoothing,
    enable_eager_anonymization = EXCLUDED.enable_eager_anonymization,
    system_audit_trail = EXCLUDED.system_audit_trail, expected_inputs = EXCLUDED.expected_inputs,
    steps = EXCLUDED.steps, historical_context_mode = EXCLUDED.historical_context_mode"""

_GET_WORKFLOW_SQL: str = """SELECT id, slug, name, description, status, version, is_public, organization_id,
       default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
       default_lexical_strictness_level, security_penalty, post_hoc_penalty, passivity_penalty,
       enable_contextual_overrides, enable_semantic_smoothing, enable_eager_anonymization,
       system_audit_trail, expected_inputs, steps, historical_context_mode
FROM workflows WHERE id = $1::uuid"""

_LIST_WORKFLOWS_SQL: str = """SELECT id, slug, name, description, status, version, is_public, organization_id,
       default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
       default_lexical_strictness_level, security_penalty, post_hoc_penalty, passivity_penalty,
       enable_contextual_overrides, enable_semantic_smoothing, enable_eager_anonymization,
       system_audit_trail, expected_inputs, steps, historical_context_mode FROM workflows"""

_UPSERT_OUTPUT_PROFILE_SQL: str = """INSERT INTO output_profiles (id, slug, workflow_id, organization_id, name,
    description, user_role_label, custom_preface, language, tone_instruction, executive_summary_directive,
    matrix_1d_synthesis_directive, matrix_2d_synthesis_directive, matrix_3d_synthesis_directive,
    matrix_text_synthesis_directive, row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive,
    visible_metadata, matrix_visible_columns, visible_block_extensions, visible_workflow_extensions,
    max_extension_items, display_scale, custom_scale_min, custom_scale_max, synthesis_length_constraint,
    row_explanation_length_constraint, xai_length_constraint, variance_length_constraint,
    matrix_graph_length_constraint, max_quotes_per_matrix, max_unmet_criteria, target_block_order,
    matrix_synthesis_groups, content_blocks, show_sources_summary_box, sources_display_mode,
    variance_target_block, user_role_target_block)
VALUES ($1::uuid, $2, $3::uuid, $4::uuid, $5::jsonb, $6::jsonb, $7::jsonb, $8::jsonb,
    $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
    $19::jsonb, $20::jsonb, $21::jsonb, $22::jsonb, $23, $24, $25, $26, $27, $28,
    $29, $30, $31, $32, $33, $34::jsonb, $35::jsonb, $36::jsonb, $37, $38, $39, $40)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, workflow_id = EXCLUDED.workflow_id,
    organization_id = EXCLUDED.organization_id, name = EXCLUDED.name, description = EXCLUDED.description,
    user_role_label = EXCLUDED.user_role_label, custom_preface = EXCLUDED.custom_preface,
    language = EXCLUDED.language, tone_instruction = EXCLUDED.tone_instruction,
    executive_summary_directive = EXCLUDED.executive_summary_directive,
    matrix_1d_synthesis_directive = EXCLUDED.matrix_1d_synthesis_directive,
    matrix_2d_synthesis_directive = EXCLUDED.matrix_2d_synthesis_directive,
    matrix_3d_synthesis_directive = EXCLUDED.matrix_3d_synthesis_directive,
    matrix_text_synthesis_directive = EXCLUDED.matrix_text_synthesis_directive,
    row_explanation_directive = EXCLUDED.row_explanation_directive,
    xai_synthesis_directive = EXCLUDED.xai_synthesis_directive,
    variance_synthesis_directive = EXCLUDED.variance_synthesis_directive,
    visible_metadata = EXCLUDED.visible_metadata, matrix_visible_columns = EXCLUDED.matrix_visible_columns,
    visible_block_extensions = EXCLUDED.visible_block_extensions,
    visible_workflow_extensions = EXCLUDED.visible_workflow_extensions,
    max_extension_items = EXCLUDED.max_extension_items, display_scale = EXCLUDED.display_scale,
    custom_scale_min = EXCLUDED.custom_scale_min, custom_scale_max = EXCLUDED.custom_scale_max,
    synthesis_length_constraint = EXCLUDED.synthesis_length_constraint,
    row_explanation_length_constraint = EXCLUDED.row_explanation_length_constraint,
    xai_length_constraint = EXCLUDED.xai_length_constraint,
    variance_length_constraint = EXCLUDED.variance_length_constraint,
    matrix_graph_length_constraint = EXCLUDED.matrix_graph_length_constraint,
    max_quotes_per_matrix = EXCLUDED.max_quotes_per_matrix, max_unmet_criteria = EXCLUDED.max_unmet_criteria,
    target_block_order = EXCLUDED.target_block_order,
    matrix_synthesis_groups = EXCLUDED.matrix_synthesis_groups, content_blocks = EXCLUDED.content_blocks,
    show_sources_summary_box = EXCLUDED.show_sources_summary_box,
    sources_display_mode = EXCLUDED.sources_display_mode,
    variance_target_block = EXCLUDED.variance_target_block,
    user_role_target_block = EXCLUDED.user_role_target_block"""

_GET_OUTPUT_PROFILE_SQL: str = """SELECT id, slug, workflow_id, organization_id, name, description,
       user_role_label, custom_preface, language, tone_instruction, executive_summary_directive,
       matrix_1d_synthesis_directive, matrix_2d_synthesis_directive, matrix_3d_synthesis_directive,
       matrix_text_synthesis_directive, row_explanation_directive, xai_synthesis_directive,
       variance_synthesis_directive, visible_metadata, matrix_visible_columns, visible_block_extensions,
       visible_workflow_extensions, max_extension_items, display_scale, custom_scale_min, custom_scale_max,
       synthesis_length_constraint, row_explanation_length_constraint, xai_length_constraint,
       variance_length_constraint, matrix_graph_length_constraint, max_quotes_per_matrix,
       max_unmet_criteria, target_block_order, matrix_synthesis_groups, content_blocks,
       show_sources_summary_box, sources_display_mode, variance_target_block, user_role_target_block
FROM output_profiles WHERE id = $1::uuid"""

_LIST_OUTPUT_PROFILES_SQL: str = """SELECT id, slug, workflow_id, organization_id, name, description,
       user_role_label, custom_preface, language, tone_instruction, executive_summary_directive,
       matrix_1d_synthesis_directive, matrix_2d_synthesis_directive, matrix_3d_synthesis_directive,
       matrix_text_synthesis_directive, row_explanation_directive, xai_synthesis_directive,
       variance_synthesis_directive, visible_metadata, matrix_visible_columns, visible_block_extensions,
       visible_workflow_extensions, max_extension_items, display_scale, custom_scale_min, custom_scale_max,
       synthesis_length_constraint, row_explanation_length_constraint, xai_length_constraint,
       variance_length_constraint, matrix_graph_length_constraint, max_quotes_per_matrix,
       max_unmet_criteria, target_block_order, matrix_synthesis_groups, content_blocks,
       show_sources_summary_box, sources_display_mode, variance_target_block, user_role_target_block
FROM output_profiles"""

_UPSERT_TASK_BRIEF_SQL: str = """INSERT INTO task_briefs (id, slug, organization_id, label, description,
    instruction_text, source_url)
VALUES ($1::uuid, $2, $3::uuid, $4::jsonb, $5::jsonb, $6, $7)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, organization_id = EXCLUDED.organization_id,
    label = EXCLUDED.label, description = EXCLUDED.description,
    instruction_text = EXCLUDED.instruction_text, source_url = EXCLUDED.source_url"""

_GET_TASK_BRIEF_SQL: str = """SELECT id, slug, organization_id, label, description, instruction_text, source_url
FROM task_briefs WHERE id = $1::uuid"""

_LIST_TASK_BRIEFS_SQL: str = """SELECT id, slug, organization_id, label, description, instruction_text, source_url
FROM task_briefs"""


async def _fetch_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float | None,
    sql: str,
    entity_uuid: object,
    entity_id: str,
    *,
    table_name: str = "workflows",
) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        entity_uuid: Parsed 16-byte UUID primary key parameter.
        entity_id: Canonical Opaque Stripe ID of the target entity for error reporting.
        table_name: Canonical PostgreSQL table name for structured diagnostics.

    Returns:
        Database record if found, or None.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetchrow(sql, entity_uuid, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name=table_name,
            entity_id=entity_id,
        ) from exc


def hydrate_workflow_row(row: AsyncPgRecordProtocol) -> Workflow:
    """Hydrate a Workflow from a database row.

    Args:
        row: Database record from the workflows table.

    Returns:
        Validated Workflow domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID formatting or Workflow schema validation fails.
    """
    wf_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.WORKFLOW)
    steps_list = validate_hydrated_row(
        _STEP_RULE_LIST_ADAPTER,
        _decode_jsonb_column(row["steps"]),
        table_name="workflows",
        entity_id=wf_id,
    )
    return validate_hydrated_row(
        Workflow,
        {
            "id": wf_id,
            "slug": row["slug"],
            "name": _decode_jsonb_column(row["name"]),
            "description": _decode_jsonb_column(row["description"]),
            "status": row["status"],
            "version": row["version"],
            "is_public": row["is_public"],
            "organization_id": _format_org_uuid7(row["organization_id"], default_system=True),
            "default_profile_id": _format_optional_uuid7(row["default_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "mcp_gateway_id": _format_optional_uuid7(row["mcp_gateway_id"], EntityPrefix.SYSTEM_CONFIG),
            "model_registry_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["model_registry_id"]), EntityPrefix.SYSTEM_CONFIG
            ),
            "default_strictness_level": row["default_strictness_level"],
            "default_lexical_strictness_level": row["default_lexical_strictness_level"],
            "security_penalty": _coerce_float(row["security_penalty"]),
            "post_hoc_penalty": _coerce_float(row["post_hoc_penalty"]),
            "passivity_penalty": _coerce_float(row["passivity_penalty"]),
            "enable_contextual_overrides": row["enable_contextual_overrides"],
            "enable_semantic_smoothing": row["enable_semantic_smoothing"],
            "enable_eager_anonymization": row["enable_eager_anonymization"],
            "system_audit_trail": row["system_audit_trail"],
            "expected_inputs": _decode_jsonb_column(row["expected_inputs"]),
            "steps": steps_list,
            "historical_context_mode": row["historical_context_mode"],
        },
        table_name="workflows",
        entity_id=wf_id,
    )


async def upsert_workflow_row(conn: AsyncPgConnectionProtocol, timeout: float, wf: Workflow) -> str:
    """Persist a Workflow into workflows.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        wf: Validated Workflow domain model.

    Returns:
        Canonical wf_<hex> workflow identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    dumped = wf.model_dump(mode="json")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_WORKFLOW_SQL,
        parse_prefixed_uuid7(wf.id, EntityPrefix.WORKFLOW),
        wf.slug,
        to_json(dumped["name"]).decode("utf-8"),
        to_json(dumped["description"]).decode("utf-8"),
        wf.status,
        wf.version,
        wf.is_public,
        _parse_org_uuid7(wf.organization_id),
        _parse_optional_uuid7(wf.default_profile_id, EntityPrefix.OUTPUT_PROFILE),
        _parse_optional_uuid7(wf.mcp_gateway_id, EntityPrefix.SYSTEM_CONFIG),
        parse_prefixed_uuid7(wf.model_registry_id, EntityPrefix.SYSTEM_CONFIG),
        wf.default_strictness_level,
        wf.default_lexical_strictness_level,
        wf.security_penalty,
        wf.post_hoc_penalty,
        wf.passivity_penalty,
        wf.enable_contextual_overrides,
        wf.enable_semantic_smoothing,
        wf.enable_eager_anonymization,
        wf.system_audit_trail,
        to_json(dumped["expected_inputs"]).decode("utf-8"),
        to_json(dumped["steps"]).decode("utf-8"),
        str(wf.historical_context_mode),
        entity_id=wf.id,
        entity_label="workflow",
    )


async def get_workflow_row(conn: AsyncPgConnectionProtocol, timeout: float, workflow_id: str) -> Workflow | None:
    """Fetch a Workflow by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        workflow_id: Canonical wf_<hex> workflow identifier.

    Returns:
        Hydrated Workflow instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    wf_uuid = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
    row = await _fetch_row(conn, timeout, _GET_WORKFLOW_SQL, wf_uuid, workflow_id)
    if row is None:
        return None
    return hydrate_workflow_row(row)


def hydrate_output_profile_row(row: AsyncPgRecordProtocol) -> OutputProfile:
    """Hydrate an OutputProfile from a database row.

    Args:
        row: Database record from the output_profiles table.

    Returns:
        Validated OutputProfile domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID formatting or OutputProfile schema validation fails.
    """
    prf_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.OUTPUT_PROFILE)
    return validate_hydrated_row(
        OutputProfile,
        {
            "id": prf_id,
            "slug": row["slug"],
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "organization_id": _format_org_uuid7(row["organization_id"], default_system=True),
            "name": _decode_jsonb_column(row["name"]),
            "description": _decode_jsonb_column(row["description"]),
            "user_role_label": _decode_jsonb_column(row["user_role_label"]),
            "custom_preface": _decode_jsonb_column(row["custom_preface"]),
            "language": row["language"],
            "tone_instruction": row["tone_instruction"],
            "executive_summary_directive": row["executive_summary_directive"],
            "matrix_1d_synthesis_directive": row["matrix_1d_synthesis_directive"],
            "matrix_2d_synthesis_directive": row["matrix_2d_synthesis_directive"],
            "matrix_3d_synthesis_directive": row["matrix_3d_synthesis_directive"],
            "matrix_text_synthesis_directive": row["matrix_text_synthesis_directive"],
            "row_explanation_directive": row["row_explanation_directive"],
            "xai_synthesis_directive": row["xai_synthesis_directive"],
            "variance_synthesis_directive": row["variance_synthesis_directive"],
            "visible_metadata": _decode_jsonb_column(row["visible_metadata"]),
            "matrix_visible_columns": _decode_jsonb_column(row["matrix_visible_columns"]),
            "visible_block_extensions": _decode_jsonb_column(row["visible_block_extensions"]),
            "visible_workflow_extensions": _decode_jsonb_column(row["visible_workflow_extensions"]),
            "max_extension_items": row["max_extension_items"],
            "display_scale": row["display_scale"],
            "custom_scale_min": row["custom_scale_min"],
            "custom_scale_max": row["custom_scale_max"],
            "synthesis_length_constraint": row["synthesis_length_constraint"],
            "row_explanation_length_constraint": row["row_explanation_length_constraint"],
            "xai_length_constraint": row["xai_length_constraint"],
            "variance_length_constraint": row["variance_length_constraint"],
            "matrix_graph_length_constraint": row["matrix_graph_length_constraint"],
            "max_quotes_per_matrix": row["max_quotes_per_matrix"],
            "max_unmet_criteria": row["max_unmet_criteria"],
            "target_block_order": _decode_jsonb_column(row["target_block_order"]),
            "matrix_synthesis_groups": _decode_jsonb_column(row["matrix_synthesis_groups"]),
            "content_blocks": _decode_jsonb_column(row["content_blocks"]),
            "show_sources_summary_box": row["show_sources_summary_box"],
            "sources_display_mode": row["sources_display_mode"],
            "variance_target_block": row["variance_target_block"],
            "user_role_target_block": row["user_role_target_block"],
        },
        table_name="output_profiles",
        entity_id=prf_id,
    )


async def upsert_output_profile_row(conn: AsyncPgConnectionProtocol, timeout: float, profile: OutputProfile) -> str:
    """Persist an OutputProfile into output_profiles.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        profile: Validated OutputProfile domain model.

    Returns:
        Canonical prf_<hex> output profile identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    dumped = profile.model_dump(mode="json")
    lang_str: str | None = None
    if profile.language is not None:
        lang_str = str(profile.language)
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_OUTPUT_PROFILE_SQL,
        parse_prefixed_uuid7(profile.id, EntityPrefix.OUTPUT_PROFILE),
        profile.slug,
        parse_prefixed_uuid7(profile.workflow_id, EntityPrefix.WORKFLOW),
        _parse_org_uuid7(profile.organization_id),
        to_json(dumped["name"]).decode("utf-8"),
        _encode_optional_jsonb(dumped["description"]),
        _encode_optional_jsonb(dumped["user_role_label"]),
        _encode_optional_jsonb(dumped["custom_preface"]),
        lang_str,
        profile.tone_instruction,
        profile.executive_summary_directive,
        profile.matrix_1d_synthesis_directive,
        profile.matrix_2d_synthesis_directive,
        profile.matrix_3d_synthesis_directive,
        profile.matrix_text_synthesis_directive,
        profile.row_explanation_directive,
        profile.xai_synthesis_directive,
        profile.variance_synthesis_directive,
        to_json(dumped["visible_metadata"]).decode("utf-8"),
        to_json(dumped["matrix_visible_columns"]).decode("utf-8"),
        to_json(dumped["visible_block_extensions"]).decode("utf-8"),
        to_json(dumped["visible_workflow_extensions"]).decode("utf-8"),
        profile.max_extension_items,
        str(profile.display_scale),
        profile.custom_scale_min,
        profile.custom_scale_max,
        profile.synthesis_length_constraint,
        profile.row_explanation_length_constraint,
        profile.xai_length_constraint,
        profile.variance_length_constraint,
        profile.matrix_graph_length_constraint,
        profile.max_quotes_per_matrix,
        profile.max_unmet_criteria,
        to_json(dumped["target_block_order"]).decode("utf-8"),
        to_json(dumped["matrix_synthesis_groups"]).decode("utf-8"),
        to_json(dumped["content_blocks"]).decode("utf-8"),
        profile.show_sources_summary_box,
        str(profile.sources_display_mode),
        profile.variance_target_block,
        profile.user_role_target_block,
        entity_id=profile.id,
        entity_label="output_profile",
    )


async def get_output_profile_row(
    conn: AsyncPgConnectionProtocol, timeout: float, profile_id: str
) -> OutputProfile | None:
    """Fetch an OutputProfile by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        profile_id: Canonical prf_<hex> output profile identifier.

    Returns:
        Hydrated OutputProfile instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    prf_uuid = parse_prefixed_uuid7(profile_id, EntityPrefix.OUTPUT_PROFILE)
    row = await _fetch_row(conn, timeout, _GET_OUTPUT_PROFILE_SQL, prf_uuid, profile_id)
    if row is None:
        return None
    return hydrate_output_profile_row(row)


def hydrate_task_brief_row(row: AsyncPgRecordProtocol) -> TaskBrief:
    """Hydrate a TaskBrief from a database row.

    Args:
        row: Database record from the task_briefs table.

    Returns:
        Validated TaskBrief domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID formatting or TaskBrief schema validation fails.
    """
    tbr_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.TASK_BRIEF)
    return validate_hydrated_row(
        TaskBrief,
        {
            "id": tbr_id,
            "slug": row["slug"],
            "organization_id": _format_org_uuid7(row["organization_id"], default_system=False),
            "label": _decode_jsonb_column(row["label"]),
            "description": _decode_jsonb_column(row["description"]),
            "instruction_text": row["instruction_text"],
            "source_url": row["source_url"],
        },
        table_name="task_briefs",
        entity_id=tbr_id,
    )


async def upsert_task_brief_row(conn: AsyncPgConnectionProtocol, timeout: float, brief: TaskBrief) -> str:
    """Persist a TaskBrief into task_briefs.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        brief: Validated TaskBrief domain model.

    Returns:
        Canonical tbr_<hex> task brief identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    dumped = brief.model_dump(mode="json")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_TASK_BRIEF_SQL,
        parse_prefixed_uuid7(brief.id, EntityPrefix.TASK_BRIEF),
        brief.slug,
        _parse_org_uuid7(brief.organization_id),
        to_json(dumped["label"]).decode("utf-8"),
        to_json(dumped["description"]).decode("utf-8"),
        brief.instruction_text,
        brief.source_url,
        entity_id=brief.id,
        entity_label="task_brief",
    )


async def get_task_brief_row(conn: AsyncPgConnectionProtocol, timeout: float, brief_id: str) -> TaskBrief | None:
    """Fetch a TaskBrief by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        brief_id: Canonical tbr_<hex> task brief identifier.

    Returns:
        Hydrated TaskBrief instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    tbr_uuid = parse_prefixed_uuid7(brief_id, EntityPrefix.TASK_BRIEF)
    row = await _fetch_row(conn, timeout, _GET_TASK_BRIEF_SQL, tbr_uuid, brief_id)
    if row is None:
        return None
    return hydrate_task_brief_row(row)


async def list_task_brief_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[TaskBrief]:
    """List all TaskBrief rows from task_briefs.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated TaskBrief domain models.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_TASK_BRIEFS_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="task_briefs",
            entity_id="*",
        ) from exc
    return [hydrate_task_brief_row(row) for row in rows]


_DELETE_WORKFLOW_SQL: str = "DELETE FROM workflows WHERE id = $1::uuid"
_DELETE_OUTPUT_PROFILE_SQL: str = "DELETE FROM output_profiles WHERE id = $1::uuid"
_DELETE_TASK_BRIEF_SQL: str = "DELETE FROM task_briefs WHERE id = $1::uuid"


async def list_workflow_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[Workflow]:
    """List all Workflow rows from workflows.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated Workflow domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_WORKFLOWS_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="workflows",
            entity_id="*",
        ) from exc
    return [hydrate_workflow_row(row) for row in rows]


async def delete_workflow_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    workflow_id: str,
) -> bool:
    """Delete a Workflow row by primary key from workflows.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        workflow_id: Canonical wf_<hex32> workflow identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    wf_uuid = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_WORKFLOW_SQL,
        wf_uuid,
        entity_id=workflow_id,
        table="workflows",
    )


async def list_output_profile_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[OutputProfile]:
    """List all OutputProfile rows from output_profiles.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated OutputProfile domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_OUTPUT_PROFILES_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="output_profiles",
            entity_id="*",
        ) from exc
    return [hydrate_output_profile_row(row) for row in rows]


async def delete_output_profile_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    profile_id: str,
) -> bool:
    """Delete an OutputProfile row by primary key from output_profiles.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        profile_id: Canonical prf_<hex32> output profile identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    prf_uuid = parse_prefixed_uuid7(profile_id, EntityPrefix.OUTPUT_PROFILE)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_OUTPUT_PROFILE_SQL,
        prf_uuid,
        entity_id=profile_id,
        table="output_profiles",
    )


async def delete_task_brief_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    brief_id: str,
) -> bool:
    """Delete a TaskBrief row by primary key from task_briefs.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        brief_id: Canonical tbr_<hex32> task brief identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    tbr_uuid = parse_prefixed_uuid7(brief_id, EntityPrefix.TASK_BRIEF)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_TASK_BRIEF_SQL,
        tbr_uuid,
        entity_id=brief_id,
        table="task_briefs",
    )
