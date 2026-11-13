-- PostgreSQL 19 Sovereign Zero-ORM Schema (Closed 21-Table Topology)
-- Enforces RFC 9562 native uuidv7(), VIRTUAL generated timestamps, extended statistics,
-- lz4 TOAST compression, Flat FinOps columns, junction referential integrity, and 1:1 Pydantic V2 Domain DTO parity.

SET default_toast_compression = 'lz4';

-- Automatic One-Way Pre-Production Cutover: Drop pre-cutover tables when legacy system_configs,
-- legacy TEXT primary keys, or pre-junction steps.criteria_block_ids columns exist so all 21 tables recreate cleanly.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'system_configs'
    ) OR EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'organizations'
          AND column_name = 'id'
          AND data_type = 'text'
    ) OR EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'steps'
          AND column_name = 'criteria_block_ids'
    ) THEN
        DROP TABLE IF EXISTS
            report_binaries,
            report_artifacts,
            quorum_edges,
            quorum_nodes,
            dependency_edges,
            proposition_nodes,
            execution_assignments,
            executions,
            workflow_step_refs,
            step_criteria_blocks,
            output_profiles,
            workflows,
            steps,
            task_briefs,
            prompt_blocks,
            tenant_secrets,
            mcp_gateways,
            model_registries,
            system_configs,
            audit_logs,
            usage_records,
            invitations,
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
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS allowed_email_domains JSONB NOT NULL DEFAULT '[]'::jsonb;

