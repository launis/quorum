# Phase 2: Atomic Seed Data Migration & Database Re-seeding Gate (Vault Protocol)

**Overview:** Perform atomic migration on `backend_v2/seed/seed_data.json` following the Seed Vault Protocol. Populate `is_system_core` on all step definitions and `is_synthesis_source` on all workflow step rules, verify JSON integrity, re-seed the local development database, and validate frontend domain parity.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[backend_v2/seed/run_seed.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify that Step and StepRule models accept `is_system_core` and `is_synthesis_source` without validation errors.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true for @[backend_v2/seed/seed_data.json].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Timestamped backup of `seed_data.json` created in `backend_v2/seed/backups/seed_data_pre_epic145.json`.
    - [ ] `"is_system_core": true` configured for `sp_db849f9790984585`, `sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, and `sp_7a8b9c0d1e2f3a4b` in `seed_data.json` under `steps`.
    - [ ] `"is_system_core": false` configured for all remaining step definitions in `steps` array.
    - [ ] `"is_synthesis_source": false` configured for `sr_f0a26d17cc9b48a7` (Input Processing) in `workflows[0].steps`.
    - [ ] `"is_synthesis_source": true` configured for all other step rules in `workflows[0].steps`.
    - [ ] Local database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
    - [ ] Frontend domain parity test `client_app_v2/test/models/domain_parity_test.dart` passes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <backend>@[backend_v2/seed/run_seed.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT edit the live development database `db_v2.json` directly.
    - Do NOT write Python one-liner terminal scripts to modify `seed_data.json`.
    - Do NOT use `grep_search` on `seed_data.json` (CRLF encoding hazard).
  </anti_targets>

  <step id="1" name="Backup Seed Data">
    <action>Execute timestamped backup of `seed_data.json` before any mutations: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic145.json`.</action>
    <constraint invariant="live_database_mutation">All modifications must occur on seed_data.json with pre-flight backup.</constraint>
  </step>

  <step id="2" name="Step Definitions Migration (is_system_core)">
    <action>In @[backend_v2/seed/seed_data.json], update all step items in the `steps` array:
1. Set `"is_system_core": true` for protected steps:
   - `sp_db849f9790984585` (Input Processing)
   - `sp_192910b5f5a34c79` (XAI Reporter)
   - `sp_d245365e4a274b9e` (Scoring Engine)
   - `sp_7a8b9c0d1e2f3a4b` (Synteesin Generointi)
2. Set `"is_system_core": false` explicitly for all remaining steps in the `steps` array.
    </action>
    <constraint invariant="seed_vault_mutation">Use native multi_replace_file_content or bounded file edits; no procedural patch scripts.</constraint>
  </step>

  <step id="3" name="Workflow Step Rules Migration (is_synthesis_source)">
    <action>In @[backend_v2/seed/seed_data.json], update all items in the `workflows[0].steps` array:
1. Set `"is_synthesis_source": false` for `sr_f0a26d17cc9b48a7` (Step 1: Input Processing `sp_db849f9790984585`).
2. Set `"is_synthesis_source": true` for all other cognitive specialist and funnel step rules in `workflows[0].steps`.
    </action>
    <constraint invariant="seed_vault_mutation">Strict alignment with Single Source of Truth structure.</constraint>
  </step>

  <step id="4" name="Seed Vault Verification & Local Re-Seeding">
    <action>Verify JSON syntax of @[backend_v2/seed/seed_data.json] and execute local database re-seed via @[backend_v2/seed/run_seed.py]: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="seeding_command_mandate">Seeding command must explicitly include the 'local' environment argument.</constraint>
  </step>

  <step id="5" name="Domain Parity & Backend Test Verification">
    <action>Run frontend domain parity test to verify background isolate deserialization: `uv run flutter test client_app_v2/test/models/domain_parity_test.dart`.</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
  </step>

  <validation_gate>
    <action>Execute Seed Script: `uv run python backend_v2/seed/run_seed.py local`</action>
    <action>Execute Domain Parity Test: `uv run flutter test client_app_v2/test/models/domain_parity_test.dart`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```
