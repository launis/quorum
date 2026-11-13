-- PostgreSQL 19 Sovereign Zero-ORM Schema (Closed 18-Table Topology)
-- Enforces RFC 9562 native uuidv7(), VIRTUAL generated timestamps, extended statistics,
-- lz4 TOAST compression, Flat FinOps columns, and 1:1 Pydantic V2 Domain DTO parity.

SET default_toast_compression = 'lz4';

-- Automatic One-Way Pre-Production Cutover: Drop pre-cutover tables when legacy system_configs
-- or legacy TEXT primary key schema exists on organizations so all tables recreate cleanly.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'system_configs'
    ) THEN
        DROP TABLE IF EXISTS
            report_binaries, report_artifacts, quorum_edges, quorum_nodes,
            execution_assignments, executions,
            workflow_step_refs, step_criteria_blocks, output_profiles,
            workflows, steps, task_briefs, prompt_blocks,
            tenant_secrets, mcp_gateways, model_registries, system_configs,
            audit_logs, usage_records, invitations, users, organizations
        CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'organizations'
          AND column_name = 'id'
          AND data_type = 'text'
    ) THEN
        DROP TABLE IF EXISTS
            audit_logs,
            usage_records,
            execution_assignments,
            task_briefs,
            tenant_secrets,
            invitations,
            dependency_edges,
            proposition_nodes,
            report_binaries,
            report_artifacts,
            executions,
            output_profiles,
            workflows,
            steps,
            prompt_blocks,
            mcp_gateways,
            model_registries,
            system_configs,
            users,
            organizations
        CASCADE;
    END IF;
END $$;

-- 1. Organizations (Tenant & Billing Root)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    tier TEXT NOT NULL,
    contact_email TEXT,
    billing_id TEXT,
    subscription_status TEXT NOT NULL,
    quota_limit NUMERIC(18, 4) NOT NULL DEFAULT 0.0,
    tpm_limit BIGINT NOT NULL CHECK (tpm_limit >= 1000),
    rpm_limit INTEGER NOT NULL CHECK (rpm_limit >= 1),
    allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb,
    CONSTRAINT enforce_organization_uuidv7 CHECK (uuid_extract_version(id) = 7)
);
-- Ensure allowed_email_domains exists on pre-existing organizations tables
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 2. Users (Identity & RBAC)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT,
    firebase_uid VARCHAR(128) UNIQUE,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    role TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    language TEXT NOT NULL,
    theme_mode TEXT NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    created_by TEXT,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT enforce_user_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_user_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);
-- Ensure firebase_uid and deleted_at exist on pre-existing users tables
ALTER TABLE users ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 3. Model Registries (Flattened Cognitive Tier Model Configurations)
CREATE TABLE IF NOT EXISTS model_registries (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    slug TEXT,
    name TEXT NOT NULL,
    default_provider TEXT NOT NULL,
    tier_definitions JSONB NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);

