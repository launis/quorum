"""PostgreSQL 19 Zero-ORM Entity Persistence Adapter & lz4 TOAST Report Binary Streaming.

Implements EntityPersistencePort over asyncpg connections for clean-slate persistence
of all 10 domain entity and binary tables (organizations, users, system_configs,
prompt_blocks, steps, workflows, output_profiles, executions, report_artifacts,
and report_binaries).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from pydantic_core import from_json, to_json

from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgRecordProtocol,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    V2CoreBase,
    format_prefixed_uuid7,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EntityPrefix, PromptBlockCategory
from backend_v2.models.state import WorkflowState
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

# Ensure ExecutionRecord deferred annotations (TraceEvent union) are rebuilt
_ = WorkflowState
ExecutionRecord.model_rebuild()

__all__ = [
    "CANONICAL_SEED_TABLES",
    "PostgresEntityAdapter",
]

CANONICAL_SEED_TABLES: tuple[str, ...] = (
    "organizations",
    "users",
    "system_configs",
    "prompt_blocks",
    "steps",
    "workflows",
    "output_profiles",
    "executions",
    "report_artifacts",
    "report_binaries",
)

_COLLECTION_TO_TABLE_MAP: dict[str, str] = {
    "organizations": "organizations",
    "users": "users",
    "system_config": "system_configs",
    "system_configs": "system_configs",
    "prompt_blocks": "prompt_blocks",
    "components": "prompt_blocks",
    "agents": "prompt_blocks",
    "steps": "steps",
    "task_blueprints": "steps",
    "workflows": "workflows",
    "output_profiles": "output_profiles",
    "executions": "executions",
    "report_artifacts": "report_artifacts",
    "report_binaries": "report_binaries",
}

# Phase 3, Step 3: Canonical table-to-EntityPrefix map and deterministic SYSTEM organization UUIDv7 bridge
_TABLE_TO_ENTITY_PREFIX: dict[str, EntityPrefix] = {
    "organizations": EntityPrefix.ORGANIZATION,
    "users": EntityPrefix.USER,
    "system_configs": EntityPrefix.SYSTEM_CONFIG,
    "prompt_blocks": EntityPrefix.PROMPT_BLOCK,
    "steps": EntityPrefix.STEP,
    "workflows": EntityPrefix.WORKFLOW,
    "output_profiles": EntityPrefix.OUTPUT_PROFILE,
    "executions": EntityPrefix.EXECUTION,
    "report_artifacts": EntityPrefix.REPORT,
    "report_binaries": EntityPrefix.REPORT,
}

_SYSTEM_ORG_UUID7: uuid.UUID = uuid.UUID("0195f3a0-0000-7000-8000-000000000000")
_ROOT_SYSTEM_ORG_UUID7: uuid.UUID = uuid.UUID("0195f3a0-0000-7000-8000-000000000001")

_SAVE_REPORT_BINARY_SQL: str = """
INSERT INTO report_binaries (report_id, mime_type, pdf_bytes, size_bytes, created_at)
VALUES ($1::uuid, $2, $3::bytea, $4::bigint, $5::timestamptz)
ON CONFLICT (report_id) DO UPDATE SET
    mime_type = EXCLUDED.mime_type,
    pdf_bytes = EXCLUDED.pdf_bytes,
    size_bytes = EXCLUDED.size_bytes,
    created_at = EXCLUDED.created_at
"""

_MARK_REPORT_ARTIFACT_PDF_SQL: str = """
UPDATE report_artifacts
SET has_pdf = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = $1::uuid
"""

_GET_REPORT_BINARY_SQL: str = """
SELECT report_id, mime_type, pdf_bytes, size_bytes, created_at
FROM report_binaries
WHERE report_id = $1::uuid
"""

_SAVE_EXECUTION_SQL: str = """
INSERT INTO executions (
    id,
    workflow_id,
    workflow_version,
    active_profile_id,
    output_profile_id,
    status,
    target_locale,
    progress,
    status_message,
    raw_inputs,
    frozen_context,
    frozen_context_storage_path,
    pdf_report_path,
    steps,
    step_states,
    profile_syntheses,
    source_identity_manifest,
    execution_trace,
    execution_trace_storage_path,
    context_variables,
    context_variables_storage_path,
    is_resumable,
    prompt_tokens,
    completion_tokens,
    cached_tokens,
    reasoning_tokens,
    cumulative_synthesis_tokens,
    dag_cost_usd,
    cumulative_synthesis_cost,
    cost_estimate,
    models_used,
    execution_summary,
    metadata,
    duration_ms,
    error,
    created_at,
    updated_at,
    completed_at,
    created_by,
    organization_id
) VALUES (
    $1::uuid,
    $2::uuid,
    $3,
    $4::uuid,
    $5::uuid,
    $6,
    $7,
    $8,
    $9,
    $10::jsonb,
    $11::jsonb,
    $12,
    $13,
    $14::jsonb,
    $15::jsonb,
    $16::jsonb,
    $17::jsonb,
    $18::jsonb,
    $19,
    $20::jsonb,
    $21,
    $22,
    $23::bigint,
    $24::bigint,
    $25::bigint,
    $26::bigint,
    $27::bigint,
    $28::numeric,
    $29::numeric,
    $30::numeric,
    $31::jsonb,
    $32::jsonb,
    $33::jsonb,
    $34::bigint,
    $35,
    $36::timestamptz,
    $37::timestamptz,
    $38::timestamptz,
    $39,
    $40::uuid
)
ON CONFLICT (id) DO UPDATE SET
    workflow_id = EXCLUDED.workflow_id,
    workflow_version = EXCLUDED.workflow_version,
    active_profile_id = EXCLUDED.active_profile_id,
    output_profile_id = EXCLUDED.output_profile_id,
    status = EXCLUDED.status,
    target_locale = EXCLUDED.target_locale,
    progress = EXCLUDED.progress,
    status_message = EXCLUDED.status_message,
    raw_inputs = EXCLUDED.raw_inputs,
    frozen_context = EXCLUDED.frozen_context,
    frozen_context_storage_path = EXCLUDED.frozen_context_storage_path,
    pdf_report_path = EXCLUDED.pdf_report_path,
    steps = EXCLUDED.steps,
    step_states = EXCLUDED.step_states,
    profile_syntheses = EXCLUDED.profile_syntheses,
    source_identity_manifest = EXCLUDED.source_identity_manifest,
    execution_trace = EXCLUDED.execution_trace,
    execution_trace_storage_path = EXCLUDED.execution_trace_storage_path,
    context_variables = EXCLUDED.context_variables,
    context_variables_storage_path = EXCLUDED.context_variables_storage_path,
    is_resumable = EXCLUDED.is_resumable,
    prompt_tokens = EXCLUDED.prompt_tokens,
    completion_tokens = EXCLUDED.completion_tokens,
    cached_tokens = EXCLUDED.cached_tokens,
    reasoning_tokens = EXCLUDED.reasoning_tokens,
    cumulative_synthesis_tokens = EXCLUDED.cumulative_synthesis_tokens,
    dag_cost_usd = EXCLUDED.dag_cost_usd,
    cumulative_synthesis_cost = EXCLUDED.cumulative_synthesis_cost,
    cost_estimate = EXCLUDED.cost_estimate,
    models_used = EXCLUDED.models_used,
    execution_summary = EXCLUDED.execution_summary,
    metadata = EXCLUDED.metadata,
    duration_ms = EXCLUDED.duration_ms,
    error = EXCLUDED.error,
    updated_at = EXCLUDED.updated_at,
    completed_at = EXCLUDED.completed_at,
    created_by = EXCLUDED.created_by,
    organization_id = EXCLUDED.organization_id
"""

_GET_EXECUTION_SQL: str = """
SELECT
    id,
    workflow_id,
    workflow_version,
    active_profile_id,
    output_profile_id,
    status,
    target_locale,
    progress,
    status_message,
    raw_inputs,
    frozen_context,
    frozen_context_storage_path,
    pdf_report_path,
    steps,
    step_states,
    profile_syntheses,
    source_identity_manifest,
    execution_trace,
    execution_trace_storage_path,
    context_variables,
    context_variables_storage_path,
    is_resumable,
    prompt_tokens,
    completion_tokens,
    cached_tokens,
    reasoning_tokens,
    cumulative_synthesis_tokens,
    dag_cost_usd,
    cumulative_synthesis_cost,
    cost_estimate,
    models_used,
    execution_summary,
    metadata,
    duration_ms,
    error,
    created_at,
    updated_at,
    completed_at,
    created_by,
    organization_id
FROM executions
WHERE id = $1::uuid
"""

_LIST_EXECUTIONS_SQL: str = """
SELECT
    id,
    workflow_id,
    workflow_version,
    active_profile_id,
    output_profile_id,
    status,
    target_locale,
    progress,
    status_message,
    raw_inputs,
    frozen_context,
    frozen_context_storage_path,
    pdf_report_path,
    steps,
    step_states,
    profile_syntheses,
    source_identity_manifest,
    execution_trace,
    execution_trace_storage_path,
    context_variables,
    context_variables_storage_path,
    is_resumable,
    prompt_tokens,
    completion_tokens,
    cached_tokens,
    reasoning_tokens,
    cumulative_synthesis_tokens,
    dag_cost_usd,
    cumulative_synthesis_cost,
    cost_estimate,
    models_used,
    execution_summary,
    metadata,
    duration_ms,
    error,
    created_at,
    updated_at,
    completed_at,
    created_by,
    organization_id
