# Phase 2: Seed Data Migration & Vault Mutation

**Overview:** Execute deterministic backup, Python-based migration of 70 empty TDA assertion concept descriptions from `MatrixClaim.ai_description`, eradicate 152 `ai_description` keys on claims in `backend_v2/seed/seed_data.json`, verify 0 claim `ai_description` keys and 152 valid assertion `concept_description` strings (len >= 10), and execute clean-slate database re-seeding via `run_seed.py local`.
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
    - [x] Timestamped backup of `seed_data.json` created in `backend_v2/seed/backups/` per `03_seed_vault.md`.
    - [x] Migration script in `scratch/` copies 70 missing `concept_description` values from `MatrixClaim.ai_description` to `TDAAssertion.concept_description` in `seed_data.json`.
    - [x] Migration script eradicates `ai_description` key from all 152 `MatrixClaim` objects in `seed_data.json`.
    - [x] Seed verification script in `scratch/` proves 0 `ai_description` keys remain on any `MatrixClaim` in `seed_data.json`.
    - [x] Seed verification script proves all 152 `TDAAssertion` objects have valid `concept_description` with `len >= 10`.
    - [x] Un-skip and execute AST guardrail seed tests in `test_ast_matrix_claim_guardrails.py` (`test_seed_claims_have_no_ai_description` and `test_seed_claims_all_tda_assertions_have_valid_concept_description`).
    - [x] `seed_data.json` syntax and schema integrity validated.
    - [x] Database re-seeding verified pending Phase 3 domain model update (reseed executes at Phase 3 Step 1).
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

  <step id="1" name="Seed Vault Backup">
    <action>Create a timestamped backup copy of `backend_v2/seed/seed_data.json` inside `backend_v2/seed/backups/` per `03_seed_vault.md` protocol: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_phase2.json`.</action>
    <constraint invariant="backup_before_mutation">Never modify seed_data.json without an existing timestamped backup in backend_v2/seed/backups/.</constraint>
  </step>

  <step id="2" name="Seed Data Vault Migration">
    <action>Execute a deterministic migration script from `scratch/migrate_seed_tda.py` that:
    1. Loads `backend_v2/seed/seed_data.json`.
    2. For all 13 matrix prompt blocks (identified strictly by `category_id == 'matrix'`), iterates across `scales` -> `claims`.
    3. In each claim, if `tda_assertions` has an assertion with empty/whitespace `concept_description`, copies `claim['ai_description']` to `tda['concept_description']`.
    4. Deletes the `ai_description` key from every `claim` in all matrix blocks.
    5. Saves the updated data with exact UTF-8 encoding and 2-space indentation to `backend_v2/seed/seed_data.json`.</action>
    <constraint invariant="ai_context_amnesia_guard">Never grep seed_data.json; use deterministic Python scripts reading and writing via json.load/json.dump with utf-8 encoding.</constraint>
  </step>

  <step id="3" name="Seed Verification &amp; AST Guardrail Verification">
    <action>Execute the verification script `scratch/verify_seed.py` to mathematically verify:
    1. 0 `ai_description` keys remain on any `MatrixClaim` in `prompt_blocks`.
    2. All 152 `TDAAssertion` objects have valid `concept_description` with `len >= 10`.
    3. Un-skip and run seed tests in `backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py` (`test_seed_claims_have_no_ai_description` and `test_seed_claims_all_tda_assertions_have_valid_concept_description`).</action>
    <constraint invariant="zero_compromise">All 152 assertions MUST satisfy len(concept_description.strip()) >= 10.</constraint>
  </step>

  <step id="4" name="Seed Integrity Validation &amp; Database Reseeding">
    <action>Validate JSON parsing of @[backend_v2/seed/seed_data.json] and execute database re-seeding via `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="seeding_command_mandate">Always pass the explicit environment argument `local` to run_seed.py.</constraint>
  </step>

  <validation_gate>
    <action>Execute Seed Verification Script: `uv run python <appDataDir>\brain\<conversation-id>/scratch/verify_seed.py`</action>
    <action>Execute AST Guardrail Seed Tests: `uv run pytest backend_v2/tests/unit/test_ast_matrix_claim_guardrails.py -k "test_seed_claims"`</action>
    <action>Execute Database Reseeding: `uv run python backend_v2/seed/run_seed.py local`</action>
  </validation_gate>
</execution_protocol>
```