-- 4. MCP Gateways (External MCP Server & Tool Registries)
CREATE TABLE IF NOT EXISTS mcp_gateways (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    endpoint_url TEXT NOT NULL,
    transport_type TEXT NOT NULL,
    auth_type TEXT NOT NULL,
    auth_env_var TEXT,
    auth_header_name TEXT,
    timeout_seconds INTEGER NOT NULL CHECK (timeout_seconds >= 1 AND timeout_seconds <= 300),
    tools JSONB NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_mcp_gateway_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_mcp_gateways_org_id ON mcp_gateways(organization_id);

-- 4. Prompt Blocks (Polymorphic Matrix, SystemRule, Persona & Protocol Blocks)
CREATE TABLE IF NOT EXISTS prompt_blocks (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    label JSONB NOT NULL,
    description JSONB NOT NULL,
    output_extensions JSONB NOT NULL DEFAULT '[]'::jsonb,
    theory_grounding JSONB,
    category_id TEXT NOT NULL,
    type TEXT NOT NULL,
    is_evaluative BOOLEAN NOT NULL DEFAULT FALSE,
    allow_decimals BOOLEAN NOT NULL DEFAULT FALSE,
    allow_contextual_override BOOLEAN NOT NULL DEFAULT FALSE,
    is_lightweight_protocol BOOLEAN NOT NULL DEFAULT FALSE,
    target_input_key TEXT,
    ai_description TEXT,
    scales JSONB,
    rows JSONB,
    columns JSONB,
    computed_min INTEGER,
    computed_max INTEGER,
    instruction_text TEXT,
    role_enforcement TEXT,
    tone_directives JSONB DEFAULT '[]'::jsonb,
    protocol_instructions TEXT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_prompt_block_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_prompt_block_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);

-- 5. Steps (Cognitive Modules & Step-Level MCP Tool Parameter Overrides)
CREATE TABLE IF NOT EXISTS steps (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    name JSONB NOT NULL,
    description JSONB,
    type TEXT NOT NULL DEFAULT 'llm',
    hook TEXT,
    role_block_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL,
    extraction_protocol_block_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL,
    execution_persona_block_id UUID REFERENCES prompt_blocks(id) ON DELETE SET NULL,
    criteria_block_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    pre_hooks JSONB NOT NULL DEFAULT '[]'::jsonb,
    post_hooks JSONB NOT NULL DEFAULT '[]'::jsonb,
    safety TEXT NOT NULL DEFAULT 'safe',
    allowed_mcp_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    mcp_tool_params JSONB NOT NULL DEFAULT '{}'::jsonb,
    cognitive_tier TEXT,
    expected_inputs JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_system_core BOOLEAN NOT NULL DEFAULT FALSE,
    engine_type TEXT NOT NULL DEFAULT 'prompt',
    zone TEXT NOT NULL DEFAULT 'zone_b',
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_step_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_step_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_step_role_block_uuidv7 CHECK (uuid_extract_version(role_block_id) = 7),
    CONSTRAINT enforce_step_protocol_block_uuidv7 CHECK (uuid_extract_version(extraction_protocol_block_id) = 7),
    CONSTRAINT enforce_step_persona_block_uuidv7 CHECK (uuid_extract_version(execution_persona_block_id) = 7)
);

-- 6. Workflows (DAG Orchestrator Definitions)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    name JSONB NOT NULL,
    description JSONB NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    default_profile_id UUID,
    mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE RESTRICT,
    model_registry_id UUID NOT NULL REFERENCES model_registries(id) ON DELETE RESTRICT,
    default_strictness_level INTEGER NOT NULL DEFAULT 50 CHECK (default_strictness_level >= 0 AND default_strictness_level <= 100),
    default_lexical_strictness_level INTEGER NOT NULL DEFAULT 50 CHECK (default_lexical_strictness_level >= 0 AND default_lexical_strictness_level <= 100),
    security_penalty DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    post_hoc_penalty DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    passivity_penalty DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    enable_contextual_overrides BOOLEAN NOT NULL DEFAULT FALSE,
    enable_semantic_smoothing BOOLEAN NOT NULL DEFAULT FALSE,
    enable_eager_anonymization BOOLEAN NOT NULL DEFAULT FALSE,
    system_audit_trail BOOLEAN NOT NULL DEFAULT FALSE,
    expected_inputs JSONB NOT NULL DEFAULT '[]'::jsonb,
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    historical_context_mode TEXT NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_workflow_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_workflow_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_workflow_default_profile_uuidv7 CHECK (uuid_extract_version(default_profile_id) = 7),
    CONSTRAINT enforce_workflow_mcp_gateway_uuidv7 CHECK (uuid_extract_version(mcp_gateway_id) = 7),
    CONSTRAINT enforce_workflow_model_registry_uuidv7 CHECK (uuid_extract_version(model_registry_id) = 7)
);

-- 7. Output Profiles (SDUI Presentation & Synthesis Recipes)
CREATE TABLE IF NOT EXISTS output_profiles (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    name JSONB NOT NULL,
    description JSONB,
    user_role_label JSONB,
    custom_preface JSONB,
    language TEXT,
    tone_instruction TEXT,
    executive_summary_directive TEXT,
    matrix_1d_synthesis_directive TEXT,
    matrix_2d_synthesis_directive TEXT,
    matrix_3d_synthesis_directive TEXT,
    matrix_text_synthesis_directive TEXT,
    row_explanation_directive TEXT,
    xai_synthesis_directive TEXT,
    variance_synthesis_directive TEXT,
    visible_metadata JSONB NOT NULL DEFAULT '[]'::jsonb,
    matrix_visible_columns JSONB NOT NULL DEFAULT '[]'::jsonb,
    visible_block_extensions JSONB NOT NULL DEFAULT '[]'::jsonb,
    visible_workflow_extensions JSONB NOT NULL DEFAULT '[]'::jsonb,
    max_extension_items INTEGER NOT NULL DEFAULT 3,
    display_scale TEXT NOT NULL DEFAULT 'original',
    custom_scale_min DOUBLE PRECISION,
    custom_scale_max DOUBLE PRECISION,
    synthesis_length_constraint INTEGER,
    row_explanation_length_constraint INTEGER,
    xai_length_constraint INTEGER,
    variance_length_constraint INTEGER,
    matrix_graph_length_constraint INTEGER,
    max_quotes_per_matrix INTEGER,
    max_unmet_criteria INTEGER,
    target_block_order JSONB NOT NULL DEFAULT '[]'::jsonb,
    matrix_synthesis_groups JSONB NOT NULL DEFAULT '[]'::jsonb,
    content_blocks JSONB NOT NULL DEFAULT '[]'::jsonb,
    show_sources_summary_box BOOLEAN NOT NULL DEFAULT TRUE,
    sources_display_mode TEXT NOT NULL DEFAULT 'verified_evidence',
    variance_target_block TEXT,
    user_role_target_block TEXT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_output_profile_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_output_profile_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_output_profile_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);