FROM executions
"""

_UPSERT_ORGANIZATION_SQL: str = """
INSERT INTO organizations (
    id, slug, name, created_at, is_active, tier, contact_email, billing_id,
    subscription_status, quota_limit, tpm_limit, rpm_limit
) VALUES ($1::uuid, $2, $3, $4::timestamptz, $5, $6, $7, $8, $9, $10::numeric, $11::bigint, $12)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    name = EXCLUDED.name,
    created_at = EXCLUDED.created_at,
    is_active = EXCLUDED.is_active,
    tier = EXCLUDED.tier,
    contact_email = EXCLUDED.contact_email,
    billing_id = EXCLUDED.billing_id,
    subscription_status = EXCLUDED.subscription_status,
    quota_limit = EXCLUDED.quota_limit,
    tpm_limit = EXCLUDED.tpm_limit,
    rpm_limit = EXCLUDED.rpm_limit
"""

_GET_ORGANIZATION_SQL: str = """
SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit
FROM organizations
WHERE id = $1::uuid
"""

_LIST_ORGANIZATIONS_SQL: str = """
SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit
FROM organizations
"""

_UPSERT_USER_SQL: str = """
INSERT INTO users (
    id, slug, email, name, role, organization_id, is_active, language, theme_mode, created_at, created_by
) VALUES ($1::uuid, $2, $3, $4, $5, $6::uuid, $7, $8, $9, $10::timestamptz, $11)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    role = EXCLUDED.role,
    organization_id = EXCLUDED.organization_id,
    is_active = EXCLUDED.is_active,
    language = EXCLUDED.language,
    theme_mode = EXCLUDED.theme_mode,
    created_at = EXCLUDED.created_at,
    created_by = EXCLUDED.created_by
"""

_GET_USER_SQL: str = """
SELECT id, slug, email, name, role, organization_id, is_active, language, theme_mode, created_at, created_by
FROM users
WHERE id = $1::uuid
"""

_LIST_USERS_SQL: str = """
SELECT id, slug, email, name, role, organization_id, is_active, language, theme_mode, created_at, created_by
FROM users
"""

_UPSERT_SYSTEM_CONFIG_SQL: str = """
INSERT INTO system_configs (
    id, name, type, slug, default_provider, tier_definitions, endpoint_url,
    transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools
) VALUES ($1::uuid, $2, $3, $4, $5, $6::jsonb, $7, $8, $9, $10, $11, $12, $13::jsonb)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    slug = EXCLUDED.slug,
    default_provider = EXCLUDED.default_provider,
    tier_definitions = EXCLUDED.tier_definitions,
    endpoint_url = EXCLUDED.endpoint_url,
    transport_type = EXCLUDED.transport_type,
    auth_type = EXCLUDED.auth_type,
    auth_header_name = EXCLUDED.auth_header_name,
    auth_env_var = EXCLUDED.auth_env_var,
    timeout_seconds = EXCLUDED.timeout_seconds,
    tools = EXCLUDED.tools
"""

_GET_SYSTEM_CONFIG_SQL: str = """
SELECT id, name, type, slug, default_provider, tier_definitions, endpoint_url,
       transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools
FROM system_configs
WHERE id = $1::uuid
"""

_LIST_SYSTEM_CONFIGS_SQL: str = """
SELECT id, name, type, slug, default_provider, tier_definitions, endpoint_url,
       transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools
FROM system_configs
"""

_UPSERT_PROMPT_BLOCK_SQL: str = """
INSERT INTO prompt_blocks (
    id, slug, organization_id, label, description, output_extensions, theory_grounding,
    category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
    is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns,
    computed_min, computed_max, instruction_text, role_enforcement, tone_directives,
    protocol_instructions
) VALUES (
    $1::uuid, $2, $3::uuid, $4::jsonb, $5::jsonb, $6::jsonb, $7::jsonb,
    $8, $9, $10, $11, $12,
    $13, $14, $15, $16::jsonb, $17::jsonb, $18::jsonb,
    $19, $20, $21, $22, $23::jsonb,
    $24
)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    organization_id = EXCLUDED.organization_id,
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    output_extensions = EXCLUDED.output_extensions,
    theory_grounding = EXCLUDED.theory_grounding,
    category_id = EXCLUDED.category_id,
    type = EXCLUDED.type,
    is_evaluative = EXCLUDED.is_evaluative,
    allow_decimals = EXCLUDED.allow_decimals,
    allow_contextual_override = EXCLUDED.allow_contextual_override,
    is_lightweight_protocol = EXCLUDED.is_lightweight_protocol,
    target_input_key = EXCLUDED.target_input_key,
    ai_description = EXCLUDED.ai_description,
    scales = EXCLUDED.scales,
    rows = EXCLUDED.rows,
    columns = EXCLUDED.columns,
    computed_min = EXCLUDED.computed_min,
    computed_max = EXCLUDED.computed_max,
    instruction_text = EXCLUDED.instruction_text,
    role_enforcement = EXCLUDED.role_enforcement,
    tone_directives = EXCLUDED.tone_directives,
    protocol_instructions = EXCLUDED.protocol_instructions
"""

_GET_PROMPT_BLOCK_SQL: str = """
SELECT id, slug, organization_id, label, description, output_extensions, theory_grounding,
       category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
       is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns,
       computed_min, computed_max, instruction_text, role_enforcement, tone_directives,
       protocol_instructions
FROM prompt_blocks
WHERE id = $1::uuid
"""

_LIST_PROMPT_BLOCKS_SQL: str = """
SELECT id, slug, organization_id, label, description, output_extensions, theory_grounding,
       category_id, type, is_evaluative, allow_decimals, allow_contextual_override,
       is_lightweight_protocol, target_input_key, ai_description, scales, rows, columns,
       computed_min, computed_max, instruction_text, role_enforcement, tone_directives,
       protocol_instructions
FROM prompt_blocks
"""

_UPSERT_STEP_SQL: str = """
INSERT INTO steps (
    id, slug, organization_id, name, description, type, hook, role_block_id,
    extraction_protocol_block_id, execution_persona_block_id, criteria_block_ids,
    pre_hooks, post_hooks, safety, allowed_mcp_tools, mcp_tool_params,
    cognitive_tier, expected_inputs, is_system_core, engine_type, zone
) VALUES (
    $1::uuid, $2, $3::uuid, $4::jsonb, $5::jsonb, $6, $7, $8::uuid,
    $9::uuid, $10::uuid, $11::jsonb,
    $12::jsonb, $13::jsonb, $14, $15::jsonb, $16::jsonb,
    $17, $18::jsonb, $19, $20, $21
)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    organization_id = EXCLUDED.organization_id,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    type = EXCLUDED.type,
    hook = EXCLUDED.hook,
    role_block_id = EXCLUDED.role_block_id,
    extraction_protocol_block_id = EXCLUDED.extraction_protocol_block_id,
    execution_persona_block_id = EXCLUDED.execution_persona_block_id,
    criteria_block_ids = EXCLUDED.criteria_block_ids,
    pre_hooks = EXCLUDED.pre_hooks,
    post_hooks = EXCLUDED.post_hooks,
    safety = EXCLUDED.safety,
    allowed_mcp_tools = EXCLUDED.allowed_mcp_tools,
    mcp_tool_params = EXCLUDED.mcp_tool_params,
    cognitive_tier = EXCLUDED.cognitive_tier,
    expected_inputs = EXCLUDED.expected_inputs,
    is_system_core = EXCLUDED.is_system_core,
    engine_type = EXCLUDED.engine_type,
    zone = EXCLUDED.zone
"""

_GET_STEP_SQL: str = """
SELECT id, slug, organization_id, name, description, type, hook, role_block_id,
       extraction_protocol_block_id, execution_persona_block_id, criteria_block_ids,
       pre_hooks, post_hooks, safety, allowed_mcp_tools, mcp_tool_params,
       cognitive_tier, expected_inputs, is_system_core, engine_type, zone
FROM steps
WHERE id = $1::uuid
"""

_LIST_STEPS_SQL: str = """
SELECT id, slug, organization_id, name, description, type, hook, role_block_id,
       extraction_protocol_block_id, execution_persona_block_id, criteria_block_ids,
       pre_hooks, post_hooks, safety, allowed_mcp_tools, mcp_tool_params,
       cognitive_tier, expected_inputs, is_system_core, engine_type, zone
FROM steps
"""

_UPSERT_WORKFLOW_SQL: str = """
INSERT INTO workflows (
    id, slug, name, description, status, version, is_public, organization_id,
    default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
    default_lexical_strictness_level, security_penalty, post_hoc_penalty,
    passivity_penalty, enable_contextual_overrides, enable_semantic_smoothing,
    enable_eager_anonymization, system_audit_trail, expected_inputs, steps,
    historical_context_mode
) VALUES (
    $1::uuid, $2, $3::jsonb, $4::jsonb, $5, $6, $7, $8::uuid,
    $9::uuid, $10::uuid, $11::uuid, $12,
    $13, $14, $15,
    $16, $17, $18,
    $19, $20, $21::jsonb, $22::jsonb,
    $23
)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    version = EXCLUDED.version,
    is_public = EXCLUDED.is_public,
    organization_id = EXCLUDED.organization_id,
    default_profile_id = EXCLUDED.default_profile_id,
    mcp_gateway_id = EXCLUDED.mcp_gateway_id,
    model_registry_id = EXCLUDED.model_registry_id,
    default_strictness_level = EXCLUDED.default_strictness_level,
    default_lexical_strictness_level = EXCLUDED.default_lexical_strictness_level,
    security_penalty = EXCLUDED.security_penalty,
    post_hoc_penalty = EXCLUDED.post_hoc_penalty,
    passivity_penalty = EXCLUDED.passivity_penalty,
    enable_contextual_overrides = EXCLUDED.enable_contextual_overrides,
    enable_semantic_smoothing = EXCLUDED.enable_semantic_smoothing,
    enable_eager_anonymization = EXCLUDED.enable_eager_anonymization,
    system_audit_trail = EXCLUDED.system_audit_trail,
    expected_inputs = EXCLUDED.expected_inputs,
    steps = EXCLUDED.steps,
    historical_context_mode = EXCLUDED.historical_context_mode