-- 2. Users (Identity & RBAC)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT,
    firebase_uid VARCHAR(128) UNIQUE,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    role TEXT NOT NULL CHECK (role IN ('ROOT', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER')),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    language TEXT NOT NULL,
    theme_mode TEXT NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT enforce_user_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_user_organization_uuidv7 CHECK (organization_id IS NULL OR uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_user_created_by_uuidv7 CHECK (created_by IS NULL OR uuid_extract_version(created_by) = 7)
);
ALTER TABLE users ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON users(created_by);

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

-- 5. Prompt Blocks (Polymorphic Matrix, SystemRule, Persona & Protocol Blocks)
CREATE TABLE IF NOT EXISTS prompt_blocks (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    label JSONB NOT NULL,
    description JSONB NOT NULL,
    output_extensions JSONB NOT NULL DEFAULT '[]'::jsonb,
    theory_grounding JSONB,
    category_id TEXT NOT NULL CHECK (
        category_id IN (
            'matrix',
            'agent_role',
            'system_rule',
            'protocol',
            'runtime_variables',
            'execution_persona'
        )
    ),
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
CREATE INDEX IF NOT EXISTS idx_prompt_blocks_organization_id ON prompt_blocks(organization_id);

-- 6. Cognitive Blueprints (steps)
CREATE TABLE IF NOT EXISTS steps (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name JSONB NOT NULL,
    description JSONB,
    type TEXT NOT NULL DEFAULT 'llm',
    hook TEXT,
    role_block_id UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    extraction_protocol_block_id UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    execution_persona_block_id UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
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
    CONSTRAINT enforce_step_role_block_uuidv7 CHECK (role_block_id IS NULL OR uuid_extract_version(role_block_id) = 7),
    CONSTRAINT enforce_step_protocol_block_uuidv7 CHECK (extraction_protocol_block_id IS NULL OR uuid_extract_version(extraction_protocol_block_id) = 7),
    CONSTRAINT enforce_step_persona_block_uuidv7 CHECK (execution_persona_block_id IS NULL OR uuid_extract_version(execution_persona_block_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_steps_organization_id ON steps(organization_id);
CREATE INDEX IF NOT EXISTS idx_steps_role_block_id ON steps(role_block_id);
CREATE INDEX IF NOT EXISTS idx_steps_extraction_protocol_block_id ON steps(extraction_protocol_block_id);
CREATE INDEX IF NOT EXISTS idx_steps_execution_persona_block_id ON steps(execution_persona_block_id);

-- 7. Blueprint Criteria Block Junction (step_criteria_blocks)
CREATE TABLE IF NOT EXISTS step_criteria_blocks (
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    prompt_block_id UUID NOT NULL REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK (position >= 0),
    PRIMARY KEY (step_id, prompt_block_id),
    CONSTRAINT enforce_scb_step_uuidv7 CHECK (uuid_extract_version(step_id) = 7),
    CONSTRAINT enforce_scb_prompt_block_uuidv7 CHECK (uuid_extract_version(prompt_block_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_step_criteria_blocks_prompt_block_id ON step_criteria_blocks(prompt_block_id);

-- 8. Workflows (DAG Orchestrator Definitions)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    name JSONB NOT NULL,
    description JSONB NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
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
    CONSTRAINT enforce_workflow_default_profile_uuidv7 CHECK (default_profile_id IS NULL OR uuid_extract_version(default_profile_id) = 7),
    CONSTRAINT enforce_workflow_mcp_gateway_uuidv7 CHECK (mcp_gateway_id IS NULL OR uuid_extract_version(mcp_gateway_id) = 7),
    CONSTRAINT enforce_workflow_model_registry_uuidv7 CHECK (uuid_extract_version(model_registry_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_workflows_organization_id ON workflows(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflows_default_profile_id ON workflows(default_profile_id);
CREATE INDEX IF NOT EXISTS idx_workflows_mcp_gateway_id ON workflows(mcp_gateway_id);
CREATE INDEX IF NOT EXISTS idx_workflows_model_registry_id ON workflows(model_registry_id);

-- 9. Workflow Blueprint Reference Junction (workflow_step_refs)
CREATE TABLE IF NOT EXISTS workflow_step_refs (
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE RESTRICT,
    PRIMARY KEY (workflow_id, step_id),
    CONSTRAINT enforce_wsr_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_wsr_step_uuidv7 CHECK (uuid_extract_version(step_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_workflow_step_refs_step_id ON workflow_step_refs(step_id);

-- 10. Output Profiles (SDUI Presentation & Synthesis Recipes)
CREATE TABLE IF NOT EXISTS output_profiles (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
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
    variance_target_block UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    user_role_target_block UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_output_profile_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_output_profile_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_output_profile_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_output_profile_variance_block_uuidv7 CHECK (variance_target_block IS NULL OR uuid_extract_version(variance_target_block) = 7),
    CONSTRAINT enforce_output_profile_user_role_block_uuidv7 CHECK (user_role_target_block IS NULL OR uuid_extract_version(user_role_target_block) = 7)
);
CREATE INDEX IF NOT EXISTS idx_output_profiles_workflow_id ON output_profiles(workflow_id);
CREATE INDEX IF NOT EXISTS idx_output_profiles_organization_id ON output_profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_output_profiles_variance_target_block ON output_profiles(variance_target_block);
CREATE INDEX IF NOT EXISTS idx_output_profiles_user_role_target_block ON output_profiles(user_role_target_block);

-- Deferrable circular Foreign Key from workflows.default_profile_id to output_profiles.id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'workflows_default_profile_id_fkey'
    ) THEN
        ALTER TABLE workflows
            ADD CONSTRAINT workflows_default_profile_id_fkey
            FOREIGN KEY (default_profile_id) REFERENCES output_profiles(id)
            ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

-- 11. Executions (Analytical Runs, Flat FinOps Columns & lz4-Compressed Trace Events)
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
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    CONSTRAINT enforce_execution_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_execution_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_execution_active_profile_uuidv7 CHECK (active_profile_id IS NULL OR uuid_extract_version(active_profile_id) = 7),
    CONSTRAINT enforce_execution_output_profile_uuidv7 CHECK (output_profile_id IS NULL OR uuid_extract_version(output_profile_id) = 7),
    CONSTRAINT enforce_execution_created_by_uuidv7 CHECK (created_by IS NULL OR uuid_extract_version(created_by) = 7),
    CONSTRAINT enforce_execution_organization_uuidv7 CHECK (organization_id IS NULL OR uuid_extract_version(organization_id) = 7)
);
ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version INTEGER NOT NULL DEFAULT 1;
CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_active_profile_id ON executions(active_profile_id);
CREATE INDEX IF NOT EXISTS idx_executions_output_profile_id ON executions(output_profile_id);
CREATE INDEX IF NOT EXISTS idx_executions_created_by ON executions(created_by);
CREATE INDEX IF NOT EXISTS idx_executions_organization_id ON executions(organization_id);
CREATE INDEX IF NOT EXISTS idx_executions_org_id_created ON executions(organization_id, id DESC);

-- 12. Report Artifacts (Materialized Report Metadata)
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
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT enforce_report_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_report_execution_uuidv7 CHECK (uuid_extract_version(execution_id) = 7),
    CONSTRAINT enforce_report_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_report_profile_uuidv7 CHECK (uuid_extract_version(profile_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_report_artifacts_execution_id ON report_artifacts(execution_id);
CREATE INDEX IF NOT EXISTS idx_report_artifacts_workflow_id ON report_artifacts(workflow_id);
CREATE INDEX IF NOT EXISTS idx_report_artifacts_profile_id ON report_artifacts(profile_id);

-- 13. Report Binaries (Sidecar BYTEA TOAST Table with lz4 Compression)
CREATE TABLE IF NOT EXISTS report_binaries (
    report_id UUID PRIMARY KEY REFERENCES report_artifacts(id) ON DELETE CASCADE,
    mime_type TEXT NOT NULL DEFAULT 'application/pdf',
    pdf_bytes BYTEA NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(report_id)) VIRTUAL,
    CONSTRAINT enforce_report_binary_uuidv7 CHECK (uuid_extract_version(report_id) = 7)
);

-- 14. Quorum Nodes (Toulmin & SCM Proposition Graph Nodes with RFC 9562 uuidv7)
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

-- 15. Quorum Edges (Causal & Toulmin Dependency Edges with Self-Loop Prevention)
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

-- 16. Invitations (One-Time Cryptographic Organization Onboarding Tokens)
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
CREATE INDEX IF NOT EXISTS idx_invitations_organization_id ON invitations(organization_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invited_by ON invitations(invited_by);

-- 17. Tenant Secrets (BYOK Envelope KMS & Cloud Secret Manager Metadata)
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
    CONSTRAINT enforce_tenant_secret_mcp_gateway_uuidv7 CHECK (mcp_gateway_id IS NULL OR uuid_extract_version(mcp_gateway_id) = 7),
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
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_updated_by ON tenant_secrets(updated_by);

-- 18. Task Briefs (Reusable Human-Facing Task Briefs & Case Descriptions)
CREATE TABLE IF NOT EXISTS task_briefs (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug TEXT NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    label JSONB NOT NULL,
    description JSONB NOT NULL,
    instruction_text TEXT NOT NULL,
    source_url TEXT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_task_brief_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_task_brief_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7)
);
CREATE INDEX IF NOT EXISTS idx_task_briefs_organization_id ON task_briefs(organization_id);

-- Idempotent Studio Organization Ownership Backfill & ON DELETE CASCADE Enforcement
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM prompt_blocks WHERE organization_id IS NULL)
       OR EXISTS (SELECT 1 FROM task_briefs WHERE organization_id IS NULL)
       OR EXISTS (SELECT 1 FROM steps WHERE organization_id IS NULL)
       OR EXISTS (SELECT 1 FROM workflows WHERE organization_id IS NULL)
       OR EXISTS (SELECT 1 FROM output_profiles WHERE organization_id IS NULL) THEN
        INSERT INTO organizations (
            id, slug, name, is_active, tier, contact_email, billing_id,
            subscription_status, quota_limit, tpm_limit, rpm_limit, allowed_email_domains
        ) VALUES (
            '0195f3a0-0000-7000-8000-000000000001'::uuid,
            'system',
            'System Administration',
            TRUE,
            'enterprise',
            'root@example.com',
            NULL,
            'active',
            999999999.0,
            10000000,
            10000,
            '[]'::jsonb
        ) ON CONFLICT (id) DO NOTHING;

        UPDATE prompt_blocks
        SET organization_id = '0195f3a0-0000-7000-8000-000000000001'::uuid
        WHERE organization_id IS NULL;

        UPDATE task_briefs
        SET organization_id = '0195f3a0-0000-7000-8000-000000000001'::uuid
        WHERE organization_id IS NULL;

        UPDATE steps
        SET organization_id = '0195f3a0-0000-7000-8000-000000000001'::uuid
        WHERE organization_id IS NULL;

        UPDATE workflows
        SET organization_id = '0195f3a0-0000-7000-8000-000000000001'::uuid
        WHERE organization_id IS NULL;

        UPDATE output_profiles
        SET organization_id = '0195f3a0-0000-7000-8000-000000000001'::uuid
        WHERE organization_id IS NULL;
    END IF;

    ALTER TABLE prompt_blocks DROP CONSTRAINT IF EXISTS prompt_blocks_organization_id_fkey;
    ALTER TABLE prompt_blocks
        ADD CONSTRAINT prompt_blocks_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
    ALTER TABLE prompt_blocks DROP CONSTRAINT IF EXISTS enforce_prompt_block_organization_uuidv7;
    ALTER TABLE prompt_blocks
        ADD CONSTRAINT enforce_prompt_block_organization_uuidv7
        CHECK (uuid_extract_version(organization_id) = 7);
    ALTER TABLE prompt_blocks ALTER COLUMN organization_id SET NOT NULL;

    ALTER TABLE steps DROP CONSTRAINT IF EXISTS steps_organization_id_fkey;
    ALTER TABLE steps
        ADD CONSTRAINT steps_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
    ALTER TABLE steps DROP CONSTRAINT IF EXISTS enforce_step_organization_uuidv7;
    ALTER TABLE steps
        ADD CONSTRAINT enforce_step_organization_uuidv7
        CHECK (uuid_extract_version(organization_id) = 7);
    ALTER TABLE steps ALTER COLUMN organization_id SET NOT NULL;

    ALTER TABLE workflows DROP CONSTRAINT IF EXISTS workflows_organization_id_fkey;
    ALTER TABLE workflows
        ADD CONSTRAINT workflows_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
    ALTER TABLE workflows DROP CONSTRAINT IF EXISTS enforce_workflow_organization_uuidv7;
    ALTER TABLE workflows
        ADD CONSTRAINT enforce_workflow_organization_uuidv7
        CHECK (uuid_extract_version(organization_id) = 7);
    ALTER TABLE workflows ALTER COLUMN organization_id SET NOT NULL;

    ALTER TABLE output_profiles DROP CONSTRAINT IF EXISTS output_profiles_organization_id_fkey;
    ALTER TABLE output_profiles
        ADD CONSTRAINT output_profiles_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
    ALTER TABLE output_profiles DROP CONSTRAINT IF EXISTS enforce_output_profile_organization_uuidv7;
    ALTER TABLE output_profiles
        ADD CONSTRAINT enforce_output_profile_organization_uuidv7
        CHECK (uuid_extract_version(organization_id) = 7);
    ALTER TABLE output_profiles ALTER COLUMN organization_id SET NOT NULL;

    ALTER TABLE task_briefs DROP CONSTRAINT IF EXISTS task_briefs_organization_id_fkey;
    ALTER TABLE task_briefs
        ADD CONSTRAINT task_briefs_organization_id_fkey
        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
    ALTER TABLE task_briefs DROP CONSTRAINT IF EXISTS enforce_task_brief_organization_uuidv7;
    ALTER TABLE task_briefs
        ADD CONSTRAINT enforce_task_brief_organization_uuidv7
        CHECK (uuid_extract_version(organization_id) = 7);
    ALTER TABLE task_briefs ALTER COLUMN organization_id SET NOT NULL;
END $$;

-- 19. Execution Assignments (Pre-Configured Task Assignments & Cohort Batches)
CREATE TABLE IF NOT EXISTS execution_assignments (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    batch_id UUID,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_email TEXT NOT NULL,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    invited_role TEXT NOT NULL DEFAULT 'MEMBER' CHECK (invited_role IN ('ROOT', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER')),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE RESTRICT,
    task_brief_id UUID REFERENCES task_briefs(id) ON DELETE RESTRICT,
    task_brief_snapshot JSONB,
    target_locale TEXT NOT NULL,
    locked_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    assignee_input_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    draft_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'activated', 'submitted', 'completed', 'expired', 'revoked')),
    email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (email_delivery_status IN ('pending', 'sent', 'failed')),
    result_visibility TEXT NOT NULL DEFAULT 'confirmation_only' CHECK (result_visibility IN ('confirmation_only', 'full_report_access')),
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
    CONSTRAINT enforce_assignment_created_by_uuidv7 CHECK (uuid_extract_version(created_by) = 7),
    CONSTRAINT enforce_assignment_task_brief_snapshot_parity CHECK ((task_brief_id IS NULL) = (task_brief_snapshot IS NULL))
);
ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_id UUID REFERENCES task_briefs(id) ON DELETE RESTRICT;
ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_snapshot JSONB;
DO $$
BEGIN
    UPDATE execution_assignments ea
    SET task_brief_snapshot = jsonb_build_object(
        'id', 'tbr_' || replace(tb.id::text, '-', ''),
        'label', tb.label,
        'instruction_text', tb.instruction_text,
        'source_url', tb.source_url
    )
    FROM task_briefs tb
    WHERE ea.task_brief_id = tb.id
      AND ea.task_brief_snapshot IS NULL;

    UPDATE execution_assignments ea
    SET task_brief_id = NULL
    WHERE ea.task_brief_id IS NOT NULL
      AND ea.task_brief_snapshot IS NULL;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'enforce_assignment_task_brief_snapshot_parity'
          AND conrelid = 'execution_assignments'::regclass
    ) THEN
        ALTER TABLE execution_assignments
        ADD CONSTRAINT enforce_assignment_task_brief_snapshot_parity
        CHECK ((task_brief_id IS NULL) = (task_brief_snapshot IS NULL));
    END IF;

    ALTER TABLE execution_assignments DROP CONSTRAINT IF EXISTS execution_assignments_workflow_id_fkey;
    ALTER TABLE execution_assignments
        ADD CONSTRAINT execution_assignments_workflow_id_fkey
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE RESTRICT;

    ALTER TABLE execution_assignments DROP CONSTRAINT IF EXISTS execution_assignments_output_profile_id_fkey;
    ALTER TABLE execution_assignments
        ADD CONSTRAINT execution_assignments_output_profile_id_fkey
        FOREIGN KEY (output_profile_id) REFERENCES output_profiles(id) ON DELETE RESTRICT;

    ALTER TABLE execution_assignments DROP CONSTRAINT IF EXISTS execution_assignments_task_brief_id_fkey;
    ALTER TABLE execution_assignments
        ADD CONSTRAINT execution_assignments_task_brief_id_fkey
        FOREIGN KEY (task_brief_id) REFERENCES task_briefs(id) ON DELETE RESTRICT;
END $$;
CREATE INDEX IF NOT EXISTS idx_execution_assignments_organization_id ON execution_assignments(organization_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_assigned_user_id ON execution_assignments(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_workflow_id ON execution_assignments(workflow_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_output_profile_id ON execution_assignments(output_profile_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_task_brief_id ON execution_assignments(task_brief_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_execution_id ON execution_assignments(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_created_by ON execution_assignments(created_by);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_org_created ON execution_assignments(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_batch_id ON execution_assignments(batch_id);

-- 20. Audit Logs (Append-Only Compliance Ledger)
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
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_execution_id ON audit_logs(execution_id);

-- 21. Usage Records (Append-Only FinOps Ledger)
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
CREATE INDEX IF NOT EXISTS idx_usage_records_user_id ON usage_records(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_execution_id ON usage_records(execution_id);

-- Dynamic PG 18+/19 VIRTUAL vs PG 17 STORED Timestamp Guard
DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 180000 THEN
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
        ALTER TABLE executions DROP COLUMN IF EXISTS created_at;
        ALTER TABLE executions ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE report_artifacts DROP COLUMN IF EXISTS created_at;
        ALTER TABLE report_artifacts ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE report_binaries DROP COLUMN IF EXISTS created_at;
        ALTER TABLE report_binaries ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(report_id)) STORED;
        ALTER TABLE invitations DROP COLUMN IF EXISTS created_at;
        ALTER TABLE invitations ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE tenant_secrets DROP COLUMN IF EXISTS created_at;
        ALTER TABLE tenant_secrets ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
        ALTER TABLE execution_assignments DROP COLUMN IF EXISTS created_at;
        ALTER TABLE execution_assignments ADD COLUMN created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) STORED;
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

-- PostgreSQL 19 Extended Multi-Column Statistics on VIRTUAL Generated Columns
DO $$
BEGIN
    IF current_setting('server_version_num')::int >= 190000 THEN
        CREATE STATISTICS IF NOT EXISTS stat_quorum_nodes_run_created ON run_id, created_at FROM quorum_nodes;
        CREATE STATISTICS IF NOT EXISTS stat_quorum_edges_run_created ON run_id, created_at FROM quorum_edges;
    END IF;
END $$;

-- B-Tree Indexes for Single-Round Wave Materialization & CTE Traversal
CREATE INDEX IF NOT EXISTS idx_quorum_nodes_run_type ON quorum_nodes (run_id, node_type);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_run_src_tgt ON quorum_edges (run_id, source_id, target_id);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_run_target ON quorum_edges (run_id, target_id);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_source_id ON quorum_edges (source_id);
CREATE INDEX IF NOT EXISTS idx_quorum_edges_target_id ON quorum_edges (target_id);
