# Phase 2: Atomic Seed Data Migration & Database Re-seeding Gate (Vault Protocol)

**Overview:** Perform atomic migration on `backend_v2/seed/seed_data.json` following the Seed Vault Protocol. Populate `is_system_core` on all step definitions (`backend_v2/seed/seed_data.json#L8065-L9005`) and `is_synthesis_source` on all workflow step rules (`backend_v2/seed/seed_data.json#L7837-L8045`), verify JSON integrity, re-seed the local development database, and validate frontend domain parity.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L7837-L8045]
- `[MODIFY]` @[backend_v2/seed/seed_data.json#L8065-L9005]
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
    - [ ] `"is_system_core": true` configured for protected step definitions in `seed_data.json#L8065-L9005`: `sp_db849f9790984585` (Input Processing), `sp_192910b5f5a34c79` (XAI Reporter), `sp_d245365e4a274b9e` (Scoring Engine), and `sp_7a8b9c0d1e2f3a4b` (Synteesin Generointi).
    - [ ] `"is_system_core": false` configured explicitly for all remaining 15 step definitions in `seed_data.json#L8065-L9005`.
    - [ ] `"is_synthesis_source": false` configured for `sr_f0a26d17cc9b48a7` (Input Processing) in `seed_data.json#L7837-L8045`.
    - [ ] `"is_synthesis_source": true` configured explicitly for all remaining 15 step rules in `seed_data.json#L7837-L8045`.
    - [ ] JSON syntax and schema integrity verified via dry-run parse before re-seeding.
    - [ ] Local database re-seeded via `uv run python backend_v2/seed/run_seed.py local`.
    - [ ] Frontend domain parity test `client_app_v2/test/models/domain_parity_test.dart` passes.
    - [ ] Backend test suite `uv run pytest backend_v2/tests/unit/test_v2_core_models.py` and audit loop pass.
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
    <action>In @[backend_v2/seed/seed_data.json#L8065-L9005], update all 19 step items in the `steps` array:
1. Set `"is_system_core": true` for protected steps:
   - `sp_db849f9790984585` (Input Processing, lines 8066-8106)
   - `sp_192910b5f5a34c79` (XAI Reporter, lines 8752-8799)
   - `sp_d245365e4a274b9e` (Scoring Engine, lines 8846-8878)
   - `sp_7a8b9c0d1e2f3a4b` (Synteesin Generointi, lines 8983-9003)
2. Set `"is_system_core": false` explicitly for all remaining 15 steps in the `steps` array (specifically: `sp_b5c751d1cbe24735`, `sp_f22db9f1dde048b7`, `sp_bd0b3054fe664960`, `sp_25664f44773a4354`, `sp_7f9649114d2344dc`, `sp_6f40b964895c426b`, `sp_ddb7cf7c8a0245d4`, `sp_48974af1fc584407`, `sp_8daee218c6b14f02`, `sp_dfc365994fa944b2`, `sp_6a45d484ad5b497c`, `sp_76eedbc020274f66`, `sp_8ffee13639e64e34`, `sp_9c6a85edc29347b9`, `sp_fb1b8e908bf24c1f`).
    </action>
    <constraint invariant="seed_vault_mutation">Use native multi_replace_file_content with exact line boundaries; procedural data patch scripts are strictly banned.</constraint>
  </step>

  <step id="3" name="Workflow Step Rules Migration (is_synthesis_source)">
    <action>In @[backend_v2/seed/seed_data.json#L7837-L8045], update all 16 items in the `workflows[0].steps` array:
1. Set `"is_synthesis_source": false` for `sr_f0a26d17cc9b48a7` (Step 1: Input Processing `sp_db849f9790984585`, lines 7838-7848).
2. Set `"is_synthesis_source": true` for all other 15 cognitive specialist and funnel step rules in `workflows[0].steps` (specifically: `sr_0f7947ec7007498c`, `sr_02b7cc1e7c2a4a62`, `sr_5a8ae009eee44fe2`, `sr_99ca8c82a5aa48cd`, `sr_87f408aeee64462f`, `sr_d56fb84fbe13463a`, `sr_4d2272d8b4864847`, `sr_1d7e6d26b02b457b`, `sr_b4c328df1c4141c6`, `sr_566e3209a60444d3`, `sr_ba028623acab447a`, `sr_0228db320e8f41bb`, `sr_5f3dd7712a7f4bb3`, `sr_2fa56dc36614469a`, `sr_9e8d7c6b5a40312b`).
    </action>
    <constraint invariant="seed_vault_mutation">Strict alignment with Single Source of Truth structure.</constraint>
  </step>

  <step id="4" name="Seed Vault Verification & Local Re-Seeding">
    <action>Verify JSON syntax of @[backend_v2/seed/seed_data.json] via dry-run parser, and execute local database re-seed via @[backend_v2/seed/run_seed.py]: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="seeding_command_mandate">Seeding command must explicitly include the 'local' environment argument.</constraint>
  </step>

  <step id="5" name="Domain Parity & Backend Test Verification">
    <action>Run frontend domain parity test to verify background Isolate deserialization: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart` (or `flutter test test/models/domain_parity_test.dart` within `client_app_v2`).</action>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
  </step>

  <validation_gate>
    <action>Execute Seed Script: `uv run python backend_v2/seed/run_seed.py local`</action>
    <action>Execute Domain Parity Test: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart`</action>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```