"""

_GET_WORKFLOW_SQL: str = """
SELECT id, slug, name, description, status, version, is_public, organization_id,
       default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
       default_lexical_strictness_level, security_penalty, post_hoc_penalty,
       passivity_penalty, enable_contextual_overrides, enable_semantic_smoothing,
       enable_eager_anonymization, system_audit_trail, expected_inputs, steps,
       historical_context_mode
FROM workflows
WHERE id = $1::uuid
"""

_LIST_WORKFLOWS_SQL: str = """
SELECT id, slug, name, description, status, version, is_public, organization_id,
       default_profile_id, mcp_gateway_id, model_registry_id, default_strictness_level,
       default_lexical_strictness_level, security_penalty, post_hoc_penalty,
       passivity_penalty, enable_contextual_overrides, enable_semantic_smoothing,
       enable_eager_anonymization, system_audit_trail, expected_inputs, steps,
       historical_context_mode
FROM workflows
"""

_UPSERT_OUTPUT_PROFILE_SQL: str = """
INSERT INTO output_profiles (
    id, slug, workflow_id, organization_id, name, description, user_role_label,
    custom_preface, language, tone_instruction, executive_summary_directive,
    matrix_1d_synthesis_directive, matrix_2d_synthesis_directive,
    matrix_3d_synthesis_directive, matrix_text_synthesis_directive,
    row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive,
    visible_metadata, matrix_visible_columns, visible_block_extensions,
    visible_workflow_extensions, max_extension_items, display_scale,
    custom_scale_min, custom_scale_max, synthesis_length_constraint,
    row_explanation_length_constraint, xai_length_constraint,
    variance_length_constraint, matrix_graph_length_constraint,
    max_quotes_per_matrix, max_unmet_criteria, target_block_order,
    matrix_synthesis_groups, content_blocks, show_sources_summary_box,
    sources_display_mode, variance_target_block, user_role_target_block
) VALUES (
    $1::uuid, $2, $3::uuid, $4::uuid, $5::jsonb, $6::jsonb, $7::jsonb,
    $8::jsonb, $9, $10, $11,
    $12, $13,
    $14, $15,
    $16, $17, $18,
    $19::jsonb, $20::jsonb, $21::jsonb,
    $22::jsonb, $23, $24,
    $25, $26, $27,
    $28, $29,
    $30, $31,
    $32, $33, $34::jsonb,
    $35::jsonb, $36::jsonb, $37,
    $38, $39, $40
)
ON CONFLICT (id) DO UPDATE SET
    slug = EXCLUDED.slug,
    workflow_id = EXCLUDED.workflow_id,
    organization_id = EXCLUDED.organization_id,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    user_role_label = EXCLUDED.user_role_label,
    custom_preface = EXCLUDED.custom_preface,
    language = EXCLUDED.language,
    tone_instruction = EXCLUDED.tone_instruction,
    executive_summary_directive = EXCLUDED.executive_summary_directive,
    matrix_1d_synthesis_directive = EXCLUDED.matrix_1d_synthesis_directive,
    matrix_2d_synthesis_directive = EXCLUDED.matrix_2d_synthesis_directive,
    matrix_3d_synthesis_directive = EXCLUDED.matrix_3d_synthesis_directive,
    matrix_text_synthesis_directive = EXCLUDED.matrix_text_synthesis_directive,
    row_explanation_directive = EXCLUDED.row_explanation_directive,
    xai_synthesis_directive = EXCLUDED.xai_synthesis_directive,
    variance_synthesis_directive = EXCLUDED.variance_synthesis_directive,
    visible_metadata = EXCLUDED.visible_metadata,
    matrix_visible_columns = EXCLUDED.matrix_visible_columns,
    visible_block_extensions = EXCLUDED.visible_block_extensions,
    visible_workflow_extensions = EXCLUDED.visible_workflow_extensions,
    max_extension_items = EXCLUDED.max_extension_items,
    display_scale = EXCLUDED.display_scale,
    custom_scale_min = EXCLUDED.custom_scale_min,
    custom_scale_max = EXCLUDED.custom_scale_max,
    synthesis_length_constraint = EXCLUDED.synthesis_length_constraint,
    row_explanation_length_constraint = EXCLUDED.row_explanation_length_constraint,
    xai_length_constraint = EXCLUDED.xai_length_constraint,
    variance_length_constraint = EXCLUDED.variance_length_constraint,
    matrix_graph_length_constraint = EXCLUDED.matrix_graph_length_constraint,
    max_quotes_per_matrix = EXCLUDED.max_quotes_per_matrix,
    max_unmet_criteria = EXCLUDED.max_unmet_criteria,
    target_block_order = EXCLUDED.target_block_order,
    matrix_synthesis_groups = EXCLUDED.matrix_synthesis_groups,
    content_blocks = EXCLUDED.content_blocks,
    show_sources_summary_box = EXCLUDED.show_sources_summary_box,
    sources_display_mode = EXCLUDED.sources_display_mode,
    variance_target_block = EXCLUDED.variance_target_block,
    user_role_target_block = EXCLUDED.user_role_target_block
"""

_GET_OUTPUT_PROFILE_SQL: str = """
SELECT id, slug, workflow_id, organization_id, name, description, user_role_label,
       custom_preface, language, tone_instruction, executive_summary_directive,
       matrix_1d_synthesis_directive, matrix_2d_synthesis_directive,
       matrix_3d_synthesis_directive, matrix_text_synthesis_directive,
       row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive,
       visible_metadata, matrix_visible_columns, visible_block_extensions,
       visible_workflow_extensions, max_extension_items, display_scale,
       custom_scale_min, custom_scale_max, synthesis_length_constraint,
       row_explanation_length_constraint, xai_length_constraint,
       variance_length_constraint, matrix_graph_length_constraint,
       max_quotes_per_matrix, max_unmet_criteria, target_block_order,
       matrix_synthesis_groups, content_blocks, show_sources_summary_box,
       sources_display_mode, variance_target_block, user_role_target_block
FROM output_profiles
WHERE id = $1::uuid
"""

_LIST_OUTPUT_PROFILES_SQL: str = """
SELECT id, slug, workflow_id, organization_id, name, description, user_role_label,
       custom_preface, language, tone_instruction, executive_summary_directive,
       matrix_1d_synthesis_directive, matrix_2d_synthesis_directive,
       matrix_3d_synthesis_directive, matrix_text_synthesis_directive,
       row_explanation_directive, xai_synthesis_directive, variance_synthesis_directive,
       visible_metadata, matrix_visible_columns, visible_block_extensions,
       visible_workflow_extensions, max_extension_items, display_scale,
       custom_scale_min, custom_scale_max, synthesis_length_constraint,
       row_explanation_length_constraint, xai_length_constraint,
       variance_length_constraint, matrix_graph_length_constraint,
       max_quotes_per_matrix, max_unmet_criteria, target_block_order,
       matrix_synthesis_groups, content_blocks, show_sources_summary_box,
       sources_display_mode, variance_target_block, user_role_target_block
FROM output_profiles
"""

_UPSERT_REPORT_ARTIFACT_SQL: str = """
INSERT INTO report_artifacts (
    id, execution_id, workflow_id, profile_id, locale, title, status,
    storage_paths, metadata, custom_preface_md, error_message, has_pdf,
    created_at, updated_at
) VALUES (
    $1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7,
    $8::jsonb, $9::jsonb, $10, $11, $12,
    $13::timestamptz, $14::timestamptz
)
ON CONFLICT (id) DO UPDATE SET
    execution_id = EXCLUDED.execution_id,
    workflow_id = EXCLUDED.workflow_id,
    profile_id = EXCLUDED.profile_id,
    locale = EXCLUDED.locale,
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    storage_paths = EXCLUDED.storage_paths,
    metadata = EXCLUDED.metadata,
    custom_preface_md = EXCLUDED.custom_preface_md,
    error_message = EXCLUDED.error_message,
    updated_at = EXCLUDED.updated_at
"""

_GET_REPORT_ARTIFACT_SQL: str = """
SELECT id, execution_id, workflow_id, profile_id, locale, title, status,
       storage_paths, metadata, custom_preface_md, error_message, has_pdf,
       created_at, updated_at
FROM report_artifacts
WHERE id = $1::uuid
"""

_LIST_REPORT_ARTIFACTS_SQL: str = """
SELECT id, execution_id, workflow_id, profile_id, locale, title, status,
       storage_paths, metadata, custom_preface_md, error_message, has_pdf,
       created_at, updated_at
FROM report_artifacts
"""


class _ReportBinaryRowDTO(V2CoreBase):
    """Strict internal boundary DTO for hydrating a ReportBinaryPayloadDTO row.

    Attributes:
        report_id: Formatted rep_<uuid7_hex> identifier.
        mime_type: MIME type string.
        pdf_bytes: Raw binary PDF payload.
        size_bytes: Exact byte length.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    report_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Report ID.")]
    mime_type: Annotated[str, Field(min_length=1, description="MIME type.")]
    pdf_bytes: Annotated[bytes, Field(description="PDF binary bytes.")]
    size_bytes: Annotated[int, Field(ge=0, description="Byte size.")]
    created_at: Annotated[datetime, Field(description="Creation timestamp.")]


def _coerce_uuid_or_str(raw: object) -> uuid.UUID | str:
    """Narrow a raw database UUID or string column value to uuid.UUID | str.

    Args:
        raw: Database value from an asyncpg record column.

    Returns:
        Value narrowed to uuid.UUID or str.
    """
    if isinstance(raw, (uuid.UUID, str)):
        return raw
    return str(raw)