-- 8. Executions (Analytical Runs, Flat FinOps Columns & lz4-Compressed Trace Events)
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    workflow_version INTEGER NOT NULL DEFAULT 1,
    state_version INTEGER NOT NULL DEFAULT 1,
    active_profile_id UUID REFERENCES output_profiles(id) ON DELETE SET NULL,
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    target_locale TEXT NOT NULL,
    progress INTEGER CHECK (progress >= 0 AND progress <= 100),
    status_message TEXT,
    raw_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    frozen_context JSONB,
    frozen_context_storage_path TEXT,
    pdf_report_path TEXT,
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    step_states JSONB NOT NULL DEFAULT '{}'::jsonb,
    profile_syntheses JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_identity_manifest JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_trace JSONB NOT NULL DEFAULT '[]'::jsonb,
    execution_trace_storage_path TEXT,
    context_variables JSONB NOT NULL DEFAULT '{}'::jsonb,
    context_variables_storage_path TEXT,
    is_resumable BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_tokens BIGINT NOT NULL DEFAULT 0,
    completion_tokens BIGINT NOT NULL DEFAULT 0,
    cached_tokens BIGINT NOT NULL DEFAULT 0,
    reasoning_tokens BIGINT NOT NULL DEFAULT 0,
    cumulative_synthesis_tokens BIGINT NOT NULL DEFAULT 0,
    dag_cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0.000000,
    cumulative_synthesis_cost NUMERIC(10, 6) NOT NULL DEFAULT 0.000000,
    cost_estimate NUMERIC(10, 6) NOT NULL DEFAULT 0.000000,
    models_used JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_summary JSONB,
    metadata JSONB,
    duration_ms BIGINT NOT NULL DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    created_by TEXT,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    CONSTRAINT enforce_execution_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_execution_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_execution_active_profile_uuidv7 CHECK (uuid_extract_version(active_profile_id) = 7),
    CONSTRAINT enforce_execution_output_profile_uuidv7 CHECK (uuid_extract_version(output_profile_id) = 7),
    CONSTRAINT enforce_execution_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);
ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version INTEGER NOT NULL DEFAULT 1;

-- 9. Report Artifacts (Materialized Report Metadata)
CREATE TABLE IF NOT EXISTS report_artifacts (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    execution_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    profile_id UUID NOT NULL REFERENCES output_profiles(id) ON DELETE RESTRICT,
    locale TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    storage_paths JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    custom_preface_md TEXT,
    error_message TEXT,
    has_pdf BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT enforce_report_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_report_execution_uuidv7 CHECK (uuid_extract_version(execution_id) = 7),
    CONSTRAINT enforce_report_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_report_profile_uuidv7 CHECK (uuid_extract_version(profile_id) = 7)
);

-- 10. Report Binaries (Sidecar BYTEA TOAST Table with lz4 Compression)
CREATE TABLE IF NOT EXISTS report_binaries (
    report_id UUID PRIMARY KEY REFERENCES report_artifacts(id) ON DELETE CASCADE,
    mime_type TEXT NOT NULL DEFAULT 'application/pdf',
    pdf_bytes BYTEA NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT enforce_report_binary_uuidv7 CHECK (uuid_extract_version(report_id) = 7)
);

-- 11. Quorum Nodes (Toulmin & SCM Proposition Graph Nodes with RFC 9562 uuidv7)
CREATE TABLE IF NOT EXISTS quorum_nodes (
    node_id UUID PRIMARY KEY DEFAULT uuidv7(),
    run_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    local_key TEXT,
    node_type TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(node_id)) VIRTUAL,
    CONSTRAINT enforce_node_uuidv7 CHECK (uuid_extract_version(node_id) = 7),
    CONSTRAINT enforce_run_uuidv7 CHECK (uuid_extract_version(run_id) = 7),
    CONSTRAINT uq_quorum_nodes_run_local_key UNIQUE (run_id, local_key)
);

