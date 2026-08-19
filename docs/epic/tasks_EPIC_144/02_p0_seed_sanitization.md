# Phase 0-B: Master Seed Sanitization & Local Reseed

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 3 "Master Seed Sanitization" (L297-L303) and 6-Step Pipeline Step 1 (L240-L242)
**Scope:** Database/Seed Data & Seed Integrity Unit Tests

**Overview:** Sanitize `seed_data.json` to verify zero occurrences of legacy `include_diagnostic_scorecard` fields, ensure all `output_profiles` have valid enum-compatible values for `display_scale`, `scoring_strategy`, `preset_view`, and `text_delivery_mode`, and ensure bilingual `metric_mappings` are complete with the 4 required metadata label keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`). Implement automated guardrail unit tests in `backend_v2/tests/unit/test_seed_architectural_guardrails.py` to lock these invariants permanently, and execute local database reseed. This step MUST complete BEFORE any Pydantic model modifications (Plan 03).

**Target Files:**
- `[MODIFY]` `@[backend_v2/seed/seed_data.json#L9185-L9925]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L1-L93]`

**Context Files (Read-Only):**
- `@[backend_v2/models/enums.py#L69-L80]` — DisplayScale enum values
- `@[backend_v2/models/v2_core.py#L1330-L1375]` — OutputProfile current schema
- `@[.agents/rules/03_seed_vault.md]` — Seed Data Vault Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 01 (Backend Config & Enums) is complete — DisplayScale enum exists in @[backend_v2/models/enums.py] and authenticity thresholds exist in @[backend_v2/settings.py].</action>
    <action>Look forward: Verify the state of @[backend_v2/seed/seed_data.json#L9185-L9925] via a deterministic Python script to check whether `metric_mappings` metadata keys need to be added and whether `include_diagnostic_scorecard` is present.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\03_seed_vault.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/models/v2_core.py — Do NOT modify domain models yet (Plan 03)</file>
    <file>backend_v2/models/dtos/output_profile.py — Do NOT modify DTOs yet (Plan 03)</file>
    <file>backend_v2/settings.py — Already done in Plan 01</file>
    <file>backend_v2/models/enums.py — Already done in Plan 01</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
    <file>PromptBlock ai_description fields — Do NOT touch prompt texts (prompt_preservation_mandate). PromptBlock cleanup is Phase 3 scope.</file>
  </anti_targets>

  <dod_checklist>
    <item>Timestamped backup created in `backend_v2/seed/backups/` before modifying `seed_data.json`.</item>
    <item>All `output_profiles` in `seed_data.json` have valid enum keys for `display_scale` ("original", "custom", "normalized_100") and `scoring_strategy`.</item>
    <item>All `metric_mappings` in `output_profiles` are complete with bilingual entries for `metadata_user`, `metadata_organization`, `metadata_scoring_engine`, and `metadata_strictness`.</item>
    <item>Zero occurrences of `include_diagnostic_scorecard` remain in `seed_data.json`.</item>
    <item>Automated unit tests added to `backend_v2/tests/unit/test_seed_architectural_guardrails.py` verifying positive and negative seed data constraints.</item>
    <item>Local database re-seeded successfully via `uv run python backend_v2/seed/run_seed.py local`.</item>
    <item>Backend audit loop passes with 100% test pass rate and >90% coverage on test file.</item>
  </dod_checklist>

  <step id="1" name="CREATE TIMESTAMPED BACKUP OF MASTER SEED DATA">
    <action>Per `03_seed_vault.md` Step 2 (BACKUP), execute a PowerShell command via `run_command` to create a timestamped backup copy inside `backend_v2/seed/backups/`:
`New-Item -ItemType Directory -Force -Path backend_v2/seed/backups ; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_backup_p0b.json`</action>
    <constraint invariant="seed_backup_mandate">Modifying `seed_data.json` without an explicit backup is strictly prohibited.</constraint>
  </step>

  <step id="2" name="AUDIT CURRENT SEED DATA STATE VIA PYTHON">
    <action>Execute a Python audit check via `run_command` (avoiding grep_search on CRLF JSON per `03_seed_vault.md`):
`uv run python -c "import json; data=json.load(open('backend_v2/seed/seed_data.json', encoding='utf-8')); profiles=data.get('output_profiles', []); print(f'Profiles: {len(profiles)}'); [print(p['id'], list(p.get('metric_mappings', {}).keys())) for p in profiles]"`</action>
    <constraint>Verify that profile `prf_5d6e7f8091a2b3c4` is ready for the `metric_mappings` enhancement and has zero `include_diagnostic_scorecard` fields.</constraint>
  </step>

  <step id="3" name="SURGICALLY INJECT BILINGUAL METADATA KEYS INTO metric_mappings">
    <action>Use `multi_replace_file_content` on @[backend_v2/seed/seed_data.json#L9260-L9355] to add the 4 required metadata label keys (`metadata_user`, `metadata_organization`, `metadata_scoring_engine`, `metadata_strictness`) to `metric_mappings` of profile `prf_5d6e7f8091a2b3c4`:
```json
        "metadata_user": {
          "default_locale": "fi",
          "translations": {
            "fi": "Käyttäjä:",
            "en": "User:"
          }
        },
        "metadata_organization": {
          "default_locale": "fi",
          "translations": {
            "fi": "Organisaatio:",
            "en": "Organization:"
          }
        },
        "metadata_scoring_engine": {
          "default_locale": "fi",
          "translations": {
            "fi": "Arviointimoottori:",
            "en": "Scoring Engine:"
          }
        },
        "metadata_strictness": {
          "default_locale": "fi",
          "translations": {
            "fi": "Ankaruustaso:",
            "en": "Strictness Level:"
          }
        },
```</action>
    <constraint invariant="seed_metadata_contract">All profiles MUST define bilingual (en + fi) I18nText entries for all 4 metadata label keys. This enables MetadataAdapter (Phase 3) to strictly resolve labels via I18nText.resolve(locale) instead of hardcoded Finnish strings.</constraint>
  </step>

  <step id="4" name="JSON INTEGRITY & SYNTAX CHECK">
    <action>Per `03_seed_vault.md` Step 3.5, verify JSON syntax immediately via:
`uv run python -c "import json; data=json.load(open('backend_v2/seed/seed_data.json', encoding='utf-8')); print('JSON VALID: True, profiles:', len(data.get('output_profiles', [])))"`</action>
    <constraint invariant="circuit_breaker_protocol">If JSON parsing fails, restore backup immediately and HALT.</constraint>
  </step>

  <step id="5" name="IMPLEMENT AUTOMATED SEED INTEGRITY UNIT TESTS">
    <action>Update @[backend_v2/tests/unit/test_seed_architectural_guardrails.py] to add dedicated test cases:
1. `test_output_profiles_zero_legacy_diagnostic_scorecard()`: Verifies no profile contains `"include_diagnostic_scorecard"`.
2. `test_output_profiles_metric_mappings_contain_bilingual_metadata_keys()`: Verifies that every profile in `output_profiles` contains `metadata_user`, `metadata_organization`, `metadata_scoring_engine`, and `metadata_strictness` in `metric_mappings`, each having non-empty `fi` and `en` translations.
3. `test_output_profiles_enums_valid()`: Verifies `display_scale` in `{"original", "custom", "normalized_100"}` and `scoring_strategy` in `{"AVERAGE", "WATERFALL", "WEIGHTED_AVERAGE", "PURE_MATH"}`.</action>
    <constraint invariant="anti_happy_path_mandate">Include negative assertions testing that a malformed profile fixture without required metadata keys or with invalid enum strings fails validation.</constraint>
  </step>

  <step id="6" name="EXECUTE LOCAL DATABASE RESEED">
    <action>Execute: `uv run python backend_v2/seed/run_seed.py local`</action>
    <constraint invariant="local_database_reseed_mandate">The local TinyDB MUST be refreshed to eliminate stale keys before executing backend model modifications in Plan 03.</constraint>
    <constraint>The command MUST complete with exit code 0.</constraint>
  </step>

  <step id="7" name="RUN QUALITY AUDIT GATE">
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_seed_architectural_guardrails.py --test`</action>
    <constraint>Must achieve 100% test pass rate, strict MyPy typing pass, Ruff format/lint pass, and >90% coverage.</constraint>
  </step>

  <validation_gate>
    <check>Python check for "include_diagnostic_scorecard" in @[backend_v2/seed/seed_data.json] — MUST return zero results</check>
    <check>Python check for metadata keys in @[backend_v2/seed/seed_data.json] — MUST find all 4 bilingual keys in every output_profile</check>
    <check>uv run python backend_v2/seed/run_seed.py local — MUST exit 0</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_seed_architectural_guardrails.py --test — MUST pass all gates</check>
  </validation_gate>
</execution_protocol>
```