def _parse_optional_uuid7(raw: str | None, prefix: EntityPrefix) -> uuid.UUID | None:
    """Parse an optional Opaque Stripe ID into a 16-byte UUIDv7 or None.

    Args:
        raw: Optional canonical {prefix}_{32_hex} string or None.
        prefix: Expected EntityPrefix for the foreign key column.

    Returns:
        Validated uuid.UUID or None.

    Raises:
        AppException: With VALIDATION_FAILED if raw is non-None and invalid.
    """
    if raw is None:
        return None
    return parse_prefixed_uuid7(raw, prefix)


def _format_optional_uuid7(raw: object, prefix: EntityPrefix) -> str | None:
    """Format an optional database UUID column value into a {prefix}_{32_hex} string or None.

    Args:
        raw: Database column value (uuid.UUID, str, or None).
        prefix: Target EntityPrefix for formatting.

    Returns:
        Canonical {prefix}_{32_hex} string or None.

    Raises:
        AppException: With VALIDATION_FAILED if raw is non-None and not a valid UUIDv7.
    """
    if raw is None:
        return None
    return format_prefixed_uuid7(_coerce_uuid_or_str(raw), prefix)


def _parse_org_uuid7(raw: str | None) -> uuid.UUID | None:
    """Parse an optional organization_id into a 16-byte UUIDv7, bridging 'SYSTEM' deterministically.

    Args:
        raw: Organization identifier ('org_<32_hex>', 'org_system000000', 'SYSTEM', or None).

    Returns:
        16-byte version-7 uuid.UUID or None.

    Raises:
        AppException: With VALIDATION_FAILED if raw is an invalid organization ID.
    """
    if raw is None:
        return None
    if raw == "SYSTEM":
        return _SYSTEM_ORG_UUID7
    if raw == "org_system000000":
        return _ROOT_SYSTEM_ORG_UUID7
    return parse_prefixed_uuid7(raw, EntityPrefix.ORGANIZATION)


def _format_org_uuid7(raw: object) -> str | None:
    """Format a database organization_id UUID column into 'org_<32_hex>', 'org_system000000', 'SYSTEM', or None.

    Args:
        raw: Database organization_id value (uuid.UUID, str, or None).

    Returns:
        Canonical 'org_<32_hex>', 'org_system000000', 'SYSTEM', or None.

    Raises:
        AppException: With VALIDATION_FAILED if raw is non-None and invalid.
    """
    if raw is None:
        return None
    coerced = _coerce_uuid_or_str(raw)
    if coerced == _SYSTEM_ORG_UUID7 or str(coerced) in {str(_SYSTEM_ORG_UUID7), "SYSTEM"}:
        return "SYSTEM"
    if coerced == _ROOT_SYSTEM_ORG_UUID7 or str(coerced) in {str(_ROOT_SYSTEM_ORG_UUID7), "org_system000000"}:
        return "org_system000000"
    return format_prefixed_uuid7(coerced, EntityPrefix.ORGANIZATION)


def _decode_jsonb_column(raw: object) -> object:
    """Decode a JSONB column value if returned as raw UTF-8 string or bytes.

    Args:
        raw: Column value returned by asyncpg or InMemoryAsyncPgConnection.

    Returns:
        Decoded Python structure ready for Pydantic validation.
    """
    if raw is None:
        return None
    if isinstance(raw, (str, bytes, bytearray)):
        return from_json(raw)
    if isinstance(raw, memoryview):
        return from_json(bytes(raw))
    return raw


def _encode_optional_jsonb(val: object) -> str | None:
    """Encode an optional value to a UTF-8 JSON string for asyncpg JSONB parameters.

    Args:
        val: Value to encode, or None.

    Returns:
        UTF-8 JSON string or None.
    """
    if val is None:
        return None
    return to_json(val).decode("utf-8")


def _coerce_float(raw: object) -> float:
    """Convert a database NUMERIC/Decimal or float column value to float.

    Args:
        raw: Database numeric column value.

    Returns:
        Python float value.
    """
    if isinstance(raw, (float, int, Decimal)):
        return float(raw)
    return float(str(raw))


class PostgresEntityAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing EntityPersistencePort.

    Attributes:
        command_timeout_seconds: Bounded query timeout in seconds resolved from settings.py.
    """

    def __init__(
        self,
        connection: AsyncPgConnectionProtocol,
        command_timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the PostgreSQL entity adapter over an active connection.

        Args:
            connection: Active database connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Explicit command timeout in seconds, or None to use settings.py.
        """
        resolved_timeout = (
            command_timeout_seconds
            if command_timeout_seconds is not None
            else get_settings().postgres_command_timeout_seconds
        )
        self._conn: AsyncPgConnectionProtocol = connection
        self.command_timeout_seconds: float = resolved_timeout

    async def save_report_binary(self, payload: ReportBinaryPayloadDTO) -> None:
        """Persist a ReportBinaryPayloadDTO into report_binaries (BYTEA TOAST) and mark has_pdf.

        Args:
            payload: Validated ReportBinaryPayloadDTO instance.

        Raises:
            AppException: With VALIDATION_FAILED if report_id is invalid or size_bytes mismatches
                len(pdf_bytes), or STORAGE_ACCESS_FAILED if persistence fails.
        """
        if len(payload.pdf_bytes) != payload.size_bytes:
            msg = (
                f"ReportBinaryPayloadDTO size_bytes ({payload.size_bytes}) does not match "
                f"actual pdf_bytes length ({len(payload.pdf_bytes)})."
            )
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "report_id": payload.report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        report_uuid = parse_prefixed_uuid7(payload.report_id, EntityPrefix.REPORT)
        try:
            await self._conn.execute(
                _SAVE_REPORT_BINARY_SQL,
                report_uuid,
                payload.mime_type,
                payload.pdf_bytes,
                payload.size_bytes,
                payload.created_at,
                timeout=self.command_timeout_seconds,
            )
            await self._conn.execute(
                _MARK_REPORT_ARTIFACT_PDF_SQL,
                report_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to persist report binary for '{payload.report_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": payload.report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

    async def get_report_binary(self, report_id: str) -> ReportBinaryPayloadDTO | None:
        """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id.

        Args:
            report_id: Canonical rep_<uuid7_hex> report identifier.

        Returns:
            Hydrated ReportBinaryPayloadDTO if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report_id or STORAGE_ACCESS_FAILED on query error.
        """
        report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        try:
            row: AsyncPgRecordProtocol | None = await self._conn.fetchrow(
                _GET_REPORT_BINARY_SQL,
                report_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to fetch report binary for '{report_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        if row is None:
            return None

        raw_bytes = row["pdf_bytes"]
        pdf_bytes: bytes = b""
        if isinstance(raw_bytes, (bytes, bytearray, memoryview)):
            pdf_bytes = bytes(raw_bytes)
        row_dto = _ReportBinaryRowDTO.model_validate(
            {
                "report_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["report_id"]), EntityPrefix.REPORT),
                "mime_type": row["mime_type"],
                "pdf_bytes": pdf_bytes,
                "size_bytes": row["size_bytes"],
                "created_at": row["created_at"],
            },
            strict=False,
        )
        return ReportBinaryPayloadDTO(
            report_id=row_dto.report_id,
            mime_type=row_dto.mime_type,
            pdf_bytes=row_dto.pdf_bytes,
            size_bytes=row_dto.size_bytes,
            created_at=row_dto.created_at,
        )

    def _hydrate_execution_row(self, row: AsyncPgRecordProtocol) -> ExecutionRecord:
        """Hydrate an ExecutionRecord from an asyncpg database record.

        Args:
            row: Database record from executions.

        Returns:
            Validated ExecutionRecord domain model.
        """
        return ExecutionRecord.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.EXECUTION),
                "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
                "workflow_version": row["workflow_version"],
                "active_profile_id": _format_optional_uuid7(row["active_profile_id"], EntityPrefix.OUTPUT_PROFILE),
                "output_profile_id": _format_optional_uuid7(row["output_profile_id"], EntityPrefix.OUTPUT_PROFILE),
                "status": row["status"],
                "target_locale": row["target_locale"],
                "progress": row["progress"],
                "status_message": row["status_message"],
                "raw_inputs": _decode_jsonb_column(row["raw_inputs"]),
                "frozen_context": _decode_jsonb_column(row["frozen_context"]),
                "frozen_context_storage_path": row["frozen_context_storage_path"],
                "pdf_report_path": row["pdf_report_path"],
                "steps": _decode_jsonb_column(row["steps"]),
                "step_states": _decode_jsonb_column(row["step_states"]),
                "profile_syntheses": _decode_jsonb_column(row["profile_syntheses"]),
                "source_identity_manifest": _decode_jsonb_column(row["source_identity_manifest"]),
                "execution_trace": _decode_jsonb_column(row["execution_trace"]),
                "execution_trace_storage_path": row["execution_trace_storage_path"],
                "context_variables": _decode_jsonb_column(row["context_variables"]),
                "context_variables_storage_path": row["context_variables_storage_path"],
                "is_resumable": row["is_resumable"],
                "prompt_tokens": int(str(row["prompt_tokens"])),
                "completion_tokens": int(str(row["completion_tokens"])),
                "cached_tokens": int(str(row["cached_tokens"])),
                "reasoning_tokens": int(str(row["reasoning_tokens"])),
                "cumulative_synthesis_tokens": int(str(row["cumulative_synthesis_tokens"])),
                "dag_cost_usd": _coerce_float(row["dag_cost_usd"]),
                "cumulative_synthesis_cost": _coerce_float(row["cumulative_synthesis_cost"]),
                "cost_estimate": _coerce_float(row["cost_estimate"]),
                "models_used": _decode_jsonb_column(row["models_used"]),
                "execution_summary": _decode_jsonb_column(row["execution_summary"]),
                "metadata": _decode_jsonb_column(row["metadata"]),
                "duration_ms": int(str(row["duration_ms"])),
                "error": row["error"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "completed_at": row["completed_at"],
                "created_by": row["created_by"],
                "organization_id": _format_org_uuid7(row["organization_id"]),
            },
            strict=False,
        )

    async def save_execution(self, record: ExecutionRecord) -> str:
        """Persist an ExecutionRecord into the PostgreSQL 19 executions table.

        Args:
            record: Validated ExecutionRecord domain model.

        Returns:
            Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid execution ID or
                STORAGE_ACCESS_FAILED if persistence fails.
        """
        exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
        wf_uuid = parse_prefixed_uuid7(record.workflow_id, EntityPrefix.WORKFLOW)
        active_prf_uuid = _parse_optional_uuid7(record.active_profile_id, EntityPrefix.OUTPUT_PROFILE)
        output_prf_uuid = _parse_optional_uuid7(record.output_profile_id, EntityPrefix.OUTPUT_PROFILE)
        org_uuid = _parse_org_uuid7(record.organization_id)
        dumped = record.model_dump(mode="json", exclude_none=True)

        frozen_ctx_json: str | None = None
        if record.frozen_context is not None:
            frozen_ctx_json = to_json(dumped["frozen_context"]).decode("utf-8")

        exec_summary_json: str | None = None
        if record.execution_summary is not None:
            exec_summary_json = to_json(dumped["execution_summary"]).decode("utf-8")

        metadata_json: str | None = None
        if record.metadata is not None:
            metadata_json = to_json(dumped["metadata"]).decode("utf-8")

        try:
            await self._conn.execute(
                _SAVE_EXECUTION_SQL,
                exec_uuid,
                wf_uuid,
                record.workflow_version,
                active_prf_uuid,
                output_prf_uuid,
                record.status.value,
                record.target_locale,
                record.progress,
                record.status_message,
                to_json(dumped["raw_inputs"]).decode("utf-8"),
                frozen_ctx_json,
                record.frozen_context_storage_path,
                record.pdf_report_path,
                to_json(dumped["steps"]).decode("utf-8"),
                to_json(dumped["step_states"]).decode("utf-8"),
                to_json(dumped["profile_syntheses"]).decode("utf-8"),
                to_json(dumped["source_identity_manifest"]).decode("utf-8"),
                to_json(dumped["execution_trace"]).decode("utf-8"),
                record.execution_trace_storage_path,
                to_json(dumped["context_variables"]).decode("utf-8"),
                record.context_variables_storage_path,
                record.is_resumable,
                record.prompt_tokens,
                record.completion_tokens,
                record.cached_tokens,
                record.reasoning_tokens,
                record.cumulative_synthesis_tokens,
                record.dag_cost_usd,
                record.cumulative_synthesis_cost,
                record.cost_estimate,
                to_json(dumped["models_used"]).decode("utf-8"),
                exec_summary_json,
                metadata_json,
                record.duration_ms,
                record.error,
                record.created_at,
                record.updated_at,
                record.completed_at,
                record.created_by,
                org_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to persist execution '{record.id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "execution_id": record.id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        return record.id

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        """Retrieve and reconstitute an ExecutionRecord from PostgreSQL by execution_id.

        Args:
            execution_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Reconstituted ExecutionRecord instance or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED on invalid execution_id or
                STORAGE_ACCESS_FAILED if query execution fails.
        """
        exec_uuid = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        try:
            row: AsyncPgRecordProtocol | None = await self._conn.fetchrow(
                _GET_EXECUTION_SQL,
                exec_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to fetch execution '{execution_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "execution_id": execution_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        if row is None:
            return None

        return self._hydrate_execution_row(row)

    async def _execute_upsert(
        self,
        sql: str,
        *args: object,
        entity_label: str,
        entity_id: str,
    ) -> str:
        """Execute a parameterized upsert statement and translate transport errors to AppException.

        Args:
            sql: Parameterized INSERT ... ON CONFLICT DO UPDATE statement.
            *args: Positional SQL bind arguments.
            entity_label: Human-readable entity type label for structured error logging.
            entity_id: Canonical Opaque Stripe ID of the entity being persisted.

        Returns:
            Canonical entity_id persisted into PostgreSQL 19.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if the database command fails.
        """
        try:
            await self._conn.execute(sql, *args, timeout=self.command_timeout_seconds)
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to upsert {entity_label} '{entity_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "entity_id": entity_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc
        return entity_id

    def _hydrate_organization_row(self, row: AsyncPgRecordProtocol) -> Organization:
        """Hydrate an Organization from a database row.

        Args:
            row: Database record from the organizations table.

        Returns:
            Validated Organization domain model.
        """
        return Organization.model_validate(
            {
                "id": str(_format_org_uuid7(row["id"])),
                "slug": row["slug"],
                "name": row["name"],
                "created_at": row["created_at"],
                "is_active": row["is_active"],
                "tier": row["tier"],
                "contact_email": row["contact_email"],
                "billing_id": row["billing_id"],
                "subscription_status": row["subscription_status"],
                "quota_limit": _coerce_float(row["quota_limit"]),
                "tpm_limit": int(str(row["tpm_limit"])),
                "rpm_limit": int(str(row["rpm_limit"])),
            },
            strict=False,
        )

    async def upsert_organization(self, org: Organization) -> str:
        """Persist an Organization into the organizations table.

        Args:
            org: Validated Organization domain model.

        Returns:
            Canonical org_<hex> organization identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        org_uuid = (
            _ROOT_SYSTEM_ORG_UUID7
            if org.id == "org_system000000"
            else parse_prefixed_uuid7(org.id, EntityPrefix.ORGANIZATION)
        )
        return await self._execute_upsert(
            _UPSERT_ORGANIZATION_SQL,
            org_uuid,
            org.slug,
            org.name,
            org.created_at,
            org.is_active,
            org.tier,
            org.contact_email,
            org.billing_id,
            org.subscription_status.value,
            org.quota_limit,
            org.tpm_limit,
            org.rpm_limit,
            entity_label="organization",
            entity_id=org.id,
        )

    async def get_organization(self, org_id: str) -> Organization | None:
        """Fetch an Organization by ID.

        Args:
            org_id: Canonical org_<hex> organization identifier.

        Returns:
            Hydrated Organization instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid org_id.
        """
        org_uuid = (
            _ROOT_SYSTEM_ORG_UUID7
            if org_id == "org_system000000"
            else parse_prefixed_uuid7(org_id, EntityPrefix.ORGANIZATION)
        )
        row = await self._conn.fetchrow(_GET_ORGANIZATION_SQL, org_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_organization_row(row)

    def _hydrate_user_row(self, row: AsyncPgRecordProtocol) -> User:
        """Hydrate a User from a database row.

        Args:
            row: Database record from the users table.

        Returns:
            Validated User domain model.
        """
        return User.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.USER),
                "slug": row["slug"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"],
                "organization_id": _format_org_uuid7(row["organization_id"]),
                "is_active": row["is_active"],
                "language": row["language"],
                "theme_mode": row["theme_mode"],
                "created_at": row["created_at"],
                "created_by": row["created_by"],
            },
            strict=False,
        )

    async def upsert_user(self, user: User) -> str:
        """Persist a User into the users table.

        Args:
            user: Validated User domain model.

        Returns:
            Canonical usr_<hex> user identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        user_uuid = parse_prefixed_uuid7(user.id, EntityPrefix.USER)
        org_uuid = _parse_org_uuid7(user.organization_id)
        return await self._execute_upsert(
            _UPSERT_USER_SQL,
            user_uuid,
            user.slug,
            str(user.email),
            user.name,
            user.role.value,
            org_uuid,
            user.is_active,
            str(user.language),
            user.theme_mode,
            user.created_at,
            user.created_by,
            entity_label="user",
            entity_id=user.id,
        )

    async def get_user(self, user_id: str) -> User | None:
        """Fetch a User by ID.

        Args:
            user_id: Canonical usr_<hex> user identifier.

        Returns:
            Hydrated User instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid user_id.
        """
        user_uuid = parse_prefixed_uuid7(user_id, EntityPrefix.USER)
        row = await self._conn.fetchrow(_GET_USER_SQL, user_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_user_row(row)

    def _hydrate_system_config_row(
        self, row: AsyncPgRecordProtocol
    ) -> SystemConfigModelRegistry | SystemConfigMCPGateways:
        """Hydrate a polymorphic SystemConfig from a database row.

        Args:
            row: Database record from the system_configs table.

        Returns:
            Validated SystemConfigModelRegistry or SystemConfigMCPGateways instance.
        """
        cfg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.SYSTEM_CONFIG)
        cfg_type = row["type"]
        if cfg_type == "mcp_gateways":
            return SystemConfigMCPGateways.model_validate(
                {
                    "id": cfg_id,
                    "type": "mcp_gateways",
                    "slug": row["slug"],
                    "endpoint_url": row["endpoint_url"],
                    "transport_type": row["transport_type"],
                    "auth_type": row["auth_type"],
                    "auth_header_name": row["auth_header_name"],
                    "auth_env_var": row["auth_env_var"],
                    "timeout_seconds": row["timeout_seconds"],
                    "tools": _decode_jsonb_column(row["tools"]),
                },
                strict=False,
            )
        return SystemConfigModelRegistry.model_validate(
            {
                "id": cfg_id,
                "name": row["name"],
                "type": "model_registry",
                "default_provider": row["default_provider"],
                "tier_definitions": _decode_jsonb_column(row["tier_definitions"]),
            },
            strict=False,
        )

    async def upsert_system_config(self, cfg: SystemConfigModelRegistry | SystemConfigMCPGateways) -> str:
        """Persist a SystemConfigModelRegistry or SystemConfigMCPGateways into system_configs.

        Args:
            cfg: Validated SystemConfigModelRegistry or SystemConfigMCPGateways domain model.

        Returns:
            Canonical sys_<hex> system configuration identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        cfg_uuid = parse_prefixed_uuid7(cfg.id, EntityPrefix.SYSTEM_CONFIG)
        dumped = cfg.model_dump(mode="json")
        if isinstance(cfg, SystemConfigMCPGateways):
            return await self._execute_upsert(
                _UPSERT_SYSTEM_CONFIG_SQL,
                cfg_uuid,
                None,
                cfg.type,
                cfg.slug,
                None,
                None,
                cfg.endpoint_url,
                str(cfg.transport_type),
                str(cfg.auth_type),
                cfg.auth_header_name,
                cfg.auth_env_var,
                cfg.timeout_seconds,
                to_json(dumped["tools"]).decode("utf-8"),
                entity_label="system_config",
                entity_id=cfg.id,
            )
        return await self._execute_upsert(
            _UPSERT_SYSTEM_CONFIG_SQL,
            cfg_uuid,
            cfg.name,
            cfg.type,
            None,
            str(cfg.default_provider),
            to_json(dumped["tier_definitions"]).decode("utf-8"),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            entity_label="system_config",
            entity_id=cfg.id,
        )

    async def get_system_config(self, config_id: str) -> SystemConfigModelRegistry | SystemConfigMCPGateways | None:
        """Fetch a SystemConfig by ID.

        Args:
            config_id: Canonical sys_<hex> system configuration identifier.

        Returns:
            Hydrated SystemConfigModelRegistry or SystemConfigMCPGateways if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid config_id.
        """
        cfg_uuid = parse_prefixed_uuid7(config_id, EntityPrefix.SYSTEM_CONFIG)
        row = await self._conn.fetchrow(_GET_SYSTEM_CONFIG_SQL, cfg_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_system_config_row(row)

    def _hydrate_prompt_block_row(self, row: AsyncPgRecordProtocol) -> AnyPromptBlock:
        """Hydrate a polymorphic AnyPromptBlock from a database row.

        Args:
            row: Database record from the prompt_blocks table.

        Returns:
            Validated MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock, or SystemRulePromptBlock.
        """
        blk_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.PROMPT_BLOCK)
        org_id = _format_org_uuid7(row["organization_id"])
        cat = str(row["category_id"])
        if cat == PromptBlockCategory.MATRIX.value:
            return MatrixPromptBlock.model_validate(
                {
                    "id": blk_id,
                    "slug": row["slug"],
                    "organization_id": org_id,
                    "label": _decode_jsonb_column(row["label"]),
                    "description": _decode_jsonb_column(row["description"]),
                    "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                    "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                    "category_id": cat,
                    "type": row["type"],
                    "is_evaluative": row["is_evaluative"],
                    "allow_decimals": row["allow_decimals"],
                    "allow_contextual_override": row["allow_contextual_override"],
                    "is_lightweight_protocol": row["is_lightweight_protocol"],
                    "target_input_key": row["target_input_key"],
                    "ai_description": row["ai_description"],
                    "scales": _decode_jsonb_column(row["scales"]),
                    "rows": _decode_jsonb_column(row["rows"]),
                    "columns": _decode_jsonb_column(row["columns"]),
                    "computed_min": row["computed_min"],
                    "computed_max": row["computed_max"],
                },
                strict=False,
            )
        if cat in (
            PromptBlockCategory.EXECUTION_PERSONA.value,
            PromptBlockCategory.AGENT_ROLE.value,
        ):
            return PersonaPromptBlock.model_validate(
                {
                    "id": blk_id,
                    "slug": row["slug"],
                    "organization_id": org_id,
                    "label": _decode_jsonb_column(row["label"]),
                    "description": _decode_jsonb_column(row["description"]),
                    "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                    "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                    "category_id": cat,
                    "type": row["type"],
                    "is_evaluative": row["is_evaluative"],
                    "allow_decimals": row["allow_decimals"],
                    "is_lightweight_protocol": row["is_lightweight_protocol"],
                    "role_enforcement": row["role_enforcement"],
                    "tone_directives": _decode_jsonb_column(row["tone_directives"]),
                },
                strict=False,
            )
        if cat == PromptBlockCategory.PROTOCOL.value:
            return ProtocolPromptBlock.model_validate(
                {
                    "id": blk_id,
                    "slug": row["slug"],
                    "organization_id": org_id,
                    "label": _decode_jsonb_column(row["label"]),
                    "description": _decode_jsonb_column(row["description"]),
                    "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                    "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                    "category_id": cat,
                    "type": row["type"],
                    "is_evaluative": row["is_evaluative"],
                    "allow_decimals": row["allow_decimals"],
                    "is_lightweight_protocol": row["is_lightweight_protocol"],
                    "protocol_instructions": row["protocol_instructions"],
                },
                strict=False,
            )
        return SystemRulePromptBlock.model_validate(
            {
                "id": blk_id,
                "slug": row["slug"],
                "organization_id": org_id,
                "label": _decode_jsonb_column(row["label"]),
                "description": _decode_jsonb_column(row["description"]),
                "output_extensions": _decode_jsonb_column(row["output_extensions"]),
                "theory_grounding": _decode_jsonb_column(row["theory_grounding"]),
                "category_id": cat,
                "type": row["type"],
                "is_evaluative": row["is_evaluative"],
                "allow_decimals": row["allow_decimals"],
                "is_lightweight_protocol": row["is_lightweight_protocol"],
                "instruction_text": row["instruction_text"],
            },
            strict=False,
        )

    async def upsert_prompt_block(self, block: AnyPromptBlock) -> str:
        """Persist a polymorphic AnyPromptBlock into prompt_blocks.

        Args:
            block: Validated concrete PromptBlock domain model.

        Returns:
            Canonical blk_<hex> prompt block identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        block_uuid = parse_prefixed_uuid7(block.id, EntityPrefix.PROMPT_BLOCK)
        org_uuid = _parse_org_uuid7(block.organization_id)
        dumped = block.model_dump(mode="json")
        allow_ctx_override = False
        target_input_key: str | None = None
        ai_description: str | None = None
        scales_json: str | None = None
        rows_json: str | None = None
        columns_json: str | None = None
        computed_min: int | None = None
        computed_max: int | None = None
        instruction_text: str | None = None
        role_enforcement: str | None = None
        tone_directives_json: str | None = None
        protocol_instructions: str | None = None

        if isinstance(block, MatrixPromptBlock):
            allow_ctx_override = block.allow_contextual_override
            target_input_key = block.target_input_key
            ai_description = block.ai_description
            scales_json = _encode_optional_jsonb(dumped["scales"])
            rows_json = _encode_optional_jsonb(dumped["rows"])
            columns_json = _encode_optional_jsonb(dumped["columns"])
            computed_min = block.computed_min
            computed_max = block.computed_max
        elif isinstance(block, PersonaPromptBlock):
            role_enforcement = block.role_enforcement
            tone_directives_json = _encode_optional_jsonb(dumped["tone_directives"])
        elif isinstance(block, ProtocolPromptBlock):
            protocol_instructions = block.protocol_instructions
        elif isinstance(block, SystemRulePromptBlock):
            instruction_text = block.instruction_text

        return await self._execute_upsert(
            _UPSERT_PROMPT_BLOCK_SQL,
            block_uuid,
            block.slug,
            org_uuid,
            to_json(dumped["label"]).decode("utf-8"),
            to_json(dumped["description"]).decode("utf-8"),
            to_json(dumped["output_extensions"]).decode("utf-8"),
            _encode_optional_jsonb(dumped["theory_grounding"]),
            str(block.category_id),
            str(block.type),
            block.is_evaluative,
            block.allow_decimals,
            allow_ctx_override,
            block.is_lightweight_protocol,
            target_input_key,
            ai_description,
            scales_json,
            rows_json,
            columns_json,
            computed_min,
            computed_max,
            instruction_text,
            role_enforcement,
            tone_directives_json,
            protocol_instructions,
            entity_label="prompt_block",
            entity_id=block.id,
        )

    async def get_prompt_block(self, block_id: str) -> AnyPromptBlock | None:
        """Fetch an AnyPromptBlock by ID.

        Args:
            block_id: Canonical blk_<hex> prompt block identifier.

        Returns:
            Hydrated AnyPromptBlock instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid block_id.
        """
        block_uuid = parse_prefixed_uuid7(block_id, EntityPrefix.PROMPT_BLOCK)
        row = await self._conn.fetchrow(_GET_PROMPT_BLOCK_SQL, block_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_prompt_block_row(row)

    def _hydrate_step_row(self, row: AsyncPgRecordProtocol) -> Step:
        """Hydrate a Step from a database row.

        Args:
            row: Database record from the steps table.

        Returns:
            Validated Step domain model.
        """
        return Step.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.STEP),
                "slug": row["slug"],
                "organization_id": _format_org_uuid7(row["organization_id"]),
                "name": _decode_jsonb_column(row["name"]),
                "description": _decode_jsonb_column(row["description"]),
                "type": row["type"],
                "hook": row["hook"],
                "role_block_id": _format_optional_uuid7(row["role_block_id"], EntityPrefix.PROMPT_BLOCK),
                "extraction_protocol_block_id": _format_optional_uuid7(
                    row["extraction_protocol_block_id"], EntityPrefix.PROMPT_BLOCK
                ),
                "execution_persona_block_id": _format_optional_uuid7(
                    row["execution_persona_block_id"], EntityPrefix.PROMPT_BLOCK
                ),
                "criteria_block_ids": _decode_jsonb_column(row["criteria_block_ids"]),
                "pre_hooks": _decode_jsonb_column(row["pre_hooks"]),
                "post_hooks": _decode_jsonb_column(row["post_hooks"]),
                "safety": row["safety"],
                "allowed_mcp_tools": _decode_jsonb_column(row["allowed_mcp_tools"]),
                "mcp_tool_params": _decode_jsonb_column(row["mcp_tool_params"]),
                "cognitive_tier": row["cognitive_tier"],
                "expected_inputs": _decode_jsonb_column(row["expected_inputs"]),
                "is_system_core": row["is_system_core"],
                "engine_type": row["engine_type"],
                "zone": row["zone"],
            },
            strict=False,
        )

    async def upsert_step(self, step: Step) -> str:
        """Persist a Step into steps.

        Args:
            step: Validated Step domain model.

        Returns:
            Canonical stp_<hex> step identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        step_uuid = parse_prefixed_uuid7(step.id, EntityPrefix.STEP)
        org_uuid = _parse_org_uuid7(step.organization_id)
        role_uuid = _parse_optional_uuid7(step.role_block_id, EntityPrefix.PROMPT_BLOCK)
        proto_uuid = _parse_optional_uuid7(step.extraction_protocol_block_id, EntityPrefix.PROMPT_BLOCK)
        persona_uuid = _parse_optional_uuid7(step.execution_persona_block_id, EntityPrefix.PROMPT_BLOCK)
        dumped = step.model_dump(mode="json")
        cognitive_tier_str: str | None = None
        if step.cognitive_tier is not None:
            cognitive_tier_str = str(step.cognitive_tier)
        return await self._execute_upsert(
            _UPSERT_STEP_SQL,
            step_uuid,
            step.slug,
            org_uuid,
            to_json(dumped["name"]).decode("utf-8"),
            _encode_optional_jsonb(dumped["description"]),
            str(step.type),
            step.hook,
            role_uuid,
            proto_uuid,
            persona_uuid,
            to_json(dumped["criteria_block_ids"]).decode("utf-8"),
            to_json(dumped["pre_hooks"]).decode("utf-8"),
            to_json(dumped["post_hooks"]).decode("utf-8"),
            step.safety,
            to_json(dumped["allowed_mcp_tools"]).decode("utf-8"),
            to_json(dumped["mcp_tool_params"]).decode("utf-8"),
            cognitive_tier_str,
            to_json(dumped["expected_inputs"]).decode("utf-8"),
            step.is_system_core,
            str(step.engine_type),
            str(step.zone),
            entity_label="step",
            entity_id=step.id,
        )

    async def get_step(self, step_id: str) -> Step | None:
        """Fetch a Step by ID.

        Args:
            step_id: Canonical stp_<hex> step identifier.

        Returns:
            Hydrated Step instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid step_id.
        """
        step_uuid = parse_prefixed_uuid7(step_id, EntityPrefix.STEP)
        row = await self._conn.fetchrow(_GET_STEP_SQL, step_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_step_row(row)

    def _hydrate_workflow_row(self, row: AsyncPgRecordProtocol) -> Workflow:
        """Hydrate a Workflow from a database row.

        Args:
            row: Database record from the workflows table.

        Returns:
            Validated Workflow domain model.
        """
        return Workflow.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.WORKFLOW),
                "slug": row["slug"],
                "name": _decode_jsonb_column(row["name"]),
                "description": _decode_jsonb_column(row["description"]),
                "status": row["status"],
                "version": row["version"],
                "is_public": row["is_public"],
                "organization_id": _format_org_uuid7(row["organization_id"]),
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
                "steps": _decode_jsonb_column(row["steps"]),
                "historical_context_mode": row["historical_context_mode"],
            },
            strict=False,
        )

    async def upsert_workflow(self, wf: Workflow) -> str:
        """Persist a Workflow into workflows.

        Args:
            wf: Validated Workflow domain model.

        Returns:
            Canonical wf_<hex> workflow identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        wf_uuid = parse_prefixed_uuid7(wf.id, EntityPrefix.WORKFLOW)
        org_uuid = _parse_org_uuid7(wf.organization_id)
        default_prf_uuid = _parse_optional_uuid7(wf.default_profile_id, EntityPrefix.OUTPUT_PROFILE)
        mcp_gw_uuid = _parse_optional_uuid7(wf.mcp_gateway_id, EntityPrefix.SYSTEM_CONFIG)
        model_reg_uuid = parse_prefixed_uuid7(wf.model_registry_id, EntityPrefix.SYSTEM_CONFIG)
        dumped = wf.model_dump(mode="json")
        return await self._execute_upsert(
            _UPSERT_WORKFLOW_SQL,
            wf_uuid,
            wf.slug,
            to_json(dumped["name"]).decode("utf-8"),
            to_json(dumped["description"]).decode("utf-8"),
            wf.status,
            wf.version,
            wf.is_public,
            org_uuid,
            default_prf_uuid,
            mcp_gw_uuid,
            model_reg_uuid,
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
            entity_label="workflow",
            entity_id=wf.id,
        )

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Fetch a Workflow by ID.

        Args:
            workflow_id: Canonical wf_<hex> workflow identifier.

        Returns:
            Hydrated Workflow instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid workflow_id.
        """
        wf_uuid = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        row = await self._conn.fetchrow(_GET_WORKFLOW_SQL, wf_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_workflow_row(row)

    def _hydrate_output_profile_row(self, row: AsyncPgRecordProtocol) -> OutputProfile:
        """Hydrate an OutputProfile from a database row.

        Args:
            row: Database record from the output_profiles table.

        Returns:
            Validated OutputProfile domain model.
        """
        return OutputProfile.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.OUTPUT_PROFILE),
                "slug": row["slug"],
                "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
                "organization_id": _format_org_uuid7(row["organization_id"]),
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
            strict=False,
        )

    async def upsert_output_profile(self, profile: OutputProfile) -> str:
        """Persist an OutputProfile into output_profiles.

        Args:
            profile: Validated OutputProfile domain model.

        Returns:
            Canonical prf_<hex> output profile identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        prf_uuid = parse_prefixed_uuid7(profile.id, EntityPrefix.OUTPUT_PROFILE)
        wf_uuid = parse_prefixed_uuid7(profile.workflow_id, EntityPrefix.WORKFLOW)
        org_uuid = _parse_org_uuid7(profile.organization_id)
        dumped = profile.model_dump(mode="json")
        language_str: str | None = None
        if profile.language is not None:
            language_str = str(profile.language)
        return await self._execute_upsert(
            _UPSERT_OUTPUT_PROFILE_SQL,
            prf_uuid,
            profile.slug,
            wf_uuid,
            org_uuid,
            to_json(dumped["name"]).decode("utf-8"),
            _encode_optional_jsonb(dumped["description"]),
            _encode_optional_jsonb(dumped["user_role_label"]),
            _encode_optional_jsonb(dumped["custom_preface"]),
            language_str,
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
            entity_label="output_profile",
            entity_id=profile.id,
        )

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        """Fetch an OutputProfile by ID.

        Args:
            profile_id: Canonical prf_<hex> output profile identifier.

        Returns:
            Hydrated OutputProfile instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid profile_id.
        """
        prf_uuid = parse_prefixed_uuid7(profile_id, EntityPrefix.OUTPUT_PROFILE)
        row = await self._conn.fetchrow(_GET_OUTPUT_PROFILE_SQL, prf_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_output_profile_row(row)

    def _hydrate_report_artifact_row(self, row: AsyncPgRecordProtocol) -> ReportArtifact:
        """Hydrate a ReportArtifact from a database row.

        Args:
            row: Database record from the report_artifacts table.

        Returns:
            Validated ReportArtifact domain model.
        """
        return ReportArtifact.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.REPORT),
                "execution_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["execution_id"]), EntityPrefix.EXECUTION),
                "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
                "profile_id": format_prefixed_uuid7(
                    _coerce_uuid_or_str(row["profile_id"]), EntityPrefix.OUTPUT_PROFILE
                ),
                "locale": row["locale"],
                "title": row["title"],
                "status": row["status"],
                "storage_paths": _decode_jsonb_column(row["storage_paths"]),
                "metadata": _decode_jsonb_column(row["metadata"]),
                "custom_preface_md": row["custom_preface_md"],
                "error_message": row["error_message"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            },
            strict=False,
        )

    async def upsert_report_artifact(self, artifact: ReportArtifact) -> str:
        """Persist a ReportArtifact into report_artifacts.

        Args:
            artifact: Validated ReportArtifact domain model.

        Returns:
            Canonical rep_<uuid7_hex> report artifact identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report ID or
                STORAGE_ACCESS_FAILED if persistence fails.
        """
        report_uuid = parse_prefixed_uuid7(artifact.id, EntityPrefix.REPORT)
        exec_uuid = parse_prefixed_uuid7(artifact.execution_id, EntityPrefix.EXECUTION)
        wf_uuid = parse_prefixed_uuid7(artifact.workflow_id, EntityPrefix.WORKFLOW)
        prf_uuid = parse_prefixed_uuid7(artifact.profile_id, EntityPrefix.OUTPUT_PROFILE)
        dumped = artifact.model_dump(mode="json")
        return await self._execute_upsert(
            _UPSERT_REPORT_ARTIFACT_SQL,
            report_uuid,
            exec_uuid,
            wf_uuid,
            prf_uuid,
            artifact.locale,
            artifact.title,
            str(artifact.status),
            to_json(dumped["storage_paths"]).decode("utf-8"),
            to_json(dumped["metadata"]).decode("utf-8"),
            artifact.custom_preface_md,
            artifact.error_message,
            False,
            artifact.created_at,
            artifact.updated_at,
            entity_label="report_artifact",
            entity_id=artifact.id,
        )

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Fetch a ReportArtifact by ID.

        Args:
            report_id: Canonical rep_<uuid7_hex> report artifact identifier.

        Returns:
            Hydrated ReportArtifact instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report_id.
        """
        report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        row = await self._conn.fetchrow(_GET_REPORT_ARTIFACT_SQL, report_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_report_artifact_row(row)

    async def seed_collection_batch(self, collection_name: str, items: Sequence[BaseModel]) -> int:
        """Idempotently upsert a validated batch of domain entities into PostgreSQL 19.

        Args:
            collection_name: Canonical seed collection or table name.
            items: Sequence of validated Pydantic BaseModel instances.

        Returns:
            Number of rows upserted.

        Raises:
            AppException: With VALIDATION_FAILED if collection_name or item type is unsupported,
                or STORAGE_ACCESS_FAILED if a database error occurs.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            msg = f"Unsupported seed collection '{collection_name}'."
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        count = 0
        for item in items:
            if table_name == "organizations" and isinstance(item, Organization):
                await self.upsert_organization(item)
            elif table_name == "users" and isinstance(item, User):
                await self.upsert_user(item)
            elif table_name == "system_configs" and isinstance(
                item, (SystemConfigModelRegistry, SystemConfigMCPGateways)
            ):
                await self.upsert_system_config(item)
            elif table_name == "prompt_blocks" and isinstance(
                item, (MatrixPromptBlock, SystemRulePromptBlock, PersonaPromptBlock, ProtocolPromptBlock)
            ):
                await self.upsert_prompt_block(item)
            elif table_name == "steps" and isinstance(item, Step):
                await self.upsert_step(item)
            elif table_name == "workflows" and isinstance(item, Workflow):
                await self.upsert_workflow(item)
            elif table_name == "output_profiles" and isinstance(item, OutputProfile):
                await self.upsert_output_profile(item)
            elif table_name == "executions" and isinstance(item, ExecutionRecord):
                await self.save_execution(item)
            elif table_name == "report_artifacts" and isinstance(item, ReportArtifact):
                await self.upsert_report_artifact(item)
            elif table_name == "report_binaries" and isinstance(item, ReportBinaryPayloadDTO):
                await self.save_report_binary(item)
            else:
                msg = f"Item type '{type(item).__name__}' does not match target table '{table_name}'."
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            count += 1
        return count

    async def verify_seed_table_counts(self, expected_counts: Mapping[str, int]) -> dict[str, int]:
        """Verify row counts across the 10 core PostgreSQL 19 tables via SELECT count(*).

        Args:
            expected_counts: Mapping of collection/table name to minimum expected row count.

        Returns:
            Dictionary mapping canonical table name to actual row count in PostgreSQL 19.

        Raises:
            AppException: With VALIDATION_FAILED if expected_counts references an unknown table,
                or STORAGE_ACCESS_FAILED if any table fails query execution or has fewer rows than expected.
        """
        actual_counts: dict[str, int] = {}
        for table_name in CANONICAL_SEED_TABLES:
            sql = f"SELECT count(*) AS row_count FROM {table_name}"
            try:
                row = await self._conn.fetchrow(sql, timeout=self.command_timeout_seconds)
            except Exception as exc:
                if isinstance(exc, AppException):
                    raise
                msg = f"Failed to verify row count for table '{table_name}': {exc}"
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": table_name},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                ) from exc

            if row is None:
                row_count = 0
            else:
                row_count = int(str(row["row_count"]))
            actual_counts[table_name] = row_count

        for key, min_expected in expected_counts.items():
            target_table = _COLLECTION_TO_TABLE_MAP[key] if key in _COLLECTION_TO_TABLE_MAP else key
            if target_table not in actual_counts:
                msg = f"Unknown table '{target_table}' in verify_seed_table_counts."
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            if actual_counts[target_table] < min_expected:
                msg = (
                    f"Seed count verification failed for table '{target_table}': "
                    f"expected >= {min_expected}, got {actual_counts[target_table]}."
                )
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": target_table},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                )

        return actual_counts

    async def list_collection_documents(self, collection_name: str) -> list[dict[str, JsonValue]]:
        """List all documents from a canonical PostgreSQL 19 table as JSON-compatible dictionaries.

        Args:
            collection_name: Canonical collection or table name.

        Returns:
            List of serialized document dictionaries from the mapped table.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return []
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        if table_name == "organizations":
            rows = await self._conn.fetch(_LIST_ORGANIZATIONS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_organization_row(r).model_dump(mode="json") for r in rows]
        if table_name == "users":
            rows = await self._conn.fetch(_LIST_USERS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_user_row(r).model_dump(mode="json") for r in rows]
        if table_name == "system_configs":
            rows = await self._conn.fetch(_LIST_SYSTEM_CONFIGS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_system_config_row(r).model_dump(mode="json") for r in rows]
        if table_name == "prompt_blocks":
            rows = await self._conn.fetch(_LIST_PROMPT_BLOCKS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_prompt_block_row(r).model_dump(mode="json") for r in rows]
        if table_name == "steps":
            rows = await self._conn.fetch(_LIST_STEPS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_step_row(r).model_dump(mode="json") for r in rows]
        if table_name == "workflows":
            rows = await self._conn.fetch(_LIST_WORKFLOWS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_workflow_row(r).model_dump(mode="json") for r in rows]
        if table_name == "output_profiles":
            rows = await self._conn.fetch(_LIST_OUTPUT_PROFILES_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_output_profile_row(r).model_dump(mode="json") for r in rows]
        if table_name == "executions":
            rows = await self._conn.fetch(_LIST_EXECUTIONS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_execution_row(r).model_dump(mode="json") for r in rows]
        if table_name == "report_artifacts":
            rows = await self._conn.fetch(_LIST_REPORT_ARTIFACTS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_report_artifact_row(r).model_dump(mode="json") for r in rows]
        return []

    async def get_collection_document(self, collection_name: str, doc_id: str) -> dict[str, JsonValue] | None:
        """Fetch a single document by ID from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.

        Returns:
            Serialized document dictionary if found and valid, or None.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return None
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        entity: BaseModel | None = None
        try:
            if table_name == "organizations":
                entity = await self.get_organization(doc_id)
            elif table_name == "users":
                entity = await self.get_user(doc_id)
            elif table_name == "system_configs":
                entity = await self.get_system_config(doc_id)
            elif table_name == "prompt_blocks":
                entity = await self.get_prompt_block(doc_id)
            elif table_name == "steps":
                entity = await self.get_step(doc_id)
            elif table_name == "workflows":
                entity = await self.get_workflow(doc_id)
            elif table_name == "output_profiles":
                entity = await self.get_output_profile(doc_id)
            elif table_name == "executions":
                entity = await self.get_execution(doc_id)
            elif table_name == "report_artifacts":
                entity = await self.get_report_artifact(doc_id)
        except AppException:
            return None
        if entity is None:
            return None
        return entity.model_dump(mode="json")

    async def upsert_collection_document(
        self, collection_name: str, doc_id: str, data: Mapping[str, JsonValue]
    ) -> bool:
        """Validate and upsert a document dictionary into its canonical PostgreSQL 19 table if schema-valid.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.
            data: Raw document dictionary to validate and persist.

        Returns:
            True if the document validated against the table's domain schema and was persisted, else False.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return False
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        payload = {k: v for k, v in data.items()}
        payload["id"] = doc_id
        try:
            if table_name == "organizations":
                await self.upsert_organization(Organization.model_validate(payload, strict=False))
                return True
            if table_name == "users":
                await self.upsert_user(User.model_validate(payload, strict=False))
                return True
            if table_name == "system_configs":
                if "type" in payload and payload["type"] == "mcp_gateways":
                    await self.upsert_system_config(SystemConfigMCPGateways.model_validate(payload, strict=False))
                else:
                    await self.upsert_system_config(SystemConfigModelRegistry.model_validate(payload, strict=False))
                return True
            if table_name == "prompt_blocks":
                block = PromptBlockAdapter.validate_python(payload, strict=False)
                await self.upsert_prompt_block(block)
                return True
            if table_name == "steps":
                await self.upsert_step(Step.model_validate(payload, strict=False))
                return True
            if table_name == "workflows":
                await self.upsert_workflow(Workflow.model_validate(payload, strict=False))
                return True
            if table_name == "output_profiles":
                await self.upsert_output_profile(OutputProfile.model_validate(payload, strict=False))
                return True
            if table_name == "executions":
                await self.save_execution(ExecutionRecord.model_validate(payload, strict=False))
                return True
            if table_name == "report_artifacts":
                await self.upsert_report_artifact(ReportArtifact.model_validate(payload, strict=False))
                return True
        except ValueError, KeyError, TypeError, AppException:
            return False
        return False

    async def delete_collection_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a row by ID from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.

        Returns:
            True if a row was deleted, else False.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return False
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        if table_name not in _TABLE_TO_ENTITY_PREFIX:
            return False
        try:
            doc_uuid = (
                _ROOT_SYSTEM_ORG_UUID7
                if table_name == "organizations" and doc_id == "org_system000000"
                else parse_prefixed_uuid7(doc_id, _TABLE_TO_ENTITY_PREFIX[table_name])
            )
        except AppException:
            return False
        status_str = await self._conn.execute(
            f"DELETE FROM {table_name} WHERE id = $1::uuid",
            doc_uuid,
            timeout=self.command_timeout_seconds,
        )
        return status_str.endswith(" 1")

    async def clear_collection_documents(self, collection_name: str) -> None:
        """Delete all rows from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        await self._conn.execute(f"DELETE FROM {table_name}", timeout=self.command_timeout_seconds)