-- 12. Quorum Edges (Causal & Toulmin Dependency Edges with Self-Loop Prevention)
CREATE TABLE IF NOT EXISTS quorum_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuidv7(),
    run_id UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES quorum_nodes(node_id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES quorum_nodes(node_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    causal_weight DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (causal_weight >= -1.0 AND causal_weight <= 1.0),
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(edge_id)) VIRTUAL,
    CONSTRAINT enforce_edge_uuidv7 CHECK (uuid_extract_version(edge_id) = 7),
    CONSTRAINT enforce_edge_run_uuidv7 CHECK (uuid_extract_version(run_id) = 7),
    CONSTRAINT no_self_loops CHECK (source_id <> target_id),
    CONSTRAINT uq_quorum_edges_run_src_tgt_rel UNIQUE (run_id, source_id, target_id, relation_type)
);

-- 13. Invitations (One-Time Cryptographic Organization Onboarding Tokens)
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    invited_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_invitation_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_invitation_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_invitation_invited_by_uuidv7 CHECK (uuid_extract_version(invited_by) = 7)
);

-- 14. Tenant Secrets (BYOK Envelope KMS & Cloud Secret Manager Metadata)
CREATE TABLE IF NOT EXISTS tenant_secrets (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE,
    scope TEXT NOT NULL,
    target_identifier VARCHAR(128) NOT NULL,
    storage_mode TEXT NOT NULL,
    secret_manager_version_uri VARCHAR(512),
    encrypted_dek BYTEA,
    ciphertext BYTEA,
    nonce BYTEA,
    kek_version VARCHAR(128) NOT NULL,
    masked_hint VARCHAR(32) NOT NULL,
    updated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT enforce_tenant_secret_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_tenant_secret_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_tenant_secret_mcp_gateway_uuidv7 CHECK (uuid_extract_version(mcp_gateway_id) = 7),
    CONSTRAINT enforce_tenant_secret_updated_by_uuidv7 CHECK (uuid_extract_version(updated_by) = 7),
    CONSTRAINT chk_tenant_secrets_mcp_gateway_scope CHECK (
        (scope = 'mcp_gateway' AND mcp_gateway_id IS NOT NULL)
        OR (scope IN ('llm_provider', 'telemetry') AND mcp_gateway_id IS NULL)
    ),
    CONSTRAINT uq_tenant_secrets_org_scope_target UNIQUE (organization_id, scope, target_identifier)
);
ALTER TABLE tenant_secrets ADD COLUMN IF NOT EXISTS mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_org_id ON tenant_secrets(organization_id);
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_mcp_gateway_id ON tenant_secrets(mcp_gateway_id);

-- 15. Task Briefs (Reusable Human-Facing Task Briefs & Case Descriptions)
CREATE TABLE IF NOT EXISTS task_briefs (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    label JSONB NOT NULL,
    description JSONB NOT NULL,
    instruction_text TEXT NOT NULL,
    source_url TEXT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_task_brief_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_task_brief_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);

-- 16. Execution Assignments (Pre-Configured Task Assignments & Cohort Batches)
CREATE TABLE IF NOT EXISTS execution_assignments (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    batch_id UUID,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_email TEXT NOT NULL,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    invited_role TEXT NOT NULL DEFAULT 'MEMBER',
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE SET NULL,
    task_brief_id UUID REFERENCES task_briefs(id) ON DELETE SET NULL,
    target_locale TEXT NOT NULL,
    locked_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    assignee_input_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    draft_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    result_visibility TEXT NOT NULL DEFAULT 'confirmation_only',
    hard_deadline_at TIMESTAMPTZ NOT NULL,
    relative_duration_seconds INTEGER CHECK (relative_duration_seconds IS NULL OR relative_duration_seconds >= 60),
    activated_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_assignment_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_assignment_batch_uuidv7 CHECK (batch_id IS NULL OR uuid_extract_version(batch_id) = 7),
    CONSTRAINT enforce_assignment_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_assignment_assigned_user_uuidv7 CHECK (assigned_user_id IS NULL OR uuid_extract_version(assigned_user_id) = 7),
    CONSTRAINT enforce_assignment_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_assignment_output_profile_uuidv7 CHECK (output_profile_id IS NULL OR uuid_extract_version(output_profile_id) = 7),
    CONSTRAINT enforce_assignment_task_brief_uuidv7 CHECK (task_brief_id IS NULL OR uuid_extract_version(task_brief_id) = 7),
    CONSTRAINT enforce_assignment_execution_uuidv7 CHECK (execution_id IS NULL OR uuid_extract_version(execution_id) = 7),
    CONSTRAINT enforce_assignment_created_by_uuidv7 CHECK (uuid_extract_version(created_by) = 7)
);
ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_id UUID REFERENCES task_briefs(id) ON DELETE SET NULL;
DO $$
DECLARE
    fk_name TEXT;
