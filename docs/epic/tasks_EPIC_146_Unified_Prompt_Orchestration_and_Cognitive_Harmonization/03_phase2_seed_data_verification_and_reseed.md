# Phase 2: Seed Data Migration & Vault Mutation (Verification-Only)

**Overview:** Execute deterministic read-only audit script on seed_data.json to mathematically verify 0 ai_description keys remain on claims and all 152 TDA assertions have valid concept_description strings, followed by clean-slate database re-seeding.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/seed/seed_data.json].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_146_Unified_Prompt_Orchestration_and_Cognitive_Harmonization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Seed verification script in `scratch/` proves 0 `ai_description` keys remain on any `MatrixClaim` in `seed_data.json`.
    - [ ] Seed verification script proves all 152 `TDAAssertion` objects have non-empty `concept_description`.
    - [ ] `seed_data.json` syntax and schema integrity validated.
    - [ ] Database re-seeding executed via `uv run python backend_v2/seed/run_seed.py local`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_pipeline.md]</knowledge_item>
    <knowledge_item>@[ki_strict_sdui_serialization.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_adapter_pattern.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `db_v2.json` directly.
    - Do NOT modify Pydantic models in Phase 2.
    - Do NOT run seed scripts without the mandatory `local` environment parameter.
  </anti_targets>

  <step id="1" name="Seed Verification Script Execution">
    <action>Execute a read-only validation script from `scratch/` to confirm: 1) 0 `ai_description` keys remain on any `MatrixClaim` in `prompt_blocks`, 2) All 152 `TDAAssertion` objects have non-empty `concept_description` (pre-min_length enforcement).</action>
    <constraint invariant="ai_context_amnesia_guard">Never grep seed_data.json; use deterministic Python scripts reading via json.load.</constraint>
  </step>

  <step id="2" name="Seed Integrity Validation &amp; Database Reseeding">
    <action>Validate JSON parsing of @[backend_v2/seed/seed_data.json] and execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="seeding_command_mandate">Always pass the explicit environment argument `local` to run_seed.py.</constraint>
  </step>

  <validation_gate>
    <action>Execute Seed Verification Script: `uv run python <appDataDir>\brain\<conversation-id>/scratch/verify_seed.py`</action>
    <action>Execute Database Reseeding: `uv run python backend_v2/seed/run_seed.py local`</action>
  </validation_gate>
</execution_protocol>
```