BEGIN
    UPDATE execution_assignments
    SET task_brief_id = NULL
    WHERE task_brief_id IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM task_briefs tb WHERE tb.id = execution_assignments.task_brief_id);

    FOR fk_name IN
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_class confrel ON confrel.oid = con.confrelid
        WHERE rel.relname = 'execution_assignments'
          AND con.contype = 'f'
          AND confrel.relname = 'prompt_blocks'
    LOOP
        EXECUTE format('ALTER TABLE execution_assignments DROP CONSTRAINT IF EXISTS %I', fk_name);
    END LOOP;

    DELETE FROM prompt_blocks WHERE category_id NOT IN ('matrix', 'system_rule', 'runtime_variables', 'persona', 'protocol');

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_class confrel ON confrel.oid = con.confrelid
        WHERE rel.relname = 'execution_assignments'
          AND con.contype = 'f'
          AND confrel.relname = 'task_briefs'
    ) THEN
        ALTER TABLE execution_assignments
            ADD CONSTRAINT execution_assignments_task_brief_id_fkey
            FOREIGN KEY (task_brief_id) REFERENCES task_briefs(id) ON DELETE SET NULL;
    END IF;
END $$;

-- 17. Audit Logs (Append-Only Compliance Ledger)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_created ON audit_logs(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_execution_id ON audit_logs(execution_id);

-- 18. Usage Records (Append-Only FinOps Ledger)
CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    model_name TEXT NOT NULL,
    prompt_tokens BIGINT NOT NULL DEFAULT 0 CHECK (prompt_tokens >= 0),
    completion_tokens BIGINT NOT NULL DEFAULT 0 CHECK (completion_tokens >= 0),
    cached_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cached_tokens >= 0),
    reasoning_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reasoning_tokens >= 0),
    cache_creation_input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cache_creation_input_tokens >= 0),
    latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),
    finish_reason TEXT,
    system_fingerprint TEXT,
    cost_usd NUMERIC(14, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    estimated_savings_usd NUMERIC(14, 6) NOT NULL DEFAULT 0 CHECK (estimated_savings_usd >= 0),
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
CREATE INDEX IF NOT EXISTS idx_usage_records_org_created ON usage_records(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_execution_id ON usage_records(execution_id);

-- Dynamic PG 18+/19 VIRTUAL vs PG 17 STORED Timestamp Guard
DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 180000 THEN
        -- Native VIRTUAL generated columns active on PostgreSQL 18+ and 19
        NULL;
    ELSE
        ALTER TABLE organizations DROP COLUMN IF EXISTS created_at;
        ALTER TABLE organizations ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE users DROP COLUMN IF EXISTS created_at;
        ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE model_registries DROP COLUMN IF EXISTS created_at;
        ALTER TABLE model_registries ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE mcp_gateways DROP COLUMN IF EXISTS created_at;
        ALTER TABLE mcp_gateways ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE prompt_blocks DROP COLUMN IF EXISTS created_at;
        ALTER TABLE prompt_blocks ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE task_briefs DROP COLUMN IF EXISTS created_at;
        ALTER TABLE task_briefs ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE steps DROP COLUMN IF EXISTS created_at;
        ALTER TABLE steps ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE workflows DROP COLUMN IF EXISTS created_at;
        ALTER TABLE workflows ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE output_profiles DROP COLUMN IF EXISTS created_at;
        ALTER TABLE output_profiles ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE audit_logs DROP COLUMN IF EXISTS created_at;
        ALTER TABLE audit_logs ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE usage_records DROP COLUMN IF EXISTS created_at;
        ALTER TABLE usage_records ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE quorum_nodes DROP COLUMN IF EXISTS created_at;
        ALTER TABLE quorum_nodes ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(node_id)) STORED;
        ALTER TABLE quorum_edges DROP COLUMN IF EXISTS created_at;
        ALTER TABLE quorum_edges ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(edge_id)) STORED;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_task_briefs_organization_id ON task_briefs (organization_id);

-- PostgreSQL 19 Extended Multi-Column Statistics on VIRTUAL Generated Columns
DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 190000 THEN
        CREATE STATISTICS IF NOT EXISTS stat_quorum_nodes_run_created ON run_id, created_at FROM quorum_nodes;
        CREATE STATISTICS IF NOT EXISTS stat_quorum_edges_run_created ON run_id, created_at FROM quorum_edges;
    END IF;
END $$;

-- B-Tree & GIN Indexes for Single-Round Wave Materialization & CTE Traversal
CREATE INDEX IF NOT EXISTS idx_quorum_nodes_run_type ON quorum_nodes (run_id, node_type);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_run_src_tgt ON quorum_edges (run_id, source_id, target_id);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_run_target ON quorum_edges (run_id, target_id);

-- Idempotent JSONB Scalar String Unwrapping & GlobalContextVarsDTO Initiator Normalization
UPDATE executions
SET
    raw_inputs = CASE WHEN jsonb_typeof(raw_inputs) = 'string' THEN (raw_inputs #>> '{}')::jsonb ELSE raw_inputs END,
    frozen_context = CASE WHEN frozen_context IS NOT NULL AND jsonb_typeof(frozen_context) = 'string' THEN (frozen_context #>> '{}')::jsonb ELSE frozen_context END,
    steps = CASE WHEN jsonb_typeof(steps) = 'string' THEN (steps #>> '{}')::jsonb ELSE steps END,
    step_states = CASE WHEN jsonb_typeof(step_states) = 'string' THEN (step_states #>> '{}')::jsonb ELSE step_states END,
    profile_syntheses = CASE WHEN jsonb_typeof(profile_syntheses) = 'string' THEN (profile_syntheses #>> '{}')::jsonb ELSE profile_syntheses END,
    source_identity_manifest = CASE WHEN jsonb_typeof(source_identity_manifest) = 'string' THEN (source_identity_manifest #>> '{}')::jsonb ELSE source_identity_manifest END,
    execution_trace = CASE WHEN jsonb_typeof(execution_trace) = 'string' THEN (execution_trace #>> '{}')::jsonb ELSE execution_trace END,
    context_variables = CASE WHEN jsonb_typeof(context_variables) = 'string' THEN (context_variables #>> '{}')::jsonb ELSE context_variables END,
    models_used = CASE WHEN jsonb_typeof(models_used) = 'string' THEN (models_used #>> '{}')::jsonb ELSE models_used END,
    execution_summary = CASE WHEN execution_summary IS NOT NULL AND jsonb_typeof(execution_summary) = 'string' THEN (execution_summary #>> '{}')::jsonb ELSE execution_summary END,
    metadata = CASE WHEN metadata IS NOT NULL AND jsonb_typeof(metadata) = 'string' THEN (metadata #>> '{}')::jsonb ELSE metadata END
WHERE
    jsonb_typeof(raw_inputs) = 'string'
    OR (frozen_context IS NOT NULL AND jsonb_typeof(frozen_context) = 'string')
    OR jsonb_typeof(steps) = 'string'
    OR jsonb_typeof(step_states) = 'string'
    OR jsonb_typeof(profile_syntheses) = 'string'
    OR jsonb_typeof(source_identity_manifest) = 'string'
    OR jsonb_typeof(execution_trace) = 'string'
    OR jsonb_typeof(context_variables) = 'string'
    OR jsonb_typeof(models_used) = 'string'
    OR (execution_summary IS NOT NULL AND jsonb_typeof(execution_summary) = 'string')
    OR (metadata IS NOT NULL AND jsonb_typeof(metadata) = 'string');

UPDATE executions
SET metadata = jsonb_set(
    metadata,
    '{global_context_vars}',
    CASE
        WHEN metadata->'global_context_vars'->>'_sys_initiator_id' IS NOT NULL THEN
            ((metadata->'global_context_vars') - '_sys_initiator_id')
            || jsonb_build_object('initiator_id', metadata->'global_context_vars'->'_sys_initiator_id')
        ELSE
            (metadata->'global_context_vars') - '_sys_initiator_id'
    END
)
WHERE metadata IS NOT NULL
  AND jsonb_typeof(metadata) = 'object'
  AND jsonb_typeof(metadata->'global_context_vars') = 'object'
  AND (metadata->'global_context_vars') ? '_sys_initiator_id';

